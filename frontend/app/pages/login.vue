<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { useRouter } from 'vue-router'

definePageMeta({
  layout: false
})

const authStore = useAuthStore()
const router = useRouter()

const isLoginMode = ref(true)
const username = ref('')
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

onMounted(() => {
  if (authStore.isLoggedIn) {
    router.push('/')
  }
})

async function handleSubmit() {
  if (!email.value || !password.value || (!isLoginMode.value && !username.value)) {
    errorMessage.value = 'Please fill out all required fields.'
    return
  }
  
  errorMessage.value = ''
  isSubmitting.value = true
  
  let result
  if (isLoginMode.value) {
    result = await authStore.login(email.value, password.value)
  } else {
    result = await authStore.register(username.value, email.value, password.value)
  }
  
  isSubmitting.value = false
  
  if (result.success) {
    router.push('/')
  } else {
    errorMessage.value = result.error || 'An error occurred. Please try again.'
  }
}

function toggleMode() {
  isLoginMode.value = !isLoginMode.value
  errorMessage.value = ''
  username.value = ''
  email.value = ''
  password.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-canvas-soft flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center">
      <span class="w-12 h-12 rounded-xl bg-primary text-white flex items-center justify-center text-xl font-mono shadow-md mb-4">$_</span>
      <h2 class="text-center text-3xl font-bold tracking-tight text-ink">
        {{ isLoginMode ? 'Sign in to LinuxMaster' : 'Create your account' }}
      </h2>
      <p class="mt-2 text-center text-sm text-ink-muted">
        Learn Linux commands & IITM degree courses interactively
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
      <div class="bg-surface py-8 px-6 border border-hairline rounded-xl shadow-notion-soft">
        <form class="space-y-5" @submit.prevent="handleSubmit">
          <div v-if="!isLoginMode">
            <label for="username" class="block text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1.5">Username</label>
            <input id="username" v-model="username" type="text" required 
                   class="block w-full border border-hairline bg-surface text-ink rounded-xs px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                   placeholder="e.g. linux_wizard" />
          </div>

          <div>
            <label for="email" class="block text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1.5">Email Address</label>
            <input id="email" v-model="email" type="email" required 
                   class="block w-full border border-hairline bg-surface text-ink rounded-xs px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                   placeholder="you@iitm.ac.in" />
          </div>

          <div>
            <label for="password" class="block text-xs font-semibold uppercase tracking-wider text-ink-muted mb-1.5">Password</label>
            <input id="password" v-model="password" type="password" required 
                   class="block w-full border border-hairline bg-surface text-ink rounded-xs px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary shadow-sm"
                   placeholder="••••••••" />
          </div>

          <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 text-xs rounded-md p-3 flex items-start gap-2">
            <span>⚠️</span>
            <span>{{ errorMessage }}</span>
          </div>

          <div>
            <button type="submit" :disabled="isSubmitting" 
                    class="w-full flex justify-center py-2 px-4 border border-transparent rounded-full shadow-sm text-sm font-semibold text-white bg-primary hover:bg-primary-active focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 transition-all">
              <span v-if="isSubmitting" class="flex items-center gap-1.5">
                <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
              <span v-else>{{ isLoginMode ? 'Log In' : 'Sign Up' }}</span>
            </button>
          </div>
        </form>

        <div class="mt-6 text-center border-t border-hairline pt-5">
          <button @click="toggleMode" class="text-sm font-medium text-primary hover:underline focus:outline-none">
            {{ isLoginMode ? "Don't have an account? Create one" : 'Already have an account? Sign in' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
