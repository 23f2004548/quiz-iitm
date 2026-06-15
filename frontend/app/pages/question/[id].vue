<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter, useRoute } from 'vue-router'
import VirtualTerminal from '~/components/VirtualTerminal.vue'
import { icon } from '@fortawesome/fontawesome-svg-core'
import { 
  faArrowLeft, 
  faBook, 
  faComments, 
  faStar, 
  faExclamationTriangle, 
  faCheckCircle, 
  faTimesCircle, 
  faLightbulb, 
  faKey,
  faUser,
  faPaperPlane,
  faCircle,
  faCheck,
  faRocket
} from '@fortawesome/free-solid-svg-icons'
import { faStar as farStar } from '@fortawesome/free-regular-svg-icons'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const questionId = computed(() => parseInt(route.params.id as string))

// Left Panel tabs: 'description' | 'discussion'
const activeTab = ref<'description' | 'discussion'>('description')

// Question details state
const question = ref<any | null>(null)
const isLoading = ref(true)
const fetchError = ref<string | null>(null)

// User answers & attempt state
const userAnswer = ref<any>('')
const gradingResult = ref<any | null>(null)
const isSubmittingAttempt = ref(false)
const showSolution = ref(false)
const showHint = ref(false)

// Discussion / Comments state
const commentsList = ref<any[]>([])
const newCommentText = ref('')
const isPostingComment = ref(false)
const isLoadingComments = ref(false)

// Helper to return FontAwesome SVG markup
function getFaIcon(iconDef: any) {
  return icon(iconDef).html[0]
}

// Fetch question details
async function fetchQuestionDetails() {
  isLoading.value = true
  fetchError.value = null
  try {
    const res = await authStore.api.get(`/api/questions/${questionId.value}`)
    question.value = res.data
    
    // Initialize answer state
    if (res.data.type === 'MSQ') {
      userAnswer.value = []
    } else {
      userAnswer.value = ''
    }
  } catch (err: any) {
    console.error('Failed to load question details', err)
    fetchError.value = err.response?.data?.error || 'Failed to retrieve question details.'
  } finally {
    isLoading.value = false
  }
}

// Fetch comments
async function fetchComments() {
  isLoadingComments.value = true
  try {
    const res = await authStore.api.get(`/api/questions/${questionId.value}/comments`)
    commentsList.value = res.data.comments
  } catch (err) {
    console.error('Failed to retrieve comments', err)
  } finally {
    isLoadingComments.value = false
  }
}

// Post a new comment
async function submitComment() {
  const text = newCommentText.value.trim()
  if (!text || isPostingComment.value) return
  isPostingComment.value = true
  try {
    const res = await authStore.api.post(`/api/questions/${questionId.value}/comments`, {
      comment_text: text
    })
    commentsList.value.unshift(res.data)
    newCommentText.value = ''
  } catch (err) {
    console.error('Failed to post comment', err)
  } finally {
    isPostingComment.value = false
  }
}

// Toggle Bookmarks
async function toggleBookmark() {
  if (!question.value || !authStore.token) return
  try {
    const res = await authStore.api.post(`/api/questions/${question.value.id}/bookmark`)
    question.value.is_bookmarked = res.data.is_bookmarked
  } catch (err) {
    console.error('Failed to toggle bookmark', err)
  }
}

// MSQ check toggle
function toggleMsqChoice(choiceText: string) {
  if (!Array.isArray(userAnswer.value)) {
    userAnswer.value = []
  }
  const idx = userAnswer.value.indexOf(choiceText)
  if (idx > -1) {
    userAnswer.value.splice(idx, 1)
  } else {
    userAnswer.value.push(choiceText)
  }
}

// Listen to terminal commands to autofill command answer
function handleTerminalCommand(cmd: string, output: string) {
  if (question.value && question.value.type === 'COMMAND') {
    userAnswer.value = cmd
  }
}

// Submit attempt for grading
async function submitAttempt() {
  if (!question.value || isSubmittingAttempt.value) return
  isSubmittingAttempt.value = true
  gradingResult.value = null
  
  let ansVal = userAnswer.value
  if (question.value.type === 'MSQ') {
    ansVal = (ansVal as string[]).join('||')
  }
  
  try {
    const res = await authStore.api.post(`/api/questions/${questionId.value}/attempt`, {
      user_answer: ansVal
    })
    gradingResult.value = res.data
    
    // Sync user stats inside auth store
    if (authStore.user) {
      authStore.user.xp = res.data.new_xp
      authStore.user.level = res.data.new_level
      authStore.user.streak = res.data.new_streak
    }
  } catch (err) {
    console.error('Failed to submit attempt', err)
  } finally {
    isSubmittingAttempt.value = false
  }
}

