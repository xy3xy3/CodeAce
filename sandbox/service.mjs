import http from 'node:http'
import { spawn } from 'node:child_process'
import { randomUUID, timingSafeEqual } from 'node:crypto'
import { compare } from './compare.mjs'
const token = process.env.SANDBOX_TOKEN
if (!token || token.length < 24) throw new Error('SANDBOX_TOKEN must be at least 24 characters')
const image = process.env.SANDBOX_IMAGE || 'codeace-runtime:local'
const jobBudget = Math.min(
  150000,
  Math.max(500, Number(process.env.SANDBOX_JOB_TIMEOUT_MS) || 150000),
)
let active = 0
function command(args, input = '', timeout = 30000, signal) {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(new Error('Job cancelled'))
    const p = spawn('docker', args)
    const abort = () => {
      p.kill('SIGKILL')
      reject(new Error('Job cancelled'))
    }
    signal?.addEventListener('abort', abort, { once: true })
    let out = '',
      err = '',
      total = 0
    const timer = setTimeout(() => {
      p.kill('SIGKILL')
      reject(new Error('Docker control timeout'))
    }, timeout)
    p.stdout.on('data', (d) => {
      total += d.length
      if (total > 1024 * 1024) p.kill('SIGKILL')
      else out += d
    })
    p.stderr.on('data', (d) => {
      if (err.length < 8000) err += d
    })
    p.on('error', (e) => {
      clearTimeout(timer)
      reject(e)
    })
    p.on('close', (code) => {
      signal?.removeEventListener('abort', abort)
      clearTimeout(timer)
      resolve({ code, out, err })
    })
    p.stdin.on('error', () => {})
    p.stdin.end(input)
  })
}
async function run(job, test, deadline, signal) {
  const name = 'codeace-job-' + randomUUID()
  const memory = Math.min(2048, Math.max(64, job.memoryMb || 512))
  const time = Math.min(30000, Math.max(100, job.timeMs || 3000))
  const started = performance.now()
  const remaining = deadline - Date.now()
  if (remaining <= 0 || signal.aborted)
    return { status: 'TLE', stderr: '超过总判题时间预算', stdout: '', timeMs: 0, memoryKb: 0 }
  try {
    const r = await command(
      [
        'run',
        '--name',
        name,
        '-i',
        '--network=none',
        '--user=65534:65534',
        '--read-only',
        '--cap-drop=ALL',
        '--security-opt=no-new-privileges',
        '--pids-limit=64',
        '--cpus=1',
        `--memory=${memory}m`,
        `--memory-swap=${memory}m`,
        '--ulimit',
        'nofile=64:64',
        '--tmpfs',
        '/work:rw,exec,nosuid,nodev,size=32m,mode=1777',
        image,
      ],
      JSON.stringify({
        source: job.code,
        language: job.language,
        harness: job.mode === 'function' ? test.harness || '' : '',
        input: test.input || '',
        timeMs: time,
      }) + '\n',
      Math.min(time + 25000, remaining),
      signal,
    )
    const inspect = await command(['inspect', '--format', '{{.State.OOMKilled}}', name])
    if (inspect.out.trim() === 'true')
      return {
        status: 'MLE',
        stderr: '超过内存限制',
        stdout: '',
        timeMs: Math.round(performance.now() - started),
        memoryKb: memory * 1024,
      }
    if (r.code !== 0)
      return { status: 'SYSTEM_ERROR', stderr: '沙箱异常退出', stdout: '', timeMs: 0, memoryKb: 0 }
    let data
    try {
      data = JSON.parse(r.out)
    } catch {
      return {
        status: 'SYSTEM_ERROR',
        stderr: '执行器返回无效数据',
        stdout: '',
        timeMs: 0,
        memoryKb: 0,
      }
    }
    // No status supplied by the container is accepted as a verdict.
    const status = data.compileError
      ? 'CE'
      : data.timeout
        ? 'TLE'
        : data.outputLimit
          ? 'OLE'
          : data.exit !== 0
            ? data.exit === -24
              ? 'TLE'
              : 'RE'
            : test.expected === undefined
              ? 'FINISHED'
              : compare(
                    data.stdout,
                    test.expected,
                    test.compare,
                    test.absTolerance,
                    test.relTolerance,
                  )
                ? 'AC'
                : 'WA'
    return { ...data, status, memoryKb: data.memoryKb || 0 }
  } catch (e) {
    if (signal.aborted || Date.now() >= deadline)
      return {
        status: 'TLE',
        stderr: signal.aborted ? '任务已取消' : '超过总判题时间预算',
        stdout: '',
        timeMs: Math.round(performance.now() - started),
        memoryKb: 0,
      }
    throw e
  } finally {
    await command(['rm', '-f', name]).catch(() => {})
  }
}
const server = http.createServer(async (req, res) => {
  const finish = (status, data) => {
    if (res.destroyed || res.writableEnded) return
    res.writeHead(status, { 'content-type': 'application/json' })
    res.end(JSON.stringify(data))
  }
  const supplied = Buffer.from((req.headers.authorization || '').replace(/^Bearer /, ''))
  const wanted = Buffer.from(token)
  if (supplied.length !== wanted.length || !timingSafeEqual(supplied, wanted))
    return finish(401, { error: 'Unauthorized' })
  if (req.method === 'GET' && req.url === '/health') return finish(200, { ok: true, active })
  if (req.method !== 'POST' || req.url !== '/judge') return finish(404, { error: 'Not found' })
  if (active >= 2) return finish(503, { error: '判题队列已满，请稍后重试' })
  active++
  const controller = new AbortController()
  res.on('close', () => {
    if (!res.writableEnded) controller.abort()
  })
  const deadline = Date.now() + jobBudget
  try {
    let body = ''
    for await (const c of req) {
      body += c
      if (body.length > 2 * 1024 * 1024) throw new Error('Request too large')
    }
    const job = JSON.parse(body)
    if (
      !['python3', 'cpp17'].includes(job.language) ||
      !['acm', 'function'].includes(job.mode) ||
      typeof job.code !== 'string' ||
      job.code.length > 100000 ||
      !Array.isArray(job.cases) ||
      !job.cases.length ||
      job.cases.length > 100
    )
      return finish(400, { error: 'Invalid job' })
    let results = []
    for (const test of job.cases) {
      const result = await run(job, test, deadline, controller.signal)
      results.push({
        ...result,
        input: test.hidden ? undefined : test.input,
        expected: test.hidden ? undefined : test.expected,
      })
      if (!['AC', 'FINISHED'].includes(result.status)) break
    }
    const fail = results.find((r) => !['AC', 'FINISHED'].includes(r.status))
    finish(200, {
      status: fail?.status || (results.every((r) => r.status === 'AC') ? 'AC' : 'FINISHED'),
      results,
      passed: results.filter((r) => r.status === 'AC').length,
      total: job.cases.length,
      timeMs: Math.max(...results.map((r) => r.timeMs || 0)),
      memoryKb: Math.max(...results.map((r) => r.memoryKb || 0)),
    })
  } catch (e) {
    finish(503, {
      error: '判题服务暂不可用',
      detail: process.env.NODE_ENV === 'test' ? String(e) : undefined,
    })
  } finally {
    active--
  }
})
server.requestTimeout = 180000
server.timeout = 175000
server.listen(Number(process.env.SANDBOX_PORT || 4311), '0.0.0.0', () =>
  console.log('CodeAce sandbox listening'),
)
