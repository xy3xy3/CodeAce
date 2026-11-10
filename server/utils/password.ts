import { scryptSync, randomBytes, timingSafeEqual, createHash } from 'node:crypto'
export function hashPassword(password: string) {
  const salt = randomBytes(16).toString('hex')
  return salt + ':' + scryptSync(password, salt, 64).toString('hex')
}
export function verifyPassword(password: string, stored: string) {
  const [salt, hash] = stored.split(':')
  if (!salt || !hash) return false
  const a = scryptSync(password, salt, 64),
    b = Buffer.from(hash, 'hex')
  return a.length === b.length && timingSafeEqual(a, b)
}
export function digest(value: string) {
  return createHash('sha256').update(value).digest('hex')
}
export function safeEqual(a: string, b: string) {
  const aa = Buffer.from(a),
    bb = Buffer.from(b)
  return aa.length === bb.length && timingSafeEqual(aa, bb)
}
