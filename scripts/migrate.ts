import 'dotenv/config'
import postgres from 'postgres'
import { readFile } from 'node:fs/promises'
const sql = postgres(process.env.NUXT_DATABASE_URL!)
await sql.unsafe(await readFile(new URL('../database/001_initial.sql', import.meta.url), 'utf8'))
// Existing interrupted jobs must never remain "running" forever after a restart.
await sql`UPDATE submissions SET status='SYSTEM_ERROR', result=${sql.json({ error: '服务重启，任务已中断' })},finished_at=now() WHERE status IN ('QUEUED','RUNNING') AND created_at<now()-interval '5 minutes'`
console.log('Database migrated; vector extension enabled')
await sql.end()
