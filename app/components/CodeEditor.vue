<script setup lang="ts">
import { EditorView, basicSetup } from 'codemirror'
import { python } from '@codemirror/lang-python'
import { oneDark } from '@codemirror/theme-one-dark'
import { cpp } from '@codemirror/lang-cpp'
const props = defineProps<{ modelValue: string; language?: string }>(),
  emit = defineEmits<{ 'update:modelValue': [string] }>(),
  container = ref<HTMLElement>(),
  view = shallowRef<EditorView>()
onMounted(() => {
  view.value = new EditorView({
    doc: props.modelValue,
    extensions: [
      basicSetup,
      oneDark,
      props.language === 'cpp17' ? cpp() : python(),
      EditorView.contentAttributes.of({ 'aria-label': '代码编辑器', spellcheck: 'false' }),
      EditorView.theme({
        '&': { height: '100%', fontSize: '14px', backgroundColor: '#242424' },
        '.cm-content': {
          fontFamily: 'Consolas, "SFMono-Regular", monospace',
          padding: '20px 0',
          minHeight: '360px',
        },
        '.cm-gutters': {
          backgroundColor: '#242424',
          color: '#b6c1b8',
          border: 'none',
          paddingRight: '12px',
        },
        '.cm-line': { paddingLeft: '12px' },
        '.cm-activeLine': { background: '#2d2d2d' },
        '.cm-activeLineGutter': { background: 'transparent' },
        '.cm-scroller': { overflow: 'auto' },
      }),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) emit('update:modelValue', update.state.doc.toString())
      }),
    ],
    parent: container.value,
  })
})
watch(
  () => props.modelValue,
  (value) => {
    const v = view.value
    if (v && value !== v.state.doc.toString())
      v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: value } })
  },
)
onBeforeUnmount(() => view.value?.destroy())
</script>
<template>
  <div
    ref="container"
    class="code-editor"
    style="height: 100%; min-height: 360px; overflow: auto"
  />
</template>
