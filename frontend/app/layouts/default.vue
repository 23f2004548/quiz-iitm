<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import { icon } from '@fortawesome/fontawesome-svg-core'
import {
  faFolder, faLaptopCode, faTrophy, faSignOutAlt,
  faFire, faStar, faChevronLeft, faChevronRight,
  faChartLine, faCalendarDays, faBookOpen
} from '@fortawesome/free-solid-svg-icons'
import CalendarPanel from '~/components/CalendarPanel.vue'

const authStore    = useAuthStore()
const router       = useRouter()
const route        = useRoute()
const calendarOpen = ref(false)

// ── Sidebar resize ─────────────────────────────────────────────
const SIDEBAR_MIN     = 200
const SIDEBAR_MAX     = 480
const SIDEBAR_DEFAULT = 256
const CLOSE_THRESHOLD = 100
const MINI_WIDTH      = 56

const sidebarOpen  = ref(true)
const sidebarWidth = ref(SIDEBAR_DEFAULT)
const isResizing   = ref(false)
let   startX       = 0
let   startWidth   = 0

const visualWidth       = computed(() => sidebarOpen.value ? sidebarWidth.value : MINI_WIDTH)
const sidebarTransition = computed(() => isResizing.value ? '' : 'sidebar-transition')

function startResize(e: MouseEvent) {
  e.preventDefault()
  isResizing.value = true
  startX     = e.clientX
  startWidth = sidebarWidth.value
  document.body.style.cursor     = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', handleResize, { passive: true })
  document.addEventListener('mouseup',   stopResize)
}
function handleResize(e: MouseEvent) {
  if (!isResizing.value) return
  const newWidth = startWidth + (e.clientX - startX)
  sidebarWidth.value = newWidth < CLOSE_THRESHOLD
    ? Math.max(newWidth, 20)
    : Math.min(Math.max(newWidth, SIDEBAR_MIN), SIDEBAR_MAX)
}
function stopResize() {
  isResizing.value = false
  document.body.style.cursor     = ''
  document.body.style.userSelect = ''
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup',   stopResize)
  if (sidebarWidth.value < CLOSE_THRESHOLD) {
    sidebarOpen.value  = false
    sidebarWidth.value = SIDEBAR_DEFAULT
  } else {
    sidebarOpen.value = true
  }
}
function toggleSidebar() { sidebarOpen.value = !sidebarOpen.value }

// ── Auth ───────────────────────────────────────────────────────
onMounted(async () => {
  if (authStore.token) {
    await authStore.fetchUser()
  } else {
    if (route.path !== '/login' && route.path !== '/signup') router.push('/login')
  }
})

