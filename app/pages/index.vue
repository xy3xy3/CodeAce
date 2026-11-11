<script setup lang="ts">
import { errorMessage } from '~/composables/useNotice'
import {
  Search,
  ArrowUpRight,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Check,
  Minus,
  Bookmark,
  Flame,
  Layers,
  BrainCircuit,
  Code2,
  SlidersHorizontal,
  RotateCcw,
} from 'lucide-vue-next'
const route = useRoute(),
  router = useRouter(),
  fetcher = useRequestFetch()
const filters = reactive({
  q: String(route.query.q || ''),
  category: String(route.query.category || ''),
  difficulty: String(route.query.difficulty || ''),
  tag: String(route.query.tag || ''),
  status: String(route.query.status || ''),
  page: Number(route.query.page) || 1,
})
const {
  data: list,
  refresh,
  error,
} = await useAsyncData('problems', () => fetcher<any>('/api/problems', { query: filters }), {
  watch: [() => ({ ...filters })],
})
const { data: stats } = await useAsyncData('stats', () => fetcher<any>('/api/stats'))
watch(
  () => ({ ...filters }),
  (v, old) => {
    if (v.page === old?.page) filters.page = 1
    router.replace({
      query: Object.fromEntries(Object.entries(filters).filter(([, x]) => x !== '' && x !== 1)),
    })
  },
)
watch(
  () => route.query,
  (query) => {
    const next = {
      q: String(query.q || ''),
      category: String(query.category || ''),
      difficulty: String(query.difficulty || ''),
      tag: String(query.tag || ''),
      status: String(query.status || ''),
      page: Number(query.page) || 1,
    }
    if (JSON.stringify(next) !== JSON.stringify(filters)) Object.assign(filters, next)
  },
)
const cards = [
  {
    category: 'Hot100',
    name: 'LeetCode Hot 100',
    caption: '高频经典，打好算法基础',
    icon: Flame,
    color: '#e9f3ed',
  },
  {
    category: '深度学习',
    name: '深度学习',
    caption: '从核心算子到注意力机制',
    icon: BrainCircuit,
    color: '#edf0fa',
  },
  {
    category: '',
    name: '全部题目',
    caption: '按自己的节奏，持续练习',
    icon: Layers,
    color: '#fcf1e4',
  },
]
function count(category: string) {
  return category
    ? stats.value?.categories?.find((c: any) => c.name === category) || { total: 0, solved: 0 }
    : { total: stats.value?.total || 0, solved: stats.value?.solved || 0 }
}
function reset() {
  Object.assign(filters, { q: '', category: '', difficulty: '', tag: '', status: '', page: 1 })
}
function shortcut(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    document.getElementById('problem-search')?.focus()
  }
}
onMounted(() => window.addEventListener('keydown', shortcut))
onBeforeUnmount(() => window.removeEventListener('keydown', shortcut))
</script>
<template>
  <div class="catalog-heading">
    <h1 class="page-title">题库</h1>
    <NuxtLink to="/progress" class="catalog-progress"
      ><Check :size="17" /> {{ stats?.solved || 0 }} / {{ stats?.total || 0 }} 已完成</NuxtLink
    >
  </div>
  <div class="category-tabs" aria-label="题目分类">
    <button
      v-for="c in cards"
      :key="c.name"
      :class="{ selected: filters.category === c.category }"
      @click="filters.category = c.category"
    >
      <component :is="c.icon" :size="19" />{{ c.name }}<span>{{ count(c.category).total }}</span>
    </button>
  </div>
  <div class="topic-strip" aria-label="知识点快捷筛选">
    <button :class="{ selected: !filters.tag }" @click="filters.tag = ''">全部知识点</button
    ><button
      v-for="tag in list?.tags?.slice(0, 12)"
      :key="tag"
      :class="{ selected: filters.tag === tag }"
      @click="filters.tag = filters.tag === tag ? '' : tag"
    >
      {{ tag }}
    </button>
  </div>
  <section class="panel content-gap">
    <div style="padding: 0 20px 20px">
      <div class="filter-bar">
        <div class="search-wrap">
          <Search :size="15" /><UiInput
            id="problem-search"
            v-model="filters.q"
            placeholder="搜索题目名称或来源编号…"
            aria-label="搜索题目"
          />
        </div>
        <select v-model="filters.difficulty" class="native-select" aria-label="难度">
          <option value="">全部难度</option>
          <option>简单</option>
          <option>中等</option>
          <option>困难</option></select
        ><select v-model="filters.status" class="native-select" aria-label="完成状态">
          <option value="">全部状态</option>
          <option value="todo">未完成</option>
          <option value="solved">已通过</option>
          <option value="favorite">我的收藏</option>
          <option value="wrong">错题本</option></select
        ><select v-model="filters.tag" class="native-select" aria-label="知识点">
          <option value="">全部知识点</option>
          <option v-for="tag in list?.tags" :key="tag">{{ tag }}</option></select
        ><UiButton variant="outline" size="icon" aria-label="重置筛选" @click="reset"
          ><RotateCcw :size="14"
        /></UiButton>
      </div>
    </div>
    <div v-if="error" class="error-box">
      加载失败：{{ errorMessage(error) }} <button @click="refresh()">重试</button>
    </div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 65px; text-align: center">状态</th>
            <th style="width: 58%">题目</th>
            <th>难度</th>
            <th>分类</th>
            <th style="text-align: right">开始练习</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in list?.items" :key="p.id">
            <td style="text-align: center">
              <Check v-if="p.solved" :size="16" style="color: #259e71" /><Minus
                v-else
                :size="14"
                style="color: #d0d9d2"
              />
            </td>
            <td>
              <NuxtLink
                :to="{ path: '/problems/' + p.id, query: { from: route.fullPath } }"
                class="problem-name"
                >{{ p.title }} <Bookmark v-if="p.favorite" :size="11" style="color: #a4b68f"
              /></NuxtLink>
              <div style="display: flex; gap: 6px; margin-top: 7px">
                <span v-for="t in p.tags?.slice(0, 3)" :key="t" class="pill">{{ t }}</span>
              </div>
            </td>
            <td>
              <span
                class="difficulty"
                :class="{
                  easy: p.difficulty === '简单',
                  medium: p.difficulty === '中等',
                  hard: p.difficulty === '困难',
                }"
                >{{ p.difficulty }}</span
              >
            </td>
            <td>
              <span class="muted" style="font-size: 13px">{{ p.category }}</span>
            </td>
            <td style="text-align: right">
              <NuxtLink
                :to="{ path: '/problems/' + p.id, query: { from: route.fullPath } }"
                class="practice-arrow"
                :aria-label="'练习 ' + p.title"
                ><ArrowRight :size="15"
              /></NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!list?.items?.length && !error" class="empty">
      没有找到匹配的题目<br /><button @click="reset" style="color: var(--primary)">
        清除筛选条件
      </button>
    </div>
    <div class="pagination">
      <span
        >共 {{ list?.total || 0 }} 道题目 · 第 {{ filters.page }} / {{ list?.pages || 1 }} 页</span
      >
      <div class="pagination-buttons">
        <UiButton
          variant="outline"
          size="icon"
          aria-label="上一页"
          :disabled="filters.page <= 1"
          @click="filters.page--"
          ><ChevronLeft :size="14" /></UiButton
        ><span style="padding: 0 10px; color: var(--primary)">{{ filters.page }}</span
        ><UiButton
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
<style scoped>
.catalog-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 16px;
}
.catalog-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted-foreground);
}
.category-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-bottom: 24px;
}
.category-tabs button {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--secondary);
  border-radius: 28px;
  padding: 13px 20px;
  font-size: 15px;
}
.category-tabs button.selected {
  background: #eee;
  color: #202020;
}
.category-tabs button span {
  opacity: 0.65;
}
.topic-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}
.topic-strip button {
  padding: 7px 11px;
  color: var(--muted-foreground);
  border-radius: 6px;
}
.topic-strip button:hover,
.topic-strip button.selected {
  color: var(--foreground);
  background: var(--secondary);
}
.content-gap {
  border: 0;
  background: transparent;
}
.content-gap > div:first-child {
  padding: 0 0 20px !important;
}
.practice-arrow {
  display: inline-grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: var(--muted-foreground);
}
.practice-arrow:hover {
  background: var(--secondary);
  color: var(--primary);
}
@media (max-width: 760px) {
  .catalog-heading {
    margin-bottom: 20px;
  }
  .category-tabs {
    gap: 8px;
  }
  .category-tabs button {
    padding: 10px 12px;
    font-size: 14px;
  }
  .catalog-progress {
    font-size: 12px;
  }
}
</style>
