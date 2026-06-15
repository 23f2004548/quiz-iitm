<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useQuizStore } from '~/stores/quiz'
import { useRouter, useRoute } from 'vue-router'

const quizStore = useQuizStore()
const router = useRouter()
const route = useRoute()

onMounted(() => {
  const subject = route.query.subject as string
  const topic = route.query.topic as string || ''
  const difficulty = route.query.difficulty as string || ''
  const limit = parseInt(route.query.limit as string) || 5
  const week = route.query.week as string || ''
  const type = route.query.type as string || ''

  if (subject) {
    quizStore.startNewQuiz(subject, topic, difficulty, limit, week, type)
  }
})

const selectedOption = ref('')
const selectedOptions = ref<string[]>([])
const natAnswer = ref('')
const commandAnswer = ref('')

const hasChecked = ref(false)
const isCorrectLocal = ref(false)
const localFeedback = ref('')

const progressPercent = computed(() => {
  if (quizStore.activeQuiz.length === 0) return 0
  return (quizStore.currentQuestionIndex / quizStore.activeQuiz.length) * 100
})

const currentQuestion = computed(() => quizStore.currentQuestion)

watch(() => quizStore.currentQuestionIndex, () => {
  selectedOption.value = ''
  selectedOptions.value = []
  natAnswer.value = ''
  commandAnswer.value = ''
  hasChecked.value = false
  isCorrectLocal.value = false
  localFeedback.value = ''
})

function selectOption(optText: string) {
  if (hasChecked.value) return
  selectedOption.value = optText
}

function toggleOption(optText: string) {
  if (hasChecked.value) return
  const idx = selectedOptions.value.indexOf(optText)
  if (idx > -1) {
    selectedOptions.value.splice(idx, 1)
  } else {
    selectedOptions.value.push(optText)
  }
}

function handleCheck() {
  if (hasChecked.value) return
  if (!currentQuestion.value) return

  const qId = currentQuestion.value.id
  let ansVal = ''
  if (currentQuestion.value.type === 'MCQ') ansVal = selectedOption.value
  else if (currentQuestion.value.type === 'MSQ') ansVal = selectedOptions.value.join('||')
  else if (currentQuestion.value.type === 'NAT') ansVal = natAnswer.value
  else if (currentQuestion.value.type === 'COMMAND') ansVal = commandAnswer.value

  if (!ansVal) return

  quizStore.saveAnswer(qId, ansVal)
  
  if (quizStore.isLastQuestion) {
    handleSubmitQuiz()
  } else {
    quizStore.nextQuestion()
  }
}

