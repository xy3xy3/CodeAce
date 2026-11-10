<script setup lang="ts">
import { ArrowLeft, ArrowUpRight } from 'lucide-vue-next'
const route = useRoute(),
  fetcher = useRequestFetch(),
  { data: s, refresh } = await useAsyncData('submission-' + route.params.id, () =>
    fetcher<any>('/api/submissions/' + route.params.id),
  )
let timer: ReturnType<typeof setInterval>
onMounted(() => {
  timer = setInterval(() => {
    if (['QUEUED', 'RUNNING'].includes(s.value?.status)) refresh()
  }, 1500)
})
onBeforeUnmount(() => clearInterval(timer))
</script>
<template>
  <div v-if="s">
    <NuxtLink to="/submissions" class="small muted"><ArrowLeft :size="13" /> 返回刷题记录</NuxtLink>
    <div class="page-heading" style="margin-top: 24px">
      <div>
        <div class="eyebrow">SUBMISSION #{{ s.id }}</div>
        <h1 class="page-title">{{ s.problem_title }}</h1>
        <p class="subtitle">
          {{ new Date(s.created_at).toLocaleString('zh-CN') }} · {{ s.language }} · {{ s.mode }} ·
          题目版本 {{ s.problem_version }}
        </p>
      </div>
      <NuxtLink v-if="s.problem_id" :to="'/problems/' + s.problem_id"
        ><UiButton variant="outline">返回练习 <ArrowUpRight :size="14" /></UiButton
      ></NuxtLink>
    </div>
    <div class="panel" style="padding: 24px">
      <div class="inline-actions">
        <span class="status-badge" :class="s.status">{{ s.status }}</span
        ><span class="small muted"
          >通过 {{ s.result?.passed || 0 }} / {{ s.result?.total || 0 }} 个用例 ·
          {{ s.result?.timeMs || 0 }} ms ·
          {{ Math.round((s.result?.memoryKb || 0) / 1024) }} MB</span
        >
      </div>
      <p v-if="s.result?.error" class="error-box" style="margin-top: 16px">{{ s.result.error }}</p>
      <div v-for="(r, i) in s.result?.results" :key="i" style="margin-top: 16px">
        <div class="small muted">用例 {{ Number(i) + 1 }} · {{ r.status }}</div>
        <details v-if="r.input !== undefined" class="small" style="margin-top: 10px">
          <summary class="muted" style="cursor: pointer">查看输入与预期输出</summary>
          <pre class="code-block">{{ r.input }}</pre>
          <pre v-if="r.expected !== undefined" class="code-block" style="margin-top: 8px">{{
            r.expected
          }}</pre>
        </details>
        <p v-else class="small muted" style="margin-top: 8px">隐藏用例的输入与预期输出不展示。</p>
        <pre v-if="r.stderr" class="code-block" style="margin-top: 8px">{{ r.stderr }}</pre>
        <pre v-if="r.stdout" class="code-block" style="margin-top: 8px">{{ r.stdout }}</pre>
      </div>
    </div>
    <section class="panel content-gap" style="padding: 24px">
      <h2 class="section-heading" style="margin-bottom: 18px">提交代码</h2>
      <pre class="code-block">{{ s.code }}</pre>
    </section>
  </div>
</template>
