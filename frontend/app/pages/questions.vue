<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { icon } from '@fortawesome/fontawesome-svg-core'
import { 
  faArrowLeft, 
  faBook, 
  faBolt, 
  faRocket, 
  faSearch, 
  faTimes, 
  faCheck, 
  faCircle, 
  faStar, 
  faFire, 
  faBullseye, 
  faPenClip, 
  faInbox, 
  faChevronLeft, 
  faChevronRight,
  faCaretUp,
  faCaretDown
} from '@fortawesome/free-solid-svg-icons'
import { faStar as farStar } from '@fortawesome/free-regular-svg-icons'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

// Active subject and subject title
const activeSubject = ref<string>('Linux System Commands')

// Sidebar custom quiz builder state
const quizWeek = ref<string>('all')
const quizDifficulty = ref<string>('all')
const quizType = ref<string>('all')
const quizLimit = ref<number>(5)

// Table-level filters state
const selectedWeek = ref<string>('all')
const selectedTopic = ref<string>('all')
const selectedType = ref<string>('all')
const selectedDifficulty = ref<string>('all')
const selectedStatus = ref<string>('all')
const searchKeyword = ref<string>('')

// Filter choices lists (shared by both quiz generator and table filters)
const weeksList = ref<number[]>([])
const topicsList = ref<string[]>([])

// Questions table state
const questions = ref<any[]>([])
const totalQuestions = ref(0)
const currentPage = ref(1)
const perPage = ref(15)
const sortBy = ref<string>('id')
const sortOrder = ref<'asc' | 'desc'>('asc')
const isTableLoading = ref(true)

// Stats state
const stats = ref({
  total_questions: 0,
  solved_questions: 0,
  attempted_questions: 0,
  accuracy: 0.0,
  streak: 0,
  questions_remaining: 0,
  easy_total: 0,
  easy_solved: 0,
  medium_total: 0,
  medium_solved: 0,
  hard_total: 0,
  hard_solved: 0,
  expert_total: 0,
  expert_solved: 0
})

// Helper to return FontAwesome SVG markup
function getFaIcon(iconDef: any) {
  return icon(iconDef).html[0]
}

// Circumference of LeetCode radial progress (radius = 34 => 213.6)
const strokeDashoffset = computed(() => {
  if (stats.value.total_questions === 0) return 213.6
  const ratio = stats.value.solved_questions / stats.value.total_questions
  return 213.6 * (1 - ratio)
})

// Subject overall completion rate
const completionRate = computed(() => {
  if (stats.value.total_questions === 0) return 0
  return Math.round((stats.value.solved_questions / stats.value.total_questions) * 100)
})

// Load unique filters list
async function loadFilters() {
  if (!authStore.token) return
  try {
    const weeksRes = await authStore.api.get('/api/weeks', { params: { subject: activeSubject.value } })
    weeksList.value = weeksRes.data.weeks
    
    const topicsRes = await authStore.api.get('/api/topics', { 
      params: { 
        subject: activeSubject.value, 
        week: selectedWeek.value 
      } 
    })
    topicsList.value = topicsRes.data.topics
  } catch (err) {
    console.error('Failed to load filter definitions', err)
  }
}

// Load stats
async function loadStats() {
  if (!authStore.token) return
  try {
    const res = await authStore.api.get('/api/user/progress', { 
      params: { subject: activeSubject.value } 
    })
    stats.value = res.data
  } catch (err) {
    console.error('Failed to load user progress stats', err)
  }
}

// Load questions table data
async function loadQuestions() {
  if (!authStore.token) return
  isTableLoading.value = true
  try {
    const params: any = {
      subject: activeSubject.value,
      week: selectedWeek.value,
      topic: selectedTopic.value,
      type: selectedType.value,
      difficulty: selectedDifficulty.value,
      status: selectedStatus.value,
      search: searchKeyword.value,
      sort_by: sortBy.value,
      sort_order: sortOrder.value,
      page: currentPage.value,
      per_page: perPage.value
    }
    const res = await authStore.api.get('/api/questions', { params })
    questions.value = res.data.questions
    totalQuestions.value = res.data.total
  } catch (err) {
    console.error('Failed to load questions list', err)
  } finally {
    isTableLoading.value = false
  }
}

