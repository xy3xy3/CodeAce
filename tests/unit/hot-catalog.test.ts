import { spawnSync } from 'node:child_process'
import { describe, expect, it } from 'vitest'
import { hotCatalog } from '../../scripts/hot-catalog'
import { problemSchema } from '../../shared/problem'
import { compare } from '../../sandbox/compare.mjs'

describe('original Hot100 catalog', () => {
  it('covers every missing inventory topic with runnable Python contracts', async () => {
    const catalog = await hotCatalog()
    expect(catalog.map((problem) => problem.sourceId)).toEqual(
      Array.from({ length: 43 }, (_, index) => String(1529 + index)),
    )
    for (const problem of catalog) {
      expect(problemSchema.safeParse(problem).success).toBe(true)
      expect(problem.source).toBe('codeace-original')
      expect(problem.sourceUrl).toMatch(/^https:\/\/leetcode\.com\/problems\//)
      expect(problem.category).toBe('Hot100')
      expect(problem.modes.function!.cases.length).toBeGreaterThanOrEqual(3)
      expect(problem.modes.function!.templates.cpp17).toBeUndefined()
      expect(problem.solution).toContain('```python\nclass ')
    }
    expect(catalog.find((p) => p.sourceId === '1564')!.description).toContain('最靠左')
    for (const id of ['1529', '1531']) {
      expect(catalog.find((p) => p.sourceId === id)!.modes.function!.cases[0]!.compare).toBe(
        'unordered_nested',
      )
    }
    expect(compare('[[2,1],[],[1],[2]]', '[[],[1],[2],[1,2]]', 'unordered_nested')).toBe(true)
    expect(compare('[["aa","b"]]', '[["b","aa"]]', 'unordered_json')).toBe(false)
    expect(catalog.find((p) => p.sourceId === '1533')!.modes.function!.cases[0]!.compare).toBe(
      'unordered_json',
    )
  })

  it('executes all authored reference solutions through the actual JSON harness', async () => {
    const catalog = await hotCatalog()
    // Only repository-authored reference text is executed here, never submitted user code.
    const jobs = catalog.map((problem) => ({
      code:
        problem.modes.function!.prelude +
        '\n' +
        problem.solution.match(/```python\n([\s\S]*?)\n```/)![1],
      harness: problem.modes.function!.harness,
      inputs: problem.modes.function!.cases.map((test) => test.input),
    }))
    const result = spawnSync(
      'python3',
      [
        '-c',
        `
import contextlib, io, json, sys
jobs = json.load(sys.stdin)
results = []
for job in jobs:
    outputs = []
    for value in job['inputs']:
        scope = {}
        output = io.StringIO()
        sys.stdin = io.StringIO(value)
        with contextlib.redirect_stdout(output):
            exec(compile(job['code'] + '\\n' + job['harness'], '<authored-reference>', 'exec'), scope)
        outputs.append(output.getvalue())
    results.append(outputs)
print(json.dumps(results))
`,
      ],
      { input: JSON.stringify(jobs), encoding: 'utf8', timeout: 30_000, maxBuffer: 4_000_000 },
    )
    expect(result.stderr).toBe('')
    expect(result.status).toBe(0)
    const outputs = JSON.parse(result.stdout) as string[][]
    catalog.forEach((problem, problemIndex) => {
      problem.modes.function!.cases.forEach((test, caseIndex) => {
        expect(
          compare(outputs[problemIndex]![caseIndex]!, test.expected, test.compare),
          `${problem.sourceId} ${problem.title}, fixture ${caseIndex}`,
        ).toBe(true)
      })
    })
  })
})
