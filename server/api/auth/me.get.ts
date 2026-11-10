import { requireAuth } from '../../utils/auth'
import { db } from '../../utils/db'
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const [a] = await db()`SELECT username FROM administrator WHERE id=1`
  return { username: a?.username }
})
