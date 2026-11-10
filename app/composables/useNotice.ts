export function useNotice() {
  const notice = useState<{ text: string; error: boolean } | null>('notice', () => null)
  function notify(text: string, error = false) {
    notice.value = { text, error }
    setTimeout(() => {
      if (notice.value?.text === text) notice.value = null
    }, 4500)
  }
  return { notice, notify }
}
export function errorMessage(e: any) {
  return e?.data?.statusMessage || e?.data?.message || e?.message || '操作失败，请重试'
}