async function handleSubmitQuiz() {
  const res = await quizStore.submitQuiz()
  if (res?.success) {
    if (process.client) {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }
}

function handleQuit() {
  quizStore.resetQuiz()
  router.push('/')
}

function handleTerminalCommandRun(cmd: string, output: string) {
  commandAnswer.value = cmd
}
</script>

<template>
  <ClientOnly>
    <div class="min-h-[calc(100vh-3.5rem)] flex flex-col bg-canvas-soft">
      <!-- Loading State -->
      <div v-if="quizStore.isLoading" class="flex-1 flex flex-col items-center justify-center p-8 text-center max-w-md mx-auto">
        <div class="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent mb-4"></div>
        <h2 class="text-xl font-bold text-ink mb-1">Generating Quiz...</h2>
        <p class="text-sm text-ink-muted leading-relaxed">Selecting the best interactive challenges for your learning path.</p>
      </div>

      <!-- Error State -->
      <div v-else-if="quizStore.error" class="flex-1 flex flex-col items-center justify-center p-8 text-center max-w-md mx-auto">
        <span class="text-5xl mb-4">⚠️</span>
        <h2 class="text-xl font-bold text-ink mb-2">Failed to Start Quiz</h2>
        <p class="text-sm text-red-600 bg-red-50 border border-red-200/50 p-4 rounded-lg leading-relaxed mb-6 font-mono text-xs w-full max-w-sm overflow-auto max-h-32">
          {{ quizStore.error }}
        </p>
        <div class="flex gap-3">
          <button @click="router.push('/')" class="btn-primary bg-white text-ink border border-hairline hover:bg-canvas-soft">
            Back to Dashboard
          </button>
          <button @click="quizStore.startNewQuiz(quizStore.activeSubject, quizStore.activeTopic)" class="btn-primary">
            Try Again
          </button>
        </div>
      </div>

      <!-- Active Quiz State -->
      <div v-else-if="quizStore.activeQuiz.length > 0 && !quizStore.quizResult" class="flex-1 flex flex-col">
        <div class="bg-surface border-b border-hairline px-6 py-4 flex items-center justify-between gap-6">
          <button @click="handleQuit" class="text-ink-muted hover:text-ink text-sm font-semibold flex items-center gap-1">
            <span>✕</span> Quit
          </button>
          
          <div class="flex-1 max-w-2xl bg-canvas-soft h-3.5 rounded-full overflow-hidden border border-hairline relative shadow-inner">
            <div class="bg-gradient-to-r from-sticker-green to-emerald-400 bg-[length:200%_auto] h-full transition-all duration-500 ease-out shadow-[0_0_6px_rgba(26,174,57,0.3)] animate-shimmer" :style="{ width: `${progressPercent}%` }"></div>
          </div>
          
          <span class="text-xs font-bold text-ink-muted">
            {{ quizStore.currentQuestionIndex + 1 }} / {{ quizStore.activeQuiz.length }}
          </span>
        </div>

        <div class="flex-1 max-w-6xl w-full mx-auto px-6 py-8 flex flex-col justify-between">
          <div class="grid grid-cols-1" :class="currentQuestion?.type === 'COMMAND' ? 'lg:grid-cols-2 gap-8' : ''">
            
            <div class="space-y-6">
              <div class="bg-surface border border-hairline rounded-xl p-6 shadow-sm">
                <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xxs font-bold uppercase tracking-wider mb-3"
                      :class="currentQuestion?.difficulty === 'Easy' ? 'bg-sticker-green/10 text-sticker-green' : currentQuestion?.difficulty === 'Medium' ? 'bg-sticker-sky/10 text-primary' : 'bg-sticker-orange/10 text-sticker-orange-deep'">
                  {{ currentQuestion?.difficulty }} • {{ currentQuestion?.topic }}
                </span>
                
                <h2 class="text-lg font-bold text-ink whitespace-pre-wrap leading-relaxed">
                  {{ currentQuestion?.prompt }}
                </h2>
              </div>

              <div v-if="currentQuestion?.type === 'MCQ'" class="space-y-3">
                <button v-for="opt in currentQuestion.options" :key="opt.id"
                        @click="selectOption(opt.option_text)"
                        class="w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between"
                        :class="selectedOption === opt.option_text ? 'bg-primary/5 border-primary font-semibold text-primary shadow-sm' : 'bg-surface border-hairline text-ink-secondary hover:bg-canvas-soft/30'">
                  <span>{{ opt.option_text }}</span>
                  <span class="w-5 h-5 rounded-full border flex items-center justify-center text-xs"
                        :class="selectedOption === opt.option_text ? 'bg-primary border-primary text-white' : 'border-hairline bg-canvas-soft'">
                    <span v-if="selectedOption === opt.option_text">✓</span>
                  </span>
                </button>
              </div>

              <div v-else-if="currentQuestion?.type === 'MSQ'" class="space-y-3">
                <p class="text-xxs font-bold text-ink-muted uppercase tracking-wider mb-2">Select all correct options:</p>
                <button v-for="opt in currentQuestion.options" :key="opt.id"
                        @click="toggleOption(opt.option_text)"
                        class="w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between"
                        :class="selectedOptions.includes(opt.option_text) ? 'bg-primary/5 border-primary font-semibold text-primary shadow-sm' : 'bg-surface border-hairline text-ink-secondary hover:bg-canvas-soft/30'">
                  <span>{{ opt.option_text }}</span>
                  <span class="w-5 h-5 rounded border flex items-center justify-center text-xs"
                        :class="selectedOptions.includes(opt.option_text) ? 'bg-primary border-primary text-white' : 'border-hairline bg-canvas-soft'">
                    <span v-if="selectedOptions.includes(opt.option_text)">✓</span>
                  </span>
                </button>
              </div>

              <div v-else-if="currentQuestion?.type === 'NAT'" class="bg-surface border border-hairline rounded-xl p-6 shadow-sm">
                <label for="nat-input" class="block text-xs font-semibold uppercase tracking-wider text-ink-muted mb-2">Numerical Answer</label>
                <input id="nat-input" v-model="natAnswer" type="text"
                       class="block w-40 border border-hairline bg-surface text-ink rounded-xs px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                       placeholder="Type a number" />
              </div>

              <div v-else-if="currentQuestion?.type === 'COMMAND'" class="bg-surface border border-hairline rounded-xl p-6 shadow-sm">
                <label for="cmd-input" class="block text-xs font-semibold uppercase tracking-wider text-ink-muted mb-2">Proposed Command Answer</label>
                <input id="cmd-input" v-model="commandAnswer" type="text"
                       class="block w-full border border-hairline bg-surface text-ink rounded-xs px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                       placeholder="e.g. ls -la" />
                <p class="text-xxs text-ink-muted mt-2">Use the Virtual Sandbox on the right to test your command output first. The last run command is copied here automatically.</p>
              </div>
            </div>

            <div v-if="currentQuestion?.type === 'COMMAND'" class="h-[450px] lg:h-auto min-h-[300px]">
              <VirtualTerminal @commandRun="handleTerminalCommandRun" />
            </div>

          </div>

          <div class="mt-8 flex items-center justify-end gap-3 border-t border-hairline pt-6">
            <button @click="handleCheck" 
                    :disabled="(currentQuestion?.type === 'MCQ' && !selectedOption) || (currentQuestion?.type === 'MSQ' && selectedOptions.length === 0) || (currentQuestion?.type === 'NAT' && !natAnswer) || (currentQuestion?.type === 'COMMAND' && !commandAnswer)"
                    class="btn-primary flex items-center gap-1.5 disabled:opacity-50">
              <span>{{ quizStore.isLastQuestion ? 'Submit Quiz' : 'Next Question' }}</span>
              <span>➔</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Quiz Result State -->
      <div v-else-if="quizStore.quizResult" class="max-w-4xl mx-auto px-6 py-8 w-full">
        <div class="bg-surface rounded-xl border border-hairline p-8 shadow-notion-soft mb-8 text-center">
          <span class="text-5xl">🏆</span>
          <h1 class="text-3xl font-bold tracking-tight text-ink mt-4 mb-2">Quiz Completed!</h1>
          <p class="text-ink-muted text-sm max-w-md mx-auto">Great job completing the review session! Your performance logs have been saved to your learning path.</p>

          <div class="grid grid-cols-3 gap-4 my-8 max-w-lg mx-auto">
            <div class="p-4 bg-canvas-soft rounded-lg border border-hairline">
              <div class="text-2xl font-bold text-ink">{{ quizStore.quizResult.score }} / {{ quizStore.quizResult.total }}</div>
              <div class="text-xxs font-semibold uppercase tracking-wider text-ink-muted mt-1">Accuracy</div>
            </div>
            <div class="p-4 bg-canvas-soft rounded-lg border border-hairline">
              <div class="text-2xl font-bold text-sticker-sky">⚡ +{{ quizStore.quizResult.xp_gained }}</div>
              <div class="text-xxs font-semibold uppercase tracking-wider text-ink-muted mt-1">XP Gained</div>
            </div>
            <div class="p-4 bg-canvas-soft rounded-lg border border-hairline">
              <div class="text-2xl font-bold text-sticker-orange">🔥 {{ quizStore.quizResult.new_streak }}</div>
              <div class="text-xxs font-semibold uppercase tracking-wider text-ink-muted mt-1">Streak Day</div>
            </div>
          </div>

          <button @click="handleQuit" class="btn-primary inline-flex items-center gap-2">
            <span>📁</span> Back to Dashboard
          </button>
        </div>

        <h3 class="text-lg font-bold text-ink mb-4 flex items-center gap-2">
          <span>🔍</span> Review Question Details
        </h3>

        <div class="space-y-4">
          <div v-for="(detail, idx) in quizStore.quizResult.details" :key="idx"
               class="bg-surface border rounded-xl p-6 shadow-sm"
               :class="detail.is_correct ? 'border-sticker-green/40' : 'border-red-200'">
            
            <div class="flex items-start justify-between gap-4">
              <div>
                <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xxs font-bold uppercase tracking-wider mb-3"
                      :class="detail.is_correct ? 'bg-sticker-green/10 text-sticker-green' : 'bg-red-50 text-red-600'">
                  {{ detail.is_correct ? 'Correct' : 'Incorrect' }}
                </span>
                <h4 class="text-base font-bold text-ink whitespace-pre-wrap">{{ detail.prompt }}</h4>
              </div>
              <span class="text-2xl">{{ detail.is_correct ? '✅' : '❌' }}</span>
            </div>

            <div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs bg-canvas-soft/40 p-4 rounded-lg border border-hairline">
              <div>
                <span class="font-semibold text-ink-muted block mb-1">Your Answer:</span>
                <span class="font-mono text-sm" :class="detail.is_correct ? 'text-sticker-green font-semibold' : 'text-red-600 font-semibold'">
                  {{ detail.user_answer ? detail.user_answer.split('||').join(', ') : '(Empty)' }}
                </span>
              </div>
              <div>
                <span class="font-semibold text-ink-muted block mb-1">Correct Answer:</span>
                <span class="font-mono text-sm text-ink font-semibold">
                  {{ detail.correct_answer ? detail.correct_answer.split('||').join(', ') : '' }}
                </span>
              </div>
            </div>

            <div class="mt-4 border-t border-hairline pt-4">
              <h5 class="text-xs font-semibold uppercase tracking-wider text-primary mb-1.5 flex items-center gap-1">
                <span>🤖</span> AI Tutor Explanation:
              </h5>
              <p class="text-xs text-ink-secondary leading-relaxed bg-primary/5 p-3 rounded border border-primary/10">
                {{ detail.explanation }}
              </p>
            </div>

          </div>
        </div>
      </div>

      <!-- Fallback / Empty State -->
      <div v-else class="flex-1 flex flex-col items-center justify-center p-8 text-center max-w-md mx-auto">
        <span class="text-5xl">📭</span>
        <h2 class="text-2xl font-bold text-ink mt-4 mb-2">No Active Quiz</h2>
        <p class="text-ink-muted text-sm mb-6">You haven't selected a learning topic yet. Return to the dashboard to choose a subject module.</p>
        <button @click="router.push('/')" class="btn-primary">
          Go to Dashboard
        </button>
      </div>
    </div>
  </ClientOnly>
</template>
