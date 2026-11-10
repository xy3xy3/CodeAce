import { z } from 'zod'
export const languageSchema = z.enum(['python3', 'cpp17'])
export const caseSchema = z.object({
  input: z.string().max(200000),
  expected: z.string().max(200000),
  harness: z.string().max(100000).optional(),
  hidden: z.boolean().default(false),
  compare: z
    .enum([
      'exact',
      'tokens',
      'unordered_tokens',
      'json',
      'unordered_json',
      'unordered_nested',
      'balanced_bst',
      'float_tokens',
    ])
    .default('tokens'),
  absTolerance: z.number().min(0).max(0.1).default(0.00001),
  relTolerance: z.number().min(0).max(0.1).default(0.00001),
})
export const variantSchema = z.object({
  templates: z.object({
    python3: z.string().max(100000).optional(),
    cpp17: z.string().max(100000).optional(),
  }),
  prelude: z.string().max(100000).default(''),
  harness: z.string().max(100000).default(''),
  cases: z.array(caseSchema).min(1).max(100),
  inputHelp: z.string().default(''),
  runtime: z.enum(['standard', 'numpy', 'torch']).default('standard'),
})
export const problemSchema = z
  .object({
    title: z.string().min(1).max(200),
    category: z.string().trim().min(1).max(100).transform(value => /^hot\s*100$/i.test(value)?'Hot100':value),
    difficulty: z.enum(['简单', '中等', '困难']),
    tags: z.array(z.string().max(100)).max(30).default([]),
    description: z.string().min(1).max(200000),
    inputDescription: z.string().default(''),
    outputDescription: z.string().default(''),
    constraints: z.string().default(''),
    hint: z.string().default(''),
    solution: z.string().max(200000).default(''),
    sourceUrl: z
      .string()
      .url()
      .refine((value) => /^https?:\/\//.test(value), '来源链接只允许 HTTP(S)')
      .optional(),
    sourceId: z.string().max(100),
    source: z.string().max(100).default('personal'),
    published: z.boolean().default(false),
    timeMs: z.number().int().min(100).max(30000).default(3000),
    memoryMb: z.number().int().min(64).max(2048).default(512),
    modes: z.object({ acm: variantSchema.optional(), function: variantSchema.optional() }),
    samples: z
      .array(
        z.object({ input: z.string(), output: z.string(), explanation: z.string().optional() }),
      )
      .default([]),
  })
  .superRefine((p, ctx) => {
    const variants = Object.values(p.modes).filter(Boolean)
    if (!variants.length)
      ctx.addIssue({ code: 'custom', message: '至少配置一种可执行模式', path: ['modes'] })
    for (const v of variants) {
      if (!v) continue
      if (!v.templates.python3 && !v.templates.cpp17)
        ctx.addIssue({ code: 'custom', message: '模式必须有代码模板', path: ['modes'] })
      if (['Hot100', '深度学习'].includes(p.category) && v.templates.cpp17)
        ctx.addIssue({ code: 'custom', message: 'Hot100/深度学习只支持 Python3', path: ['modes'] })
    }
  })
export type Problem = z.infer<typeof problemSchema>
export type Variant = z.infer<typeof variantSchema>
