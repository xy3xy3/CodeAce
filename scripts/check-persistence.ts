import 'dotenv/config'
import postgres from 'postgres'
import {spawnSync} from 'node:child_process'
import {isDeepStrictEqual} from 'node:util'
const url=process.env.NUXT_DATABASE_URL!
async function snapshot(){const sql=postgres(url,{max:1,connect_timeout:2});try{
 const [row]=await sql`SELECT (SELECT count(*) FROM problems)::int AS problems,(SELECT count(*) FROM submissions)::int AS submissions,(SELECT count(*) FROM drafts)::int AS drafts,(SELECT count(*) FROM personal)::int AS personal,(SELECT extversion FROM pg_extension WHERE extname='vector') AS vector,(SELECT md5(coalesce(string_agg(data::text,'|' ORDER BY id),'')) FROM problems) AS problem_fingerprint`
 return row
}finally{await sql.end()}}
const before=await snapshot()
const result=spawnSync('docker',['compose','restart','postgres'],{stdio:'inherit',timeout:60000});if(result.status!==0)process.exit(1)
let after:any
for(let i=0;i<40;i++){try{after=await snapshot();break}catch{await new Promise(r=>setTimeout(r,500))}}
if(!after||!isDeepStrictEqual(before,after))throw new Error('Persistence comparison failed')
console.log(JSON.stringify({result:'passed',before,after},null,2))
