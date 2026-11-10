import { db } from './db'
import type { Problem } from '../../shared/problem'
let pending = 0,
  active = 0
const queue: (() => Promise<void>)[] = []
async function drain() {
  if (active >= 2 || !queue.length) return
  active++
  const work = queue.shift()!
  try {
    await work()
  } finally {
    active--
    pending--
    void drain()
  }
}
export async function judge(
  p: Problem,
  language: string,
  mode: 'acm' | 'function',
  code: string,
  customInput?: string,
  sampleOnly = false,
) {
  const variant = p.modes[mode]
  if (!variant || !variant.templates[language as 'python3' | 'cpp17'])
    throw createError({ statusCode: 400, statusMessage: '题目不支持该语言或输入模式' })
  if (['Hot100', '深度学习'].includes(p.category) && language !== 'python3')
    throw createError({ statusCode: 400, statusMessage: '该分类仅支持 Python3' })
  const cases =
    customInput !== undefined
      ? [
          {
            input: mode === 'function' && variant.runtime !== 'standard' ? '' : customInput,
            harness:
              mode === 'function' && variant.runtime !== 'standard' ? customInput : variant.harness,
          },
        ]
      : variant.cases
          .filter((c) => !sampleOnly || !c.hidden)
          .map((c) => ({ ...c, harness: c.harness || variant.harness }))
  if (!cases.length) throw createError({ statusCode: 400, statusMessage: '没有可运行用例' })
  const url = process.env.NUXT_SANDBOX_URL || 'http://127.0.0.1:4311',
    token = process.env.NUXT_SANDBOX_TOKEN
  try {
    const controller = new AbortController(),
      timer = setTimeout(() => controller.abort(), 180000)
    try {
      const response = await fetch(url + '/judge', {
        method: 'POST',
        headers: { authorization: 'Bearer ' + token, 'content-type': 'application/json' },
        body: JSON.stringify({
          code: variant.prelude + '\n' + code,
          language,
          mode,
          cases,
          timeMs: p.timeMs,
          memoryMb: p.memoryMb,
        }),
        signal: controller.signal,
      })
      if (!response.ok) throw new Error('sandbox unavailable')
      return await response.json()
    } finally {
      clearTimeout(timer)
    }
  } catch {
    throw createError({ statusCode: 503, statusMessage: '判题服务暂不可用，请检查沙箱服务' })
  }
}
export function enqueue(
  id: string,
  p: Problem,
  language: string,
  mode: 'acm' | 'function',
  code: string,
) {
  if (pending >= 8)
    throw createError({ statusCode: 429, statusMessage: '判题队列已满，请稍后重试' })
  pending++
  queue.push(async () => {
    const sql = db()
    await sql`UPDATE submissions SET status='RUNNING' WHERE id=${id}`
    try {
      const r = await judge(p, language, mode, code)
      await sql`UPDATE submissions SET status=${r.status},result=${sql.json(r)},finished_at=now() WHERE id=${id}`
    } catch {
      await sql`UPDATE submissions SET status='SYSTEM_ERROR',result=${sql.json({ error: '判题服务暂不可用' })},finished_at=now() WHERE id=${id}`
    }
  })
  void drain()
}
