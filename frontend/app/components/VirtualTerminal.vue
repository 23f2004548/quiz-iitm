<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useVirtualTerminal } from '~/composables/useVirtualTerminal'

const props = defineProps<{
  initialCommand?: string
}>()

const emit = defineEmits<{
  (e: 'commandRun', cmd: string, output: string): void
}>()

const terminal = useVirtualTerminal()
const currentInput = ref('')
const commandHistory = ref<string[]>([])
const historyIndex = ref(-1)
const terminalBodyRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  focusTerminal()
  if (props.initialCommand) {
    currentInput.value = props.initialCommand
  }
})

function focusTerminal() {
  inputRef.value?.focus()
}

function handleEnter() {
  const cmd = currentInput.value.trim()
  if (!cmd) return

  commandHistory.value.push(cmd)
  historyIndex.value = commandHistory.value.length

  const output = terminal.executeCommand(cmd)
  currentInput.value = ''
  
  emit('commandRun', cmd, output)

  nextTick(() => {
    if (terminalBodyRef.value) {
      terminalBodyRef.value.scrollTop = terminalBodyRef.value.scrollHeight
    }
  })
}

function handleKeyUp() {
  if (commandHistory.value.length === 0) return
  if (historyIndex.value > 0) {
    historyIndex.value--
    currentInput.value = commandHistory.value[historyIndex.value]
  }
}

function handleKeyDown() {
  if (commandHistory.value.length === 0) return
  if (historyIndex.value < commandHistory.value.length - 1) {
    historyIndex.value++
    currentInput.value = commandHistory.value[historyIndex.value]
  } else {
    historyIndex.value = commandHistory.value.length
    currentInput.value = ''
  }
}

function handleReset() {
  terminal.resetFs()
  focusTerminal()
}
</script>

<template>
  <div class="flex flex-col h-full bg-neutral-950 text-neutral-200 font-mono text-sm rounded-lg border border-neutral-800 shadow-lg overflow-hidden" @click="focusTerminal">
    <!-- Title Bar -->
    <div class="bg-neutral-900 border-b border-neutral-800 px-4 py-2 flex items-center justify-between">
      <div class="flex items-center gap-1.5">
        <span class="w-3 h-3 rounded-full bg-red-500"></span>
        <span class="w-3 h-3 rounded-full bg-yellow-500"></span>
        <span class="w-3 h-3 rounded-full bg-green-500"></span>
        <span class="text-xs text-neutral-400 ml-2 font-medium">Virtual Terminal Sandbox</span>
      </div>
      <button @click.stop="handleReset" class="text-xxs bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 px-2 py-0.5 rounded transition-all">
        🔄 Reset FS
      </button>
    </div>

    <!-- Output Body -->
    <div ref="terminalBodyRef" class="flex-1 p-4 overflow-y-auto space-y-2 select-text">
      <div class="text-neutral-500 text-xs">
        LinuxMaster Virtual Shell v1.0.0
        Type 'help' to see list of commands. Filesystem changes are stored in-memory.
      </div>
      
      <!-- Executed History -->
      <div v-for="(line, idx) in terminal.history.value" :key="idx">
        <div class="flex items-center gap-1.5 text-neutral-400">
          <span class="text-emerald-500 font-bold">learner@linux:~{{ terminal.currentDir.value }}#</span>
          <span>{{ line.command }}</span>
        </div>
        <div class="whitespace-pre-wrap mt-0.5 leading-relaxed" :class="line.error ? 'text-red-400' : 'text-neutral-300'">
          {{ line.output }}
        </div>
      </div>

      <!-- Active Input Line -->
      <div class="flex items-center gap-1.5">
        <span class="text-emerald-500 font-bold flex-shrink-0">learner@linux:~{{ terminal.currentDir.value }}#</span>
        <input ref="inputRef" v-model="currentInput" type="text"
               class="flex-1 bg-transparent border-none outline-none focus:ring-0 p-0 m-0 text-neutral-200 font-mono caret-primary text-sm"
               @keydown.enter="handleEnter"
               @keydown.up.prevent="handleKeyUp"
               @keydown.down.prevent="handleKeyDown"
               autofocus
               autocomplete="off"
               autocorrect="off"
               autocapitalize="off"
               spellcheck="false" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-xxs {
  font-size: 0.65rem;
}
</style>
