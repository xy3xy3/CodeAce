export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path === '/login') return
  const auth = useState<{ username: string } | null>('auth', () => null)
  if (!auth.value) {
    try {
      auth.value = await useRequestFetch()('/api/auth/me')
    } catch {
      return navigateTo('/login?next=' + encodeURIComponent(to.fullPath))
    }
  }
})