// Watch filters to trigger reloading
watch([selectedWeek, selectedTopic, selectedType, selectedDifficulty, selectedStatus, sortBy, sortOrder, currentPage], () => {
  loadQuestions()
})

// When week changes, refresh topics list and reset topic filter
watch(selectedWeek, async () => {
  selectedTopic.value = 'all'
  currentPage.value = 1
  try {
    const topicsRes = await authStore.api.get('/api/topics', { 
      params: { 
        subject: activeSubject.value, 
        week: selectedWeek.value 
      } 
    })
    topicsList.value = topicsRes.data.topics
  } catch (err) {
    console.error('Failed to update topics lists', err)
  }
})

// Toggle bookmarks
async function toggleBookmark(question: any) {
  if (!authStore.token) return
  try {
    const res = await authStore.api.post(`/api/questions/${question.id}/bookmark`)
    question.is_bookmarked = res.data.is_bookmarked
    loadStats()
  } catch (err) {
    console.error('Failed to toggle bookmark', err)
  }
}

// Route to dedicated question page
function navigateToQuestion(qId: number) {
  router.push(`/question/${qId}`)
}

// Custom Quiz Generator trigger
function handleGenerateCustomQuiz() {
  router.push({
    path: '/quiz',
    query: {
      subject: activeSubject.value,
      week: quizWeek.value,
      difficulty: quizDifficulty.value,
      type: quizType.value,
      limit: quizLimit.value
    }
  })
}

// Sort column handler
function handleSort(column: string) {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'asc'
  }
  currentPage.value = 1
}

// Search debounce / trigger
let searchTimeout: any = null
function triggerSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadQuestions()
  }, 400)
}

