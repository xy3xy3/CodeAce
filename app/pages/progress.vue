<script setup lang="ts">
import { CheckCheck, Flame, CalendarDays, ArrowRight, TrendingUp } from 'lucide-vue-next'
const { data: stats } = await useAsyncData('progress', () => useRequestFetch()<any>('/api/stats'))
const dates = computed(() =>
  Array.from({ length: 140 }, (_, i) => {
    const d = new Date()
    d.setDate(d.getDate() - 139 + i)
    const day = d.toLocaleDateString('sv-SE', { timeZone: 'Asia/Shanghai' })
    return { day, count: stats.value?.daily?.find((x: any) => x.day === day)?.count || 0 }
  }),
)
</script>
<template>
  <div class="page-heading">
    <div>
      <h1 class="page-title">学习进度</h1>
    </div>
    <NuxtLink to="/"
      ><UiButton variant="outline">继续练习 <ArrowRight :size="14" /></UiButton
    ></NuxtLink>
  </div>
  <div class="metric-grid">
    <div
      v-for="c in [
        { label: '已通过题目', value: stats?.solved || 0, icon: CheckCheck },
        { label: '累计提交', value: stats?.submissions || 0, icon: TrendingUp },
        { label: '练习天数', value: stats?.days || 0, icon: CalendarDays },
      ]"
      :key="c.label"
      class="panel metric-card"
    >
      <div class="inline-actions muted small">
        <component :is="c.icon" :size="16" />{{ c.label }}
      </div>
      <div class="stat-value" style="margin-top: 18px">
        {{ c.value
        }}<span style="font-size: 12px; color: #a8a8a8; margin-left: 8px">{{
          c.label === '练习天数' ? '天' : c.label === '已通过题目' ? '道' : '次'
        }}</span>
      </div>
    </div>
  </div>
  <section class="panel content-gap" style="padding: 24px">
    <div class="section-heading">练习足迹</div>
    <div class="activity-grid">
      <div
        v-for="d in dates"
        :key="d.day"
        class="activity-cell"
        :style="{ background: d.count ? (d.count > 3 ? '#46895c' : '#267c50') : '#353535' }"
        :title="d.day + ' · ' + d.count + ' 次提交'"
      />
    </div>
    <div class="small muted" style="text-align: right">少 ▫ ▪ 多</div>
  </section>
  <section class="panel content-gap" style="padding: 24px">
    <div class="section-heading">题库进度</div>
    <div v-for="c in stats?.categories" :key="c.name" style="margin-top: 25px">
      <div style="display: flex; justify-content: space-between; margin-bottom: 10px">
        <span>{{ c.name }}</span
        ><span class="small muted">{{ c.solved }} / {{ c.total }}</span>
      </div>
      <div class="line-progress">
        <div :style="{ width: (c.solved / (c.total || 1)) * 100 + '%' }" />
      </div>
    </div>
  </section>
</template>
<style scoped>
.activity-grid {
  display: grid;
  grid-template-rows: repeat(7, 1fr);
  grid-auto-flow: column;
  gap: 5px;
  margin: 25px 0 16px;
  max-width: 800px;
}
.activity-cell {
  aspect-ratio: 1;
  border-radius: 3px;
}
</style>
