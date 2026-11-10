import 'dotenv/config'
import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import type { Problem } from '../shared/problem'
const parse = (s: any, fallback: any) => {
  try {
    return typeof s === 'string' ? JSON.parse(s) : (s ?? fallback)
  } catch {
    return fallback
  }
}
export async function convertSource(p: any): Promise<Problem> {
  const prelude = await readFile(
    new URL('../database/function_prelude.py', import.meta.url),
    'utf8',
  )
  const templates = parse(p.function_template_map || p.function_template, {}),
    params = parse(p.function_params, []),
    sample = parse(p.sample_io, {}).examples || []
  const category = /^Hot ?100$/.test(p.category) ? 'Hot100' : p.category
  const modes: any = {}
  const rawCases = p.test_cases || []
  const clean = (s: any) =>
    String(s || '')
      .replace(/<!--ck-wm:[\s\S]*?-->/g, '')
      .trim()
  const baseCase = (c: any) => ({
    input: String(c.input || ''),
    expected: String(c.expected_output ?? ''),
    hidden: false,
    compare:
      c.compare_mode === 'float_tokens'
        ? 'float_tokens'
        : c.compare_mode === 'unordered_tokens'
          ? 'unordered_tokens'
          : 'tokens',
    absTolerance: c.abs_tolerance ?? 1e-5,
    relTolerance: c.rel_tolerance ?? 1e-5,
  })
  if (p.judge_mode !== 'function' && p.input_desc && rawCases.length) {
    modes.acm = {
      templates: {
        python3:
          'import sys\n\ndef main():\n    data = sys.stdin.read()\n    # 读取输入，打印答案\n    pass\n\nif __name__ == "__main__":\n    main()\n',
      },
      prelude: '',
      harness: '',
      runtime: 'standard',
      cases: rawCases.map(baseCase),
      inputHelp: p.input_desc,
    }
  }
  const runtime = templates.torch ? 'torch' : templates.numpy ? 'numpy' : 'standard',
    template = templates[runtime === 'standard' ? 'python' : runtime]
  if (template && rawCases.length && p.test_case_mode === 'code_input') {
    const cases = rawCases.map((c: any) => ({
      ...baseCase(c),
      harness: c.input_by_lang?.[runtime],
    }))
    if (cases.every((c: any) => c.harness))
      modes.function = {
        templates: { python3: template },
        prelude: '',
        harness: '',
        runtime,
        cases,
        inputHelp:
          '函数模式自定义输入填写 Python 调用代码，仅在沙箱执行；例如构造 tensor 后调用模板函数并 print 结果。',
      }
  }
  if (template && category === 'Hot100' && sample.length) {
    const methods = [...template.matchAll(/def\s+(\w+)\(/g)].map((m: any) => m[1]),
      design = !template.includes('class Solution') && !template.includes('class Codec')
    const meta = {
      id: p.id,
      method: methods.find((m: any) => !m.startsWith('__')),
      params: params.filter((x: any) => !x.is_return),
      design,
      returnType: params.find((x: any) => x.is_return)?.type,
      inplace: params.some((x: any) => x.is_return && x.type === 'void'),
    }
    const cases = sample.map((s: any) => {
      let expected = s.output
      if (p.id === 1493)
        expected = /无/.test(expected) ? 'null' : String(expected.match(/-?\d+/)?.[0] ?? 'null')
      if (p.id === 1497)
        expected = /null/.test(expected) ? '-1' : String(expected.match(/-?\d+/)?.[0] ?? '-1')
      let compare = 'json'
      if ([1472, 1473, 1477, 1480, 1507, 1512, 1526].includes(p.id))
        compare = [1473, 1477].includes(p.id)
          ? 'unordered_nested'
          : [1507, 1512].includes(p.id)
            ? 'json'
            : 'unordered_json'
      return { input: s.input, expected, hidden: false, compare, absTolerance: 0, relTolerance: 0 }
    })
    modes.function = {
      templates: { python3: template },
      prelude,
      harness: '\n_ca_call(json.loads(' + JSON.stringify(JSON.stringify(meta)) + '))',
      runtime: 'standard',
      cases,
      inputHelp: design
        ? '两行 JSON：第一行为操作名数组，第二行为参数数组；也支持 {"operations": [...], "arguments": [...]}。'
        : '输入 JSON 对象或 name = value；链表与树使用数组，空节点使用 null。',
    }
  }
  if (!Object.keys(modes).length) throw new Error('缺少受支持的模板、用例或输入规格')
  return {
    title: p.title,
    category,
    difficulty: p.difficulty,
    tags: String(p.knowledge_point || '')
      .split(/\s+/)
      .filter(Boolean),
    description: clean(p.description),
    inputDescription: clean(p.input_desc),
    outputDescription: clean(p.output_desc),
    constraints: clean(p.data_range),
    hint: clean(p.hint),
    solution: '',
    sourceUrl: 'https://codeky.online/problem/' + p.id,
    sourceId: String(p.id),
    source: 'codeky',
    published: true,
    timeMs: Math.min(30000, Math.max(p.time_limit || 3000, category === '深度学习' ? 10000 : 3000)),
    memoryMb:
      category === '深度学习'
        ? 1024
        : Math.max(256, Math.min(1024, Math.ceil((p.memory_limit || 524288) / 1024))),
    modes,
    samples: sample.length
      ? sample.map((s: any) => ({
          input: s.input,
          output: s.output,
          explanation: s.explanation || '',
        }))
      : [{ input: p.sample_input || '', output: p.sample_output || '' }],
  }
}
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const raw = JSON.parse(await readFile(process.argv[2] || 'database/sources/codeky.json', 'utf8'))
  const data = typeof raw.data === 'string' ? JSON.parse(raw.data) : raw
  const converted = []
  const report = []
  for (const r of data.records) {
    if (!r.problem || r.problem.access_locked) continue
    try {
      converted.push(await convertSource(r.problem))
      report.push({ id: r.sourceId, status: 'ready' })
    } catch (e) {
      report.push({ id: r.sourceId, status: 'needs-review', reason: String(e) })
    }
  }
  await writeFile('database/sources/problems.json', JSON.stringify(converted, null, 2) + '\n')
  console.log({ converted: converted.length, report })
}
