/** The account owner reported a temporary anti-crawler restriction.
 * Authenticated CodeKy collection is disabled, including automatic retries.
 * Use offline snapshots and the independently authored catalogs instead.
 */
console.error(
  'CodeKy 在线采集已停用：账户曾触发反爬限制。不会发送任何网络请求。请使用 pnpm db:seed 导入现有快照与独立题库。',
)
process.exitCode = 1
