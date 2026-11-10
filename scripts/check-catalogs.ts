import { spawnSync } from 'node:child_process'
import { resolve } from 'node:path'
const checks = [
  ['python3', ['database/hot-verify.py']],
  [
    'docker',
    [
      'run',
      '--rm',
      '--network=none',
      '--read-only',
      '--cap-drop=ALL',
      '--security-opt=no-new-privileges',
      '--user=65534:65534',
      '--memory=1536m',
      '--pids-limit=64',
      '--tmpfs',
      '/tmp:rw,nosuid,nodev,size=64m',
      '-v',
      resolve('database') + ':/repo/database:ro',
      '-w',
      '/repo',
      '--entrypoint',
      'python3',
      'codeace-runtime:local',
      '/repo/database/deep-reference.py',
    ],
  ],
] as const
for (const [program, args] of checks) {
  const result = spawnSync(program, [...args], { stdio: 'inherit', timeout: 180000 })
  if (result.status !== 0) process.exit(result.status || 1)
}
