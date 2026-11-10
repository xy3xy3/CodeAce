import 'dotenv/config'
import { readFile } from 'node:fs/promises'
import postgres from 'postgres'
import { problemSchema, type Problem } from '../shared/problem'
import { convertSource } from './convert-codeky'
import { hotCatalog } from './hot-catalog'
import { deepCatalog } from './deep-catalog'
const sql = postgres(process.env.NUXT_DATABASE_URL!)
const envelope = JSON.parse(await readFile('database/sources/codeky.json', 'utf8'))
const source = typeof envelope.data === 'string' ? JSON.parse(envelope.data) : envelope
const supplemental = new Map(
  [...(await hotCatalog()), ...deepCatalog()].map((p) => [p.sourceId, p]),
)
let imported = 0
for (const item of source.inventory) {
  const r = source.records.find((r: any) => r.sourceId === item.id)
  let status = !r
      ? 'pending'
      : r.status === 429
        ? 'rate-limited'
        : r.problem?.access_locked
          ? 'locked'
          : !r.problem
            ? 'error'
            : 'ready',
    reason = ''
  let p: Problem | undefined
  if (status === 'ready') {
    try {
      p = problemSchema.parse(await convertSource(r.problem))
    } catch (e) {
      status = 'needs-review'
      reason = String(e)
    }
  }
  if (!p && supplemental.has(String(item.id))) {
    p = supplemental.get(String(item.id))
    status = 'ready-original'
    reason = 'CodeAce 独立编写的同主题练习，保留题名目录关联；未访问原站'
  }
  if (p) {
    await sql`INSERT INTO problems(source,source_id,data) VALUES(${p.source},${p.sourceId},${sql.json(p)}) ON CONFLICT(source,source_id) DO UPDATE SET data=excluded.data,version=CASE WHEN problems.data=excluded.data THEN problems.version ELSE problems.version+1 END,updated_at=now() WHERE NOT problems.locally_edited`
    imported++
  }
  if (status === 'locked') reason = r.problem.access_lock_reason || 'source locked'
  if (status === 'rate-limited') reason = '历史源站 429；在线采集已停用'
  await sql`INSERT INTO source_inventory(source,source_id,title,category,status,reason) VALUES('codeky',${String(item.id)},${item.title},${/^Hot ?100$/.test(item.category) ? 'Hot100' : item.category},${status},${reason}) ON CONFLICT(source,source_id) DO UPDATE SET status=excluded.status,reason=excluded.reason`
}
const demo: Problem = problemSchema.parse({
  title: '两整数求和',
  source: 'personal',
  sourceId: 'sum-two',
  category: '通用算法',
  difficulty: '简单',
  tags: ['入门', '输入输出'],
  description: '给定两个整数 **a** 和 **b**，计算它们的和。\n\n这是开始练习 ACM 输入输出的第一步。',
  inputDescription: '一行两个整数 a、b，以空格分隔。',
  outputDescription: '输出一个整数，表示 a + b。',
  constraints: '−10⁹ ≤ a, b ≤ 10⁹',
  hint: 'Python 可使用 map(int, input().split())；C++ 可使用 cin。',
  solution:
    '```python\na, b = map(int, input().split())\nprint(a + b)\n```\n\n时间复杂度 O(1)，空间复杂度 O(1)。',
  published: true,
  modes: {
    acm: {
      templates: {
        python3: 'a, b = map(int, input().split())\n# 输出 a + b\n',
        cpp17:
          '#include <iostream>\nusing namespace std;\nint main() {\n    long long a, b;\n    cin >> a >> b;\n    // 输出 a + b\n    return 0;\n}\n',
      },
      cases: [
        { input: '3 5\n', expected: '8' },
        { input: '-2 7\n', expected: '5', hidden: true },
        { input: '1000000000 1000000000\n', expected: '2000000000', hidden: true },
      ],
    },
    function: {
      templates: { python3: 'def add(a: int, b: int) -> int:\n    pass\n' },
      harness: 'import json,sys\nargs=json.loads(sys.stdin.read())\nprint(add(*args))',
      inputHelp: 'JSON 参数数组，例如 [3, 5]',
      cases: [
        { input: '[3,5]', expected: '8' },
        { input: '[-2,7]', expected: '5', hidden: true },
      ],
    },
  },
})
await sql`INSERT INTO problems(source,source_id,data) VALUES(${demo.source},${demo.sourceId},${sql.json(demo)}) ON CONFLICT(source,source_id) DO UPDATE SET data=excluded.data WHERE NOT problems.locally_edited`
console.log({
  target: source.inventory.length,
  imported,
  notes: 'See source-report for locked, pending and rate-limited entries',
})
await sql.end()
