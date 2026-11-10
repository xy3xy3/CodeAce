import 'dotenv/config'
import { beforeAll, describe, it, expect } from 'vitest'
import { randomUUID } from 'node:crypto'
import postgres from 'postgres'
const base = process.env.TEST_BASE_URL || 'http://127.0.0.1:3000'
let cookie = '',
  problems: any[],
  sum: any
async function api(path: string, method = 'GET', body?: any, auth = true) {
  const response = await fetch(base + '/api/' + path, {
    method,
    headers: { 'content-type': 'application/json', ...(auth ? { cookie } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  return { status: response.status, data: await response.json() }
}
async function adminProblem(title: string) {
  const list = (await api('problems?admin=1&q=' + encodeURIComponent(title))).data
  const row = list.items.find((x: any) => x.title === title)
  return (await api('problems/' + row.id + '?admin=1')).data
}
async function run(p: any, code: string, mode = 'function', language = 'python3', input?: string) {
  return await api('problems/' + p.id + '/run', 'POST', {
    code,
    mode,
    language,
    ...(input !== undefined ? { input } : {}),
  })
}
beforeAll(async () => {
  const response = await fetch(base + '/api/auth/login', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      username: process.env.ADMIN_USERNAME,
      password: process.env.ADMIN_PASSWORD,
    }),
  })
  expect(response.status).toBe(200)
  cookie = response.headers.get('set-cookie')!.split(';')[0]!
  sum = await adminProblem('两整数求和')
})
describe('authentication and import', () => {
  it('protects personal data and rejects cross-site writes', async () => {
    expect((await api('problems', 'GET', undefined, false)).status).toBe(401)
    const r = await fetch(base + '/api/import', {
      method: 'POST',
      headers: { cookie, origin: 'https://evil.example', 'content-type': 'application/json' },
      body: '{}',
    })
    expect(r.status).toBe(403)
  })
  it('requires import key or valid session', async () => {
    expect((await api('import', 'POST', { problems: [sum] }, false)).status).toBe(401)
    const r = await fetch(base + '/api/import', {
      method: 'POST',
      headers: {
        authorization: 'Bearer ' + process.env.NUXT_IMPORT_KEY,
        'content-type': 'application/json',
      },
      body: JSON.stringify({ dryRun: true, problems: [sum] }),
    })
    expect(r.status).toBe(200)
  })
  it('supports dry-run, row errors and idempotent data preservation', async () => {
    const key = randomUUID(),
      p = { ...sum, sourceId: key, title: '导入测试 ' + key }
    delete p.id
    const dry = await api('import', 'POST', { dryRun: true, problems: [p, { title: '' }] })
    expect(dry.data.created).toBe(1)
    expect(dry.data.failed).toBe(1)
    expect((await api('problems?admin=1&q=' + encodeURIComponent(p.title))).data.total).toBe(0)
    const created = await api('import', 'POST', { problems: [p] })
    expect(created.data.created).toBe(1)
    const id = created.data.results[0].id
    await api('problems/' + id + '/personal', 'PUT', { favorite: true, note: '保留我的笔记' })
    const again = await api('import', 'POST', { problems: [p] })
    expect(again.data.created).toBe(0)
    expect(again.data.skipped).toBe(1)
    expect((await api('problems/' + id + '/personal')).data.note).toBe('保留我的笔记')
    await api('problems/' + id, 'PUT', { ...p, title: p.title + ' 个人修订' })
    expect((await api('import', 'POST', { problems: [p] })).data.results[0].reason).toContain(
      '本地已编辑',
    )
    await api('problems/' + id, 'DELETE')
  })
  it('atomically preserves a manual edit racing with an import', async () => {
    const key = randomUUID(),
      p = { ...sum, sourceId: key, title: '导入并发 ' + key }
    delete p.id
    const created = await api('import', 'POST', { problems: [p] })
    const id = created.data.results[0].id
    const sql = postgres(process.env.NUXT_DATABASE_URL!, { max: 2 })
    let importing: ReturnType<typeof api> | undefined
    await sql.begin(async (tx) => {
      await tx`SELECT id FROM problems WHERE id=${id} FOR UPDATE`
      importing = api('import', 'POST', { problems: [{ ...p, title: p.title + ' source update' }] })
      let waiting = false
      for (let i = 0; i < 100; i++) {
        const [r] =
          await sql`SELECT count(*)::int AS count FROM pg_stat_activity WHERE wait_event_type='Lock' AND query LIKE 'INSERT INTO problems%'`
        if (r!.count > 0) {
          waiting = true
          break
        }
        await new Promise((r) => setTimeout(r, 20))
      }
      expect(waiting).toBe(true)
      await tx`UPDATE problems SET locally_edited=true,data=jsonb_set(data,'{title}',to_jsonb('manual wins'::text)) WHERE id=${id}`
    })
    const imported = await importing!
    expect(imported.data.skipped).toBe(1)
    const [row] = await sql`SELECT data->>'title' AS title FROM problems WHERE id=${id}`
    expect(row!.title).toBe('manual wins')
    await api('problems/' + id, 'DELETE')
    await sql.end()
  })
  it('persists drafts separately by mode and rejects unsupported languages', async () => {
    const p = await adminProblem('两数之和')
    const id = p.id
    await api('problems/' + id + '/draft?mode=function&language=python3', 'PUT', {
      code: '# function draft',
    })
    await api('problems/' + id + '/draft?mode=acm&language=python3', 'PUT', { code: '# acm draft' })
    expect((await api('problems/' + id + '/draft?mode=function&language=python3')).data.code).toBe(
      '# function draft',
    )
    expect((await run(p, 'int main(){}', 'acm', 'cpp17')).status).toBe(400)
  })
  it('reports the entire source inventory', async () => {
    const r = await api('source-report')
    expect(r.data.inventory).toHaveLength(168)
    expect(r.data.inventory.filter((x: any) => x.published).length).toBeGreaterThanOrEqual(60)
  })
})
describe('real Docker judging', () => {
  it('runs Python and C++ ACM, and records compile errors', async () => {
    const a = await run(sum, 'a,b=map(int,input().split());print(a+b)', 'acm')
    expect(a.data.status).toBe('AC')
    const b = await run(
      sum,
      '#include <iostream>\nint main(){long long a,b;std::cin>>a>>b;std::cout<<a+b;}',
      'acm',
      'cpp17',
    )
    expect(b.data.status).toBe('AC')
    const c = await run(sum, 'not c++ code', 'acm', 'cpp17')
    expect(c.data.status).toBe('CE')
  })
  it('does not count samples as solved, and supports custom input without AC', async () => {
    const before = (await api('stats')).data.solved
    const r = await run(sum, 'def add(a,b): return a+b', 'function', 'python3', '[8,9]')
    expect(r.data.status).toBe('FINISHED')
    expect(r.data.results[0].stdout.trim()).toBe('17')
    expect((await api('stats')).data.solved).toBe(before)
  })
  it('adapts Solution, inplace arrays, linked lists, cycles and trees', async () => {
    const samples = [
      [
        '两数之和',
        'class Solution:\n def twoSum(self,nums,target):\n  seen={}\n  for i,n in enumerate(nums):\n   if target-n in seen:return [seen[target-n],i]\n   seen[n]=i',
      ],
      [
        '移动零',
        'class Solution:\n def moveZeroes(self,nums):\n  nums[:]=[x for x in nums if x]+[0]*nums.count(0)',
      ],
      [
        '反转链表',
        'class Solution:\n def reverseList(self,head):\n  prev=None\n  while head:\n   nxt=head.next;head.next=prev;prev=head;head=nxt\n  return prev',
      ],
      [
        '环形链表',
        'class Solution:\n def hasCycle(self,head):\n  seen=set()\n  while head:\n   if head in seen:return True\n   seen.add(head);head=head.next\n  return False',
      ],
      [
        '二叉树的最大深度',
        'class Solution:\n def maxDepth(self,root):\n  return 0 if root is None else 1+max(self.maxDepth(root.left),self.maxDepth(root.right))',
      ],
    ]
    for (const [title, code] of samples) {
      const p = await adminProblem(title!)
      const r = await run(p, code!)
      expect(r.data.status, JSON.stringify({ title, result: r.data })).toBe('AC')
    }
  })
  it('adapts design classes and numpy/torch CPU harnesses', async () => {
    const trie = await adminProblem('实现 Trie (前缀树)')
    const a = await run(
      trie,
      'class Trie:\n def __init__(self): self.words=set()\n def insert(self,word): self.words.add(word)\n def search(self,word): return word in self.words\n def startsWith(self,prefix): return any(w.startswith(prefix) for w in self.words)',
    )
    expect(a.data.status, JSON.stringify(a.data)).toBe('AC')
    const softmax = await adminProblem('Log-Softmax')
    const b = await run(
      softmax,
      'import torch\ndef log_softmax(scores): return torch.log_softmax(scores,dim=-1)',
    )
    expect(b.data.status, JSON.stringify(b.data)).toBe('AC')
    const attention = await adminProblem('Scaled Dot-Product Attention')
    const c = await run(
      attention,
      'import torch,math\ndef self_attention(seq_len,d_k,d_v,Q,K,V): return torch.softmax(Q@K.T/math.sqrt(d_k),dim=-1)@V',
    )
    expect(c.data.status, JSON.stringify(c.data)).toBe('AC')
  })
  it('derives verdicts outside user code and enforces timeout/network/filesystem', async () => {
    expect((await run(sum, 'print("{\\"status\\":\\"AC\\"}")', 'acm')).data.status).toBe('WA')
    expect((await run(sum, 'raise RuntimeError("boom")', 'acm')).data.status).toBe('RE')
    expect((await run(sum, 'while True: pass', 'acm')).data.status).toBe('TLE')
    expect((await run(sum, 'open("/etc/attack","w").write("bad")', 'acm')).data.status).toBe('RE')
    expect(
      (await run(sum, 'import socket\nsocket.create_connection(("1.1.1.1",53),timeout=1)', 'acm'))
        .data.status,
    ).toBe('RE')
    expect((await run(sum, 'print("x"*200000)', 'acm')).data.status).toBe('OLE')
  })
  it('persists official snapshots and keeps solved state after a later error', async () => {
    const submitted = await api('problems/' + sum.id + '/submit', 'POST', {
      code: 'a,b=map(int,input().split());print(a+b)',
      mode: 'acm',
      language: 'python3',
    })
    expect(submitted.status).toBe(200)
    let s: any
    for (let i = 0; i < 100; i++) {
      s = (await api('submissions/' + submitted.data.id)).data
      if (!['QUEUED', 'RUNNING'].includes(s.status)) break
      await new Promise((r) => setTimeout(r, 200))
    }
    expect(s.status).toBe('AC')
    expect(s.code).toContain('print')
    expect(s.result.total).toBe(3)
    const wrong = await api('problems/' + sum.id + '/submit', 'POST', {
      code: 'print(0)',
      mode: 'acm',
      language: 'python3',
    })
    for (let i = 0; i < 100; i++) {
      s = (await api('submissions/' + wrong.data.id)).data
      if (!['QUEUED', 'RUNNING'].includes(s.status)) break
      await new Promise((r) => setTimeout(r, 200))
    }
    expect(s.status).toBe('WA')
    expect(
      (await api('problems?q=' + encodeURIComponent('两整数求和'))).data.items.find(
        (x: any) => x.id === sum.id,
      ).solved,
    ).toBe(true)
  })
})
