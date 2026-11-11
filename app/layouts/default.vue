<script setup lang="ts">
import {
  Code2,
  BookOpen,
  History,
  ChartNoAxesCombined,
  Settings2,
  ArrowUpRight,
  LogOut,
  Command,
  Leaf,
} from 'lucide-vue-next'
const { notice } = useNotice(),
  auth = useState<{ username: string } | null>('auth'),
  route = useRoute()
const links = [
  { to: '/', label: '题库', icon: BookOpen },
  { to: '/submissions', label: '刷题记录', icon: History },
  { to: '/progress', label: '我的进度', icon: ChartNoAxesCombined },
  { to: '/admin', label: '后台管理', icon: Settings2 },
]
async function logout() {
  await $fetch('/api/auth/logout', { method: 'POST' })
  auth.value = null
  await navigateTo('/login')
}
</script>
<template>
  <div :class="{ 'workspace-shell': route.path.startsWith('/problems/') }">
    <header class="shell-header">
      <NuxtLink to="/" class="brand"
        ><span class="brand-mark"><Code2 :size="22" /></span>CodeAce</NuxtLink
      >
      <nav class="header-nav" aria-label="主导航">
        <NuxtLink v-for="l in links" :key="l.to" :to="l.to">{{ l.label }}</NuxtLink>
      </nav>
      <div class="header-right">
        <span class="avatar">{{ auth?.username?.slice(0, 1).toUpperCase() || 'A' }}</span
        ><span>{{ auth?.username || '个人空间' }}</span
        ><button v-if="auth" aria-label="退出登录" @click="logout"><LogOut :size="18" /></button>
      </div>
    </header>
    <div v-if="route.path !== '/login'" class="shell-body">
      <aside class="sidebar" aria-label="练习导航">
        <NuxtLink v-for="l in links" :key="l.to" :to="l.to" class="nav-item"
          ><component :is="l.icon" :size="19" />{{ l.label }}</NuxtLink
        >
        <div class="sidebar-divider" />
        <NuxtLink
          to="/?status=favorite"
          class="nav-item"
          exact-active-class=""
          :class="{ selected: route.query.status === 'favorite' }"
          ><BookOpen :size="19" />我的收藏</NuxtLink
        >
        <NuxtLink
          to="/?status=wrong"
          class="nav-item"
          exact-active-class=""
          :class="{ selected: route.query.status === 'wrong' }"
          ><History :size="19" />错题本</NuxtLink
        >
      </aside>
      <main class="main-area"><slot /></main>
    </div>
    <main v-else><slot /></main>
    <div v-if="notice" role="alert" class="toast" :class="{ error: notice.error }">
      {{ notice.text }}
    </div>
  </div>
</template>
