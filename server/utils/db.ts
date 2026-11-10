import postgres from 'postgres'
let client: ReturnType<typeof postgres>
export function db() {
  if (!client) {
    const url = process.env.NUXT_DATABASE_URL
    if (!url) throw new Error('NUXT_DATABASE_URL is required')
    client = postgres(url, { max: 8, idle_timeout: 20, connect_timeout: 10 })
  }
  return client
}
