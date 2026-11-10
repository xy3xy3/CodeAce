export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook('app:mounted', () => {
    document.documentElement.dataset.codeaceReady = 'true'
  })
})
