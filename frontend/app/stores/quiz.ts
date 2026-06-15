import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useAuthStore } from './auth'

export const useQuizStore = defineStore('quiz', () => {
  const authStore = useAuthStore()
  
  const activeQuiz = ref<any[]>([])
  const currentQuestionIndex = ref(0)
  const answers = ref<Record<number, string>>({})
  const quizResult = ref<any>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  const activeSubject = ref('')
  const activeTopic = ref('')
  
  const currentQuestion = computed(() => {
    if (activeQuiz.value.length === 0) return null
    return activeQuiz.value[currentQuestionIndex.value]
  })

  const isLastQuestion = computed(() => {
    return currentQuestionIndex.value === activeQuiz.value.length - 1
  })

  async function startNewQuiz(subject: string, topic: string, difficulty: string = '', limit: number = 5, week: string = '', type: string = '') {
    isLoading.value = true
    error.value = null
    quizResult.value = null
    answers.value = {}
    currentQuestionIndex.value = 0
    activeSubject.value = subject
    activeTopic.value = topic

    try {
      const response = await authStore.api.get('/api/quizzes/generate', {
        params: { subject, topic, difficulty, limit, week, type }
      })
      activeQuiz.value = response.data.questions
    } catch (err: any) {
      console.error('Quiz generation error:', err)
      error.value = err.response?.data?.error || err.message || 'Failed to generate quiz'
      activeQuiz.value = []
    } finally {
      isLoading.value = false
    }
  }

  function saveAnswer(questionId: number, answer: string) {
    answers.value[questionId] = answer
  }

  async function submitQuiz() {
    if (activeQuiz.value.length === 0) return
    isLoading.value = true
    error.value = null
    
    try {
      const response = await authStore.api.post('/api/quizzes/submit', {
        answers: answers.value
      })
      quizResult.value = response.data
      
      // Update user state (XP, Level, Streaks) in auth store
      if (authStore.user) {
        authStore.user.xp = response.data.new_xp
        authStore.user.level = response.data.new_level
        authStore.user.streak = response.data.new_streak
      }
      return { success: true, result: response.data }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to submit quiz answers'
      return { success: false }
    } finally {
      isLoading.value = false
    }
  }

  function nextQuestion() {
    if (currentQuestionIndex.value < activeQuiz.value.length - 1) {
      currentQuestionIndex.value++
    }
  }

  function prevQuestion() {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--
    }
  }

  function resetQuiz() {
    activeQuiz.value = []
    currentQuestionIndex.value = 0
    answers.value = {}
    quizResult.value = null
    error.value = null
  }

  return {
    activeQuiz,
    currentQuestionIndex,
    answers,
    quizResult,
    isLoading,
    error,
    activeSubject,
    activeTopic,
    currentQuestion,
    isLastQuestion,
    startNewQuiz,
    saveAnswer,
    submitQuiz,
    nextQuestion,
    prevQuestion,
    resetQuiz
  }
})
