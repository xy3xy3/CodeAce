<script setup lang="ts">
import { errorMessage } from '~/composables/useNotice'
import { ArrowLeft, Save, Plus, Trash2, Code2 } from 'lucide-vue-next'
const route = useRoute(),
  isNew = route.params.id === 'new',
  fetcher = useRequestFetch(),
  { notify } = useNotice()
const initial = isNew
  ? {
      title: '',
      category: '通用算法',
      difficulty: '简单',
      tags: [],
      description: '',
      inputDescription: '',
      outputDescription: '',
      constraints: '',
      hint: '',
      solution: '',
      source: 'personal',
      sourceId: crypto.randomUUID(),
      sourceUrl: '',
      published: false,
      timeMs: 3000,
      memoryMb: 512,
      samples: [],
      modes: {
        acm: {
          templates: { python3: 'import sys\n\n# 在这里编写代码\n' },
          prelude: '',
          harness: '',
          inputHelp: '',
          runtime: 'standard',
          cases: [
            {
              input: '',
              expected: '',
              hidden: false,
              compare: 'tokens',
              absTolerance: 0.00001,
              relTolerance: 0.00001,
            },
          ],
        },
      },
    }
  : await fetcher<any>('/api/problems/' + route.params.id, { query: { admin: '1' } })
const form = reactive<any>(initial),
  tags = ref((initial.tags || []).join(' ')),
  busy = ref(false),
  active = ref('basic'),
  advanced = ref(JSON.stringify(initial.modes, null, 2)),
  rawError = ref('')
