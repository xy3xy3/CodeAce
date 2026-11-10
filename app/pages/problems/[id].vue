<script setup lang="ts">
import { errorMessage } from '~/composables/useNotice'
import {
  ArrowLeft,
  Play,
  Send,
  ChevronLeft,
  ChevronRight,
  Bookmark,
  Check,
  Code2,
  Terminal,
  RotateCcw,
  BookOpen,
  History,
  FileText,
  Lightbulb,
  ExternalLink,
  ArrowRight,
  LoaderCircle,
} from 'lucide-vue-next'
const route = useRoute(),
  fetcher = useRequestFetch(),
  { notify } = useNotice()
const { data: p, error } = await useAsyncData('problem-' + route.params.id, () =>
  fetcher<any>('/api/problems/' + route.params.id),
)
const back = computed(() => {
  const s = String(route.query.from || '/')
  return s.startsWith('/') && !s.startsWith('//') ? s : '/'
})
const mode = ref(
    p.value?.modes[String(route.query.mode)]
      ? String(route.query.mode)
      : p.value?.modes.function
        ? 'function'
        : 'acm',
  ),
  language = ref(String(route.query.language || 'python3')),
  tab = ref('statement'),
  code = ref(''),
  input = ref(''),
  custom = ref(false),
  busy = ref(''),
  result = ref<any>(null),
  saved = ref('加载草稿…'),
  width = ref(47),
  favorite = ref(!!p.value?.personal.favorite),
  note = ref(p.value?.personal.note || ''),
  noteBusy = ref(false)
const variant = computed(() => p.value?.modes[mode.value]),
  languages = computed(() => Object.keys(variant.value?.templates || {})),
  neighbors = computed(() => p.value?.neighbors || []),
  index = computed(() =>
    neighbors.value.findIndex((n: any) => String(n.id) === String(p.value?.id)),
  )
const { data: records, refresh: refreshRecords } = await useAsyncData(
  'problem-records-' + route.params.id,
  () => fetcher<any>('/api/submissions', { query: { problemId: route.params.id } }),
)
let draftTimer: ReturnType<typeof setTimeout> | undefined,
  poll: ReturnType<typeof setInterval> | undefined,
  loadingDraft = false,
  requestSerial = 0
