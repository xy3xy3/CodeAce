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
  <div>
    <header class="shell-header">
      <NuxtLink to="/" class="brand"
        ><span class="brand-mark"><Code2 :size="23" /></span>
        <div>
          Code<span>Ace</span
          ><span
            style="
              font-size: 9px;
              letter-spacing: 1px;
              color: #9ca99f;
              margin-left: 10px;
              font-weight: 500;
            "
            >PERSONAL</span
          >
        </div></NuxtLink
      >
      <div class="header-right">
        <span class="header-note"><Leaf :size="13" /> &nbsp;专注练习，持续生长</span
        ><span style="height: 20px; width: 1px; background: var(--border)" /><span class="avatar">{{
          auth?.username?.slice(0, 1).toUpperCase() || 'A'
        }}</span
        ><span>{{ auth?.username || '个人空间' }}</span
        ><button v-if="auth" aria-label="退出登录" @click="logout"><LogOut :size="14" /></button>
      </div>
    </header>
    <nav v-if="route.path !== '/login'" class="mobile-nav">
      <NuxtLink v-for="l in links" :key="l.to" :to="l.to">{{ l.label }}</NuxtLink>
    </nav>
    <div v-if="route.path !== '/login'" class="shell-body">
      <aside class="sidebar">
        <div>
          <div class="nav-caption">学习空间 / WORKSPACE</div>
          <NuxtLink v-for="l in links.slice(0, 3)" :key="l.to" :to="l.to" class="nav-item"
            ><component :is="l.icon" :size="17" />{{ l.label
            }}<span
              v-if="l.to === '/'"
              style="
                margin-left: auto;
                font-size: 9px;
                border: 1px solid #d7e7db;
                border-radius: 3px;
                padding: 1px 4px;
              "
              >⌘ K</span
            ></NuxtLink
          >
        </div>
        <div>
          <div class="nav-caption">管理 / MANAGE</div>
          <NuxtLink to="/admin" class="nav-item"
            ><Settings2 :size="17" />后台管理<ArrowUpRight :size="13" style="margin-left: auto"
          /></NuxtLink>
        </div>
        <div class="sidebar-footer">
          <Leaf :size="16" style="color: #49896a; margin-bottom: 8px" />
          <p style="color: #54725c; font-weight: 600; font-size: 12px">慢慢来，也是在前进。</p>
          <p>每天一道题，让思考成为习惯。</p>
          <div
            style="
              margin-top: 12px;
              border-top: 1px solid #e1eae2;
              padding-top: 10px;
              font-size: 9px;
              letter-spacing: 1px;
            "
          >
            YOUR CODE. YOUR PACE.
          </div>
        </div>
      </aside>
      <main class="main-area"><slot /></main>
    </div>
    <main v-else><slot /></main>
    <div v-if="notice" role="alert" class="toast" :class="{ error: notice.error }">
      {{ notice.text }}
    </div>
  </div>
</template>
