import { randomUUID } from 'node:crypto'
import { problemSchema } from '../../shared/problem'
import { db } from '../utils/db'
import { requireAuth } from '../utils/auth'
import { importProblems } from '../utils/importer'
import { judge, enqueue } from '../utils/judge'

export default defineEventHandler(async (event): Promise<any> => {
  const path = (getRouterParam(event, 'path') || '').split('/'),
    method = event.method,
    sql = db(),
    query = getQuery(event)
  await requireAuth(event, path[0] === 'import' && method === 'POST')
  const body = () => readBody(event)
  if (path[0] === 'categories') {
    if (method === 'GET') return await sql`SELECT * FROM categories ORDER BY position,name`
    const b = await body()
    if (method === 'POST') {
      if (typeof b.name !== 'string' || !b.name.trim() || b.name.length > 100)
        throw createError({ statusCode: 400, statusMessage: '分类名称无效' })
      await sql`INSERT INTO categories(name) VALUES(${b.name.trim()}) ON CONFLICT DO NOTHING`
      return { ok: true }
    }
    if (method === 'DELETE') {
      const name = String(query.name || '')
      const [used] =
        await sql`SELECT count(*)::int AS count FROM problems WHERE data->>'category'=${name}`
      if (used!.count) throw createError({ statusCode: 409, statusMessage: '分类下仍有题目' })
      await sql`DELETE FROM categories WHERE name=${name}`
      return { ok: true }
    }
  }
  if (path[0] === 'stats' && method === 'GET') {
    const [totals] =
      await sql`SELECT count(*)::int AS total,count(*) FILTER (WHERE EXISTS(SELECT 1 FROM submissions s WHERE s.problem_id=p.id AND s.status='AC'))::int AS solved FROM problems p WHERE (data->>'published')::boolean=true`
    const [activity] =
      await sql`SELECT count(*)::int AS submissions,count(*) FILTER(WHERE status='AC')::int AS accepted,count(DISTINCT (created_at AT TIME ZONE 'Asia/Shanghai')::date)::int AS days FROM submissions`
    const daily =
      await sql`SELECT to_char(created_at AT TIME ZONE 'Asia/Shanghai','YYYY-MM-DD') AS day,count(*)::int AS count,count(*) FILTER(WHERE status='AC')::int AS accepted FROM submissions WHERE created_at>now()-interval '180 days' GROUP BY day ORDER BY day`
    const categories =
      await sql`SELECT data->>'category' AS name,count(*)::int AS total,count(*) FILTER(WHERE EXISTS(SELECT 1 FROM submissions s WHERE s.problem_id=p.id AND s.status='AC'))::int AS solved FROM problems p WHERE (data->>'published')::boolean=true GROUP BY data->>'category'`
    return { ...totals, ...activity, daily, categories }
  }
  if (path[0] === 'import' && method === 'POST') {
    const b = await body()
    if (!Array.isArray(b?.problems) || b.problems.length < 1 || b.problems.length > 100)
      throw createError({ statusCode: 400, statusMessage: 'problems 必须为 1–100 道题目的数组' })
    return await importProblems(b.problems, b.dryRun === true)
  }
  if (path[0] === 'source-report' && method === 'GET') {
    return {
      inventory:
        await sql`SELECT i.*,p.id AS problem_id,coalesce((p.data->>'published')::boolean,false) AS published FROM source_inventory i LEFT JOIN problems p ON p.source_id=i.source_id AND (p.source=i.source OR p.source='codeace-original') ORDER BY i.category,i.source_id`,
      imports: await sql`SELECT * FROM imports ORDER BY id DESC LIMIT 10`,
    }
  }
  if (path[0] === 'problems') {
    const id = path[1]
    if (!id && method === 'GET') {
      const admin = query.admin === '1',
        search = String(query.q || '').slice(0, 200),
        category = String(query.category || ''),
        difficulty = String(query.difficulty || ''),
        tag = String(query.tag || ''),
        status = String(query.status || ''),
        page = Math.max(1, Math.min(10000, Number(query.page) || 1)),
        limit = 20
      const rows =
        await sql`SELECT p.id,p.version,p.updated_at,p.data->>'title' AS title,p.data->>'category' AS category,p.data->>'difficulty' AS difficulty,p.data->'tags' AS tags,(p.data->>'published')::boolean AS published,coalesce(x.favorite,false) AS favorite,EXISTS(SELECT 1 FROM submissions s WHERE s.problem_id=p.id AND s.status='AC') AS solved,(SELECT s.status FROM submissions s WHERE s.problem_id=p.id ORDER BY id DESC LIMIT 1) AS last_status FROM problems p LEFT JOIN personal x ON x.problem_id=p.id WHERE (${admin} OR (p.data->>'published')::boolean=true) AND (${search}='' OR p.data->>'title' ILIKE ${'%' + search + '%'} OR p.source_id=${search}) AND (${category}='' OR p.data->>'category'=${category}) AND (${difficulty}='' OR p.data->>'difficulty'=${difficulty}) AND (${tag}='' OR p.data->'tags' ? ${tag}) ORDER BY p.id`
      const filtered = rows.filter((p) =>
        status === 'solved'
          ? p.solved
          : status === 'todo'
            ? !p.solved
            : status === 'favorite'
              ? p.favorite
              : status === 'wrong'
                ? p.last_status && p.last_status !== 'AC' && !p.solved
                : true,
      )
      return {
        items: filtered.slice((page - 1) * limit, page * limit),
        total: filtered.length,
        page,
        pages: Math.max(1, Math.ceil(filtered.length / limit)),
        tags: [...new Set(rows.flatMap((p) => p.tags || []))],
      }
    }
    if (!id && method === 'POST') {
      const parsed = problemSchema.safeParse(await body())
      if (!parsed.success)
        throw createError({ statusCode: 400, statusMessage: parsed.error.issues[0]!.message })
      const p = parsed.data
      await sql`INSERT INTO categories(name) VALUES(${p.category}) ON CONFLICT DO NOTHING`
      const [row] =
        await sql`INSERT INTO problems(source,source_id,data,locally_edited) VALUES(${p.source},${p.sourceId || randomUUID()},${sql.json(p)},true) RETURNING id`
      return row
    }
    if (!/^\d+$/.test(id || ''))
      throw createError({ statusCode: 400, statusMessage: '题目编号无效' })
    const [row] = await sql`SELECT * FROM problems WHERE id=${id!}`
    if (!row) throw createError({ statusCode: 404, statusMessage: '题目不存在' })
    if (path[2] === 'personal') {
      if (method === 'GET') {
        const [p] = await sql`SELECT * FROM personal WHERE problem_id=${id!}`
        return p || { favorite: false, note: '' }
      }
      if (method === 'PUT') {
        const b = await body()
        if (typeof b.favorite !== 'boolean' || typeof b.note !== 'string' || b.note.length > 100000)
          throw createError({ statusCode: 400, statusMessage: '笔记数据无效' })
        await sql`INSERT INTO personal(problem_id,favorite,note) VALUES(${id!},${b.favorite},${b.note}) ON CONFLICT(problem_id) DO UPDATE SET favorite=excluded.favorite,note=excluded.note,updated_at=now()`
        return { ok: true }
      }
    }
    if (path[2] === 'draft') {
      const language = String(query.language || ''),
        mode = String(query.mode || '')
      if (!['python3', 'cpp17'].includes(language) || !['acm', 'function'].includes(mode))
        throw createError({ statusCode: 400, statusMessage: '语言或模式无效' })
      if (method === 'GET') {
        const [draft] =
          await sql`SELECT code FROM drafts WHERE problem_id=${id!} AND language=${language} AND mode=${mode}`
        return { code: draft?.code ?? null }
      }
      if (method === 'PUT') {
        const b = await body()
        if (typeof b.code !== 'string' || b.code.length > 100000)
          throw createError({ statusCode: 400, statusMessage: '代码过长' })
        await sql`INSERT INTO drafts(problem_id,language,mode,code) VALUES(${id!},${language},${mode},${b.code}) ON CONFLICT(problem_id,language,mode) DO UPDATE SET code=excluded.code,updated_at=now()`
        return { ok: true }
      }
    }
    if (path[2] === 'run' || path[2] === 'submit') {
      if (method !== 'POST') throw createError({ statusCode: 405 })
      const b = await body(),
        p = row.data
      if (!p.published) throw createError({ statusCode: 400, statusMessage: '题目尚未发布' })
      if (
        typeof b.code !== 'string' ||
        !b.code.trim() ||
        b.code.length > 100000 ||
        !['acm', 'function'].includes(b.mode) ||
        !['python3', 'cpp17'].includes(b.language) ||
        !p.modes[b.mode]?.templates[b.language]
      )
        throw createError({ statusCode: 400, statusMessage: '无效的代码、语言或模式' })
      if (['Hot100', '深度学习'].includes(p.category) && b.language !== 'python3')
        throw createError({ statusCode: 400, statusMessage: '该分类仅支持 Python3' })
      if (path[2] === 'run') {
        if (b.input !== undefined && (typeof b.input !== 'string' || b.input.length > 200000))
          throw createError({ statusCode: 400, statusMessage: '输入过长' })
        return await judge(p, b.language, b.mode, b.code, b.input, true)
      }
      const [submission] =
        await sql`INSERT INTO submissions(problem_id,problem_title,problem_snapshot,problem_version,language,mode,code,status) VALUES(${id!},${p.title},${sql.json(p)},${row.version},${b.language},${b.mode},${b.code},'QUEUED') RETURNING id`
      try {
        enqueue(submission!.id, p, b.language, b.mode, b.code)
      } catch (e) {
        await sql`DELETE FROM submissions WHERE id=${submission!.id}`
        throw e
      }
      return submission
    }
    if (method === 'GET') {
      if (query.admin === '1')
        return { ...row.data, id: row.id, version: row.version, locallyEdited: row.locally_edited }
      if (!row.data.published) throw createError({ statusCode: 404, statusMessage: '题目未发布' })
      const [personal] = await sql`SELECT favorite,note FROM personal WHERE problem_id=${id!}`
      const neighbors =
        await sql`SELECT id,data->>'title' AS title,data->'tags' AS tags FROM problems WHERE data->>'category'=${row.data.category} AND (data->>'published')::boolean=true ORDER BY id`
      const modes = Object.fromEntries(
        Object.entries(row.data.modes).map(([k, v]: [string, any]) => [
          k,
          {
            ...v,
            prelude: undefined,
            harness: undefined,
            cases: v.cases
              .filter((c: any) => !c.hidden)
              .map((c: any) => ({ input: c.input, expected: c.expected })),
          },
        ]),
      )
      return {
        ...row.data,
        modes,
        id: row.id,
        version: row.version,
        personal: personal || { favorite: false, note: '' },
        neighbors,
        similar: neighbors
          .filter(
            (n) => n.id !== row.id && n.tags?.some((tag: string) => row.data.tags.includes(tag)),
          )
          .sort(
            (a, b) =>
              b.tags.filter((tag: string) => row.data.tags.includes(tag)).length -
              a.tags.filter((tag: string) => row.data.tags.includes(tag)).length,
          )
          .slice(0, 4),
      }
    }
    if (method === 'PUT') {
      const parsed = problemSchema.safeParse(await body())
      if (!parsed.success)
        throw createError({
          statusCode: 400,
          statusMessage: parsed.error.issues
            .map((x) => x.path.join('.') + ': ' + x.message)
            .join('; '),
        })
      const p = parsed.data
      if (p.source !== row.source || p.sourceId !== row.source_id)
        throw createError({ statusCode: 409, statusMessage: '来源关联键不可修改，请新建题目' })
      await sql`INSERT INTO categories(name) VALUES(${p.category}) ON CONFLICT DO NOTHING`
      await sql`UPDATE problems SET data=${sql.json(p)},version=version+1,locally_edited=true,updated_at=now() WHERE id=${id!}`
      return { ok: true }
    }
    if (method === 'DELETE') {
      await sql`UPDATE problems SET data=jsonb_set(data,'{published}','false'),locally_edited=true,version=version+1,updated_at=now() WHERE id=${id!}`
      return { ok: true }
    }
  }
  if (path[0] === 'submissions' && method === 'GET') {
    if (path[1]) {
      if (!/^\d+$/.test(path[1])) throw createError({ statusCode: 400 })
      const [s] =
        await sql`SELECT id,problem_id,problem_title,problem_version,language,mode,code,status,result,created_at,finished_at FROM submissions WHERE id=${path[1]}`
      if (!s) throw createError({ statusCode: 404 })
      return s
    }
    const pid = String(query.problemId || ''),
      status = String(query.status || ''),
      language = String(query.language || ''),
      q = String(query.q || '')
    const page = Math.max(1, Number(query.page) || 1)
    const rows =
      await sql`SELECT id,problem_id,problem_title,language,mode,status,result,created_at FROM submissions WHERE (${pid}='' OR problem_id::text=${pid}) AND (${status}='' OR status=${status}) AND (${language}='' OR language=${language}) AND (${q}='' OR problem_title ILIKE ${'%' + q + '%'}) ORDER BY id DESC LIMIT 1000`
    return {
      items: rows.slice((page - 1) * 20, page * 20),
      total: rows.length,
      pages: Math.max(1, Math.ceil(rows.length / 20)),
      page,
    }
  }
  throw createError({ statusCode: 404, statusMessage: '接口不存在' })
})
