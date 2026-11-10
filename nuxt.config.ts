import tailwindcss from '@tailwindcss/vite'
export default defineNuxtConfig({
  compatibilityDate: '2026-11-10',
  devtools: { enabled: false },
  modules: ['shadcn-nuxt'],
  shadcn: { prefix: 'Ui', componentDir: './app/components/ui' },
  css: ['~/assets/css/main.css', 'katex/dist/katex.min.css'],
  vite: { plugins: [tailwindcss()] },
  app: {
    head: {
      title: 'CodeAce · 每天进步一题',
      htmlAttrs: { lang: 'zh-CN' },
      meta: [{ name: 'description', content: '你的个人算法与深度学习练习工作台' }],
    },
  },
  runtimeConfig: {
    databaseUrl: '',
    sandboxUrl: 'http://127.0.0.1:4311',
    sandboxToken: '',
    importKey: '',
    cookieSecure: false,
  },
  typescript: { strict: true },
  nitro: { experimental: { tasks: true } },
})
