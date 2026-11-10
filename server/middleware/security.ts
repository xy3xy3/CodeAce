import { getHeader, setHeader, createError, getRequestURL } from 'h3'
export default defineEventHandler((event) => {
  setHeader(event, 'X-Content-Type-Options', 'nosniff')
  setHeader(event, 'X-Frame-Options', 'DENY')
  setHeader(event, 'Referrer-Policy', 'same-origin')
  if (!event.path.startsWith('/api/')) return
  setHeader(event, 'Cache-Control', 'no-store')
  if (!['GET', 'HEAD', 'OPTIONS'].includes(event.method)) {
    const origin = getHeader(event, 'origin')
    if (origin && origin !== getRequestURL(event).origin)
      throw createError({ statusCode: 403, statusMessage: '禁止跨站写入' })
    const length = Number(getHeader(event, 'content-length') || 0)
    if (length > 3 * 1024 * 1024) throw createError({ statusCode: 413, statusMessage: '请求过大' })
  }
})
