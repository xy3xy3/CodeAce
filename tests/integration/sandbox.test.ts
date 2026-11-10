import { spawn, type ChildProcess } from 'node:child_process'
import { beforeAll, afterAll, it, expect } from 'vitest'
const port = 14312,
  token = 'local-integration-token-with-no-user-secrets'
let service: ChildProcess
const headers = { authorization: 'Bearer ' + token, 'content-type': 'application/json' }
async function send(body: any, signal?: AbortSignal) {
  const r = await fetch(`http://127.0.0.1:${port}/judge`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
    signal,
  })
  return await r.json()
}
const base = {
  language: 'python3',
  mode: 'acm',
  timeMs: 5000,
  memoryMb: 128,
  cases: [{ input: '', expected: '1' }],
}
beforeAll(async () => {
  service = spawn('node', ['sandbox/service.mjs'], {
    env: {
      ...process.env,
      SANDBOX_PORT: String(port),
      SANDBOX_TOKEN: token,
      SANDBOX_JOB_TIMEOUT_MS: '1500',
    },
    stdio: 'ignore',
  })
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${port}/health`, { headers })
      if (r.ok) return
    } catch {}
    await new Promise((r) => setTimeout(r, 50))
  }
  throw new Error('Test sandbox not listening')
})
afterAll(() => service?.kill('SIGTERM'))
it('supports C++ function harness and treats binary output as WA', async () => {
  const r = await send({
    ...base,
    code: 'int add(int a,int b){return a+b;}',
    language: 'cpp17',
    mode: 'function',
    cases: [
      {
        input: '',
        expected: '3',
        harness: '#include <iostream>\nint main(){std::cout<<add(1,2);}',
      },
    ],
  })
  expect(r.status).toBe('AC')
  const binary = await send({ ...base, code: 'import os\nos.write(1,bytes([255]))' })
  expect(binary.status).toBe('WA')
})
it('enforces total job deadline and frees the execution slot', async () => {
  const started = Date.now()
  const r = await send({ ...base, code: 'while True: pass' })
  expect(r.status).toBe('TLE')
  expect(Date.now() - started).toBeLessThan(6000)
  const state = await fetch(`http://127.0.0.1:${port}/health`, { headers }).then((r) => r.json())
  expect(state.active).toBe(0)
})
it('cancels a disconnected client and releases the slot', async () => {
  const controller = new AbortController()
  const pending = send({ ...base, code: 'import time\ntime.sleep(20)' }, controller.signal).catch(
    () => null,
  )
  await new Promise((r) => setTimeout(r, 250))
  controller.abort()
  await pending
  let active = 2
  for (let i = 0; i < 80; i++) {
    const s = await fetch(`http://127.0.0.1:${port}/health`, { headers }).then((r) => r.json())
    active = s.active
    if (active === 0) break
    await new Promise((r) => setTimeout(r, 50))
  }
  expect(active).toBe(0)
})
