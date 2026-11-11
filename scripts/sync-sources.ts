/** Assemble the independently authored exercise catalog without network access. */
import { writeFile } from 'node:fs/promises'
import { hotCatalog } from './hot-catalog'
import { deepCatalog } from './deep-catalog'
const problems = [...(await hotCatalog()), ...deepCatalog()]
await writeFile('database/sources/problems.json', JSON.stringify(problems, null, 2) + '\n')
console.log('Built', problems.length, 'offline exercises.')