const { data: categories } = await useAsyncData('edit-categories', () =>
  fetcher<any[]>('/api/categories'),
)
function normalize() {
  form.tags = tags.value.split(/[,，\s]+/).filter(Boolean)
  if (!form.sourceUrl) delete form.sourceUrl
  const { id, version, locallyEdited, ...body } = form
  return body
}
async function save() {
  busy.value = true
  rawError.value = ''
  try {
    form.modes = JSON.parse(advanced.value)
    const p = normalize()
    const result = await $fetch<any>('/api/problems' + (isNew ? '' : '/' + route.params.id), {
      method: isNew ? 'POST' : 'PUT',
      body: p,
    })
    notify('题目已保存')
    if (isNew) await navigateTo('/admin/' + result.id)
  } catch (e) {
    rawError.value = errorMessage(e)
    notify(rawError.value, true)
  } finally {
    busy.value = false
  }
}
function enableCpp() {
  try {
    const m = JSON.parse(advanced.value)
    if (!m.acm) throw new Error('请先配置 ACM 模式')
    m.acm.templates.cpp17 =
      '#include <iostream>\nusing namespace std;\nint main() {\n    // 读取输入，输出答案\n    return 0;\n}\n'
    advanced.value = JSON.stringify(m, null, 2)
  } catch (e) {
    notify(errorMessage(e), true)
  }
}
</script>
<template>
  <NuxtLink to="/admin" class="small muted"><ArrowLeft :size="13" /> 返回后台管理</NuxtLink>
  <div class="page-heading" style="margin-top: 22px">
    <div>
      <div class="eyebrow">PROBLEM EDITOR</div>
      <h1 class="page-title">{{ isNew ? '新建题目' : form.title }}</h1>
      <p class="subtitle">
        {{
          isNew ? '从一份完整的题面开始。' : '编辑题面、模板与判题配置。保存后会创建新的题目版本。'
        }}
      </p>
    </div>
    <div class="inline-actions">
      <label class="inline-actions small"
        ><input v-model="form.published" type="checkbox" />发布到题库</label
      ><UiButton :disabled="busy" @click="save"
        ><Save :size="14" />{{ busy ? '保存中…' : '保存题目' }}</UiButton
      >
    </div>
  </div>
  <p v-if="rawError" role="alert" class="error-box" style="margin-bottom: 20px">{{ rawError }}</p>
  <section class="panel">
    <div class="panel-tabs">
      <button
        v-for="t in [
          { id: 'basic', name: '基础信息' },
          { id: 'statement', name: '题面与题解' },
          { id: 'judge', name: '模板与用例' },
        ]"
        :key="t.id"
        :class="{ active: active === t.id }"
        @click="active = t.id"
      >
        {{ t.name }}
      </button>
    </div>
    <div style="padding: 24px">
      <div v-show="active === 'basic'" class="form-grid">
        <div class="form-field full">
          <label for="title">题目标题</label
          ><UiInput id="title" v-model="form.title" placeholder="例如：两数之和" />
        </div>
        <div class="form-field">
          <label for="category">分类</label
          ><select id="category" v-model="form.category" class="native-select">
            <option v-for="c in categories" :key="c.name">{{ c.name }}</option>
          </select>
        </div>
        <div class="form-field">
          <label for="difficulty">难度</label
          ><select id="difficulty" v-model="form.difficulty" class="native-select">
            <option>简单</option>
            <option>中等</option>
            <option>困难</option>
          </select>
        </div>
        <div class="form-field full">
          <label for="tags">知识点标签（空格或逗号分隔）</label><UiInput id="tags" v-model="tags" />
        </div>
        <div class="form-field">
          <label for="time">时间限制 / ms</label
          ><UiInput id="time" v-model.number="form.timeMs" type="number" min="100" max="30000" />
        </div>
        <div class="form-field">
          <label for="memory">内存限制 / MB</label
          ><UiInput id="memory" v-model.number="form.memoryMb" type="number" min="64" max="2048" />
        </div>
        <div class="form-field">
          <label for="source">来源标识</label
          ><UiInput id="source" v-model="form.source" :disabled="!isNew" />
        </div>
        <div class="form-field">
          <label for="sourceId">来源编号 / 幂等键</label
          ><UiInput id="sourceId" v-model="form.sourceId" :disabled="!isNew" />
        </div>
        <div class="form-field full">
          <label for="sourceUrl">来源链接（可选）</label
          ><UiInput id="sourceUrl" v-model="form.sourceUrl" placeholder="https://…" />
        </div>
      </div>
      <div v-show="active === 'statement'" style="display: flex; flex-direction: column; gap: 22px">
        <div
          v-for="f in [
            { key: 'description', label: '题目描述 · Markdown / LaTeX' },
            { key: 'inputDescription', label: '输入说明' },
            { key: 'outputDescription', label: '输出说明' },
            { key: 'constraints', label: '数据范围' },
            { key: 'hint', label: '提示' },
            { key: 'solution', label: '题解' },
          ]"
          :key="f.key"
          class="form-field"
        >
          <label :for="f.key">{{ f.label }}</label
          ><UiTextarea
            :id="f.key"
            v-model="form[f.key]"
            :style="{
              minHeight: f.key === 'description' || f.key === 'solution' ? '220px' : '100px',
            }"
          />
          <details v-if="form[f.key]">
            <summary class="small muted" style="cursor: pointer">预览</summary>
            <MarkdownContent :content="form[f.key]" />
          </details>
        </div>
      </div>
      <div v-show="active === 'judge'">
        <div class="inline-actions" style="justify-content: space-between">
          <h2 class="section-heading">执行契约</h2>
          <UiButton
            v-if="!['Hot100', '深度学习'].includes(form.category)"
            variant="outline"
            size="sm"
            @click="enableCpp"
            >添加 C++17 模板</UiButton
          >
        </div>
        <p class="subtitle">
          按 acm / function 配置模板、用例、输入约定和比较器。harness
          是平台调用代码，仅在沙箱运行。hidden=true 的用例用于正式判题，不展示为公开样例。
        </p>
        <p class="subtitle">
          支持比较器：tokens、exact、json、unordered_tokens、unordered_json、unordered_nested、float_tokens；浮点比较可配置
          absTolerance、relTolerance。
        </p>
        <UiTextarea
          v-model="advanced"
          aria-label="模板与用例 JSON"
          class="admin-editor"
          style="min-height: 580px; margin-top: 18px"
        />
        <p class="subtitle">
          Hot100 / 深度学习仅允许
          Python3。保存时会校验模板、用例、内存及时间限制，不完整配置会被拒绝。
        </p>
      </div>
    </div>
  </section>
</template>
