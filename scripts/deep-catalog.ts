import { readFileSync } from 'node:fs'
import { problemSchema, type Problem } from '../shared/problem'

/** Original CPU PyTorch exercises. See database/deep-reference.py for fixture provenance. */
export function deepCatalog(): Problem[] {
  const raw: unknown = JSON.parse(
    readFileSync(new URL('../database/deep-catalog.json', import.meta.url), 'utf8'),
  )
  return problemSchema.array().parse(raw)
}
