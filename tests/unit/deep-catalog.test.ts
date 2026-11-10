import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { deepCatalog } from '../../scripts/deep-catalog'
import { problemSchema } from '../../shared/problem'

describe('原创深度学习练习目录', () => {
  it('覆盖剩余 65 个库存主题并明确原创来源', async () => {
    const catalog = await deepCatalog()
    const inventory = JSON.parse(
      readFileSync(new URL('../../database/sources/codeky.json', import.meta.url), 'utf8'),
    ).inventory
    const ids = inventory
      .filter(
        (x: { category: string; id: number }) =>
          x.category === '深度学习' && ![1320, 1467, 1471].includes(x.id),
      )
      .map((x: { id: number }) => String(x.id))
      .sort()
    expect(catalog.map((x) => x.sourceId).sort()).toEqual(ids)
    expect(catalog).toHaveLength(65)
    for (const p of catalog) {
      expect(problemSchema.safeParse(p).success, p.title).toBe(true)
      expect(p.source).toBe('codeace-original')
      expect(p.sourceUrl).toMatch(/^https:\/\/docs\.pytorch\.org\//)
      expect(p.description).toContain('原创')
      expect(p.solution).toContain('def solve(data):')
      expect(p.modes.acm).toBeUndefined()
      expect(p.modes.function?.templates.cpp17).toBeUndefined()
    }
  })
  it('每题有保留嵌套形状的确定性数值用例和函数契约', async () => {
    for (const p of await deepCatalog()) {
      const v = p.modes.function!
      expect(v.cases.length, p.title).toBeGreaterThanOrEqual(3)
      expect(new Set(v.cases.map((c) => c.input)).size).toBe(v.cases.length)
      expect(v.harness).toContain('solve(')
      expect(v.templates.python3).toContain('def solve(data):')
      expect(p.inputDescription.length).toBeGreaterThan(20)
      expect(p.outputDescription.length).toBeGreaterThan(10)
      for (const c of v.cases) {
        expect(c.compare).toBe('float_tokens')
        expect(c.absTolerance).toBeGreaterThan(0)
        expect(() => JSON.parse(c.input)).not.toThrow()
        expect(() => JSON.parse(c.expected)).not.toThrow()
      }
    }
  })
})