async function saveDraft(m = mode.value, l = language.value, c = code.value) {
  try {
    await $fetch('/api/problems/' + p.value.id + '/draft', {
      method: 'PUT',
      query: { mode: m, language: l },
      body: { code: c },
    })
    saved.value = '已保存'
  } catch {
    saved.value = '保存失败，请重试'
  }
}
async function loadDraft() {
  if (!p.value || !variant.value) return
  const serial = ++requestSerial
  loadingDraft = true
  clearTimeout(draftTimer)
  try {
    const draft = await $fetch<any>('/api/problems/' + p.value.id + '/draft', {
      query: { mode: mode.value, language: language.value },
    })
    if (serial !== requestSerial) return
    code.value = draft.code ?? variant.value.templates[language.value] ?? ''
    input.value = variant.value.cases[0]?.input || ''
    saved.value = '已保存'
  } catch {
    code.value = variant.value.templates[language.value] || ''
    saved.value = '未能读取草稿'
  } finally {
    await nextTick()
    loadingDraft = false
  }
}
watch(code, () => {
  if (loadingDraft) return
  saved.value = '正在保存…'
  clearTimeout(draftTimer)
  draftTimer = setTimeout(() => saveDraft(), 800)
})
async function switchMode(e: Event) {
  const next = (e.target as HTMLSelectElement).value
  await saveDraft()
  mode.value = next
  if (!languages.value.includes(language.value)) language.value = languages.value[0] || 'python3'
  result.value = null
  await navigateTo(
    { query: { ...route.query, mode: mode.value, language: language.value } },
    { replace: true },
  )
  await loadDraft()
}
async function switchLanguage(e: Event) {
  await saveDraft()
  language.value = (e.target as HTMLSelectElement).value
  result.value = null
  await navigateTo(
    { query: { ...route.query, mode: mode.value, language: language.value } },
    { replace: true },
  )
  await loadDraft()
}
onMounted(loadDraft)
onBeforeUnmount(() => {
  clearTimeout(draftTimer)
  clearInterval(poll)
  if (!loadingDraft && saved.value === '正在保存…') void saveDraft()
})
async function reset() {
  if (!confirm('恢复初始模板？当前模式下的草稿会被替换。')) return
  code.value = variant.value.templates[language.value] || ''
  await saveDraft()
}
async function personal() {
  await $fetch('/api/problems/' + p.value.id + '/personal', {
    method: 'PUT',
    body: { favorite: favorite.value, note: note.value },
  })
}
async function toggleFavorite() {
  favorite.value = !favorite.value
  try {
    await personal()
    notify(favorite.value ? '已加入收藏' : '已取消收藏')
  } catch (e) {
    favorite.value = !favorite.value
    notify(errorMessage(e), true)
  }
}
async function saveNote() {
  noteBusy.value = true
  try {
    await personal()
    notify('笔记已保存')
  } catch (e) {
    notify(errorMessage(e), true)
  } finally {
    noteBusy.value = false
  }
}
async function execute(submit = false) {
  busy.value = submit ? 'submit' : 'run'
  result.value = null
  await saveDraft()
  try {
    const body: any = { code: code.value, language: language.value, mode: mode.value }
    if (!submit && custom.value) body.input = input.value
    const response = await $fetch<any>(
      '/api/problems/' + p.value.id + (submit ? '/submit' : '/run'),
      { method: 'POST', body, timeout: 180000 },
    )
    if (!submit) {
      result.value = response
      busy.value = ''
      return
    }
    result.value = { status: 'QUEUED', submissionId: response.id }
    let attempts = 0
    poll = setInterval(async () => {
      try {
        const s = await $fetch<any>('/api/submissions/' + response.id)
        if (!['QUEUED', 'RUNNING'].includes(s.status)) {
          clearInterval(poll)
          result.value = { ...s.result, status: s.status, submissionId: s.id }
          busy.value = ''
          await refreshRecords()
        } else {
          result.value = { status: s.status, submissionId: s.id }
          if (++attempts > 120) {
            clearInterval(poll)
            busy.value = ''
            notify('任务仍在处理，可到刷题记录查看', true)
          }
        }
      } catch (e) {
        clearInterval(poll)
        busy.value = ''
        notify(errorMessage(e), true)
      }
    }, 1000)
  } catch (e) {
    busy.value = ''
    result.value = { status: 'SYSTEM_ERROR', error: errorMessage(e) }
    notify(errorMessage(e), true)
  }
}
</script>
<template>
  <div v-if="error" class="error-box">
    {{ errorMessage(error) }} <NuxtLink to="/">返回题库</NuxtLink>
  </div>
  <div v-else-if="p" class="workbench">
    <div class="workbench-nav">
      <div class="inline-actions">
        <NuxtLink :to="back" class="small muted"><ArrowLeft :size="14" /> &nbsp;返回题库</NuxtLink
        ><span class="nav-divider" /><span class="small">{{ p.category }}</span
        ><span class="pill">{{ index + 1 }} / {{ neighbors.length }}</span
        ><NuxtLink
          v-if="index > 0"
          :to="{ path: '/problems/' + neighbors[index - 1].id, query: route.query }"
          aria-label="上一题"
          ><ChevronLeft :size="16" /></NuxtLink
        ><NuxtLink
          v-if="index < neighbors.length - 1"
          :to="{ path: '/problems/' + neighbors[index + 1].id, query: route.query }"
          aria-label="下一题"
          ><ChevronRight :size="16"
        /></NuxtLink>
      </div>
      <div class="inline-actions">
        <UiButton variant="outline" size="sm" :disabled="!!busy" @click="execute(false)"
          ><LoaderCircle v-if="busy === 'run'" :size="14" class="animate-spin" /><Play
            v-else
            :size="14"
          />运行</UiButton
        ><UiButton size="sm" :disabled="!!busy" @click="execute(true)"
          ><LoaderCircle v-if="busy === 'submit'" :size="14" class="animate-spin" /><Send
            v-else
            :size="13"
          />提交代码</UiButton
        >
      </div>
    </div>
    <div class="workbench-grid" :style="{ '--left-width': width + '%' }">
      <section class="panel statement-panel">
        <div class="panel-tabs" role="tablist" aria-label="题目信息">
          <button
            v-for="t in [
              { id: 'statement', label: '题目描述', icon: BookOpen },
              { id: 'solution', label: '题解', icon: Lightbulb },
              { id: 'records', label: '提交记录', icon: History },
              { id: 'note', label: '我的笔记', icon: FileText },
            ]"
            :key="t.id"
            role="tab"
            :aria-selected="tab === t.id"
            :class="{ active: tab === t.id }"
            @click="tab = t.id"
          >
            <component :is="t.icon" :size="13" /> &nbsp;{{ t.label }}
          </button>
        </div>
        <div class="statement-scroll">
          <template v-if="tab === 'statement'"
            ><div
              style="
                display: flex;
                align-items: flex-start;
                justify-content: space-between;
                gap: 12px;
              "
            >
              <h1 style="font-size: 22px; font-weight: 650; letter-spacing: -0.5px">
                {{ p.title }}
              </h1>
              <button
                :aria-label="favorite ? '取消收藏' : '收藏题目'"
                :aria-pressed="favorite"
                @click="toggleFavorite"
              >
                <Bookmark
                  :size="18"
                  :fill="favorite ? '#459b70' : 'none'"
                  :style="{ color: favorite ? '#459b70' : '#a8b6ac' }"
                />
              </button>
            </div>
            <div class="problem-meta">
              <span
                class="difficulty"
                :class="{
                  easy: p.difficulty === '简单',
                  medium: p.difficulty === '中等',
                  hard: p.difficulty === '困难',
                }"
                >{{ p.difficulty }}</span
              ><span v-for="t in p.tags" :key="t" class="pill">{{ t }}</span>
            </div>
            <MarkdownContent :content="p.description" /><template v-if="mode === 'acm'"
              ><h2 class="minor-heading">输入格式</h2>
              <MarkdownContent :content="p.inputDescription" />
              <h2 class="minor-heading">输出格式</h2>
              <MarkdownContent :content="p.outputDescription"
            /></template>
            <h2 class="minor-heading">{{ mode === 'function' ? '函数输入约定' : '输入约定' }}</h2>
            <p class="small muted" style="line-height: 1.9">{{ variant?.inputHelp }}</p>
            <h2 class="minor-heading">示例</h2>
            <div
              v-for="(sample, i) in (variant?.cases || []).slice(0, 3)"
              :key="i"
              class="sample-card"
            >
              <div class="sample-title">示例 {{ Number(i) + 1 }}</div>
              <div class="sample-pair">
                <span>输入</span>
                <pre>{{ sample.input }}</pre>
              </div>
              <div class="sample-pair">
                <span>输出</span>
                <pre>{{ sample.expected }}</pre>
              </div>
              <div
                v-if="p.samples?.[Number(i)]?.explanation"
                class="sample-explanation"
                style="margin-top: 12px; border-top: 1px solid var(--border); padding-top: 8px"
              >
                <span class="small muted">解释</span
                ><MarkdownContent :content="p.samples[Number(i)].explanation" />
              </div>
            </div>
            <template v-if="p.constraints"
              ><h2 class="minor-heading">数据范围</h2>
              <MarkdownContent :content="p.constraints" /></template
            ><template v-if="p.hint"
              ><details class="hint-card">
                <summary><Lightbulb :size="13" /> &nbsp;思考提示</summary>
                <MarkdownContent :content="p.hint" /></details
            ></template>
            <div class="limit-row">
              <span>时间 {{ p.timeMs }} ms</span><span>内存 {{ p.memoryMb }} MB</span
              ><span>{{
                variant?.runtime === 'torch'
                  ? 'PyTorch CPU'
                  : variant?.runtime === 'numpy'
                    ? 'NumPy'
                    : 'Python 3 / C++17'
              }}</span>
            </div>
            <div v-if="p.sourceUrl" style="margin-top: 20px">
              <a :href="p.sourceUrl" target="_blank" rel="noopener noreferrer" class="small muted"
                >{{ p.source === 'codeky' ? '来源：CodeKy' : '独立练习 · 参考资料' }} #{{
                  p.sourceId
                }}
                <ExternalLink :size="11"
              /></a>
            </div>
            <div
              v-if="p.similar?.length"
              style="margin-top: 28px; border-top: 1px solid var(--border); padding-top: 20px"
            >
              <h2 class="minor-heading" style="margin-top: 0">继续练习</h2>
              <NuxtLink
                v-for="n in p.similar"
                :key="n.id"
                :to="{ path: '/problems/' + n.id, query: route.query }"
                class="similar-link"
                >{{ n.title }}<ArrowRight :size="12"
              /></NuxtLink></div
          ></template>
          <template v-else-if="tab === 'solution'"
            ><h2 class="section-heading">题解</h2>
            <MarkdownContent v-if="p.solution" :content="p.solution" />
            <div v-else class="empty">
              <Lightbulb :size="25" style="margin-bottom: 12px" />
              <p>暂无可用题解</p>
              <p class="small">先试着独立思考，也可以在后台整理自己的解法。</p>
            </div>
            <NuxtLink :to="'/admin/' + p.id" class="small" style="color: var(--primary)"
              >在后台编辑题解 <ArrowRight :size="12" /></NuxtLink
          ></template>
          <template v-else-if="tab === 'records'"
            ><div class="inline-actions" style="justify-content: space-between">
              <h2 class="section-heading">提交记录</h2>
              <button class="small muted" @click="refreshRecords()">刷新</button>
            </div>
            <div v-if="!records?.items?.length" class="empty">
              还没有提交记录<br /><span class="small">完成一次正式提交，让思考留下痕迹。</span>
            </div>
            <NuxtLink
              v-for="r in records?.items"
              :key="r.id"
              :to="'/submissions/' + r.id"
              class="record-row"
              ><span class="status-badge" :class="r.status">{{ r.status }}</span
              ><span class="small muted"
                >{{ r.language === 'python3' ? 'Python 3' : 'C++17' }} ·
                {{ r.mode === 'function' ? '函数模式' : 'ACM 模式' }} ·
                <span class="record-case-count"
                  >{{ r.result?.passed ?? '–' }} / {{ r.result?.total ?? '–' }} 个用例</span
                ><br />{{ r.result?.timeMs ?? '–' }} ms ·
                {{ r.result?.memoryKb ? Math.round(r.result.memoryKb / 1024) : '–' }} MB<br />{{
                  new Date(r.created_at).toLocaleString('zh-CN')
                }}</span
              ><ArrowRight :size="13" /></NuxtLink
          ></template>
          <template v-else
            ><h2 class="section-heading" style="margin-bottom: 14px">我的笔记</h2>
            <UiTextarea
              v-model="note"
              aria-label="个人笔记"
              placeholder="记录思路、易错点和复杂度分析，支持 Markdown…"
              style="min-height: 260px; line-height: 1.9" /><UiButton
              size="sm"
              style="margin-top: 14px"
              :disabled="noteBusy"
              @click="saveNote"
              >保存笔记</UiButton
            ><MarkdownContent v-if="note" :content="note"
          /></template>
        </div>
      </section>
      <section class="editor-column">
        <div class="panel editor-panel">
          <div class="editor-heading">
            <div class="inline-actions small">
              <Code2 :size="15" style="color: #5f8b6c" /><span>代码</span
              ><span class="pill">{{ mode === 'function' ? '函数模式' : 'ACM 模式' }}</span>
            </div>
            <div class="inline-actions">
              <select
                :value="language"
                aria-label="代码语言"
                class="editor-select"
                :disabled="!!busy"
                @change="switchLanguage"
              >
                <option v-for="l in languages" :key="l" :value="l">
                  {{ l === 'python3' ? 'Python 3' : 'C++17' }}
                </option></select
              ><select
                :value="mode"
                aria-label="输入模式"
                class="editor-select"
                :disabled="!!busy"
                @change="switchMode"
              >
                <option v-for="m in Object.keys(p.modes)" :key="m" :value="m">
                  {{ m === 'function' ? '函数模式' : 'ACM 模式' }}
                </option></select
              ><button aria-label="恢复模板" @click="reset">
                <RotateCcw :size="13" class="muted" />
              </button>
            </div>
          </div>
          <ClientOnly
            ><CodeEditor :key="language" v-model="code" :language="language" /><template #fallback
              ><div class="empty">正在加载编辑器…</div></template
            ></ClientOnly
          >
          <div class="editor-footer">
            <span class="saving-state"><Check :size="10" /> {{ saved }}</span
            ><span>{{ code.split('\n').length }} 行 · UTF-8</span>
          </div>
        </div>
        <div class="panel test-panel">
          <div class="panel-tabs" role="tablist" aria-label="测试输入">
            <button
              :class="{ active: !custom }"
              :aria-selected="!custom"
              role="tab"
              @click="custom = false"
            >
              测试用例</button
            ><button
              :class="{ active: custom }"
              :aria-selected="custom"
              role="tab"
              @click="custom = true"
            >
              自定义输入</button
            ><span style="margin-left: auto; align-self: center; color: #a4afa7; font-size: 10px"
              ><Terminal :size="12" /> &nbsp;CONSOLE</span
            >
          </div>
          <div class="test-content">
            <UiTextarea
              v-if="custom"
              v-model="input"
              aria-label="自定义测试输入"
              style="min-height: 95px; font-family: Consolas, monospace; font-size: 12px"
            />
            <div v-else class="small muted">
              运行 {{ variant?.cases?.length || 0 }} 个公开用例。正式提交会运行该题的全部判题用例。
            </div>
            <div v-if="!result" class="console-empty">
              <Terminal :size="20" /><span>点击「运行」，看看代码的表现。</span>
            </div>
            <div v-else class="judge-result" aria-live="polite">
              <div class="inline-actions" style="justify-content: space-between">
                <div class="inline-actions">
                  <span class="status-badge" :class="result.status">{{ result.status }}</span
                  ><span class="small muted" v-if="result.total"
                    >{{ result.passed }} / {{ result.total }} 通过 · {{ result.timeMs }} ms</span
                  >
                </div>
                <NuxtLink
                  v-if="result.submissionId"
                  :to="'/submissions/' + result.submissionId"
                  class="small muted"
                  >查看记录 <ArrowRight :size="11"
                /></NuxtLink>
              </div>
              <p v-if="result.error" class="error-box" style="margin-top: 12px">
                {{ result.error }}
              </p>
              <div v-for="(r, i) in result.results" :key="i" class="case-result">
                <div class="small muted">Case {{ Number(i) + 1 }} · {{ r.status }}</div>
                <details
                  v-if="r.status !== 'AC' && r.input !== undefined"
                  class="small"
                  style="margin-top: 8px"
                >
                  <summary class="muted" style="cursor: pointer">查看失败输入</summary>
                  <pre class="code-block">{{ r.input }}</pre>
                  <pre v-if="r.expected !== undefined" class="code-block">
