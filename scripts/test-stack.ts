/** Reproducible real-service tests in a disposable database; personal data is never touched. */
import 'dotenv/config'
import postgres from 'postgres'
import { spawn, type ChildProcess } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { once } from 'node:events'
const original = process.env.NUXT_DATABASE_URL
if (!original) throw new Error('Configure .env and start PostgreSQL and sandbox first')
const admin = postgres(original, { max: 1 }),
  name = 'codeace_test_' + randomUUID().replaceAll('-', '').slice(0, 16)
const url = new URL(original)
url.pathname = '/' + name
const port = process.env.TEST_APP_PORT || '3010'
const env = {
  ...process.env,
  NUXT_DATABASE_URL: url.toString(),
  PORT: port,
  TEST_BASE_URL: 'http://127.0.0.1:' + port,
}
let app: ChildProcess | undefined
async function run(program: string, args: string[]) {
  const child = spawn(program, args, { env, stdio: 'inherit' })
  const [code] = await once(child, 'exit')
  if (code !== 0) throw new Error(program + ' ' + args[0] + ' failed (' + code + ')')
}
await admin.unsafe('CREATE DATABASE "' + name + '"')
try {
  for (const script of ['migrate', 'setup', 'seed'])
    await run('pnpm', ['exec', 'tsx', 'scripts/' + script + '.ts'])
  app = spawn(process.execPath, ['.output/server/index.mjs'], {
    env,
    stdio: ['ignore', 'ignore', 'inherit'],
  })
  let ready = false
  for (let i = 0; i < 150; i++) {
    try {
      const r = await fetch(env.TEST_BASE_URL + '/api/auth/me')
      if (r.status === 401) {
        ready = true
        break
      }
    } catch {}
    await new Promise((r) => setTimeout(r, 100))
  }
  if (!ready) throw new Error('Test application did not start')
  await run('pnpm', ['exec', 'vitest', 'run'])
  await run('pnpm', ['exec', 'playwright', 'test'])
  console.log('Isolated test stack passed. Personal database was not modified.')
} finally {
  if (app && app.exitCode === null) {
    app.kill('SIGTERM')
    await Promise.race([once(app, 'exit'), new Promise((r) => setTimeout(r, 2000))])
    if (app.exitCode === null) app.kill('SIGKILL')
  }
  await admin.unsafe('DROP DATABASE "' + name + '" WITH (FORCE)')
  await admin.end()
}
