<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter } from 'vue-router'
import { icon } from '@fortawesome/fontawesome-svg-core'
import { 
  faLaptop, 
  faClipboardCheck, 
  faCheckCircle, 
  faCircle, 
  faGraduationCap, 
  faTerminal, 
  faDatabase, 
  faRobot, 
  faBolt, 
  faFire 
} from '@fortawesome/free-solid-svg-icons'
import { faGithub, faPython } from '@fortawesome/free-brands-svg-icons'

const authStore = useAuthStore()
const router = useRouter()

const progressSummary = ref<any[]>([])
const isLoadingProgress = ref(true)

// Helper to return FontAwesome SVG markup
function getFaIcon(iconDef: any) {
  return icon(iconDef).html[0]
}

const subjects = [
  {
    name: 'Linux System Commands',
    description: 'Learn directory navigation, file operations, grep filters, and terminal editing.',
    icon: faTerminal,
    colorClass: 'bg-sticker-sky/10 border-sticker-sky/30 text-sticker-sky',
    badgeColor: 'bg-sticker-sky',
    topics: ['Basic Commands', 'Filesystem Hierarchy', 'Linux Permissions', 'Links', 'Redirection', 'Command Line Environment']
  },
  {
    name: 'Git & GitHub',
    description: 'Master version control, branches, committing, staging, merging, and collaboration.',
    icon: faGithub,
    colorClass: 'bg-sticker-purple/10 border-sticker-purple/30 text-sticker-purple-deep',
    badgeColor: 'bg-sticker-purple',
    topics: ['Branching & Merging']
  },
  {
    name: 'Python',
    description: 'Solve coding challenges, learn dictionary structures, sets, arrays, and scripting.',
    icon: faPython,
    colorClass: 'bg-sticker-green/10 border-sticker-green/30 text-sticker-green',
    badgeColor: 'bg-sticker-green',
    topics: ['Data Structures']
  },
  {
    name: 'SQL',
    description: 'Write database queries, group aggregations, window functions, and joins.',
    icon: faDatabase,
    colorClass: 'bg-sticker-orange/10 border-sticker-orange/30 text-sticker-orange-deep',
    badgeColor: 'bg-sticker-orange',
    topics: ['Aggregations']
  },
  {
    name: 'Machine Learning',
    description: 'Understand regression, classification, Lasso/Ridge regularizations, and metrics.',
    icon: faRobot,
    colorClass: 'bg-sticker-teal/10 border-sticker-teal/30 text-sticker-teal',
    badgeColor: 'bg-sticker-teal',
    topics: ['Regularization']
  }
]

const daysList = ref<any[]>([])

onMounted(async () => {
  if (authStore.token) {
    try {
      // Load progress
      const res = await authStore.api.get('/api/quizzes/progress')
      progressSummary.value = res.data.progress || res.data

      // Load attempts activity history
      const activityRes = await authStore.api.get('/api/quizzes/activity')
      const activityMap = activityRes.data.activity || {}

      // Generate 53 weeks (371 days) ending on the Saturday of the current week
      const list = []
      const today = new Date()
      const dayOfWeek = today.getDay() // 0 = Sunday, 6 = Saturday
      const endDate = new Date(today)
      endDate.setDate(today.getDate() + (6 - dayOfWeek)) // Saturday of current week

      for (let i = 370; i >= 0; i--) {
        const d = new Date(endDate)
        d.setDate(endDate.getDate() - i)
        
        // Convert to YYYY-MM-DD local date string format
        const year = d.getFullYear()
        const month = String(d.getMonth() + 1).padStart(2, '0')
        const dateDay = String(d.getDate()).padStart(2, '0')
        const dateStr = `${year}-${month}-${dateDay}`
        
        // Is it in the future compared to today?
        const isFuture = d > today
        
        const solved = isFuture ? 0 : (activityMap[dateStr]?.solved || 0)
        const attempted = isFuture ? 0 : (activityMap[dateStr]?.attempted || 0)
        
        list.push({
          date: dateStr,
          dayNum: d.getDate(),
          solved,
          attempted,
          isFuture
        })
      }
      daysList.value = list
    } catch (err) {
      console.error('Failed to load user progress or activity logs', err)
    } finally {
      isLoadingProgress.value = false
    }
  }
})

