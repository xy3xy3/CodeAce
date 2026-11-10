import { randomBytes } from 'node:crypto'
import { digest, verifyPassword } from '../../utils/password'
import { db } from '../../utils/db'
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  if (
    typeof body?.username !== 'string' ||
    typeof body?.password !== 'string' ||
    body.password.length > 200
  )
    throw createError({ statusCode: 400, statusMessage: '请输入用户名和密码' })
  const address = digest(getRequestIP(event) || 'local'),
    sql = db()
  const [attempt] =
    await sql`INSERT INTO login_attempts(address_hash,attempts) VALUES(${address},1) ON CONFLICT(address_hash) DO UPDATE SET attempts=CASE WHEN login_attempts.window_start<now()-interval '10 minutes' THEN 1 ELSE login_attempts.attempts+1 END,window_start=CASE WHEN login_attempts.window_start<now()-interval '10 minutes' THEN now() ELSE login_attempts.window_start END RETURNING attempts`
  if (attempt!.attempts > 15)
    throw createError({ statusCode: 429, statusMessage: '登录尝试过多，请稍后重试' })
  const [admin] = await sql`SELECT * FROM administrator WHERE id=1`
  if (
    !admin ||
    body.username !== admin.username ||
    !verifyPassword(body.password, admin.password_hash)
  )
    throw createError({ statusCode: 401, statusMessage: '用户名或密码错误' })
  const token = randomBytes(32).toString('hex')
  await sql`INSERT INTO sessions(token_hash,expires_at) VALUES(${digest(token)},now()+interval '14 days')`
  await sql`DELETE FROM sessions WHERE expires_at<now()`
  await sql`DELETE FROM login_attempts WHERE address_hash=${address}`
  setCookie(event, 'codeace_session', token, {
    httpOnly: true,
    sameSite: 'strict',
    secure: process.env.NUXT_COOKIE_SECURE === 'true',
    path: '/',
    maxAge: 14 * 86400,
  })
  return { username: admin.username }
})