// Format relative date string
function formatCommentDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).toLowerCase()
}

onMounted(() => {
  if (!authStore.token) {
    router.push('/login')
    return
  }
  fetchQuestionDetails()
  fetchComments()
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6 min-h-[calc(100vh-3.5rem)] flex flex-col justify-stretch">
    
    <!-- Header Navigation bar -->
    <div class="mb-4 flex items-center justify-between border-b border-hairline pb-3 select-none">
      <div class="flex items-center gap-2">
        <button @click="router.back()" class="text-ink-muted hover:text-ink text-xs font-bold flex items-center gap-1.5 cursor-pointer">
          <span v-html="getFaIcon(faArrowLeft)" class="w-3 h-3 flex items-center"></span> Back
        </button>
        <span class="text-ink-faint">/</span>
        <span class="text-xxs font-mono font-bold text-ink-muted">Question #{{ questionId }}</span>
      </div>

      <!-- Bookmark Star in header -->
      <button v-if="question" @click="toggleBookmark" 
              class="btn-secondary px-3 py-1.5 text-xs font-semibold flex items-center gap-1.5 active:scale-95 duration-100 cursor-pointer">
        <span v-html="getFaIcon(question.is_bookmarked ? faStar : farStar)" 
              :class="question.is_bookmarked ? 'text-sticker-orange' : 'text-ink-faint'" 
              class="w-3.5 h-3.5 flex items-center"></span>
        <span>{{ question.is_bookmarked ? 'Bookmarked' : 'Bookmark' }}</span>
      </button>
    </div>

    <!-- Error State -->
    <div v-if="fetchError" class="bg-surface border border-red-200 p-8 rounded-xl shadow-notion-soft text-center max-w-md mx-auto my-12">
      <span v-html="getFaIcon(faExclamationTriangle)" class="w-10 h-10 text-sticker-orange mx-auto mb-4 flex items-center justify-center"></span>
      <h2 class="text-lg font-bold text-ink mb-2">Question Unavailable</h2>
      <p class="text-xs text-red-600 bg-red-50 border border-red-100 p-4 rounded-lg leading-relaxed mb-6 font-mono">
        {{ fetchError }}
      </p>
      <button @click="router.back()" class="btn-primary">Return to Bank</button>
    </div>

    <!-- Loading State -->
    <div v-else-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-24">
      <div class="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent mb-2"></div>
      <p class="text-xs font-semibold text-ink-muted">Loading question specifications...</p>
    </div>

    <!-- Main Workspace Split Pane -->
    <div v-else-if="question" class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
      
      <!-- Left Panel: Tabs for Description & Comments -->
      <div class="lg:col-span-6 bg-surface border border-hairline rounded-xl shadow-notion-soft flex flex-col overflow-hidden min-h-[500px]">
        
        <!-- Tabs selector header -->
        <div class="flex border-b border-hairline bg-canvas-soft/40 select-none">
          <button @click="activeTab = 'description'" 
                  class="px-5 py-3 text-xs font-bold border-r border-hairline transition-all duration-150 flex items-center gap-1.5"
                  :class="activeTab === 'description' ? 'bg-surface text-ink border-b-2 border-b-primary' : 'text-ink-muted hover:text-ink hover:bg-canvas-soft/20'">
            <span v-html="getFaIcon(faBook)" class="w-3.5 h-3.5 text-primary flex items-center"></span>
            <span>Problem Description</span>
          </button>
          <button @click="activeTab = 'discussion'" 
                  class="px-5 py-3 text-xs font-bold border-r border-hairline transition-all duration-150 flex items-center gap-1.5"
                  :class="activeTab === 'discussion' ? 'bg-surface text-ink border-b-2 border-b-primary' : 'text-ink-muted hover:text-ink hover:bg-canvas-soft/20'">
            <span v-html="getFaIcon(faComments)" class="w-3.5 h-3.5 text-primary flex items-center"></span>
            <span>Discussion Forum</span>
            <span class="bg-canvas-soft text-ink-muted font-mono text-[9px] px-1.5 py-0.5 rounded-full border border-hairline">
              {{ commentsList.length }}
            </span>
          </button>
        </div>

        <!-- Tab Content Box -->
        <div class="flex-1 overflow-y-auto p-6">
          
          <!-- Tab 1: Description -->
          <div v-if="activeTab === 'description'" class="space-y-6">
            <!-- Metadata bar -->
            <div class="flex flex-wrap gap-2 items-center text-[10px] select-none">
              <span class="px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider"
                    :class="question.difficulty === 'Easy' ? 'bg-sticker-green/10 text-sticker-green' : question.difficulty === 'Medium' ? 'bg-primary/10 text-primary' : question.difficulty === 'Hard' ? 'bg-sticker-orange/10 text-sticker-orange-deep' : 'bg-sticker-pink/10 text-sticker-pink'">
                {{ question.difficulty }}
              </span>
              <span class="bg-[#f0f4f8] text-[#334e68] px-2 py-0.5 rounded border border-hairline">
                Topic: {{ question.topic }}
              </span>
              <span class="bg-[#f3f0ff] text-[#553c9a] px-2 py-0.5 rounded border border-hairline">
                Week {{ question.week }}
              </span>
            </div>

            <!-- Question prompt text -->
            <div class="select-text">
              <h2 class="text-lg font-bold text-ink leading-relaxed whitespace-pre-wrap select-text">
                {{ question.prompt }}
              </h2>
            </div>

            <!-- Tags -->
            <div v-if="question.tags && question.tags.length > 0" class="flex flex-wrap gap-1.5 pt-2 select-none">
              <span v-for="tag in question.tags" :key="tag" 
                    class="bg-canvas-soft border border-hairline text-ink-muted px-2 py-0.5 rounded-sm text-[10px]">
                #{{ tag }}
              </span>
            </div>

            <!-- Solution Revealed Block -->
            <div v-if="showSolution" class="p-4 bg-yellow-50/40 border border-yellow-200/50 rounded-xl text-xs select-text">
              <span class="font-bold text-yellow-800 block mb-1.5 select-none flex items-center gap-1.5">
                <span v-html="getFaIcon(faKey)" class="w-3.5 h-3.5 text-yellow-700 flex items-center"></span>
                <span>Answer Formula / Key:</span>
              </span>
              <code class="font-mono bg-surface border border-hairline px-2 py-0.5 rounded font-bold text-ink select-text">
                {{ question.answer.split('||').join(', ') }}
              </code>
            </div>

            <!-- Hint Revealed Block -->
            <div v-if="showHint" class="p-4 bg-primary/5 border border-primary/10 rounded-xl text-xs leading-relaxed select-text">
              <span class="font-bold text-primary block mb-1.5 select-none flex items-center gap-1.5">
                <span v-html="getFaIcon(faLightbulb)" class="w-3.5 h-3.5 text-primary flex items-center"></span>
                <span>Tutor Explanation Blueprint:</span>
              </span>
              <p class="text-ink-secondary select-text">{{ question.explanation }}</p>
            </div>
          </div>

          <!-- Tab 2: Comments / Discussion Forum -->
          <div v-else-if="activeTab === 'discussion'" class="flex flex-col h-full space-y-4">
            <!-- Add comment editor -->
            <div class="space-y-2.5 bg-canvas-soft/40 border border-hairline rounded-xl p-4">
              <label for="comment-text" class="block font-bold text-ink-muted text-[10px] uppercase tracking-wider select-none">Post a Solution or Ask a Question</label>
              <textarea id="comment-text" v-model="newCommentText" rows="3"
                        class="w-full border border-hairline bg-surface text-ink text-xs rounded-md p-3 focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                        placeholder="Discuss your code logic, explain the command variables, or ask a doubt..."></textarea>
              <div class="flex justify-end select-none">
                <button @click="submitComment" :disabled="isPostingComment || !newCommentText.trim()"
                        class="btn-primary py-1.5 px-4 text-xs font-semibold flex items-center justify-center gap-1.5 disabled:opacity-50 cursor-pointer">
                  <span v-if="isPostingComment" class="animate-spin rounded-full h-3 w-3 border-2 border-white border-t-transparent"></span>
                  <span v-else v-html="getFaIcon(faPaperPlane)" class="w-3 h-3 text-white flex items-center"></span>
                  <span>Post to Forum</span>
                </button>
              </div>
            </div>

            <!-- Comments Feed -->
            <div class="flex-1 space-y-4 overflow-y-auto pt-2">
              <div v-if="isLoadingComments" class="text-center py-6 text-ink-muted text-xs select-none">
                Loading forum feed...
              </div>
              <div v-else-if="commentsList.length === 0" class="text-center py-12 text-ink-muted select-none">
                <span v-html="getFaIcon(faComments)" class="w-8 h-8 text-ink-faint mx-auto mb-2 flex items-center justify-center"></span>
                <p class="font-semibold text-xs mb-0.5">No discussions yet</p>
                <p class="text-[10px] text-ink-faint">Be the first to share your approach or ask a question!</p>
              </div>
              <div v-else v-for="c in commentsList" :key="c.id" 
                   class="bg-surface border border-hairline rounded-xl p-4 shadow-xxs select-text">
                <div class="flex items-center justify-between border-b border-hairline/60 pb-1.5 mb-2 text-[10px] font-mono text-ink-muted select-none">
                  <span class="font-bold text-ink flex items-center gap-1.5">
                    <span v-html="getFaIcon(faUser)" class="w-2.5 h-2.5 text-ink-muted flex items-center"></span>
                    <span>{{ c.username }}</span>
                  </span>
                  <span>{{ formatCommentDate(c.created_at) }}</span>
                </div>
                <p class="text-xs text-ink-secondary leading-relaxed whitespace-pre-wrap select-text">
                  {{ c.comment_text }}
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>

      <!-- Right Panel: Sandbox / Question Inputs form -->
      <div class="lg:col-span-6 flex flex-col justify-between space-y-6">
        
        <!-- Answer details card -->
        <div class="bg-surface border border-hairline rounded-xl p-6 shadow-notion-soft flex-1 flex flex-col justify-between">
          
          <div class="space-y-6">
            <div>
              <h3 class="text-xs font-bold uppercase tracking-wider text-ink-faint mb-3 select-none">Proposed Answer Input</h3>
              
              <!-- MCQ Options list -->
              <div v-if="question.type === 'MCQ'" class="space-y-2.5 select-none">
                <button v-for="opt in question.options" :key="opt.id"
                        @click="userAnswer = opt.option_text"
                        :disabled="gradingResult !== null"
                        class="w-full text-left p-4 rounded-xl border text-xs transition-all flex items-center justify-between active:scale-[0.99] cursor-pointer"
                        :class="userAnswer === opt.option_text ? 'bg-primary/5 border-primary font-bold text-primary shadow-sm' : 'bg-surface border-hairline text-ink-secondary hover:bg-canvas-soft/30'">
                  <span>{{ opt.option_text }}</span>
                  <span class="w-5 h-5 rounded-full border flex items-center justify-center text-[10px]"
                        :class="userAnswer === opt.option_text ? 'bg-primary border-primary text-white font-bold' : 'border-hairline bg-canvas-soft'">
                    <span v-if="userAnswer === opt.option_text" v-html="getFaIcon(faCheck)" class="w-2.5 h-2.5 flex items-center text-white"></span>
                  </span>
                </button>
              </div>

              <!-- MSQ Choices checkboxes list -->
              <div v-else-if="question.type === 'MSQ'" class="space-y-2.5 select-none">
                <p class="text-[10px] text-ink-faint italic mb-2">Select all choices that apply:</p>
                <button v-for="opt in question.options" :key="opt.id"
                        @click="toggleMsqChoice(opt.option_text)"
                        :disabled="gradingResult !== null"
                        class="w-full text-left p-4 rounded-xl border text-xs transition-all flex items-center justify-between active:scale-[0.99] cursor-pointer"
                        :class="userAnswer?.includes(opt.option_text) ? 'bg-primary/5 border-primary font-bold text-primary shadow-sm' : 'bg-surface border-hairline text-ink-secondary hover:bg-canvas-soft/30'">
                  <span>{{ opt.option_text }}</span>
                  <span class="w-5 h-5 rounded border flex items-center justify-center text-[10px]"
                        :class="userAnswer?.includes(opt.option_text) ? 'bg-primary border-primary text-white font-bold' : 'border-hairline bg-canvas-soft'">
                    <span v-if="userAnswer?.includes(opt.option_text)" v-html="getFaIcon(faCheck)" class="w-2.5 h-2.5 flex items-center text-white"></span>
                  </span>
                </button>
              </div>

              <!-- NAT numerical answer input -->
              <div v-else-if="question.type === 'NAT'">
                <input v-model="userAnswer" type="text"
                       :disabled="gradingResult !== null"
                       class="block w-48 border border-hairline bg-surface text-ink rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary font-mono shadow-sm"
                       placeholder="e.g. 15.4" />
              </div>

              <!-- COMMAND shell answer input -->
              <div v-else-if="question.type === 'COMMAND'">
                <input v-model="userAnswer" type="text"
                       :disabled="gradingResult !== null"
                       class="block w-full border border-hairline bg-surface text-ink rounded px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary font-mono shadow-sm"
                       placeholder="e.g. ls -la /etc" />
                <p class="text-[10px] text-ink-muted mt-2 select-none">
                  Use the virtual Linux console below to test commands. The last run command is loaded here automatically.
                </p>
              </div>
            </div>

            <!-- Terminal sandbox container -->
            <div v-if="question.type === 'COMMAND'" class="h-[280px] min-h-[220px]">
              <VirtualTerminal @commandRun="handleTerminalCommand" />
            </div>

            <!-- Attempt grading report alert -->
            <div v-if="gradingResult" class="p-4 rounded-xl border select-text"
                 :class="gradingResult.is_correct ? 'bg-sticker-green/5 border-sticker-green/20' : 'bg-red-50 border-red-200/50'">
              <div class="flex items-center justify-between mb-2 select-none">
                <span class="font-bold text-xs flex items-center gap-1.5" :class="gradingResult.is_correct ? 'text-sticker-green' : 'text-red-700'">
                  <span v-html="getFaIcon(gradingResult.is_correct ? faCheckCircle : faTimesCircle)" 
                        :class="gradingResult.is_correct ? 'text-sticker-green' : 'text-red-600'" 
                        class="w-4 h-4 flex items-center"></span>
                  <span>{{ gradingResult.is_correct ? 'Solution Solved Correctly!' : 'Incorrect Attempt' }}</span>
                </span>
                <span class="text-xxs font-bold px-2 py-0.5 rounded bg-canvas-soft border border-hairline font-mono text-ink-muted">
                  {{ gradingResult.is_correct ? `+${gradingResult.xp_gained} XP` : `+${gradingResult.xp_gained} XP (Attempt)` }}
                </span>
              </div>
              
              <div class="text-xs space-y-1.5 mt-2">
                <p v-if="!gradingResult.is_correct" class="text-ink-secondary">
                  Correct answer formula: <code class="font-mono bg-canvas-soft border border-hairline px-1.5 py-0.5 rounded text-red-600 font-bold">{{ gradingResult.correct_answer.split('||').join(', ') }}</code>
                </p>
                
                <div class="pt-2 border-t border-hairline/60 mt-3 select-text">
                  <span class="text-[10px] font-bold uppercase tracking-wider text-primary block mb-1 select-none flex items-center gap-1">
                    <span v-html="getFaIcon(faLightbulb)" class="w-3.5 h-3.5 text-primary flex items-center"></span>
                    <span>AI Tutor explanation:</span>
                  </span>
                  <p class="leading-relaxed text-ink-secondary text-[11px] bg-white p-2.5 border border-hairline rounded shadow-inner select-text">
                    {{ gradingResult.explanation }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Bottom Footer buttons -->
          <div class="border-t border-hairline pt-4 flex flex-col sm:flex-row gap-3 mt-6 select-none">
            <!-- Reveal solution key -->
            <button v-if="gradingResult === null" @click="showSolution = !showSolution"
                    class="btn-secondary px-4 py-2 text-xs font-semibold text-center flex-1 cursor-pointer flex items-center justify-center gap-1.5">
              <span v-html="getFaIcon(faKey)" class="w-3.5 h-3.5 text-ink-secondary flex items-center"></span>
              <span>{{ showSolution ? 'Hide Solution' : 'Reveal Solution' }}</span>
            </button>
            
            <!-- AI Hint -->
            <button @click="showHint = !showHint"
                    class="btn-secondary px-4 py-2 text-xs font-semibold text-center flex-1 cursor-pointer flex items-center justify-center gap-1.5">
              <span v-html="getFaIcon(faLightbulb)" class="w-3.5 h-3.5 text-ink-secondary flex items-center"></span>
              <span>{{ showHint ? 'Hide Tutor Hint' : 'AI Tutor Hint' }}</span>
            </button>

            <!-- Submit Check -->
            <button @click="submitAttempt"
                    :disabled="isSubmittingAttempt || !userAnswer || (Array.isArray(userAnswer) && userAnswer.length === 0)"
                    class="btn-primary px-6 py-2 text-xs font-semibold flex items-center justify-center gap-2 flex-1 disabled:opacity-50 cursor-pointer">
              <span v-if="isSubmittingAttempt" class="animate-spin rounded-full h-3.5 w-3.5 border-2 border-white border-t-transparent"></span>
              <span v-else v-html="getFaIcon(faRocket)" class="w-3.5 h-3.5 text-white flex items-center"></span>
              <span>{{ gradingResult ? 'Re-Submit Check' : 'Submit Answer' }}</span>
            </button>
          </div>

        </div>

      </div>

    </div>

  </div>
</template>

<style scoped>
.backdrop-blur-xxs {
  backdrop-filter: blur(1px);
}
</style>
