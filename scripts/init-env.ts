import { randomBytes } from 'node:crypto'
import { writeFile } from 'node:fs/promises'
const password = randomBytes(24).toString('hex'),
  admin = randomBytes(18).toString('base64url')
const text = `POSTGRES_DB=codeace
POSTGRES_USER=codeace
POSTGRES_PASSWORD=${password}
POSTGRES_PORT=5436
NUXT_DATABASE_URL=postgres://codeace:${password}@127.0.0.1:5436/codeace
NUXT_SANDBOX_URL=http://127.0.0.1:4311
NUXT_SANDBOX_TOKEN=${randomBytes(32).toString('hex')}
NUXT_IMPORT_KEY=${randomBytes(32).toString('hex')}
ADMIN_USERNAME=admin
ADMIN_PASSWORD=${admin}
NUXT_COOKIE_SECURE=false
`
try {
  await writeFile('.env', text, { flag: 'wx', mode: 0o600 })
  console.log(
    'Created .env with random credentials. Read ADMIN_USERNAME / ADMIN_PASSWORD locally to sign in.',
  )
} catch (e: any) {
  if (e.code === 'EEXIST') console.log('.env already exists; preserved without changes.')
  else throw e
}
