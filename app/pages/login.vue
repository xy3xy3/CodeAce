<script setup lang="ts">
import { errorMessage } from '~/composables/useNotice'
import { ArrowRight, LockKeyhole, Code2 } from 'lucide-vue-next'
const ready = ref(false)
onMounted(() => {
  ready.value = true
})
const username = ref('admin'),
  password = ref(''),
  busy = ref(false),
  error = ref(''),
  route = useRoute(),
  auth = useState<{ username: string } | null>('auth', () => null)
async function login() {
  busy.value = true
  error.value = ''
  try {
    auth.value = await $fetch<{ username: string }>('/api/auth/login', {
      method: 'POST',
      body: { username: username.value, password: password.value },
    })
    const next = String(route.query.next || '/')
    await navigateTo(next.startsWith('/') && !next.startsWith('//') ? next : '/')
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <div class="login-page">
    <div class="login-intro">
      <div class="eyebrow">A LITTLE BETTER, EVERY DAY</div>
      <h1>留一点时间，<br />给更好的自己<span>。</span></h1>
      <p>算法思维，从每一次认真练习开始。<br />欢迎回到你的个人刷题空间。</p>
      <div class="login-code">
        <span>// today.ts</span>
        <p>const progress = practice + patience;</p>
        <span>// 让每一行代码，都有回响。</span>
      </div>
    </div>
    <form class="panel login-form" @submit.prevent="login">
      <span class="brand-mark" style="margin-bottom: 24px"><LockKeyhole :size="19" /></span>
      <h2 style="font-size: 23px; font-weight: 650">欢迎回来</h2>
      <p class="subtitle" style="margin-bottom: 28px">登录你的 CodeAce 个人空间</p>
      <div class="form-field">
        <label for="username">用户名</label
        ><UiInput
          id="username"
          v-model="username"
          :disabled="!ready"
          autocomplete="username"
          required
        />
      </div>
      <div class="form-field" style="margin-top: 20px">
        <label for="password">密码</label
        ><UiInput
          id="password"
          v-model="password"
          :disabled="!ready"
          type="password"
          autocomplete="current-password"
          required
        />
      </div>
      <p v-if="error" role="alert" class="error-box" style="margin-top: 18px">{{ error }}</p>
      <UiButton class="w-full mt-7" type="submit" :disabled="busy || !ready"
        >{{ busy ? '正在登录…' : '进入学习空间' }}<ArrowRight :size="15"
      /></UiButton>
      <p style="font-size: 10px; color: #a3afa6; text-align: center; margin-top: 22px">
        仅供个人使用 · 无需注册
      </p>
    </form>
  </div>
</template>
<style scoped>
.login-page {
  max-width: 1040px;
  min-height: calc(100vh - 72px);
  margin: auto;
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  align-items: center;
  gap: 90px;
  padding: 50px;
}
.login-intro h1 {
  font-size: 43px;
  font-weight: 650;
  line-height: 1.5;
  letter-spacing: -1.5px;
}
.login-intro h1 span {
  color: var(--primary);
}
.login-intro > p {
  margin-top: 20px;
  line-height: 2.1;
  color: #8c9a90;
  font-size: 13px;
}
.login-code {
  margin-top: 48px;
  border-left: 2px solid #d8e9de;
  padding-left: 20px;
  font:
    12px/2.4 Consolas,
    monospace;
  color: #49815d;
}
.login-code span {
  color: #a1b0a4;
}
.login-form {
  padding: 36px;
}
@media (max-width: 760px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 28px;
    gap: 28px;
    max-width: 460px;
  }
  .login-intro h1 {
    font-size: 28px;
  }
  .login-code {
    display: none;
  }
  .login-form {
    padding: 26px;
  }
}
</style>
