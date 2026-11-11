<script setup lang="ts">
import { errorMessage } from '~/composables/useNotice'
import {
  Plus,
  Search,
  ArrowUpRight,
  Upload,
  Database,
  FileJson,
  Check,
  RefreshCw,
} from 'lucide-vue-next'
const importExample = `{
  "dryRun": true,
  "problems": [{
    "source": "personal", "sourceId": "unique-key",
    "title": "两整数求和", "category": "通用算法",
    "difficulty": "简单", "description": "输入 a 和 b，输出它们的和。",
    "published": true,
    "modes": { "acm": {
      "templates": {"python3": "# 读取输入并输出答案"},
      "cases": [{"input": "1 2", "expected": "3", "compare": "tokens", "hidden": false}]
    }}
  }]
}`
const fetcher = useRequestFetch(),
  { notify } = useNotice(),
  query = reactive({ admin: '1', q: '', page: 1 }),
  section = ref('problems'),
  payload = ref('{"problems": []}'),
  dryRun = ref(true),
  busy = ref(false),
  report = ref<any>(null),
  categoryName = ref('')
const { data: list, refresh } = await useAsyncData(
  'admin-problems',
  () => fetcher<any>('/api/problems', { query }),
  { watch: [() => ({ ...query })] },
)
const { data: source, refresh: refreshSource } = await useAsyncData('source-report', () =>
  fetcher<any>('/api/source-report'),
)
const { data: categories, refresh: refreshCategories } = await useAsyncData(
  'admin-categories',
  () => fetcher<any[]>('/api/categories'),
)
const counts = computed(() => ({
  target: source.value?.inventory.length || 0,
  ready: source.value?.inventory.filter((x: any) => x.published).length || 0,
  pending: source.value?.inventory.filter((x: any) => !x.published).length || 0,
}))
async function importData() {
  busy.value = true
  try {
    const b = JSON.parse(payload.value)
    report.value = await $fetch('/api/import', {
      method: 'POST',
      body: { ...b, dryRun: dryRun.value },
    })
    notify(dryRun.value ? '格式检查完成' : '导入完成')
    if (!dryRun.value) {
      await refresh()
      await refreshSource()
    }
  } catch (e) {
    notify(errorMessage(e), true)
  } finally {
    busy.value = false
  }
}
async function archive(id: string) {
  if (!confirm('下架后将从练习题库隐藏，历史提交仍保留。继续？')) return
  try {
    await $fetch('/api/problems/' + id, { method: 'DELETE' })
    await refresh()
    notify('已下架题目')
  } catch (e) {
    notify(errorMessage(e), true)
  }
}
async function addCategory() {
  try {
    await $fetch('/api/categories', { method: 'POST', body: { name: categoryName.value } })
    categoryName.value = ''
    await refreshCategories()
    notify('分类已添加')
  } catch (e) {
    notify(errorMessage(e), true)
  }
}
async function removeCategory(name: string) {
  if (!confirm('删除分类 ' + name + '？')) return
  try {
    await $fetch('/api/categories', { method: 'DELETE', query: { name } })
    await refreshCategories()
  } catch (e) {
    notify(errorMessage(e), true)
  }
}
</script>
<template>
  <div class="page-heading">
    <div>
      <h1 class="page-title">后台管理</h1>
    </div>
    <NuxtLink to="/admin/new"
      ><UiButton><Plus :size="15" />新建题目</UiButton></NuxtLink
    >
  </div>
  <section class="panel">
    <div class="panel-tabs">
      <button
        v-for="t in [
          { id: 'problems', name: '题目管理' },
          { id: 'import', name: 'API / 批量导入' },
          { id: 'source', name: '来源同步报告' },
          { id: 'categories', name: '分类管理' },
        ]"
        :key="t.id"
        :class="{ active: section === t.id }"
        @click="section = t.id"
      >
        {{ t.name }}
      </button>
    </div>
    <template v-if="section === 'problems'"
      ><div class="filter-bar" style="padding: 20px">
        <div class="search-wrap">
          <Search :size="15" /><UiInput
            v-model="query.q"
            placeholder="搜索题目…"
            aria-label="管理题目搜索"
          />
        </div>
        <UiButton variant="outline" @click="refresh()"><RefreshCw :size="13" />刷新</UiButton>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>题目</th>
              <th>分类</th>
              <th>难度</th>
              <th>发布状态</th>
              <th style="text-align: right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in list?.items" :key="p.id">
              <td>
                <NuxtLink :to="'/admin/' + p.id" class="problem-name">{{ p.title }}</NuxtLink>
              </td>
              <td class="muted">{{ p.category }}</td>
              <td class="muted">{{ p.difficulty }}</td>
              <td>
                <span class="status-badge" :class="p.published ? 'AC' : ''">{{
                  p.published ? '已发布' : '草稿 / 已下架'
                }}</span>
              </td>
              <td>
                <div class="inline-actions" style="justify-content: flex-end">
                  <NuxtLink :to="'/admin/' + p.id"
                    ><UiButton variant="outline" size="sm">编辑</UiButton></NuxtLink
                  ><UiButton v-if="p.published" variant="ghost" size="sm" @click="archive(p.id)"
                    >下架</UiButton
                  >
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!list?.items?.length" class="empty">暂无题目</div>
      <div class="pagination">
        <span>共 {{ list?.total || 0 }} 道 · 第 {{ query.page }} / {{ list?.pages || 1 }} 页</span>
        <div class="inline-actions">
          <UiButton size="sm" variant="outline" :disabled="query.page <= 1" @click="query.page--"
            >上一页</UiButton
          ><UiButton
            size="sm"
            variant="outline"
            :disabled="query.page >= (list?.pages || 1)"
            @click="query.page++"
            >下一页</UiButton
          >
        </div>
      </div></template
    >
    <div v-else-if="section === 'import'" style="padding: 24px">
      <h2 class="section-heading">导入题目数据</h2>
      <p class="subtitle">
        粘贴 JSON，一次最多 100
        道。建议先执行预检查，确认后再写入。来源标识用于幂等更新，本地已编辑的题目会保留。
      </p>
      <UiTextarea
        v-model="payload"
        aria-label="导入 JSON"
        class="admin-editor"
        style="margin-top: 20px"
      />
      <div class="inline-actions" style="margin-top: 16px">
        <label class="inline-actions small"
          ><input v-model="dryRun" type="checkbox" />仅预检查，不写入数据库</label
        ><UiButton :disabled="busy" style="margin-left: auto" @click="importData"
          ><Upload :size="14" />{{ dryRun ? '检查格式' : '执行导入' }}</UiButton
        >
      </div>
      <pre
        v-if="report"
        class="code-block"
        style="margin-top: 20px; max-height: 400px; overflow: auto"
        aria-label="导入结果"
        >{{ JSON.stringify(report, null, 2) }}</pre>
      <details style="margin-top: 24px">
        <summary class="small" style="cursor: pointer; color: var(--primary)">
          <FileJson :size="14" /> &nbsp;查看 API 与数据格式
        </summary>
        <p class="subtitle">
          POST /api/import · Content-Type: application/json<br />使用当前登录会话或 Authorization:
          Bearer &lt;NUXT_IMPORT_KEY&gt;。密钥保存在服务器 .env 中，请勿写入题目数据。
        </p>
        <pre class="code-block" style="margin-top: 12px">{{ importExample }}</pre>
        <p class="subtitle">
          完整 schema：shared/problem.ts。函数模式在 mode 下配置 prelude、harness
          及每个用例的调用代码；脚本仅在受限沙箱执行。
        </p>
      </details>
    </div>
    <div v-else-if="section === 'source'" style="padding: 24px">
      <div class="page-heading">
        <div>
          <h2 class="section-heading">来源覆盖与导入质量</h2>
          <p class="subtitle">
            目标目录 {{ counts.target }} 道 · 当前可刷 {{ counts.ready }} 道 · 待处理
            {{ counts.pending }} 道。目录数量不等于已导入数量。
          </p>
        </div>
        <UiButton variant="outline" size="sm" @click="refreshSource()">刷新</UiButton>
      </div>
      <div class="table-wrap" style="max-height: 520px">
        <table class="data-table">
          <thead>
            <tr>
              <th>来源编号</th>
              <th>题目</th>
              <th>分类</th>
              <th>状态</th>
              <th>原因</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in source?.inventory" :key="r.source_id">
              <td class="mono muted">{{ r.source_id }}</td>
              <td>{{ r.title }}</td>
              <td class="muted">{{ r.category }}</td>
              <td>
                <span class="status-badge" :class="r.published ? 'AC' : ''">{{
                  r.published ? '可刷' : r.status
                }}</span>
              </td>
              <td class="muted">{{ r.reason || '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else style="padding: 24px">
      <h2 class="section-heading">分类管理</h2>
      <div class="inline-actions" style="max-width: 420px; margin: 20px 0">
        <UiInput v-model="categoryName" placeholder="新分类名称" aria-label="分类名称" /><UiButton
          @click="addCategory"
          >添加</UiButton
        >
      </div>
      <div
        v-for="c in categories"
        :key="c.name"
        class="inline-actions"
        style="padding: 14px 0; border-bottom: 1px solid var(--border); max-width: 600px"
      >
        <span>{{ c.name }}</span
        ><UiButton
          size="sm"
          variant="ghost"
          style="margin-left: auto"
          @click="removeCategory(c.name)"
          >删除</UiButton
        >
      </div>
      <p class="subtitle">已有题目的分类需先移动题目，才能删除。</p>
    </div>
  </section>
</template>
