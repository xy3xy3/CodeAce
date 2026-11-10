import { readFile } from 'node:fs/promises'
import { problemSchema, type Problem } from '../shared/problem'

type Entry = {
  id: number
  title: string
  sourceUrl: string
  difficulty: Problem['difficulty']
  method: string
  args: string[]
  description: string
  output: string
  constraints: string
  idea: string
  complexity: string
  tags: string[]
  compare: NonNullable<Problem['modes']['function']>['cases'][number]['compare']
  cases: { input: Record<string, unknown>; expected: unknown }[]
}

// Statements, explanations and implementations are authored for CodeAce.
// The IDs retain the local inventory topic mapping; they do not imply copied source text.
export async function hotCatalog(): Promise<Problem[]> {
  const data = JSON.parse(
    await readFile(new URL('../database/hot-data.json', import.meta.url), 'utf8'),
  ) as Entry[]
  const references = await readFile(
    new URL('../database/hot-reference.py', import.meta.url),
    'utf8',
  )
  return data.map((entry) => {
    const reference = references
      .match(new RegExp(`# @${entry.id}\\n([\\s\\S]*?)(?=\\n# @|$)`))?.[1]
      ?.trim()
    if (!reference) throw new Error(`Missing original Hot100 reference ${entry.id}`)
    const className =
      entry.id === 1541 ? 'MinStack' : entry.id === 1547 ? 'MedianFinder' : undefined
    const mutate = entry.id === 1569 || entry.id === 1570
    const template = className
      ? className === 'MinStack'
        ? 'class MinStack:\n    def __init__(self):\n        pass\n\n    def push(self, val):\n        pass\n\n    def pop(self):\n        pass\n\n    def top(self):\n        pass\n\n    def getMin(self):\n        pass\n'
        : 'class MedianFinder:\n    def __init__(self):\n        pass\n\n    def addNum(self, num):\n        pass\n\n    def findMedian(self):\n        pass\n'
      : `class Solution:\n    def ${entry.method}(self, ${entry.args.join(', ')}):\n        # ${mutate ? '原地修改 nums；无需返回值' : '返回题目要求的结果'}\n        pass\n`
    const harness = className
      ? `import json, sys
_payload = json.loads(sys.stdin.read())
_operations, _arguments = _payload['operations'], _payload['arguments']
if not _operations or _operations[0] != '${className}' or len(_operations) != len(_arguments):
    raise ValueError('operations/arguments 格式错误')
_instance = ${className}(*_arguments[0])
_results = [None]
_allowed = ${className === 'MinStack' ? "{'push', 'pop', 'top', 'getMin'}" : "{'addNum', 'findMedian'}"}
for _operation, _args in zip(_operations[1:], _arguments[1:]):
    if _operation not in _allowed:
        raise ValueError('不支持的操作: ' + _operation)
    _value = getattr(_instance, _operation)(*_args)
    _results.append(None if _operation in {'push', 'pop', 'addNum'} else _value)
print(json.dumps(_results, ensure_ascii=False, allow_nan=False))
`
      : `import json, sys
_payload = json.loads(sys.stdin.read())
_result = Solution().${entry.method}(${entry.args.map((arg) => `_payload[${JSON.stringify(arg)}]`).join(', ')})
print(json.dumps(${mutate ? "_payload['nums']" : '_result'}, ensure_ascii=False, allow_nan=False))
`
    const inputHelp = className
      ? '输入一个 JSON 对象，包含等长的 operations（操作名数组）和 arguments（逐次调用的参数数组）。首个操作为构造函数。示例：' +
        JSON.stringify(entry.cases[0]!.input)
      : `输入一个 JSON 对象，字段按函数参数命名：${entry.args.join('、')}。示例：${JSON.stringify(entry.cases[0]!.input)}。无需自行读取输入或打印输出。`
    return problemSchema.parse({
      title: entry.title,
      category: 'Hot100',
      difficulty: entry.difficulty,
      tags: entry.tags,
      description:
        entry.description +
        '\n\n本题题面与参考题解由 CodeAce 原创编写，题源链接提供公开的同主题算法题参考。',
      inputDescription: inputHelp,
      outputDescription: entry.output,
      constraints: entry.constraints,
      hint: entry.idea,
      solution: `${entry.idea}\n\n${entry.complexity}\n\n\`\`\`python\n${reference}\n\`\`\``,
      source: 'codeace-original',
      sourceUrl: entry.sourceUrl,
      sourceId: String(entry.id),
      published: true,
      timeMs: 3000,
      memoryMb: 512,
      modes: {
        function: {
          templates: { python3: template },
          prelude:
            'from typing import *\nfrom collections import *\nimport heapq\nimport bisect\nimport math\n',
          harness,
          inputHelp,
          runtime: 'standard',
          cases: entry.cases.map((test, index) => ({
            input: JSON.stringify(test.input),
            expected: JSON.stringify(test.expected),
            hidden: index >= 2,
            compare: entry.compare,
          })),
        },
      },
      samples: entry.cases.slice(0, 2).map((test) => ({
        input: JSON.stringify(test.input),
        output: JSON.stringify(test.expected),
        explanation: className
          ? '结果与每次操作一一对应，构造与修改操作的结果为 null。'
          : entry.output,
      })),
    })
  })
}