预期：{{ r.expected }}</pre>
                </details>
                <pre v-if="r.stdout" class="code-block">{{ r.stdout }}</pre>
                <pre v-if="r.stderr" class="code-block error-output">{{ r.stderr }}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
    <div class="resize-control">
      <label for="split-width">题面宽度</label
      ><input
        id="split-width"
        v-model="width"
        type="range"
        min="35"
        max="65"
        aria-label="题面宽度"
      /><span>{{ width }}%</span
      ><span style="margin-left: auto">保持专注，享受解决问题的过程。</span>
    </div>
  </div>
</template>
<style scoped>
:global(.main-area:has(.workbench)) {
  padding: 20px 24px;
  max-width: none;
}
.workbench-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  gap: 12px;
}
.nav-divider {
  height: 14px;
  width: 1px;
  background: var(--border);
  margin: 0 4px;
}
.workbench-grid {
  display: grid;
  grid-template-columns: var(--left-width) minmax(0, 1fr);
  gap: 14px;
  align-items: start;
}
.statement-panel {
  min-width: 0;
  overflow: hidden;
}
.statement-scroll {
  padding: 25px;
  max-height: calc(100vh - 230px);
  overflow: auto;
  min-height: 640px;
}
.problem-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0 25px;
  flex-wrap: wrap;
}
.minor-heading {
  font-size: 13px;
  font-weight: 650;
  margin: 24px 0 12px;
  color: #344f3e;
}
.sample-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  margin: 12px 0;
  background: #fcfdfb;
  padding: 14px;
}
.sample-title {
  font-weight: 600;
  font-size: 11px;
  margin-bottom: 12px;
  color: #708a75;
}
.sample-pair {
  display: grid;
  grid-template-columns: 36px 1fr;
  gap: 10px;
  font-size: 11px;
  margin-top: 9px;
}
.sample-pair > span {
  color: #96a398;
}
.sample-pair pre {
  margin: 0;
  font:
    12px/1.8 Consolas,
    monospace;
  white-space: pre-wrap;
  word-break: break-word;
  color: #506c56;
}
.hint-card {
  background: #faf8ef;
  border: 1px solid #eee8d4;
  border-radius: 8px;
  padding: 13px 15px;
  margin-top: 24px;
}
.hint-card summary {
  cursor: pointer;
  list-style: none;
  font-size: 11px;
  color: #a88d50;
}
.limit-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  color: #9eaba0;
  font-size: 10px;
  margin-top: 28px;
}
.similar-link {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #789080;
  padding: 9px 0;
}
.record-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border);
  padding: 16px 0;
  line-height: 1.8;
}
.editor-column {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.editor-panel {
  overflow: hidden;
}
.editor-heading {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-height: 50px;
}
.editor-select {
  background: transparent;
  border: none;
  color: #6c8372;
  font-size: 10px;
  max-width: 95px;
}
.editor-footer {
  border-top: 1px solid var(--border);
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: #a9b4ab;
}
.test-content {
  padding: 18px;
}
.console-empty {
  min-height: 105px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  gap: 12px;
  color: #b5bfb6;
  font-size: 11px;
}
.judge-result {
  margin-top: 15px;
}
.case-result {
  margin-top: 12px;
}
.case-result .code-block {
  padding: 10px;
  font-size: 11px;
  margin-top: 5px;
}
.error-output {
  color: #b9644c;
}
.resize-control {
  display: flex;
  gap: 9px;
  align-items: center;
  font-size: 9px;
  color: #a5b0a7;
  margin-top: 12px;
}
.resize-control input {
  width: 80px;
  height: 3px;
  accent-color: var(--primary);
}
@media (max-width: 1100px) {
  .statement-scroll {
    padding: 20px;
  }
  .panel-tabs {
    gap: 14px;
    padding: 0 16px;
  }
  .panel-tabs button {
    font-size: 10px;
  }
  .editor-heading {
    flex-wrap: wrap;
  }
  .statement-scroll {
    min-height: 600px;
  }
}
@media (max-width: 850px) {
  .workbench-grid {
    grid-template-columns: 1fr;
  }
  .statement-scroll {
    max-height: none;
    min-height: 0;
  }
  .resize-control {
    display: none;
  }
  .workbench-nav .nav-divider,
  .workbench-nav .pill {
    display: none;
  }
  .workbench-nav > .inline-actions:first-child {
    gap: 6px;
  }
  :global(.main-area:has(.workbench)) {
    padding: 18px 12px;
  }
  .panel-tabs {
    gap: 22px;
  }
  .workbench-nav {
    flex-wrap: wrap;
  }
}
</style>
