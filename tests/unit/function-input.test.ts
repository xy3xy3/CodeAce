import { spawnSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { it, expect } from 'vitest'
it('parses JSON literals without modifying quoted strings or executing input', () => {
  const prelude = readFileSync('database/function_prelude.py', 'utf8')
  const result = spawnSync(
    'python3',
    [
      '-c',
      prelude +
        `\nprint(json.dumps(_ca_values('s = "null true false", root = [1,null], flag = true')))`,
    ],
    { encoding: 'utf8' },
  )
  expect(result.status).toBe(0)
  expect(JSON.parse(result.stdout)).toEqual({ s: 'null true false', root: [1, null], flag: true })
  const malicious = spawnSync(
    'python3',
    ['-c', prelude + `\n_ca_values('x = __import__("os").getuid()')`],
    { encoding: 'utf8' },
  )
  expect(malicious.status).not.toBe(0)
})