function getCellClass(solved: number, isFuture: boolean) {
  if (isFuture) return 'bg-canvas-soft opacity-40 cursor-default pointer-events-none'
  if (solved === 0) return 'bg-canvas-soft border border-hairline hover:border-neutral-400 hover:scale-110'
  if (solved < 10) return 'bg-sticker-green/20 hover:scale-110 hover:shadow-[0_0_4px_rgba(26,174,57,0.2)]'
  if (solved >= 10 && solved < 20) return 'bg-sticker-green/45 hover:scale-110 hover:shadow-[0_0_5px_rgba(26,174,57,0.4)]'
  if (solved >= 20 && solved < 25) return 'bg-sticker-green/70 hover:scale-110 hover:shadow-[0_0_6px_rgba(26,174,57,0.6)]'
  return 'bg-sticker-green hover:scale-110 hover:shadow-[0_0_8px_rgba(26,174,57,0.8)] z-10'
}

function formatDateLabel(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const day = d.getDate()
  const month = d.toLocaleDateString('en-US', { month: 'short' })
  const year = d.getFullYear()
  return `${day} ${month} ${year}`.toLowerCase()
}

const totalAttempts = computed(() => {
  return daysList.value.reduce((sum, day) => sum + day.attempted, 0)
})

const monthLabels = computed(() => {
  if (daysList.value.length === 0) return []
  const labels: { text: string; colIndex: number }[] = []
  let lastMonth = ''
  
  for (let week = 0; week < 53; week++) {
    const firstDayOfWeek = daysList.value[week * 7]
    if (firstDayOfWeek) {
      const d = new Date(firstDayOfWeek.date)
      const monthName = d.toLocaleDateString('en-US', { month: 'short' }).toLowerCase()
      if (monthName !== lastMonth) {
        labels.push({ text: monthName, colIndex: week })
        lastMonth = monthName
      }
    }
  }
  return labels
})

function handleStartQuiz(subject: string, topic: string) {
  router.push({
    path: '/questions',
    query: { subject, topic }
  })
}

