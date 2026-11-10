import 'dotenv/config'
import postgres from 'postgres'
import { hashPassword } from '../server/utils/password'
const username = process.env.ADMIN_USERNAME || 'admin',
  password = process.env.ADMIN_PASSWORD
if (!password || password.length < 12)
  throw new Error('Set ADMIN_PASSWORD (at least 12 characters) in .env')
const sql = postgres(process.env.NUXT_DATABASE_URL!)
await sql`INSERT INTO administrator(id,username,password_hash) VALUES(1,${username},${hashPassword(password)}) ON CONFLICT(id) DO UPDATE SET username=excluded.username,password_hash=excluded.password_hash`
await sql`DELETE FROM sessions`
console.log('Administrator configured; credentials remain in your .env')
await sql.end()
