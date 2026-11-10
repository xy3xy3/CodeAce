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
  <div class="page-heading">
    <div>
      <div class="eyebrow">YOUR DAILY PRACTICE</div>
      <h1 class="page-title">
        把每一次练习，变成进步<span style="color: var(--primary)">。</span>
      </h1>
      <p class="subtitle">从一道题开始，在自己的节奏里，走得更远。</p>
    </div>
    <div class="today-note">
      <span class="pulse-dot" />今天也是适合写代码的一天 <Code2 :size="14" />
    </div>
  </div>
  <div class="metric-grid">
    <button
      v-for="c in cards"
      :key="c.name"
      class="panel category-card"
      :class="{ selected: filters.category === c.category }"
      @click="filters.category = c.category"
    >
      <div class="category-top">
        <span class="category-icon" :style="{ background: c.color }"
          ><component :is="c.icon" :size="20" /></span
        ><ArrowUpRight :size="15" style="color: #a7b3a9" />
      </div>
      <h2>{{ c.name }}</h2>
      <p>{{ c.caption }}</p>
      <div class="category-progress">
        <span
          ><strong>{{ count(c.category).solved }}</strong> /
          {{ count(c.category).total }} 已完成</span
        ><span
          >{{
            count(c.category).total
              ? Math.round((count(c.category).solved / count(c.category).total) * 100)
              : 0
          }}%</span
        >
      </div>
      <div class="line-progress">
        <div
          :style="{
            width: (count(c.category).solved / (count(c.category).total || 1)) * 100 + '%',
          }"
        />
      </div>
    </button>
  </div>
  <section class="panel content-gap">
    <div class="list-heading">
      <div class="inline-actions">
        <span class="section-heading">练习题库</span
        ><span class="pill">{{ list?.total || 0 }} 道题目</span>
      </div>
      <NuxtLink to="/progress" class="small muted">查看学习进度 <ArrowRight :size="13" /></NuxtLink>
    </div>
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
              <span class="muted" style="font-size: 11px">{{ p.category }}</span>
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
  <footer class="site-footer">
    <span>每一次 AC，都是积累的回声。</span><span>CODEACE · BUILT FOR YOUR GROWTH</span>
  </footer>
</template>
<style scoped>
.today-note {
  display: flex;
  align-items: center;
  gap: 9px;
  background: #f0f5f0;
  color: #7f9582;
  font-size: 10px;
  padding: 9px 12px;
  border-radius: 6px;
  margin-top: 12px;
}
.pulse-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #7ca48b;
}
.category-card {
  text-align: left;
  padding: 22px;
  transition:
    border-color 0.2s,
    transform 0.2s;
}
.category-card:hover {
  transform: translateY(-2px);
  border-color: #bed5c5;
}
.category-card.selected {
  border-color: #abcdb8;
  box-shadow: 0 0 0 1px #edf5ee;
}
.category-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.category-icon {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 10px;
  color: #4b795c;
}
.category-card h2 {
  font-size: 15px;
  font-weight: 650;
}
.category-card > p {
  font-size: 10px;
  color: #9ba79e;
  margin-top: 7px;
}
.category-progress {
  margin: 24px 0 9px;
  font-size: 10px;
  color: #9eaba1;
  display: flex;
  justify-content: space-between;
}
.category-progress strong {
  color: #62856c;
  font-weight: 600;
}
.list-heading {
  padding: 22px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.practice-arrow {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 1px solid #e7ede8;
  border-radius: 6px;
  color: #8ca28f;
}
.practice-arrow:hover {
  background: #e9f3eb;
  color: var(--primary);
}
@media (max-width: 760px) {
  .today-note {
    display: none;
  }
  .category-card {
    padding: 14px;
  }
  .category-card h2 {
    font-size: 12px;
  }
  .category-card > p {
    display: none;
  }
  .category-progress {
    margin-top: 18px;
    font-size: 9px;
  }
  .category-icon {
    width: 30px;
    height: 30px;
  }
  .category-top {
    margin-bottom: 12px;
  }
}
</style>
