/** Offline, reproducible catalog assembly. Does not access any website or account. */
import { readFile, writeFile } from 'node:fs/promises'
import { convertSource } from './convert-codeky'
import { hotCatalog } from './hot-catalog'
import { deepCatalog } from './deep-catalog'
import { problemSchema } from '../shared/problem'
const raw = JSON.parse(await readFile('database/sources/codeky.json', 'utf8'))
const source = typeof raw.data === 'string' ? JSON.parse(raw.data) : raw
const problems = []
for (const row of source.records) {
  if (row.problem && !row.problem.access_locked)
    problems.push(problemSchema.parse(await convertSource(row.problem)))
}
problems.push(...(await hotCatalog()), ...deepCatalog())
// Supplemental independent catalogs are checked in and deterministically assembled at seed time.
await writeFile('database/sources/problems.json', JSON.stringify(problems, null, 2) + '\n')
console.log('Rebuilt', problems.length, 'complete offline problems. No network requests were sent.')
console.log('Run pnpm db:seed to include independently authored Hot100/deep learning supplements.')
