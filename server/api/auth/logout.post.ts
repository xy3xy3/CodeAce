import { db } from '../../utils/db'
import { digest } from '../../utils/password'
export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'codeace_session')
  if (token) await db()`DELETE FROM sessions WHERE token_hash=${digest(token)}`
  deleteCookie(event, 'codeace_session', { path: '/' })
  return { ok: true }
})
