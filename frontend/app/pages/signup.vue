<script setup lang="ts">
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

definePageMeta({
  layout: false
})

const router = useRouter()

onMounted(() => {
  router.replace('/login')
})
</script>

<template>
  <div class="min-h-screen bg-canvas-soft flex items-center justify-center">
    <p class="text-ink-muted text-sm font-mono">Redirecting to login portal...</p>
  </div>
</template>