const xpProgress = computed(() => authStore.user ? authStore.user.xp % 100 : 0)
function handleLogout() { authStore.logout(); router.push('/login') }
function getFaIcon(def: any) { return icon(def).html[0] }
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-canvas">

    <!-- ══════════════════ SIDEBAR ══════════════════ -->
    <aside
      v-if="authStore.isLoggedIn"
      :class="[sidebarTransition, 'flex-shrink-0 bg-canvas-soft border-r border-hairline flex flex-col h-full relative select-none']"
      :style="{ width: `${visualWidth}px`, overflow: 'visible' }"
    >
      <!-- Drag handle -->
      <div @mousedown="startResize"
        :class="['absolute top-0 right-0 w-2 h-full z-30 cursor-col-resize group', isResizing ? 'bg-primary/30' : '']">
        <div :class="['absolute inset-y-0 right-0 w-[3px] transition-all duration-200 rounded-full',
          isResizing ? 'bg-primary/60' : 'bg-transparent group-hover:bg-primary/35']"></div>
        <button @mousedown.stop @click.stop="toggleSidebar"
          :class="[
            'absolute top-1/2 -translate-y-1/2 -right-3.5 w-7 h-7 rounded-full',
            'bg-surface border border-hairline shadow-notion-soft flex items-center justify-center',
            'opacity-0 group-hover:opacity-100 transition-opacity duration-200',
            'hover:bg-primary hover:border-primary hover:text-white hover:scale-110 transition-all duration-200',
            'text-ink-muted cursor-pointer z-40'
          ]">
          <span v-html="getFaIcon(sidebarOpen ? faChevronLeft : faChevronRight)"
            class="w-2.5 h-2.5 flex items-center justify-center pointer-events-none"></span>
        </button>
      </div>

      <!-- ══ FULL SIDEBAR ══ -->
      <template v-if="sidebarOpen">
        <!-- Logo -->
        <div class="p-5 flex items-center gap-2 border-b border-hairline flex-shrink-0">
          <span class="text-xl font-bold flex items-center gap-1.5 text-ink">
            <span class="w-6 h-6 rounded bg-primary text-white flex items-center justify-center text-xs font-mono">$_</span>
            LinuxMaster
          </span>
        </div>

        <!-- User card -->
        <div v-if="authStore.user" class="p-5 border-b border-hairline bg-surface mx-4 my-3 rounded-lg border hover:shadow-notion-soft transition-all duration-300 flex-shrink-0">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-sticker-purple flex items-center justify-center font-bold text-ink-secondary text-sm hover:rotate-12 hover:scale-105 transition-all duration-300 shadow-sm relative cursor-pointer flex-shrink-0">
              {{ authStore.user.username.slice(0, 2).toUpperCase() }}
              <span class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-sticker-green border-2 border-surface animate-pulse"></span>
            </div>
            <div class="min-w-0 flex-1">
              <h4 class="font-semibold text-sm truncate text-ink">{{ authStore.user.username }}</h4>
              <div class="flex items-center gap-1.5 mt-0.5">
                <span class="inline-block px-1.5 py-0.5 rounded bg-sticker-purple/10 border border-sticker-purple/20 text-sticker-purple-deep font-bold text-[9px] uppercase tracking-wide">
                  Lvl {{ authStore.user.level }}
                </span>
                <span class="text-xxs text-ink-muted">Learner</span>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <div class="flex justify-between text-xs font-medium text-ink-muted mb-1">
              <span>{{ authStore.user.xp % 100 }} / 100 XP</span>
              <span>Lvl {{ authStore.user.level + 1 }}</span>
            </div>
            <div class="w-full bg-canvas-soft h-2 rounded-full overflow-hidden border border-hairline relative">
              <div class="bg-gradient-to-r from-primary via-sticker-sky to-primary bg-[length:200%_auto] h-full transition-all duration-500 ease-out shadow-[0_0_8px_rgba(0,117,222,0.4)] animate-shimmer"
                :style="{ width: `${xpProgress}%` }"></div>
            </div>
          </div>
        </div>

        <!-- Streak widget -->
        <div v-if="authStore.user" class="px-4 mb-3 flex-shrink-0">
          <div class="bg-surface rounded-lg border border-hairline p-3 flex items-center justify-between shadow-sm">
            <div class="flex items-center gap-2">
              <span v-html="getFaIcon(faFire)" class="text-2xl text-sticker-orange animate-bounce w-7 h-7 flex items-center justify-center shrink-0"></span>
              <div>
                <div class="text-sm font-bold text-ink">{{ authStore.user.streak }} Day Streak</div>
                <div class="text-xxs text-ink-muted">Keep practicing daily!</div>
              </div>
            </div>
            <div class="flex gap-0.5">
              <div v-for="n in 5" :key="n" class="w-2 h-2 rounded-full border border-hairline"
                :class="n <= Math.min(authStore.user.streak, 5) ? 'bg-sticker-orange border-sticker-orange' : 'bg-canvas-soft'"></div>
            </div>
          </div>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 px-3 space-y-1 overflow-y-auto">
          <NuxtLink to="/"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="$route.path === '/' ? 'bg-surface text-ink border border-hairline font-semibold shadow-sm' : 'text-ink-secondary hover:bg-surface/50 hover:text-ink'">
            <span v-html="getFaIcon(faFolder)" class="w-4 h-4 flex items-center justify-center shrink-0"
              :class="$route.path === '/' ? 'text-primary' : 'text-ink-faint'"></span>
            Dashboard
          </NuxtLink>

          <NuxtLink to="/terminal"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="$route.path === '/terminal' ? 'bg-surface text-ink border border-hairline font-semibold shadow-sm' : 'text-ink-secondary hover:bg-surface/50 hover:text-ink'">
            <span v-html="getFaIcon(faLaptopCode)" class="w-4 h-4 flex items-center justify-center shrink-0"
              :class="$route.path === '/terminal' ? 'text-primary' : 'text-ink-faint'"></span>
            Sandbox
          </NuxtLink>

          <NuxtLink to="/leaderboard"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="$route.path === '/leaderboard' ? 'bg-surface text-ink border border-hairline font-semibold shadow-sm' : 'text-ink-secondary hover:bg-surface/50 hover:text-ink'">
            <span v-html="getFaIcon(faTrophy)" class="w-4 h-4 flex items-center justify-center shrink-0"
              :class="$route.path === '/leaderboard' ? 'text-primary' : 'text-ink-faint'"></span>
            Leaderboard
          </NuxtLink>

          <NuxtLink to="/progress"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="$route.path === '/progress' ? 'bg-surface text-ink border border-hairline font-semibold shadow-sm' : 'text-ink-secondary hover:bg-surface/50 hover:text-ink'">
            <span v-html="getFaIcon(faChartLine)" class="w-4 h-4 flex items-center justify-center shrink-0"
              :class="$route.path === '/progress' ? 'text-primary' : 'text-ink-faint'"></span>
            Progress
          </NuxtLink>



          <NuxtLink to="/notes"
            class="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            :class="$route.path.startsWith('/notes') ? 'bg-surface text-ink border border-hairline font-semibold shadow-sm' : 'text-ink-secondary hover:bg-surface/50 hover:text-ink'">
            <span v-html="getFaIcon(faBookOpen)" class="w-4 h-4 flex items-center justify-center shrink-0"
              :class="$route.path.startsWith('/notes') ? 'text-primary' : 'text-ink-faint'"></span>
            Notes
          </NuxtLink>

          <!-- Calendar toggle -->
          <button @click="calendarOpen = !calendarOpen"
            class="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer"
            :class="calendarOpen ? 'bg-surface text-ink border border-hairline font-semibold shadow-sm' : 'text-ink-secondary hover:bg-surface/50 hover:text-ink'">
            <span v-html="getFaIcon(faCalendarDays)" class="w-4 h-4 flex items-center justify-center shrink-0"
              :class="calendarOpen ? 'text-primary' : 'text-ink-faint'"></span>
            Calendar
          </button>
        </nav>

        <!-- Logout -->
        <div class="p-4 border-t border-hairline flex-shrink-0">
          <button @click="handleLogout"
            class="w-full flex items-center justify-center gap-2 px-3 py-2 border border-hairline rounded-md text-sm font-medium text-ink-muted hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer">
            <span v-html="getFaIcon(faSignOutAlt)" class="w-4 h-4 flex items-center justify-center shrink-0 text-ink-faint"></span>
            Logout
          </button>
        </div>
      </template>

      <!-- ══ MINI ICON RAIL (collapsed) ══ -->
      <template v-else>
        <div class="flex flex-col items-center gap-1 py-4 flex-1">
          <div class="w-8 h-8 rounded bg-primary text-white flex items-center justify-center text-xs font-mono mb-3 flex-shrink-0">$_</div>
          <div v-if="authStore.user" class="w-8 h-8 rounded-full bg-sticker-purple flex items-center justify-center font-bold text-ink-secondary text-xs mb-3 shadow-sm relative flex-shrink-0">
            {{ authStore.user.username.slice(0, 2).toUpperCase() }}
            <span class="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-sticker-green border-2 border-canvas-soft animate-pulse"></span>
          </div>
          <div class="w-full px-2 h-px bg-hairline mb-1"></div>

          <NuxtLink to="/" class="w-10 h-10 rounded-md flex items-center justify-center transition-colors group relative"
            :class="$route.path === '/' ? 'bg-surface border border-hairline text-primary shadow-sm' : 'text-ink-faint hover:bg-surface/60 hover:text-ink'">
            <span v-html="getFaIcon(faFolder)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Dashboard</span>
          </NuxtLink>

          <NuxtLink to="/terminal" class="w-10 h-10 rounded-md flex items-center justify-center transition-colors group relative"
            :class="$route.path === '/terminal' ? 'bg-surface border border-hairline text-primary shadow-sm' : 'text-ink-faint hover:bg-surface/60 hover:text-ink'">
            <span v-html="getFaIcon(faLaptopCode)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Sandbox</span>
          </NuxtLink>

          <NuxtLink to="/leaderboard" class="w-10 h-10 rounded-md flex items-center justify-center transition-colors group relative"
            :class="$route.path === '/leaderboard' ? 'bg-surface border border-hairline text-primary shadow-sm' : 'text-ink-faint hover:bg-surface/60 hover:text-ink'">
            <span v-html="getFaIcon(faTrophy)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Leaderboard</span>
          </NuxtLink>

          <NuxtLink to="/progress" class="w-10 h-10 rounded-md flex items-center justify-center transition-colors group relative"
            :class="$route.path === '/progress' ? 'bg-surface border border-hairline text-primary shadow-sm' : 'text-ink-faint hover:bg-surface/60 hover:text-ink'">
            <span v-html="getFaIcon(faChartLine)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Progress</span>
          </NuxtLink>



          <NuxtLink to="/notes" class="w-10 h-10 rounded-md flex items-center justify-center transition-colors group relative"
            :class="$route.path.startsWith('/notes') ? 'bg-surface border border-hairline text-primary shadow-sm' : 'text-ink-faint hover:bg-surface/60 hover:text-ink'">
            <span v-html="getFaIcon(faBookOpen)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Notes</span>
          </NuxtLink>

          <!-- Calendar mini toggle -->
          <button @click="calendarOpen = !calendarOpen"
            class="w-10 h-10 rounded-md flex items-center justify-center transition-colors group relative cursor-pointer"
            :class="calendarOpen ? 'bg-surface border border-hairline text-primary shadow-sm' : 'text-ink-faint hover:bg-surface/60 hover:text-ink'">
            <span v-html="getFaIcon(faCalendarDays)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Calendar</span>
          </button>

          <div class="flex-1"></div>

          <button @click="handleLogout"
            class="w-10 h-10 rounded-md flex items-center justify-center text-ink-faint hover:bg-red-50 hover:text-red-500 transition-colors cursor-pointer group relative">
            <span v-html="getFaIcon(faSignOutAlt)" class="w-4 h-4 flex items-center justify-center"></span>
            <span class="mini-tooltip">Logout</span>
          </button>
        </div>
      </template>
    </aside>

    <!-- ══════════════════ MAIN CONTENT ══════════════════ -->
    <div class="flex-1 flex flex-col h-full bg-canvas-soft overflow-y-auto min-w-0">
      <header v-if="authStore.isLoggedIn"
        class="bg-canvas border-b border-hairline h-14 flex-shrink-0 flex items-center justify-between px-6 sticky top-0 z-10 shadow-sm select-none">
        <div class="flex items-center gap-2 text-sm text-ink-muted font-medium">
          <span>Workspace</span>
          <span>/</span>
          <span class="text-ink font-semibold">
            {{ $route.path === '/' ? 'Dashboard' : $route.path === '/terminal' ? 'Sandbox' : $route.path === '/leaderboard' ? 'Leaderboard' : $route.path === '/progress' ? 'Progress' : $route.path.startsWith('/notes') ? 'Notes' : 'Quiz Session' }}
          </span>
        </div>
        <div v-if="authStore.user" class="flex items-center gap-4 text-xs font-semibold text-ink-secondary">
          <span class="flex items-center gap-1 bg-canvas-soft border border-hairline px-2.5 py-1 rounded-full">
            <span v-html="getFaIcon(faStar)" class="w-3 h-3 text-sticker-sky flex items-center justify-center shrink-0"></span>
            <span>{{ authStore.user.xp }} XP</span>
          </span>
          <span class="flex items-center gap-1 bg-canvas-soft border border-hairline px-2.5 py-1 rounded-full">
            <span v-html="getFaIcon(faFire)" class="w-3 h-3 text-sticker-orange flex items-center justify-center shrink-0"></span>
            <span>{{ authStore.user.streak }} Streak</span>
          </span>
        </div>
      </header>
      <main class="flex-1"><slot /></main>
    </div>
  </div>

  <!-- Floating Calendar Panel -->
  <CalendarPanel v-if="calendarOpen" @close="calendarOpen = false" />
</template>

<style scoped>
.text-xxs {
  font-size: 0.65rem;
}

.sidebar-transition {
  transition: width 280ms cubic-bezier(0.4, 0, 0.2, 1);
}

.mini-tooltip {
  @apply pointer-events-none absolute left-full ml-2.5 top-1/2 -translate-y-1/2
         bg-ink text-canvas text-xs font-medium px-2 py-1 rounded-md whitespace-nowrap
         opacity-0 scale-95 group-hover:opacity-100 group-hover:scale-100
         transition-all duration-150 z-50 shadow-md;
}

.shadow-notion-soft {
  box-shadow:
    rgba(0,0,0,0.01) 0 0.175px 1.041px,
    rgba(0,0,0,0.02) 0 0.8px 2.925px,
    rgba(0,0,0,0.027) 0 2.025px 7.847px,
    rgba(0,0,0,0.04) 0 4px 18px;
}
</style>
