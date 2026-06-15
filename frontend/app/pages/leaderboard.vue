<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'

const authStore = useAuthStore()
const leaderboard = ref<any[]>([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const res = await authStore.api.get('/api/quizzes/leaderboard')
    leaderboard.value = res.data.leaderboard
  } catch (err) {
    console.error('Failed to load leaderboard', err)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto px-6 py-8">
    <div class="mb-8">
      <h1 class="text-3xl font-bold tracking-tight text-ink mb-2">XP Leaderboard</h1>
      <p class="text-ink-muted text-sm">See how you rank against other learners on LinuxMaster. XP is earned by completing quizzes and commands.</p>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 bg-surface rounded-xl border border-hairline shadow-sm">
      <svg class="animate-spin h-8 w-8 text-primary mb-3" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span class="text-sm text-ink-muted">Loading leaderboard data...</span>
    </div>

    <div v-else class="bg-surface rounded-xl border border-hairline overflow-hidden shadow-notion-soft">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-canvas-soft border-b border-hairline text-xxs font-semibold uppercase tracking-wider text-ink-muted">
            <th class="py-4 px-6 w-20">Rank</th>
            <th class="py-4 px-6">Learner</th>
            <th class="py-4 px-6 w-32 text-center">Streak</th>
            <th class="py-4 px-6 w-32 text-right">Total XP</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-hairline">
          <tr v-for="(user, index) in leaderboard" :key="user.username"
              class="hover:bg-canvas-soft/40 transition-colors"
              :class="authStore.user && user.username === authStore.user.username ? 'bg-primary/5 font-semibold text-primary' : 'text-ink-secondary'">
            
            <td class="py-4 px-6">
              <span v-if="index === 0" class="flex items-center justify-center w-7 h-7 rounded-full bg-sticker-orange text-white text-xs font-bold" title="Gold Medal">🥇</span>
              <span v-else-if="index === 1" class="flex items-center justify-center w-7 h-7 rounded-full bg-sticker-sky text-white text-xs font-bold" title="Silver Medal">🥈</span>
              <span v-else-if="index === 2" class="flex items-center justify-center w-7 h-7 rounded-full bg-sticker-brown text-white text-xs font-bold animate-pulse" style="background-color: #d1a153;" title="Bronze Medal">🥉</span>
              <span v-else class="text-sm font-semibold pl-2.5 text-ink-muted">{{ index + 1 }}</span>
            </td>

            <td class="py-4 px-6 flex items-center gap-3">
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-ink-secondary"
                   :class="index === 0 ? 'bg-sticker-purple' : index === 1 ? 'bg-sticker-pink' : 'bg-canvas-soft border border-hairline'">
                {{ user.username.slice(0, 2).toUpperCase() }}
              </div>
              <div class="truncate">
                <span class="text-sm">{{ user.username }}</span>
                <span v-if="authStore.user && user.username === authStore.user.username" class="ml-2 text-xxs bg-primary text-white px-2 py-0.5 rounded-full font-medium">You</span>
                <div class="text-xxs text-ink-muted">Level {{ user.level }}</div>
              </div>
            </td>

            <td class="py-4 px-6 text-center text-sm">
              <span class="inline-flex items-center gap-1 bg-sticker-orange/10 border border-sticker-orange/20 text-sticker-orange px-2 py-0.5 rounded-full text-xs font-semibold">
                🔥 {{ user.streak }} days
              </span>
            </td>

            <td class="py-4 px-6 text-right font-mono text-sm">
              {{ user.xp.toLocaleString() }} XP
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!isLoading && leaderboard.length === 0" class="py-16 text-center bg-surface border border-hairline rounded-xl">
      <span class="text-4xl">📭</span>
      <p class="mt-2 text-sm text-ink-muted">No leaderboard rankings available yet.</p>
    </div>
  </div>
</template>
