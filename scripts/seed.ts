import 'dotenv/config'
import { readFile } from 'node:fs/promises'
import postgres from 'postgres'
import { problemSchema, type Problem } from '../shared/problem'
import { hotCatalog } from './hot-catalog'
import { deepCatalog } from './deep-catalog'
const sql = postgres(process.env.NUXT_DATABASE_URL!)
const problems = [...(await hotCatalog()), ...deepCatalog()]
let imported = 0
for (const p of problems) {
  await sql`INSERT INTO problems(source,source_id,data) VALUES(${p.source},${p.sourceId},${sql.json(p)}) ON CONFLICT(source,source_id) DO UPDATE SET data=excluded.data,version=CASE WHEN problems.data=excluded.data THEN problems.version ELSE problems.version+1 END,updated_at=now() WHERE NOT problems.locally_edited`
  await sql`INSERT INTO source_inventory(source,source_id,title,category,status,reason) VALUES(${p.source},${p.sourceId},${p.title},${p.category},'ready','') ON CONFLICT(source,source_id) DO UPDATE SET title=excluded.title,category=excluded.category,status=excluded.status,reason=excluded.reason`
  imported++
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
console.log({ imported: imported + 1 })
await sql.end()
