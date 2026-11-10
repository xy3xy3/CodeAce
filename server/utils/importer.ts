import { isDeepStrictEqual } from 'node:util'
import { problemSchema } from '../../shared/problem'
import { db } from './db'
export async function importProblems(items: unknown[], dryRun = false) {
  const sql = db()
  const results: any[] = []
  for (let i = 0; i < items.length; i++) {
    const parsed = problemSchema.safeParse(items[i])
    if (!parsed.success) {
      results.push({
        index: i,
        status: 'error',
        errors: parsed.error.issues.map((x) => ({ path: x.path.join('.'), message: x.message })),
      })
      continue
    }
    const p = parsed.data
    const [existing] =
      await sql`SELECT id,locally_edited,data FROM problems WHERE source=${p.source} AND source_id=${p.sourceId}`
    if (existing?.locally_edited) {
      results.push({
        index: i,
        sourceId: p.sourceId,
        status: 'skipped',
        reason: '本地已编辑，保留个人修改',
        id: existing.id,
      })
      continue
    }
    if (existing && isDeepStrictEqual(existing.data, p)) {
      results.push({
        index: i,
        sourceId: p.sourceId,
        status: 'skipped',
        reason: '内容未变',
        id: existing.id,
      })
      continue
    }
    let id = existing?.id
    if (!dryRun) {
      await sql`INSERT INTO categories(name) VALUES(${p.category}) ON CONFLICT DO NOTHING`
      const [saved] =
        await sql`INSERT INTO problems(source,source_id,data) VALUES(${p.source},${p.sourceId},${sql.json(p)}) ON CONFLICT(source,source_id) DO UPDATE SET data=excluded.data,version=problems.version+1,updated_at=now() WHERE NOT problems.locally_edited RETURNING id`
      if (!saved) {
        results.push({
          index: i,
          sourceId: p.sourceId,
          status: 'skipped',
          reason: '本地已编辑，保留个人修改',
          id: existing?.id,
        })
        continue
      }
      id = saved.id
    }
    results.push({ index: i, sourceId: p.sourceId, status: existing ? 'updated' : 'created', id })
  }
  const report = {
    dryRun,
    created: results.filter((x) => x.status === 'created').length,
    updated: results.filter((x) => x.status === 'updated').length,
    skipped: results.filter((x) => x.status === 'skipped').length,
    failed: results.filter((x) => x.status === 'error').length,
    results,
  }
  if (!dryRun) await sql`INSERT INTO imports(report) VALUES(${sql.json(report)})`
  return report
}
