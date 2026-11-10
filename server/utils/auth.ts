import type { H3Event } from 'h3'
import { getCookie, createError, getHeader } from 'h3'
import { db } from './db'
import { digest, safeEqual } from './password'
export async function requireAuth(event: H3Event, allowImport = false) {
  const bearer = (getHeader(event, 'authorization') || '').replace(/^Bearer /, '')
  if (allowImport && process.env.NUXT_IMPORT_KEY && safeEqual(bearer, process.env.NUXT_IMPORT_KEY))
    return
  const token = getCookie(event, 'codeace_session')
  if (!token) throw createError({ statusCode: 401, statusMessage: '请先登录' })
  const rows =
    await db()`SELECT token_hash FROM sessions WHERE token_hash=${digest(token)} AND expires_at>now()`
  if (!rows.length) throw createError({ statusCode: 401, statusMessage: '登录已过期' })
}
