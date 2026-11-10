import { describe, it, expect } from 'vitest'
// @ts-expect-error native sandbox module intentionally has no TS dependency
import { compare } from '../../sandbox/compare.mjs'
import { problemSchema } from '../../shared/problem'
import { readFileSync } from 'node:fs'
describe('answer semantics', () => {
  it('never changes string literals during Python compatibility parsing', () => {
    expect(compare('"None"', '"null"', 'json')).toBe(false)
    expect(compare('"True"', '"true"', 'json')).toBe(false)
  })
  it('accepts alternate balanced BSTs and rejects invalid trees', () => {
    expect(compare('[-3,-10,5,null,null,0,9]', '[0,-3,9,-10,null,5]', 'balanced_bst')).toBe(true)
    expect(compare('[3,2,null,1]', '[2,1,3]', 'balanced_bst')).toBe(false)
    expect(compare('[2,3,1]', '[2,1,3]', 'balanced_bst')).toBe(false)
  })
  it('accepts JSON null but rejects invalid JSON', () => {
    expect(compare('null', 'null', 'json')).toBe(true)
    expect(compare('oops', 'oops', 'json')).toBe(false)
  })
  it('compares tokens and multiplicities', () => {
    expect(compare('1  2\n', '1 2')).toBe(true)
    expect(compare('2 1', '1 2', 'unordered_tokens')).toBe(true)
    expect(compare('1 1', '1 2', 'unordered_tokens')).toBe(false)
  })
  it('does not flatten tensor shapes', () => {
    expect(compare('[[1,2]]', '[1,2]', 'float_tokens')).toBe(false)
    expect(compare('[[1,2],[3,4]]', '[[1,2],[3,4.00001]]', 'float_tokens', 1e-4, 1e-4)).toBe(true)
  })
  it('rejects missing elements, nonfinite values and invalid numbers', () => {
    expect(compare('1 2', '1 2 3', 'float_tokens')).toBe(false)
    expect(compare('NaN', 'NaN', 'float_tokens')).toBe(false)
    expect(compare('Infinity', 'Infinity', 'float_tokens')).toBe(false)
    expect(compare('bad', 'bad', 'float_tokens')).toBe(false)
  })
  it('supports unordered outer collections while preserving permutation contents', () => {
    expect(compare('[[2,1],[1,2]]', '[[1,2],[2,1]]', 'unordered_json')).toBe(true)
    expect(compare('[[1,2],[1,2]]', '[[1,2],[2,1]]', 'unordered_json')).toBe(false)
    expect(compare('[["eat","tea"],["bat"]]', '[["bat"],["tea","eat"]]', 'unordered_nested')).toBe(
      true,
    )
  })
})
describe('source and language invariants', () => {
  const problems = JSON.parse(readFileSync('database/sources/problems.json', 'utf8'))
  it('validates every converted source problem', () => {
    expect(problems.length).toBeGreaterThanOrEqual(60)
    for (const p of problems) expect(problemSchema.safeParse(p).success, p.title).toBe(true)
  })
  it('rejects C++ in Python-only categories', () => {
    const p = structuredClone(problems.find((x: any) => x.category === 'Hot100'))
    p.modes.acm.templates.cpp17 = 'int main() {}'
    expect(problemSchema.safeParse(p).success).toBe(false)
  })
})
