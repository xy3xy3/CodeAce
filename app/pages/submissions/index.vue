<script setup lang="ts">
import { Search, ArrowUpRight, ChevronLeft, ChevronRight, History } from 'lucide-vue-next'
const route = useRoute(),
  fetcher = useRequestFetch(),
  filters = reactive({
    q: '',
    status: '',
    language: '',
    page: 1,
    problemId: String(route.query.problemId || ''),
  })
const { data: list, refresh } = await useAsyncData(
  'submissions',
  () => fetcher<any>('/api/submissions', { query: filters }),
  { watch: [() => ({ ...filters })] },
)
const format = (s: string) => new Date(s).toLocaleString('zh-CN', { hour12: false })
</script>
<template>
  <div class="page-heading">
    <div>
      <h1 class="page-title">刷题记录</h1>
    </div>
    <UiButton variant="outline" @click="refresh()">刷新记录</UiButton>
  </div>
  <section class="panel">
    <div class="filter-bar" style="padding: 20px">
      <div class="search-wrap">
        <Search :size="15" /><UiInput
          v-model="filters.q"
          placeholder="搜索题目…"
          aria-label="搜索提交题目"
        />
      </div>
      <select v-model="filters.status" class="native-select" aria-label="判题结果">
        <option value="">全部结果</option>
        <option
          v-for="s in [
            'AC',
            'WA',
            'CE',
            'RE',
            'TLE',
            'MLE',
            'OLE',
            'SYSTEM_ERROR',
            'QUEUED',
            'RUNNING',
          ]"
          :key="s"
        >
          {{ s }}
        </option></select
      ><select v-model="filters.language" class="native-select" aria-label="提交语言">
        <option value="">全部语言</option>
        <option value="python3">Python 3</option>
        <option value="cpp17">C++17</option>
      </select>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>提交编号</th>
            <th>题目</th>
            <th>结果</th>
            <th>通过用例</th>
            <th>语言 / 模式</th>
            <th>用时 / 内存</th>
            <th>提交时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in list?.items" :key="s.id">
            <td class="mono muted">
              <NuxtLink :to="'/submissions/' + s.id"
                >#{{ s.id }} <ArrowUpRight :size="11"
              /></NuxtLink>
            </td>
            <td>
              <NuxtLink :to="'/submissions/' + s.id" class="problem-name">{{
                s.problem_title
              }}</NuxtLink>
            </td>
            <td>
              <span class="status-badge" :class="s.status">{{ s.status }}</span>
            </td>
            <td class="mono muted submission-case-count">
              {{ s.result?.passed ?? '–' }} / {{ s.result?.total ?? '–' }}
            </td>
            <td class="muted">
              {{ s.language === 'python3' ? 'Python 3' : 'C++17' }} ·
              {{ s.mode === 'function' ? '函数' : 'ACM' }}
            </td>
            <td class="mono muted">
              {{ s.result?.timeMs ?? '–' }} ms /
              {{ s.result?.memoryKb ? Math.round(s.result.memoryKb / 1024) + ' MB' : '–' }}
            </td>
            <td class="muted" style="font-size: 13px">{{ format(s.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!list?.items?.length" class="empty">
      <History :size="28" style="margin-bottom: 12px; color: #b5c4b7" />
      <p>还没有提交记录</p>
    </div>
    <div class="pagination">
      <span>共 {{ list?.total || 0 }} 次提交</span>
      <div class="pagination-buttons">
        <UiButton
          variant="outline"
          size="icon"
          aria-label="上一页"
          :disabled="filters.page <= 1"
          @click="filters.page--"
          ><ChevronLeft :size="14" /></UiButton
        >{{ filters.page }} / {{ list?.pages || 1
        }}<UiButton
          variant="outline"
          size="icon"
          aria-label="下一页"
          :disabled="filters.page >= (list?.pages || 1)"
          @click="filters.page++"
          ><ChevronRight :size="14"
        /></UiButton>
      </div>
    </div>
  </section>
</template>
