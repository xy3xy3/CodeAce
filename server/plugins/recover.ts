import { db } from '../utils/db'
export default defineNitroPlugin(async () => {
  try {
    const sql = db()
    await sql`UPDATE submissions SET status='SYSTEM_ERROR',result=${sql.json({ error: '服务重启，任务已中断，请重新提交' })},finished_at=now() WHERE status IN ('QUEUED','RUNNING')`
  } catch {
    console.warn('数据库尚未初始化；请运行 pnpm db:migrate')
  }
})
