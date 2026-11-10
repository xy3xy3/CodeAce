<script setup lang="ts">
import MarkdownIt from 'markdown-it'
// @ts-expect-error the small markdown-it plugin has no type package
import katex from 'markdown-it-katex'
import DOMPurify from 'isomorphic-dompurify'
const props = defineProps<{ content?: string }>()
const md = new MarkdownIt({ html: true, linkify: true, breaks: true }).use(katex, {
  throwOnError: false,
})
const html = computed(() =>
  DOMPurify.sanitize(md.render(props.content || ''), {
    ADD_TAGS: ['annotation', 'semantics'],
    ADD_ATTR: ['encoding'],
  }),
)
</script>
<template><div class="markdown" v-html="html" /></template>