// Find progress for a topic
function getTopicAccuracy(subject: string, topic: string) {
  const record = progressSummary.value.find(p => p.subject === subject && p.topic === topic)
  return record ? `${record.accuracy}% accuracy (${record.questions_correct}/${record.questions_attempted} correct)` : 'Not attempted yet'
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-6 py-8">
    <!-- Welcome Header -->
    <div v-if="authStore.user" class="mb-8 flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-ink mb-1 flex items-center gap-2 select-none">
          Welcome back, {{ authStore.user.username }}
          <span v-html="getFaIcon(faLaptop)" class="w-7 h-7 text-primary mt-1"></span>
        </h1>
        <p class="text-ink-muted text-sm">Here is your interactive learning dashboard. Ready to expand your streak?</p>
      </div>
    </div>

    <!-- Grid Layout: Goals & Progress Details -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      
      <!-- Monkeytype Streak Grid View (Light Theme) -->
      <div class="lg:col-span-3 bg-surface rounded-xl p-6 shadow-notion-soft flex flex-col justify-between text-ink-muted font-mono border border-hairline">
        <div>
          <!-- Header: Dropdown, total, legend -->
          <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4 select-none">
            <div class="flex items-center gap-1.5">
              <select class="bg-transparent text-ink-muted hover:text-ink transition-colors duration-150 cursor-pointer focus:outline-none text-xs font-mono font-bold py-1 border-none outline-none">
                <option value="last-12-months" class="bg-surface text-ink-muted">last 12 months</option>
              </select>
            </div>
            
            <div class="text-xs text-ink-muted font-mono font-bold">
              {{ totalAttempts }} attempts
            </div>
            
            <div class="flex items-center gap-2 text-xs text-ink-muted">
              <span>less</span>
              <div class="flex gap-1.5">
                <div class="w-3 h-3 rounded-[2px] bg-canvas-soft border border-hairline"></div>
                <div class="w-3 h-3 rounded-[2px] bg-sticker-green/20"></div>
                <div class="w-3 h-3 rounded-[2px] bg-sticker-green/45"></div>
                <div class="w-3 h-3 rounded-[2px] bg-sticker-green/70"></div>
                <div class="w-3 h-3 rounded-[2px] bg-sticker-green"></div>
              </div>
              <span>more</span>
            </div>
          </div>
          
          <!-- Contribution Grid Wrapper -->
          <div class="w-full overflow-x-auto pb-2 scrollbar-thin select-none">
            <div class="min-w-[850px] flex flex-col">
              <!-- Grid Container -->
              <div class="flex items-center w-full">
                <!-- Left Day labels -->
                <div class="grid grid-rows-7 gap-1 pr-3 text-[10px] text-ink-muted font-mono text-right select-none w-16" style="grid-template-rows: repeat(7, minmax(0, 1fr));">
                  <span></span>
                  <span class="flex items-center justify-end h-3">monday</span>
                  <span></span>
                  <span class="flex items-center justify-end h-3">wednesday</span>
                  <span></span>
                  <span class="flex items-center justify-end h-3">friday</span>
                  <span></span>
                </div>
                
                <!-- Cells Grid -->
                <div class="grid grid-flow-col grid-rows-7 gap-[3px] flex-1" style="grid-template-rows: repeat(7, minmax(0, 1fr)); grid-template-columns: repeat(53, minmax(0, 1fr));">
                  <div v-for="day in daysList" :key="day.date" 
                       class="w-3 h-3 rounded-[2px] transition-all duration-150 cursor-pointer relative group/cell"
                       :class="getCellClass(day.solved, day.isFuture)">
                    <!-- Tooltip -->
                    <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover/cell:block z-30 bg-[#18181b] text-[#646669] border border-neutral-800 text-[10px] font-mono py-1.5 px-2.5 rounded shadow-xl whitespace-nowrap pointer-events-none">
                      <div class="text-[#e2e8f0] font-bold mb-0.5">{{ formatDateLabel(day.date) }}</div>
                      <div>attempts: <span class="text-[#e2e8f0]">{{ day.attempted }}</span></div>
                      <div>solved: <span class="text-sticker-green">{{ day.solved }}</span></div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Month labels row -->
              <div class="relative w-full h-4 mt-2 select-none" style="padding-left: 64px;">
                <div class="relative w-full h-full">
                  <span v-for="label in monthLabels" :key="label.colIndex" 
                        class="absolute text-[10px] text-ink-muted font-mono" 
                        :style="{ left: `${(label.colIndex / 53) * 100}%` }">
                    {{ label.text }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer Info: UTC Note & Active Streak Info -->
        <div class="mt-4 pt-3 border-t border-hairline flex flex-col sm:flex-row items-center justify-between text-xs text-ink-muted font-mono select-none gap-2">
          <span>note: all activity data is using utc time.</span>
          <div class="flex items-center gap-3">
            <span class="text-ink-muted flex items-center gap-1">
              active streak:
              <span v-html="getFaIcon(faFire)" class="w-3.5 h-3.5 text-sticker-orange"></span>
              <strong class="text-ink">{{ authStore.user?.streak || 0 }} days</strong>
            </span>
            <span class="text-sticker-orange flex items-center gap-1">
              <span v-html="getFaIcon(faCircle)" class="w-1.5 h-1.5 text-sticker-orange animate-ping"></span>
              active
            </span>
          </div>
        </div>
      </div>

      <!-- Daily Checklist -->
      <div class="lg:col-span-3 bg-surface rounded-xl border border-hairline p-6 shadow-notion-soft">
        <div class="flex items-center justify-between mb-4 select-none">
          <h3 class="text-base font-bold text-ink flex items-center gap-2">
            <span v-html="getFaIcon(faClipboardCheck)" class="w-5 h-5 text-primary"></span>
            Daily Goals Checklist
          </h3>
          <span class="text-xxs bg-sticker-green/10 border border-sticker-green/20 text-sticker-green px-2.5 py-0.5 rounded-full font-bold">
            Updated daily
          </span>
        </div>
        <div class="space-y-3">
          
          <div class="flex items-center justify-between p-3 bg-canvas-soft/40 rounded-lg border border-hairline">
            <div class="flex items-center gap-3">
              <span v-html="getFaIcon(faCheckCircle)" class="h-4.5 w-4.5 text-sticker-green flex items-center"></span>
              <div>
                <span class="text-sm font-medium text-ink line-through opacity-60">Log in to LinuxMaster</span>
                <p class="text-xxs text-ink-muted">Earned +10 XP</p>
              </div>
            </div>
            <span class="text-xs text-sticker-green font-semibold select-none">Done</span>
          </div>

          <div class="flex items-center justify-between p-3 bg-canvas-soft/40 rounded-lg border border-hairline">
            <div class="flex items-center gap-3">
              <span v-html="getFaIcon(authStore.user?.streak >= 1 ? faCheckCircle : faCircle)"
                    :class="authStore.user?.streak >= 1 ? 'text-sticker-green' : 'text-ink-faint/30'"
                    class="h-4.5 w-4.5 flex items-center"></span>
              <div>
                <span class="text-sm font-medium text-ink" :class="authStore.user?.streak >= 1 ? 'line-through opacity-60' : ''">Maintain active streak</span>
                <p class="text-xxs text-ink-muted">Currently at {{ authStore.user?.streak }} days</p>
              </div>
            </div>
            <span class="text-xs font-semibold select-none" :class="authStore.user?.streak >= 1 ? 'text-sticker-green' : 'text-primary'">+20 XP</span>
          </div>

          <div class="flex items-center justify-between p-3 bg-canvas-soft/40 rounded-lg border border-hairline">
            <div class="flex items-center gap-3">
              <span v-html="getFaIcon(authStore.user?.xp >= 100 ? faCheckCircle : faCircle)"
                    :class="authStore.user?.xp >= 100 ? 'text-sticker-green' : 'text-ink-faint/30'"
                    class="h-4.5 w-4.5 flex items-center"></span>
              <div>
                <span class="text-sm font-medium text-ink" :class="authStore.user?.xp >= 100 ? 'line-through opacity-60' : ''">Achieve 100 XP overall</span>
                <p class="text-xxs text-ink-muted">Current: {{ authStore.user?.xp }} XP</p>
              </div>
            </div>
            <span class="text-xs font-semibold select-none" :class="authStore.user?.xp >= 100 ? 'text-sticker-green' : 'text-primary'">+50 XP</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Course Catalog Sections Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6 select-none">
      <h2 class="text-xl font-bold text-ink flex items-center gap-2">
        <span v-html="getFaIcon(faGraduationCap)" class="w-5 h-5 text-primary"></span>
        Learning Paths & Subject Modules
      </h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="sub in subjects" :key="sub.name"
           @click="handleStartQuiz(sub.name, '')"
           class="bg-surface rounded-xl border border-hairline overflow-hidden shadow-sm flex flex-col justify-between hover:shadow-notion-elevated hover:border-primary/40 hover:-translate-y-1 active:scale-[0.99] transition-all duration-300 ease-out cursor-pointer group card-sweep-container">
        <div class="p-5">
          <!-- Header layout -->
          <div class="flex items-center justify-between mb-3 select-none">
            <span class="p-2 rounded-lg bg-canvas-soft border border-hairline group-hover:bg-primary/5 group-hover:border-primary group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 ease-out flex items-center justify-center w-10 h-10 text-ink"
                  title="Open subject question bank">
              <span v-html="getFaIcon(sub.icon)" class="w-5 h-5 flex items-center justify-center"></span>
            </span>
            <span class="text-xxs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider" :class="sub.colorClass">
              {{ sub.name.split(' ')[0] }}
            </span>
          </div>
          <h3 class="text-base font-bold text-ink mb-1.5 group-hover:text-primary transition-colors duration-300"
              title="Open subject question bank">
            {{ sub.name }}
          </h3>
          <p class="text-xs text-ink-muted leading-relaxed">{{ sub.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar matching styling variables */
.scrollbar-thin::-webkit-scrollbar {
  height: 4px;
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: var(--hairline);
  border-radius: 2px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: var(--ink-faint);
}
</style>