onMounted(() => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  
  // Read query parameters
  if (route.query.subject) {
    activeSubject.value = route.query.subject as string
  }
  if (route.query.topic) {
    selectedTopic.value = route.query.topic as string
  }
  
  loadFilters()
  loadStats()
  loadQuestions()
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
    
    <!-- Title Header -->
    <div class="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <div class="flex items-center gap-2 mb-1.5 text-ink-muted text-xs font-semibold uppercase tracking-wider">
          <NuxtLink to="/" class="hover:text-primary transition-colors">Study Desk</NuxtLink>
          <span>/</span>
          <span class="text-ink-secondary">{{ activeSubject }}</span>
        </div>
        <h1 class="text-3xl font-bold tracking-tight text-ink flex items-center gap-2.5 select-none">
          {{ activeSubject }} Question Bank
          <span v-html="getFaIcon(faBook)" class="w-6 h-6 text-primary flex items-center"></span>
        </h1>
      </div>
      
      <!-- Back button -->
      <NuxtLink to="/" class="btn-secondary text-sm font-semibold flex items-center gap-1.5 px-4 py-2 self-start md:self-auto select-none">
        <span v-html="getFaIcon(faArrowLeft)" class="w-3.5 h-3.5 text-ink-secondary flex items-center"></span>
        <span>Back to Study Desk</span>
      </NuxtLink>
    </div>

    <!-- Overall Subject Syllabus Completion Bar -->
    <div class="bg-surface border border-hairline p-5 rounded-xl shadow-notion-soft mb-8 select-none">
      <div class="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-ink-muted mb-2">
        <span>Subject Course Syllabus Complete</span>
        <span class="text-sticker-green font-mono">{{ completionRate }}%</span>
      </div>
      <div class="w-full bg-canvas-soft border border-hairline h-3.5 rounded-full overflow-hidden relative shadow-inner">
        <div class="bg-gradient-to-r from-sticker-green to-emerald-400 bg-[length:200%_auto] h-full transition-all duration-700 ease-out shadow-[0_0_6px_rgba(26,174,57,0.3)] animate-shimmer" 
             :style="{ width: `${completionRate}%` }"></div>
      </div>
    </div>

    <!-- Stats Header Panel -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-6 mb-8 select-none">
      
      <!-- LeetCode Progress Ring & Breakdown Widget -->
      <div class="lg:col-span-2 bg-surface border border-hairline p-5 rounded-xl shadow-notion-soft flex items-center justify-between gap-6">
        <!-- Circular Progress SVG -->
        <div class="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 80 80">
            <!-- Base track -->
            <circle cx="40" cy="40" r="34" stroke="var(--canvas-soft)" stroke-width="5.5" fill="transparent" />
            <!-- Active indicator (Neon green glow) -->
            <circle cx="40" cy="40" r="34" 
                    stroke="var(--sticker-green)" 
                    stroke-width="5.5" 
                    fill="transparent" 
                    :stroke-dasharray="213.6" 
                    :stroke-dashoffset="strokeDashoffset" 
                    stroke-linecap="round" 
                    class="transition-all duration-500 ease-out" 
                    style="filter: drop-shadow(0 0 1.5px rgba(26,174,57,0.5));" />
          </svg>
          <div class="absolute inset-0 flex flex-col items-center justify-center font-mono">
            <span class="text-base font-bold text-ink leading-none">{{ stats.solved_questions }}</span>
            <span class="text-[9px] text-ink-muted mt-0.5 leading-none">/{{ stats.total_questions }}</span>
            <span class="text-[7px] text-ink-faint uppercase font-bold tracking-wider mt-1 font-sans">solved</span>
          </div>
        </div>
        
        <!-- Horizontal Difficulty Bars -->
        <div class="flex-1 space-y-1.5 text-[10px]">
          <!-- Easy -->
          <div class="space-y-0.5">
            <div class="flex justify-between font-bold text-[#615d59]">
              <span class="text-sticker-green uppercase">Easy</span>
              <span class="font-mono text-ink-secondary">{{ stats.easy_solved }}/{{ stats.easy_total }}</span>
            </div>
            <div class="w-full bg-canvas-soft h-1.5 rounded-full overflow-hidden">
              <div class="bg-sticker-green h-full rounded-full transition-all duration-500" 
                   :style="{ width: `${stats.easy_total ? (stats.easy_solved/stats.easy_total)*100 : 0}%` }"></div>
            </div>
          </div>
          
          <!-- Medium -->
          <div class="space-y-0.5">
            <div class="flex justify-between font-bold text-[#615d59]">
              <span class="text-primary uppercase">Medium</span>
              <span class="font-mono text-ink-secondary">{{ stats.medium_solved }}/{{ stats.medium_total }}</span>
            </div>
            <div class="w-full bg-canvas-soft h-1.5 rounded-full overflow-hidden">
              <div class="bg-primary h-full rounded-full transition-all duration-500" 
                   :style="{ width: `${stats.medium_total ? (stats.medium_solved/stats.medium_total)*100 : 0}%` }"></div>
            </div>
          </div>
          
          <!-- Hard -->
          <div class="space-y-0.5">
            <div class="flex justify-between font-bold text-[#615d59]">
              <span class="text-sticker-orange uppercase">Hard</span>
              <span class="font-mono text-ink-secondary">{{ stats.hard_solved }}/{{ stats.hard_total }}</span>
            </div>
            <div class="w-full bg-canvas-soft h-1.5 rounded-full overflow-hidden">
              <div class="bg-sticker-orange h-full rounded-full transition-all duration-500" 
                   :style="{ width: `${stats.hard_total ? (stats.hard_solved/stats.hard_total)*100 : 0}%` }"></div>
            </div>
          </div>
          
          <!-- Expert -->
          <div class="space-y-0.5">
            <div class="flex justify-between font-bold text-[#615d59]">
              <span class="text-sticker-pink uppercase">Expert</span>
              <span class="font-mono text-ink-secondary">{{ stats.expert_solved }}/{{ stats.expert_total }}</span>
            </div>
            <div class="w-full bg-canvas-soft h-1.5 rounded-full overflow-hidden">
              <div class="bg-sticker-pink h-full rounded-full transition-all duration-500" 
                   :style="{ width: `${stats.expert_total ? (stats.expert_solved/stats.expert_total)*100 : 0}%` }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Streak -->
      <div class="bg-surface border border-hairline p-5 rounded-xl shadow-notion-soft flex flex-col justify-between">
        <div class="text-xxs font-bold uppercase tracking-wider text-ink-muted mb-1">Active Streak</div>
        <div class="flex items-baseline gap-1 mt-1">
          <span class="text-3xl font-extrabold text-sticker-orange font-mono">{{ stats.streak }}</span>
          <span class="text-xs text-ink-muted">days</span>
        </div>
        <div class="text-[10px] text-sticker-orange flex items-center gap-1.5 font-semibold mt-2">
          <span v-html="getFaIcon(faFire)" class="w-3.5 h-3.5 text-sticker-orange flex items-center"></span>
          <span>Daily action active</span>
        </div>
      </div>

      <!-- Accuracy -->
      <div class="bg-surface border border-hairline p-5 rounded-xl shadow-notion-soft flex flex-col justify-between">
        <div class="text-xxs font-bold uppercase tracking-wider text-ink-muted mb-1">Overall Accuracy</div>
        <div class="flex items-baseline gap-1 mt-1">
          <span class="text-3xl font-extrabold text-ink font-mono">{{ stats.accuracy }}</span>
          <span class="text-xs text-ink-muted">%</span>
        </div>
        <div class="text-[10px] text-primary flex items-center gap-1.5 font-semibold mt-2">
          <span v-html="getFaIcon(faBullseye)" class="w-3.5 h-3.5 text-primary flex items-center"></span>
          <span>Correct / total attempts</span>
        </div>
      </div>

      <!-- Attempted -->
      <div class="bg-surface border border-hairline p-5 rounded-xl shadow-notion-soft flex flex-col justify-between">
        <div class="text-xxs font-bold uppercase tracking-wider text-ink-muted mb-1">Total Attempted</div>
        <div class="flex items-baseline gap-1 mt-1">
          <span class="text-3xl font-extrabold text-ink font-mono">{{ stats.attempted_questions }}</span>
          <span class="text-xs text-ink-muted">questions</span>
        </div>
        <div class="text-[10px] text-ink-muted flex items-center gap-1.5 font-semibold mt-2">
          <span v-html="getFaIcon(faPenClip)" class="w-3.5 h-3.5 text-ink-muted flex items-center"></span>
          <span>Unique challenged</span>
        </div>
      </div>

      <!-- Remaining -->
      <div class="bg-surface border border-hairline p-5 rounded-xl shadow-notion-soft flex flex-col justify-between">
        <div class="text-xxs font-bold uppercase tracking-wider text-ink-muted mb-1">Remaining</div>
        <div class="flex items-baseline gap-1 mt-1">
          <span class="text-3xl font-extrabold text-ink-muted font-mono">{{ stats.questions_remaining }}</span>
          <span class="text-xs text-ink-muted">unsolved</span>
        </div>
        <div class="text-[10px] text-ink-faint flex items-center gap-1.5 font-semibold mt-2">
          <span v-html="getFaIcon(faInbox)" class="w-3.5 h-3.5 text-ink-faint flex items-center"></span>
          <span>Questions left</span>
        </div>
      </div>
      
    </div>

    <!-- Main Content Area: Quiz Generator Sidebar + Question Table -->
    <div class="flex flex-col lg:flex-row gap-6 items-start">
      
      <!-- Left Sidebar: Custom Quiz Generator Form -->
      <div class="w-full lg:w-64 flex-shrink-0 bg-surface border border-hairline rounded-xl p-5 shadow-notion-soft relative self-stretch lg:self-auto select-none">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-hairline pb-3 mb-4 select-none">
          <h3 class="text-sm font-bold text-ink flex items-center gap-1.5">
            <span v-html="getFaIcon(faBolt)" class="w-4 h-4 text-primary flex items-center"></span>
            <span>Custom Quiz Builder</span>
          </h3>
        </div>
        
        <!-- Form fields -->
        <div class="space-y-4 text-xs">
          <!-- Week filter -->
          <div class="flex flex-col gap-1.5">
            <label class="font-bold text-ink-muted uppercase tracking-wider text-[10px]">Select Week</label>
            <select v-model="quizWeek" class="bg-canvas-soft border border-hairline rounded-md p-2 text-ink outline-none focus:border-primary transition-all cursor-pointer">
              <option value="all">All Weeks</option>
              <option v-for="wk in weeksList" :key="wk" :value="wk">Week {{ wk }}</option>
            </select>
          </div>

          <!-- Question type filter -->
          <div class="flex flex-col gap-1.5">
            <label class="font-bold text-ink-muted uppercase tracking-wider text-[10px]">Question Type</label>
            <select v-model="quizType" class="bg-canvas-soft border border-hairline rounded-md p-2 text-ink outline-none focus:border-primary transition-all cursor-pointer">
              <option value="all">All Formats</option>
              <option value="MCQ">Multiple Choice (MCQ)</option>
              <option value="MSQ">Multiple Select (MSQ)</option>
              <option value="NAT">Numerical Answer (NAT)</option>
              <option value="CODING">Terminal command (Coding)</option>
            </select>
          </div>

          <!-- Difficulty filter -->
          <div class="flex flex-col gap-1.5">
            <label class="font-bold text-ink-muted uppercase tracking-wider text-[10px]">Difficulty</label>
            <select v-model="quizDifficulty" class="bg-canvas-soft border border-hairline rounded-md p-2 text-ink outline-none focus:border-primary transition-all cursor-pointer">
              <option value="all">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
              <option value="Expert">Expert</option>
            </select>
          </div>

          <!-- Question Length Limit -->
          <div class="flex flex-col gap-1.5">
            <label class="font-bold text-ink-muted uppercase tracking-wider text-[10px]">Quiz Length</label>
            <select v-model="quizLimit" class="bg-canvas-soft border border-hairline rounded-md p-2 text-ink outline-none focus:border-primary transition-all cursor-pointer">
              <option :value="5">5 Questions</option>
              <option :value="10">10 Questions</option>
              <option :value="20">20 Questions</option>
              <option :value="100">All Questions</option>
            </select>
          </div>

          <!-- Generate Action -->
          <button @click="handleGenerateCustomQuiz"
                  class="w-full text-center py-2.5 bg-primary text-white hover:bg-primary-active transition-colors font-semibold rounded-full mt-4 flex items-center justify-center gap-1.5 active:scale-95 duration-100 cursor-pointer">
            <span v-html="getFaIcon(faRocket)" class="w-3.5 h-3.5 text-white flex items-center"></span>
            <span>Generate Custom Quiz</span>
          </button>
        </div>
      </div>

      <!-- Main Table Card (with Integrated Toolbar Filters) -->
      <div class="flex-1 bg-surface border border-hairline rounded-xl shadow-notion-soft overflow-hidden w-full">
        
        <!-- Table-level Toolbar Filters -->
        <div class="p-4 border-b border-hairline bg-canvas-soft/40 flex flex-wrap items-center gap-3 select-none">
          <!-- Search box -->
          <div class="relative w-full md:w-56 lg:w-64">
            <span v-html="getFaIcon(faSearch)" class="absolute inset-y-0 left-0 pl-2.5 flex items-center text-ink-faint text-xs w-3.5 h-3.5 top-1/2 -translate-y-1/2"></span>
            <input v-model="searchKeyword" @input="triggerSearch" type="text"
                   class="w-full border border-hairline bg-surface text-ink text-xs rounded-md pl-8 pr-7 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                   placeholder="Search commands/prompts..." />
            <button v-if="searchKeyword" @click="() => { searchKeyword=''; loadQuestions(); }"
                    class="absolute inset-y-0 right-0 pr-2.5 flex items-center text-ink-faint hover:text-ink text-xs cursor-pointer">
              <span v-html="getFaIcon(faTimes)" class="w-3 h-3 flex items-center"></span>
            </button>
          </div>

          <!-- Week Filter -->
          <select v-model="selectedWeek" class="bg-surface border border-hairline text-ink-secondary text-xs rounded-md py-1.5 px-2.5 outline-none focus:ring-1 focus:ring-primary cursor-pointer">
            <option value="all">All Weeks</option>
            <option v-for="wk in weeksList" :key="wk" :value="wk">Week {{ wk }}</option>
          </select>

          <!-- Topic Filter -->
          <select v-model="selectedTopic" class="bg-surface border border-hairline text-ink-secondary text-xs rounded-md py-1.5 px-2.5 outline-none focus:ring-1 focus:ring-primary max-w-[140px] truncate cursor-pointer">
            <option value="all">All Topics</option>
            <option v-for="t in topicsList" :key="t" :value="t">{{ t }}</option>
          </select>

          <!-- Type Filter -->
          <select v-model="selectedType" class="bg-surface border border-hairline text-ink-secondary text-xs rounded-md py-1.5 px-2.5 outline-none focus:ring-1 focus:ring-primary cursor-pointer">
            <option value="all">All Types</option>
            <option value="MCQ">MCQ</option>
            <option value="MSQ">MSQ</option>
            <option value="NAT">NAT</option>
            <option value="CODING">Coding</option>
          </select>

          <!-- Difficulty Filter -->
          <select v-model="selectedDifficulty" class="bg-surface border border-hairline text-ink-secondary text-xs rounded-md py-1.5 px-2.5 outline-none focus:ring-1 focus:ring-primary cursor-pointer">
            <option value="all">All Difficulties</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
            <option value="Expert">Expert</option>
          </select>

          <!-- Status Filter -->
          <select v-model="selectedStatus" class="bg-surface border border-hairline text-ink-secondary text-xs rounded-md py-1.5 px-2.5 outline-none focus:ring-1 focus:ring-primary cursor-pointer">
            <option value="all">All Statuses</option>
            <option value="solved">Solved</option>
            <option value="attempted">Attempted</option>
            <option value="unattempted">Unattempted</option>
            <option value="bookmarked">Bookmarked</option>
          </select>

          <span class="text-xxs text-ink-faint font-mono font-bold ml-auto">{{ totalQuestions }} items</span>
        </div>

        <!-- Scrollable Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-hairline text-left text-xs">
            <thead class="bg-canvas-soft text-ink-muted uppercase tracking-wider font-bold text-[10px] select-none">
              <tr>
                <th class="px-4 py-3 w-12 text-center">Status</th>
                <th class="px-4 py-3 w-20 cursor-pointer hover:bg-neutral-200 transition-all" @click="handleSort('id')">
                  <div class="flex items-center justify-center gap-1">
                    ID
                    <span v-if="sortBy === 'id'" v-html="getFaIcon(sortOrder === 'asc' ? faCaretUp : faCaretDown)" class="w-2 h-2 flex items-center"></span>
                  </div>
                </th>
                <th class="px-6 py-3 min-w-[280px]">Question Title</th>
                <th class="px-4 py-3 cursor-pointer hover:bg-neutral-200 transition-all" @click="handleSort('type')">
                  <div class="flex items-center gap-1">
                    Type
                    <span v-if="sortBy === 'type'" v-html="getFaIcon(sortOrder === 'asc' ? faCaretUp : faCaretDown)" class="w-2 h-2 flex items-center"></span>
                  </div>
                </th>
                <th class="px-4 py-3 cursor-pointer hover:bg-neutral-200 transition-all" @click="handleSort('difficulty')">
                  <div class="flex items-center gap-1">
                    Difficulty
                    <span v-if="sortBy === 'difficulty'" v-html="getFaIcon(sortOrder === 'asc' ? faCaretUp : faCaretDown)" class="w-2 h-2 flex items-center"></span>
                  </div>
                </th>
                <th class="px-4 py-3 cursor-pointer hover:bg-neutral-200 transition-all" @click="handleSort('topic')">
                  <div class="flex items-center gap-1">
                    Topic
                    <span v-if="sortBy === 'topic'" v-html="getFaIcon(sortOrder === 'asc' ? faCaretUp : faCaretDown)" class="w-2 h-2 flex items-center"></span>
                  </div>
                </th>
                <th class="px-4 py-3 cursor-pointer hover:bg-neutral-200 transition-all text-center w-16" @click="handleSort('week')">
                  <div class="flex items-center justify-center gap-1">
                    Week
                    <span v-if="sortBy === 'week'" v-html="getFaIcon(sortOrder === 'asc' ? faCaretUp : faCaretDown)" class="w-2 h-2 flex items-center"></span>
                  </div>
                </th>
                <th class="px-4 py-3 w-12 text-center">Fav</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-hairline bg-surface text-ink-secondary">
              <!-- Loading spinner -->
              <tr v-if="isTableLoading">
                <td colspan="8" class="px-6 py-12 text-center">
                  <div class="inline-block animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent mb-2"></div>
                  <p class="text-ink-muted text-xs font-semibold">Loading questions dataset...</p>
                </td>
              </tr>
              
              <!-- Empty state -->
              <tr v-else-if="questions.length === 0">
                <td colspan="8" class="px-6 py-12 text-center text-ink-muted select-none">
                  <span class="text-3xl mb-2 block">📭</span>
                  <p class="font-bold mb-1">No questions match the active filters</p>
                  <p class="text-xxs">Try adjusting your filters above or typing a different search query.</p>
                </td>
              </tr>

              <!-- Questions rows -->
              <tr v-else v-for="q in questions" :key="q.id" 
                  @click="navigateToQuestion(q.id)"
                  class="hover:bg-canvas-soft/50 cursor-pointer transition-colors duration-150 group">
                <!-- Status icon -->
                <td class="px-4 py-3.5 text-center font-bold">
                  <span v-if="q.status === 'solved'" v-html="getFaIcon(faCheck)" class="text-sticker-green w-3.5 h-3.5 inline-flex items-center justify-center" title="Solved"></span>
                  <span v-else-if="q.status === 'attempted'" v-html="getFaIcon(faCircle)" class="text-primary w-2 h-2 inline-flex items-center justify-center" title="Attempted"></span>
                  <span v-else v-html="getFaIcon(faCircle)" class="text-ink-faint/30 w-1.5 h-1.5 inline-flex items-center justify-center"></span>
                </td>
                
                <!-- ID -->
                <td class="px-4 py-3.5 font-mono text-ink-muted font-bold text-center">#{{ q.id }}</td>
                
                <!-- Title -->
                <td class="px-6 py-3.5 font-semibold text-ink group-hover:text-primary transition-colors truncate max-w-sm" :title="q.prompt">
                  {{ q.prompt }}
                </td>

                <!-- Type -->
                <td class="px-4 py-3.5">
                  <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider"
                        :class="q.type === 'MCQ' ? 'bg-[#f0f4f8] text-[#334e68]' : q.type === 'MSQ' ? 'bg-[#f3f0ff] text-[#553c9a]' : q.type === 'NAT' ? 'bg-[#fff9db] text-[#8c6d1f]' : 'bg-neutral-900 text-neutral-100 font-mono'">
                    {{ q.type === 'COMMAND' ? 'coding' : q.type }}
                  </span>
                </td>

                <!-- Difficulty -->
                <td class="px-4 py-3.5 font-bold">
                  <span :class="q.difficulty === 'Easy' ? 'text-sticker-green' : q.difficulty === 'Medium' ? 'text-primary' : q.difficulty === 'Hard' ? 'text-sticker-orange' : 'text-sticker-pink'">
                    {{ q.difficulty }}
                  </span>
                </td>

                <!-- Topic -->
                <td class="px-4 py-3.5 text-ink-muted truncate max-w-[140px]">{{ q.topic }}</td>

                <!-- Week -->
                <td class="px-4 py-3.5 text-center font-mono text-ink-muted">W{{ q.week }}</td>

                <!-- Bookmark/Favorite -->
                <td class="px-4 py-3.5 text-center" @click.stop="toggleBookmark(q)">
                  <button class="focus:outline-none transition-transform duration-150 active:scale-125 flex items-center justify-center mx-auto cursor-pointer">
                    <span v-if="q.is_bookmarked" v-html="getFaIcon(faStar)" class="text-sticker-orange w-3.5 h-3.5 flex items-center"></span>
                    <span v-else v-html="getFaIcon(farStar)" class="text-ink-faint hover:text-ink opacity-30 group-hover:opacity-100 w-3.5 h-3.5 flex items-center"></span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Table Pagination Footer -->
        <div v-if="questions.length > 0" class="p-4 border-t border-hairline bg-canvas-soft/40 flex items-center justify-between select-none">
          <button @click="currentPage--" :disabled="currentPage === 1"
                  class="btn-secondary px-3 py-1.5 text-xxs font-bold disabled:opacity-40 disabled:pointer-events-none flex items-center gap-1.5 cursor-pointer">
            <span v-html="getFaIcon(faChevronLeft)" class="w-2.5 h-2.5"></span>
            <span>Previous</span>
          </button>
          
          <span class="text-xxs font-mono text-ink-muted">
            Page <strong class="text-ink font-bold">{{ currentPage }}</strong> of <strong class="text-ink font-bold">{{ Math.ceil(totalQuestions / perPage) }}</strong>
          </span>

          <button @click="currentPage++" :disabled="currentPage * perPage >= totalQuestions"
                  class="btn-secondary px-3 py-1.5 text-xxs font-bold disabled:opacity-40 disabled:pointer-events-none flex items-center gap-1.5 cursor-pointer">
            <span>Next</span>
            <span v-html="getFaIcon(faChevronRight)" class="w-2.5 h-2.5"></span>
          </button>
        </div>
      </div>

    </div>

  </div>
</template>

<style scoped>
/* Custom scrollbar modifiers */
::-webkit-scrollbar {
  height: 4px;
  width: 4px;
}
::-webkit-scrollbar-thumb {
  background: var(--hairline);
  border-radius: 2px;
}
</style>
