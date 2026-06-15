<script setup lang="ts">
import { ref, computed } from 'vue'
import { icon } from '@fortawesome/fontawesome-svg-core'
import {
  faBookOpen, faTerminal, faDatabase, faRobot, faLaptopCode,
  faArrowLeft, faPrint, faCopy, faCheck, faComment,
  faPaperPlane, faBookmark, faShareNodes, faSearch,
  faUser, faStar, faClock, faCalendarDays, faChevronRight,
  faInfoCircle, faChevronDown, faChevronLeft
} from '@fortawesome/free-solid-svg-icons'
import { faGithub, faPython } from '@fortawesome/free-brands-svg-icons'
import { marked } from 'marked'

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true
})

// ── Markdown Parser Helper ────────────────────────────────────────
function renderMarkdown(md: string): string {
  if (!md) return ''
  return marked.parse(md) as string
}

// ── Icons Helper ──────────────────────────────────────────────────
function getFaIcon(iconDef: any) {
  return icon(iconDef).html[0]
}

// ── State variables ───────────────────────────────────────────────
const activeSubject = ref<any | null>(null)
const activeChapterIndex = ref(0)
const searchQuery = ref('')
const selectedCategory = ref('All')
const sortBy = ref('latest')
const showBookmarkedOnly = ref(false)

// Drag resizing state
const leftSidebarWidth = ref(256)
const rightSidebarWidth = ref(320)
const isResizingLeft = ref(false)
const isResizingRight = ref(false)

const showTutorTab = ref(true)

// Dummy User Info (Matches the app theme)
const usersList = [
  { name: 'Alice Johnson', role: 'Project Manager', initials: 'AJ', color: 'bg-sticker-purple text-sticker-purple-deep' },
  { name: 'David Lee', role: 'UX/UI Designer', initials: 'DL', color: 'bg-sticker-sky text-primary-active' },
  { name: 'Emily Chen', role: 'Frontend Developer', initials: 'EC', color: 'bg-sticker-green text-ink-secondary' },
  { name: 'Mark Thompson', role: 'Content Lead', initials: 'MT', color: 'bg-sticker-orange text-sticker-orange-deep' }
]

// Custom Comments Feed State
const comments = ref<{ [key: string]: Array<{ author: string, initials: string, color: string, text: string, time: string, reactions?: { [key: string]: number } }> }>({
  'linux_1': [
    { author: 'Emily Chen', initials: 'EC', color: 'bg-sticker-green text-ink-secondary', text: 'This explanation of file descriptor 2 redirection is so clear! I used to always get confused between > and 2>.', time: '2 hours ago', reactions: { '👍': 4, '❤️': 2, '🎉': 0, '💡': 3 } },
    { author: 'Mark Thompson', initials: 'MT', color: 'bg-sticker-orange text-sticker-orange-deep', text: 'Added the diagram below to clarify how standard streams map to the kernel files table.', time: '1 day ago', reactions: { '👍': 2, '❤️': 0, '🎉': 1, '💡': 5 } }
  ],
  'linux_2': [
    { author: 'David Lee', initials: 'DL', color: 'bg-sticker-sky text-primary-active', text: 'Loved the visual redirect model here. Helps visualize the stream flows.', time: '3 hours ago', reactions: { '👍': 1, '❤️': 0, '🎉': 0, '💡': 2 } }
  ],
  'vue_0': [
    { author: 'Emily Chen', initials: 'EC', color: 'bg-sticker-green text-ink-secondary', text: 'This SFC template model is so neat. Having script, template, and style in one file makes styling component boundaries really straightforward.', time: '1 hour ago', reactions: { '👍': 5, '❤️': 3, '🎉': 2, '💡': 6 } },
    { author: 'David Lee', initials: 'DL', color: 'bg-sticker-sky text-primary-active', text: 'Love the comparison with vanilla JS! It shows how clean Vue code stays even as the app scales.', time: '5 hours ago', reactions: { '👍': 8, '❤️': 1, '🎉': 0, '💡': 4 } }
  ]
})

const newCommentText = ref('')
function submitComment(chapterId: string) {
  if (!newCommentText.value.trim()) return
  if (!comments.value[chapterId]) {
    comments.value[chapterId] = []
  }
  comments.value[chapterId].push({
    author: 'You (Learner)',
    initials: 'YO',
    color: 'bg-primary text-white',
    text: newCommentText.value.trim(),
    time: 'Just now',
    reactions: { '👍': 0, '❤️': 0, '🎉': 0, '💡': 0 }
  })
  newCommentText.value = ''
}

// User-specific comment reactions tracking (key: `${chapterId}_${commentIndex}_${emoji}`)
const userCommentReactions = ref<Set<string>>(new Set())

function toggleCommentReaction(chapterId: string, commentIdx: number, emoji: string) {
  const comment = comments.value[chapterId]?.[commentIdx]
  if (!comment) return
  
  if (!comment.reactions) {
    comment.reactions = { '👍': 0, '❤️': 0, '🎉': 0, '💡': 0 }
  }
  
  const reactionKey = `${chapterId}_${commentIdx}_${emoji}`
  if (userCommentReactions.value.has(reactionKey)) {
    userCommentReactions.value.delete(reactionKey)
    comment.reactions[emoji] = Math.max(0, comment.reactions[emoji] - 1)
  } else {
    userCommentReactions.value.add(reactionKey)
    comment.reactions[emoji] = (comment.reactions[emoji] || 0) + 1
  }
}

function hasCommentReaction(chapterId: string, commentIdx: number, emoji: string) {
  const reactionKey = `${chapterId}_${commentIdx}_${emoji}`
  return userCommentReactions.value.has(reactionKey)
}

// Note Sheet (Chapter) reactions state
const chapterReactions = ref<{ [key: string]: { [emoji: string]: number } }>({
  'linux_1': { '👍': 12, '💡': 8, '🎉': 5, '❤️': 3 },
  'linux_2': { '👍': 7, '💡': 14, '🎉': 2, '❤️': 4 },
  'vue_0': { '👍': 18, '💡': 22, '🎉': 9, '❤️': 11 },
})
const userChapterReactions = ref<{ [key: string]: Set<string> }>({})

function toggleChapterReaction(emoji: string) {
  if (!activeSubject.value) return
  const chId = activeSubject.value.chapters[activeChapterIndex.value].id
  
  if (!chapterReactions.value[chId]) {
    chapterReactions.value[chId] = { '👍': 0, '💡': 0, '🎉': 0, '❤️': 0 }
  }
  if (!userChapterReactions.value[chId]) {
    userChapterReactions.value[chId] = new Set()
  }
  
  if (userChapterReactions.value[chId].has(emoji)) {
    userChapterReactions.value[chId].delete(emoji)
    chapterReactions.value[chId][emoji] = Math.max(0, (chapterReactions.value[chId][emoji] || 1) - 1)
  } else {
    userChapterReactions.value[chId].add(emoji)
    chapterReactions.value[chId][emoji] = (chapterReactions.value[chId][emoji] || 0) + 1
  }
}

function hasChapterReaction(emoji: string) {
  if (!activeSubject.value) return false
  const chId = activeSubject.value.chapters[activeChapterIndex.value].id
  return userChapterReactions.value[chId]?.has(emoji) || false
}

function getChapterReactionCount(emoji: string) {
  if (!activeSubject.value) return 0
  const chId = activeSubject.value.chapters[activeChapterIndex.value].id
  return chapterReactions.value[chId]?.[emoji] || 0
}

// ── Syntax Highlighter Helper ────────────────────────────────────
function highlightCode(code: string, lang: string): string {
  if (!code) return ''
  
  // Escape HTML tags to prevent raw rendering
  let escaped = code
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  if (!lang) return escaped

  const l = lang.toLowerCase()
  
  if (l === 'javascript' || l === 'typescript' || l === 'vue' || l === 'html') {
    const regex = /(\/\/.*|\/\*[\s\S]*?\*\/)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)|(&lt;\/?[a-zA-Z0-9:-]+(?:\s+[^&]*?)?&gt;)|(\{\{[\s\S]*?\}\})|(\b(?:const|let|var|function|return|import|export|from|default|if|else|for|while|new|try|catch|class|extends|await|async)\b)/g
    return escaped.replace(regex, (match, comment, string, htmlTag, vueInterp, keyword) => {
      if (comment) return `<span class="text-ink-faint italic">${comment}</span>`
      if (string) return `<span class="text-sticker-green text-ink-secondary">${string}</span>`
      if (htmlTag) return `<span class="text-accent-pink">${htmlTag}</span>`
      if (vueInterp) return `<span class="text-accent-orange">${vueInterp}</span>`
      if (keyword) return `<span class="text-primary">${keyword}</span>`
      return match
    })
  } else if (l === 'bash' || l === 'shell') {
    const regex = /(#.*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b(?:echo|cat|find|grep|ls|sort|uniq|wc|cut|tr|file|mkdir|rmdir|touch|cp|mv|rm|pwd|cd|fg|jobs|export|unset|sudo)\b)|(&gt;{1,2}|2&gt;&amp;1|\|{1,2}|&amp;{1,2})/g
    return escaped.replace(regex, (match, comment, string, command, operator) => {
      if (comment) return `<span class="text-ink-faint italic">${comment}</span>`
      if (string) return `<span class="text-sticker-green text-ink-secondary">${string}</span>`
      if (command) return `<span class="text-primary">${command}</span>`
      if (operator) return `<span class="text-accent-orange">${operator}</span>`
      return match
    })
  } else if (l === 'python') {
    const regex = /(#.*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b(?:def|class|return|import|from|if|elif|else|for|while|in|is|not|and|or|try|except|as|with|lambda|pass)\b)/g
    return escaped.replace(regex, (match, comment, string, keyword) => {
      if (comment) return `<span class="text-ink-faint italic">${comment}</span>`
      if (string) return `<span class="text-sticker-green text-ink-secondary">${string}</span>`
      if (keyword) return `<span class="text-primary">${keyword}</span>`
      return match
    })
  } else if (l === 'sql') {
    const regex = /(--.*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|(\b(?:SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|ON|ORDER\s+BY|GROUP\s+BY|HAVING|LIMIT|DESC|ASC|AS|AND|OR|NOT|IN|LIKE|NULL|COUNT|SUM|AVG|MIN|MAX)\b)/gi
    return escaped.replace(regex, (match, comment, string, keyword) => {
      if (comment) return `<span class="text-ink-faint italic">${comment}</span>`
      if (string) return `<span class="text-sticker-green text-ink-secondary">${string}</span>`
      if (keyword) return `<span class="text-primary">${keyword}</span>`
      return match
    })
  }
  
  return escaped
}

// Resizing logic for Left Sidebar
function startResizeLeft(e: MouseEvent) {
  isResizingLeft.value = true
  const startX = e.clientX
  const startWidth = leftSidebarWidth.value

  const onMouseMove = (moveEvent: MouseEvent) => {
    const deltaX = moveEvent.clientX - startX
    const newWidth = startWidth + deltaX
    if (newWidth >= 160 && newWidth <= 400) {
      leftSidebarWidth.value = newWidth
    }
  }

  const onMouseUp = () => {
    isResizingLeft.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
}

// Resizing logic for Right Sidebar
function startResizeRight(e: MouseEvent) {
  isResizingRight.value = true
  const startX = e.clientX
  const startWidth = rightSidebarWidth.value

  const onMouseMove = (moveEvent: MouseEvent) => {
    const deltaX = moveEvent.clientX - startX
    const newWidth = startWidth - deltaX
    if (newWidth >= 240 && newWidth <= 500) {
      rightSidebarWidth.value = newWidth
    }
  }

  const onMouseUp = () => {
    isResizingRight.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
}

// Custom AI Tutor State
const aiMessages = ref<Array<{ sender: 'tutor' | 'user', text: string }>>([
  { sender: 'tutor', text: "Hello! I am your LinuxMaster AI Tutor. Select one of the quick questions below or ask anything about this section!" }
])
const aiInput = ref('')
const aiIsTyping = ref(false)

const quickQuestions = computed(() => {
  if (!activeSubject.value) return []
  const ch = activeSubject.value.chapters[activeChapterIndex.value]
  if (activeSubject.value.id === 'linux') {
    if (ch.id === 'linux_1') {
      return ['What happens if I redirect stdout to a file that does not exist?', 'Why is file descriptor 0 called stdin?', 'How do I run a command completely silently?']
    } else if (ch.id === 'linux_2') {
      return ['What is the difference between > and >>?', 'How does 2>&1 work?', 'Can I redirect output of one script to multiple files?']
    }
  } else if (activeSubject.value.id === 'vue') {
    if (ch.id === 'vue_0') {
      return ['Why is direct DOM manipulation slow?', 'How does Vue reactivity track variables?', 'Explain Virtual DOM in simple terms']
    } else if (ch.id === 'vue_1') {
      return ['What is the difference between Webpack and Vite?', 'What is the execution flow when Vue starts?', 'What is the difference between a component and a view?']
    } else if (ch.id === 'vue_2') {
      return ['What is the difference between imperative and declarative programming?', 'How does Vue compile templates under the hood?', 'What is the difference between an expression and a statement inside {{ }}?']
    } else if (ch.id === 'vue_3') {
      return ['What is the difference between {{ }} and :attribute binding?', 'How do you bind class dynamically based on variables?', 'How do you bind inline styles dynamically in Vue?']
    } else if (ch.id === 'vue_4') {
      return ['What is event bubbling and how do we stop it?', 'When should we use the .prevent modifier?', 'How do we pass both custom arguments and the event object?']
    } else if (ch.id === 'vue_5') {
      return ['Why do we need .value for refs in JS but not templates?', 'What is the difference between ref and reactive?', 'How does Vue track changes under the hood?']
    } else if (ch.id === 'vue_6') {
      return ['What is the difference between v-if and v-show?', 'When should we use v-if vs v-show?', 'What happens to the DOM when v-if is false?']
    } else if (ch.id === 'vue_7') {
      return ['Why does Vue require a unique key for list items?', 'Why is using array index as a key considered bad practice?', 'How do we filter or sort a list before rendering it with v-for?']
    } else if (ch.id === 'vue_8') {
      return ['Explain two-way data binding in simple terms', 'What is the difference between value binding and v-model?', 'How does v-model work on select/checkbox dropdowns?']
    } else if (ch.id === 'vue_9') {
      return ['Why are computed properties cached while functions are not?', 'Can computed properties be modified directly?', 'When should I use computed properties instead of watchers?']
    } else if (ch.id === 'vue_10') {
      return ['What is the difference between watch and watchEffect?', 'Why do we use a getter function to watch properties of reactive objects?', 'When is it appropriate to use immediate or deep options?']
    } else if (ch.id === 'vue_11') {
      return ['What is the difference between setup() and onMounted()?', 'Why is cleaning up timers and event listeners in onUnmounted() critical?', 'What is the correct execution order of parent and child components lifecycle?']
    } else if (ch.id === 'vue_12') {
      return ['What is a Component Tree in Vue applications?', 'What does style scoped do in a single file component?', 'When is it appropriate to extract code into a reusable component?']
    } else if (ch.id === 'vue_13') {
      return ['Why are props read-only inside child components?', 'What is the difference between static and dynamic props?', 'What is Prop Drilling and how do we prevent it?']
    } else if (ch.id === 'vue_14') {
      return ['What is the difference between props and emits?', 'How do we pass data along with an emit event?', 'Why should a child not modify the parent state directly?']
    } else if (ch.id === 'vue_15') {
      return ['What is the difference between props and slots?', 'How do we define and use named slots in Vue?', 'Explain scoped slots and their use cases in simple terms']
    } else if (ch.id === 'vue_16') {
      return ['What problem does Provide/Inject solve?', 'Why must we pass a ref/reactive to provide for reactivity?', 'What is the difference between Provide/Inject and Pinia?']
    } else if (ch.id === 'vue_17') {
      return ['What is the difference between dynamic components and Vue Router?', 'How does KeepAlive cache and restore component states?', 'What are onActivated and onDeactivated lifecycle hooks?']
    } else if (ch.id === 'vue_18') {
      return ['What problem does defineAsyncComponent solve?', 'What are loadingComponent and errorComponent options in async components?', 'What is the difference between KeepAlive and defineAsyncComponent?']
    } else if (ch.id === 'vue_19') {
      return ['What problem does Teleport solve?', 'Does Teleport break props, emits, or Provide/Inject?', 'When should we use Teleport vs z-index?']
    } else if (ch.id === 'vue_20') {
      return ['What is a Composable in Vue?', 'What is the naming convention for composables, and why?', 'What is the difference between local state and shared state in composables?']
    } else if (ch.id === 'vue_21') {
      return ['What is an SPA, and how does Vue Router support it?', 'What is the difference between RouterLink and standard HTML anchor tags?', 'Explain createWebHistory and history mode in Vue Router']
    } else if (ch.id === 'vue_22') {
      return ['Difference between useRoute() and useRouter()?', 'When should we use router.replace() instead of router.push()?', 'Why does Vue reuse components on parameter changes, and how do we react to it?']
    } else if (ch.id === 'vue_23') {
      return ['What is the difference between global guards and route guards?', 'Why does checking (!loggedIn) redirecting to login cause a loop?', 'Can navigation guards block backend API calls?']
    } else if (ch.id === 'vue_24') {
      return ['What problem does Pinia solve in scaling applications?', 'What is the difference between state, getters, and actions?', 'Why does destructuring a Pinia store directly break reactivity, and how do we fix it?']
    } else if (ch.id === 'vue_25') {
      return ['Difference between Option Stores and Setup Stores?', 'When should we use storeToRefs() vs normal destructuring?', 'What is Store Composition and when is it helpful?']
    } else if (ch.id === 'vue_26') {
      return ['How does JWT Authentication flow work in Vue apps?', 'Why is storing passwords in localStorage a bad practice?', 'What is the correct startup execution flow when initializing auth in main.js?']
    } else if (ch.id === 'vue_27') {
      return ['Why use a service layer instead of calling APIs from components?', 'Where should JWT token attachment and 401 error redirect handling happen?', 'Explain how Refresh Tokens work inside API interceptors']
    } else if (ch.id === 'vue_28') {
      return ['Why are computed properties preferred over methods in templates?', 'What is Virtual Scrolling and why does it improve performance?', 'Explain why :key="Math.random()" degrades list rendering performance']
    }
  }
  return [`Can you give me another example of ${ch.title}?`, 'Explain this section in simple terms.', 'What are the common errors or gotchas here?']
})

async function askAiTutor(question: string) {
  if (aiIsTyping.value) return
  aiMessages.value.push({ sender: 'user', text: question })
  aiIsTyping.value = true
  
  // Simulate AI Response delay
  setTimeout(() => {
    let reply = "That's a great question! "
    const subjId = activeSubject.value?.id
    const chId = activeSubject.value?.chapters[activeChapterIndex.value]?.id

    if (subjId === 'linux') {
      if (question.includes('difference between > and >>')) {
        reply += "In Linux, the `>` operator redirects output and **overwrites** the contents of the target file. On the other hand, the `>>` operator redirects output and **appends** the data to the end of the file, preserving its existing contents. For example, `echo 'hello' > file.txt` erases whatever was there and writes 'hello', while `echo 'world' >> file.txt` adds 'world' on a new line at the bottom."
      } else if (question.includes('2>&1')) {
        reply += "The syntax `2>&1` redirects File Descriptor 2 (stderr) to the same place File Descriptor 1 (stdout) is currently pointed. In shell operations, order matters: `command > file.log 2>&1` first redirects stdout to `file.log`, then redirects stderr to stdout (which is already pointed at `file.log`), effectively capturing all output in that single file."
      } else if (question.includes('not exist')) {
        reply += "If you redirect output to a file that does not exist (e.g. `command > newfile.txt`), the shell will automatically create the file for you. If the directory paths in the filename do not exist, however, the shell will return a 'No such file or directory' error."
      } else if (question.includes('completely silently')) {
        reply += "To run a command completely silently in Linux, you should redirect both stdout and stderr to the special null device `/dev/null`. You can do this with: `command > /dev/null 2>&1` or the modern shorthand `command &> /dev/null`."
      } else {
        reply += `Regarding this section on **${activeSubject.value.chapters[activeChapterIndex.value].title}**: Always keep in mind that Linux treats everything as a file, including your keyboard input (stdin) and terminal display (stdout). Mastering these stream interactions is key to automation scripting.`
      }
    } else if (subjId === 'vue') {
      if (question.includes('direct DOM manipulation')) {
        reply += "Direct DOM manipulation is slow because every change triggers a browser style recalculation, layout (reflow), and repaint of the page. Vue uses a Virtual DOM to batch updates and apply only the minimum necessary changes, which is much faster."
      } else if (question.includes('reactivity track')) {
        reply += "Vue 3 uses JavaScript **Proxies** to intercept access and modification of state variables. When a component reads a reactive variable (like a `ref`), Vue records it as a dependency. When the variable is modified, Vue triggers the associated render effect to update the UI."
      } else if (question.includes('Virtual DOM')) {
        reply += "The Virtual DOM is a lightweight copy of the real DOM represented as JavaScript objects. Instead of modifying the screen directly, Vue compares (diffs) the new Virtual DOM tree against the old one, finds the differences, and updates only those specific parts of the real screen."
      } else if (question.includes('Webpack and Vite')) {
        reply += "Webpack is a traditional bundler that builds your entire application before starting the dev server, which makes it slow for large projects. Vite, on the other hand, starts immediately by serving files as native ES Modules on-demand, which means the browser compiles and loads only the files currently active on the page."
      } else if (question.includes('execution flow')) {
        reply += "When a Vue application starts, the browser first loads `index.html`. The index page requests `/src/main.js` via a module script tag. In `main.js`, `createApp(App)` creates the Vue runtime application instance using `App.vue` as the root component. Finally, `.mount('#app')` tells Vue to find the `<div id=\"app\"></div>` container in `index.html` and mount the rendered component tree there."
      } else if (question.includes('component and a view')) {
        reply += "In Vue development, **Components** are reusable, modular UI widgets (like a custom Button, Navbar, or Card). **Views** represent full pages or route destinations (like HomeView, AboutView, or ProfileView) that are loaded by the router and serve as containers organizing multiple child components."
      } else if (question.includes('imperative and declarative')) {
        reply += "Imperative programming is a style where you tell the browser step-by-step **HOW** to do something (e.g. `document.createElement('h1')`, `appendChild`). Declarative programming is where you describe **WHAT** you want the UI to look like (e.g. `<template><h1>Hello</h1></template>`), and Vue handles the DOM manipulation steps for you."
      } else if (question.includes('compile templates')) {
        reply += "Vue compiles HTML templates into optimized JavaScript **render functions** conceptualized as `h('h1', 'Hello')` (HyperScript). These render functions create Virtual DOM nodes (VNodes), which Vue compares (diffs) against the previous Virtual DOM tree to calculate and execute the minimum required patches to the real DOM."
      } else if (question.includes('expression and a statement')) {
        reply += "An **expression** evaluates to a value (like `5 + 5`, `user.name`, or `isOk ? 'yes' : 'no'`), which is allowed inside Vue double curly braces `{{ }}`. A **statement** performs an action or controls execution structure (like `if (x) { }` or `for (let i = 0; ...)`) and does not produce a value, which makes it invalid inside `{{ }}`."
      } else if (question.includes('curly braces and :attribute')) {
        reply += "Double curly braces `{{ }}` are used to insert dynamic text directly **inside HTML content** (between tags). Attribute binding `:attribute` (shorthand for `v-bind:attribute`) is used to bind dynamic variables **inside HTML attributes** (like `:src`, `:href`, `:class`, `:disabled`, etc.)."
      } else if (question.includes('class dynamically')) {
        reply += "You can bind classes dynamically in Vue using either: 1. **Object Syntax** (`:class=\"{ active: isActive }\"` where the class `active` is added only if `isActive` is truthy), or 2. **Array Syntax** (`:class=\"[btnClass, activeClass]\"` which lists multiple class variables), or 3. **Ternary Operators** (`:class=\"isLoggedIn ? 'success' : 'danger'\"`)."
      } else if (question.includes('styles dynamically')) {
        reply += "You can bind inline styles dynamically using `:style` and passing a JavaScript object, like `:style=\"{ color: textColor, fontSize: fontSizeValue }\"`. Note that style property names use camelCase (like `fontSize`) instead of CSS kebab-case (like `font-size`) because they are JavaScript object keys."
      } else if (question.includes('event bubbling')) {
        reply += "In HTML, events bubble up through parents. Vue provides the `.stop` modifier (e.g. `@click.stop`) to call `event.stopPropagation()` and prevent the event from triggering handlers on parent elements."
      } else if (question.includes('.prevent modifier')) {
        reply += "The `.prevent` modifier calls `event.preventDefault()` under the hood. It is most commonly used on forms (`@submit.prevent=\"save\"`) to prevent the default browser submission behavior, which would otherwise refresh the page and destroy all local reactive state."
      } else if (question.includes('custom arguments and the event')) {
        reply += "To pass custom arguments and the original event object, Vue provides the special `$event` variable. For example: `@click=\"greet(\'Satyam\', $event)\"`. In the function, you receive it as a parameter: `function greet(name, event) { ... }`."
      } else if (question.includes('.value for refs')) {
        reply += "Refs are JavaScript objects wrapping the real value inside a `.value` property. In script blocks, you must access and modify `.value` because JavaScript variables cannot otherwise intercept property writes to track changes. In templates, Vue automatically unwraps them, allowing you to write `{{ count }}` instead of `{{ count.value }}`."
      } else if (question.includes('ref and reactive')) {
        reply += "`ref()` wraps any value (including primitives) in a ref object with a `.value` property. `reactive()` directly proxies objects or arrays without wrapping them, so you access properties directly without `.value`. However, `reactive()` cannot be used on primitives (like numbers/strings) and cannot be reassigned entirely without losing reactivity."
      } else if (question.includes('track changes under the hood')) {
        reply += "Vue 3 wraps reactive objects in a JavaScript **Proxy**. When a property is accessed during rendering, Vue's custom Proxy getter registers that component as a dependency. When the property is changed, the Proxy setter detects the update and notifies the dependent components to run their render functions."
      } else if (question.includes('v-if and v-show')) {
        reply += "`v-if` conditionally renders elements by completely creating or destroying the DOM nodes. If false, the element is absent. `v-show` always compiles and mounts the element to the DOM but toggles its visibility by adding the CSS rule `display: none`."
      } else if (question.includes('v-if vs v-show')) {
        reply += "Use `v-if` for sections that change rarely (like authentication blocks or pages), since it has lower initial rendering costs. Use `v-show` for frequently toggled components (like dropdowns, accordions, or modal dialogues), since toggling a CSS property is much cheaper than destroying and rebuilding DOM structures."
      } else if (question.includes('DOM when v-if is false')) {
        reply += "When `v-if` is false, Vue completely removes the element from the DOM tree, replacing it with a comment placeholder (e.g. `<!---->`). It does not exist on the page, meaning any lifecycle hooks are destroyed and style sheets/scripts cannot select it."
      } else if (question.includes('unique key for list items')) {
        reply += "Vue uses the `:key` attribute to identify elements uniquely in the Virtual DOM. During updates (diffing), if an item is reordered, added, or removed, the key tells Vue precisely which DOM element corresponds to which object in the array. This allows Vue to reuse existing DOM nodes, improving rendering performance and preserving temporary element states (like input values or focus)."
      } else if (question.includes('index as a key considered bad')) {
        reply += "Using the array index as a key (e.g. `:key=\"index\"`) is bad because indexes are not stable when items are inserted, deleted, or reordered. For example, if you insert an item at the beginning of an array, the new item gets index 0, and all existing items have their indexes incremented by 1. Vue thinks all elements have changed and re-creates/re-renders them all, defeating the purpose of Virtual DOM key tracking."
      } else if (question.includes('filter or sort a list')) {
        reply += "Instead of using `v-if` inside a `v-for` loop on the same tag, the recommended practice is to use a **computed property** to filter or sort your array. For example: `const adults = computed(() => users.value.filter(u => u.age >= 18))`. Then, you loop over `adults` in the template: `v-for=\"user in adults\" :key=\"user.id\"`. This is cleaner, safer, and much faster."
      } else if (question.includes('two-way data binding')) {
        reply += "Two-way data binding means that any changes to your JavaScript data (state) are automatically reflected in the template inputs (HTML), and vice versa. It links the form inputs on the page directly to the variables in memory so they stay in perfect sync without manual DOM selections or event handler code."
      } else if (question.includes('value binding and v-model')) {
        reply += "Value binding `:value=\"name\"` is **one-way**: changing the `name` variable updates the input element, but typing in the input does not update the variable. `v-model=\"name\"` is **two-way**: it automatically combines value binding and event listening (`:value=\"name\" @input=\"name = $event.target.value\"`) to synchronize changes both ways."
      } else if (question.includes('select/checkbox dropdowns')) {
        reply += "On checkboxes, `v-model` binds to a boolean value (`true`/`false`) if it is a single checkbox. If multiple checkboxes share the same `v-model`, it binds to an array containing the values of all checked boxes. On a select dropdown, `v-model` binds to a string representing the value of the currently selected option, matching options by their `value` attributes."
      } else if (question.includes('computed properties cached')) {
        reply += "Computed properties are cached based on their reactive dependencies. When a computed property is read, Vue records the reactive variables it depends on. If those dependencies don't change, subsequent accesses immediately return the cached result without executing the getter function again. A normal function, however, has no cache and must execute its entire code block on every component re-render."
      } else if (question.includes('modified directly')) {
        reply += "By default, computed properties are read-only, meaning if you try to assign a value directly (e.g. `fullName.value = 'Rahul'`), Vue will print a warning/error. However, you can create a writable computed property by defining both a `get()` and a `set(value)` handler inside the computed options. The `set` handler intercepts writes and updates the underlying source reactive state variables."
      } else if (question.includes('computed properties instead of watchers')) {
        reply += "Use computed properties when you are **calculating and deriving a new value** directly from existing reactive state (e.g. calculating a filtered list, a sum total, or a formatted string). Use watchers when you need to execute **side-effects** (e.g. making an asynchronous network request, syncing data to localStorage, or modifying the route) in response to a state change."
      } else if (question.includes('watch and watchEffect')) {
        reply += "`watch` is explicit: you must specify the exact data source(s) to monitor, and it provides both new and old values in the callback. It only runs when changes occur (unless `immediate: true` is configured). `watchEffect` is implicit: it automatically tracks any reactive variable accessed inside its callback and runs immediately on mount."
      } else if (question.includes('watch properties of reactive objects')) {
        reply += "When watching a reactive object property directly (e.g., `watch(user.name)`), you are passing a static string value instead of the reactive proxy reference. Wrapping it in a getter function (e.g., `watch(() => user.name)`) returns a function that Vue can invoke dynamically to evaluate and track changes over time."
      } else if (question.includes('immediate or deep options')) {
        reply += "Use `immediate: true` when you need the watcher callback to execute immediately upon mounting (e.g., loading user profile data on load based on a `userId` prop). Use `deep: true` when you need to watch nested properties inside a complex object or array, since Vue normally only monitors top-level object assignment references."
      } else if (question.includes('setup() and onMounted()')) {
        reply += "`setup()` runs during component creation, before any HTML templates are compiled or elements are attached to the page. It is meant for state declaration only. `onMounted()` runs after the template is compiled and inserted into the real DOM, meaning you can safely query DOM elements and trigger async requests."
      } else if (question.includes('cleaning up timers')) {
        reply += "If you register persistent browser listeners like `window.addEventListener('resize')` or background tasks like `setInterval` inside a component, the browser keeps them in memory. When the component is destroyed (unmounted), those tasks remain active, causing memory leaks and executing stale handlers. Always release them using `clearInterval` and `removeEventListener` in `onUnmounted()`."
      } else if (question.includes('parent and child components')) {
        reply += "When mounting a component tree, Vue starts setup from parent to child, but finishes mounting from child to parent. The execution order is: Parent `setup()` ➔ Child `setup()` ➔ Child `onMounted()` ➔ Parent `onMounted()`. This ensures that a parent component is only marked as fully mounted once all of its nested children are fully loaded and rendered."
      } else if (question.includes('Component Tree in Vue')) {
        reply += "A Component Tree represents the hierarchical relationship between components in a Vue app. The root component (typically `App.vue`) sits at the top, rendering layout containers (like `Navbar`), which in turn render page view components, which render individual reusable units (like `UserCard`). This nested structure allows developers to easily trace data flow and component interactions."
      } else if (question.includes('style scoped do')) {
        reply += "The `scoped` attribute on a `<style>` block instructs Vue's compiler to generate unique data attributes (e.g. `data-v-51e023bd`) for that component's elements. Vue appends these attributes to the CSS rules so they only select elements within that specific component, preventing styling rules from bleeding out and accidentally modifying elements in parent or child components."
      } else if (question.includes('extract code into reusable')) {
        reply += "As a general rule of thumb, you should extract code into a component when: 1. You find yourself copy-pasting the exact same UI structure three or more times. 2. The code in a single file becomes too large (e.g. over 500 lines) and difficult to maintain. 3. The UI element represents a distinct, standalone piece of logic (like a calendar picker, modal popup, or graph panel)."
      } else if (question.includes('props read-only inside child')) {
        reply += "Props are read-only to enforce **one-way data flow**. If children could mutate props, data changes would propagate horizontally and vertically in unpredictable ways, making state management impossible to debug. The parent owns the data, and if the child needs to update it, it must communicate back to the parent using **Events** (which we will learn next)."
      } else if (question.includes('static and dynamic props')) {
        reply += "Static props are passed as plain string attributes (e.g., `name=\"Satyam\"`). They are evaluated literally as string literals. Dynamic props use the `:` bind syntax (e.g., `:age=\"21\"` or `:user=\"userVar\"`), directing Vue to compile the value as JavaScript, allowing variables, numbers, objects, and arrays to be passed."
      } else if (question.includes('Prop Drilling and how do prevent')) {
        reply += "Prop Drilling is passing props through components that don't need them, simply to reach a deeply nested child component. We prevent this in large apps by using **Pinia** (global state management) which lets any component access a centralized data store directly without intermediate prop passing, or using Vue's **Provide / Inject** API."
      } else if (question.includes('difference between props and emits')) {
        reply += "Props are used to pass data **downwards** from a parent component to a child component, while Emits are used to send event notifications **upwards** from a child component to its parent. Think of it as 'Props Down, Events Up' – a core design pattern in Vue that establishes a predictable data flow."
      } else if (question.includes('pass data along with an emit event')) {
        reply += "To pass data along with an emit, you pass the payload as additional arguments to the `emit()` function after the event name. For example, `emit('delete', 5)` or `emit('save', { id: 1, name: 'Satyam' })`. The parent listens via `@delete=\"removeTodo\"` and the argument is automatically passed to the handler function: `function removeTodo(id) { ... }`."
      } else if (question.includes('should a child not modify the parent state directly')) {
        reply += "A child component should not modify parent state directly to ensure components remain isolated and reusable. If children could mutate parent state directly, debugging data changes would become extremely difficult because state could be changed from anywhere. By emitting an event instead, the child simply *requests* a change, and the parent (which owns the state) retains full control over how and when to update it."
      } else if (question.includes('difference between props and slots')) {
        reply += "Props are used to pass data parameters down to a component, while Slots are used to pass entire UI content, templates, or HTML markup inside a component's template. Use props for pure data (like strings or objects) and slots for layout customization (like buttons with icons or rich cards)."
      } else if (question.includes('define and use named slots')) {
        reply += "To use named slots, define them in the child component with `\x3cslot name=\"header\" /\x3e`. In the parent component, wrap the content in a `\x3ctemplate\x3e` tag with the `#` symbol or `v-slot:` shorthand matching the slot name: `\x3ctemplate #header\x3eTitle Content\x3c/template\x3e`. Any content not wrapped in a named template goes into the default unnamed `\x3cslot /\x3e`."
      } else if (question.includes('scoped slots and their use cases')) {
        reply += "Scoped slots allow a child component to pass data back *up* to the parent's slot template. In the child, you bind attributes to the slot: `\x3cslot :item=\"data\" /\x3e`. In the parent, you destructure these attributes within the template directive: `\x3ctemplate #default=\"{ item }\"\x3e ... \x3c/template\x3e`. This is highly useful for reusable UI libraries like custom Tables or Lists where the child component controls iteration logic but the parent decides how to render each item's styling."
      } else if (question.includes('What problem does Provide/Inject solve')) {
        reply += "Provide/Inject solves the problem of **Prop Drilling**. In large component trees, passing props through multiple levels of intermediate components that do not actually need the data clutters the code and makes maintenance difficult. Provide/Inject allows an ancestor component to 'provide' data that any deeply nested descendant can directly 'inject' without intermediate props."
      } else if (question.includes('Why must we pass a ref/reactive to provide')) {
        reply += "By default, providing a plain primitive value (like a number or string: `provide('count', 0)`) only passes the static initial value. Descendants that inject it will not receive updates when the ancestor updates it. To make the data reactive, you must wrap it in a `ref` or `reactive` object: `provide('count', countRef)`. Vue tracks dependencies on refs and reactively propagates changes to all injected consumers."
      } else if (question.includes('difference between Provide/Inject and Pinia')) {
        reply += "Provide/Inject is bound to the **component tree hierarchy**. It only allows ancestors to share data with descendants. Pinia, on the other hand, is a **global state management store** that operates independently of the component tree. Any component in the application, whether sibling or nested, can access or mutate Pinia store states directly without requiring a common ancestor component."
      } else if (question.includes('difference between dynamic components and Vue Router')) {
        reply += "Dynamic components switcher `\x3ccomponent :is=\"...\" /\x3e` is used to toggle between components within the **same page view** (like switching settings tabs, form wizard steps, or panels). Vue Router is used for **full page transitions** with URL routing updates, supporting browser back/forward history tracking, and deep linking paths (e.g. `/settings/profile`). Use dynamic components for intra-page toggling, and Router for page navigation."
      } else if (question.includes('KeepAlive cache and restore component states')) {
        reply += "When wrapping a dynamic component inside `\x3cKeepAlive\x3e`, Vue does not destroy the child component instance when it is swapped out. Instead, it **deactivates** the component instance, storing its current state tree, DOM nodes, and reactive values in a memory cache. When switching back, Vue **reactivates** and re-mounts the cached instance directly, preserving any user inputs, form selections, or scrolled positions exactly as they were."
      } else if (question.includes('activated and onDeactivated lifecycle hooks')) {
        reply += "These are custom lifecycle hooks introduced when using `\x3cKeepAlive\x3e`. Since cached components are not destroyed or rebuilt when switching tabs, standard hooks like `onMounted` and `onUnmounted` do not execute. Instead, Vue runs `onActivated()` whenever the component is pulled from the cache and made active, and `onDeactivated()` when it is hidden and cached. They are useful for starting/stopping background page animations, WebSockets, or polling feeds."
      } else if (question.includes('defineAsyncComponent solve')) {
        reply += "It solves the problem of **large initial JavaScript bundles**. By default, importing components standardly builds them all into a single massive file that must be downloaded, parsed, and run on app startup (even if the user only visits the homepage). `defineAsyncComponent()` enables **lazy loading** or **code splitting** – splitting components into separate chunks that Vue only downloads from the server when they are actually rendered on screen."
      } else if (question.includes('loadingComponent and errorComponent options')) {
        reply += "When loading a component asynchronously over a network, it takes time to download. Vue allows you to specify a `loadingComponent` (like a spinner) to show during loading, and an `errorComponent` (like a connection error warning) to render if the download fails or times out. This prevents the page from flashing a blank screen or crashing during network latency."
      } else if (question.includes('difference between KeepAlive and defineAsyncComponent')) {
        reply += "`defineAsyncComponent` optimizes **performance and bundle sizes** by controlling *when* a component's JavaScript code is downloaded from the server (lazy loading). `KeepAlive` optimizes **user experience and state preservation** by caching compiled *instances* of components in memory so they are not destroyed when toggled out of view. You can combine them to lazy-load a component once and cache its state thereafter."
      } else if (question.includes('What problem does Teleport solve')) {
        reply += "Teleport solves the problem of DOM container trapping. When building modals, dropdown portfolios, tooltips, or overlays, they are HTML children of nested layouts. If an ancestor has `overflow: hidden`, `position: relative`, or a different `z-index` stacking context, the modal gets cut off, hidden, or incorrectly positioned. Teleport allows you to escape this by rendering the element's DOM node directly under the `<body>` (or another target) while keeping it in the exact same logical component hierarchy."
      } else if (question.includes('Does Teleport break props, emits, or Provide/Inject')) {
        reply += "No, Teleport does not affect component relationships. It only changes where the elements are rendered in the physical DOM. Vue handles all virtual node references behind the scenes. This means props, custom event emits, `provide/inject` boundaries, and lifecycles (like `onMounted`/`onUnmounted`) continue to function normally as if the component were rendered in place."
      } else if (question.includes('When should we use Teleport vs z-index')) {
        reply += "Use Teleport for overlays that need to sit on top of the entire viewport screen, such as full-page dialog modals, success alert toast notifications, context right-click menus, and viewport tooltips. For simpler sibling layouts (like sidebars vs main page columns), configuring CSS `z-index` rules is cleaner. Avoid using Teleport if standard CSS styles can solve the layout constraints."
      } else if (question.includes('What is a Composable in Vue')) {
        reply += "A Composable is a reusable JavaScript/TypeScript function that encapsulates reactive state and Composition API logic (like refs, computed values, watchers, or lifecycle hooks). It allows you to extract complex or repeating logic (such as fetching data from an API, checking auth, or listening to window resize events) from a component file and share it cleanly across multiple different components without duplicating code."
      } else if (question.includes('naming convention for composables')) {
        reply += "By convention, composables always use camelCase names starting with the prefix `use` (e.g. `useFetch`, `useAuth`, `useCounter`, `useWindowSize`). This prefix signals to developers that the function is a composable that uses Vue's reactivity APIs internally, distinguishes it from normal helper/utility functions, and matches standard conventions in modern composition framework libraries."
      } else if (question.includes('difference between local state and shared state in composables')) {
        reply += "By default, calling a composable (like `const counter = useCounter()`) creates a **local, independent state instance** for that component. If Component A and Component B both call `useCounter()`, they get separate counters. However, you can create a **shared state** by declaring reactive variables *outside* the exported function container in the composable file. In this case, all components calling the composable will read and write to the same single reactive state reference, acting as a lightweight global store."
      } else if (question.includes('What is an SPA, and how does Vue Router support it')) {
        reply += "An SPA (Single Page Application) is a web application that loads only a single HTML document (usually `index.html`) and dynamically updates the page as the user interacts. Vue Router supports SPAs by intercepting URL modifications and mapping the active route path to specific component views. It swaps views inside the `<RouterView />` container dynamically via JavaScript without triggering a full browser refresh."
      } else if (question.includes('RouterLink and standard HTML anchor tags')) {
        reply += "A standard HTML anchor tag (`<a href=\"/profile\">`) triggers a full page reload, causing the browser to send a request to the server, download a new HTML file, and reset all Vue reactive state. A `<RouterLink to=\"/profile\">` intercepts the click event, prevents the default browser reload behavior, updates the history state of the browser, and instructs Vue Router to render the matching view component instantly, preserving state and loading views much faster."
      } else if (question.includes('createWebHistory and history mode')) {
        reply += "`createWebHistory()` configures the router to use HTML5 History API mode. This enables clean, normal-looking URLs (such as `website.com/profile`) without needing hash character symbols (like `website.com/#/profile`). Note that when using HTML5 History mode in production, you must configure your production web server (Nginx, Apache, or Vercel config rules) to redirect all subpage requests back to `index.html` so Vue can resolve routes on initial load."
      } else if (question.includes('useRoute() and useRouter()')) {
        reply += "`useRoute()` is a Vue hook that returns the active route details object, allowing you to read current URL parameters, query parameters, query filters, hash values, and metadata (e.g. `route.params.id`). `useRouter()` returns the primary router navigation manager instance, allowing you to perform programmatic route transitions and redirect users dynamically (e.g. `router.push('/dashboard')` or `router.replace('/login')`). In short, `useRoute()` is for reading, while `useRouter()` is for navigating."
      } else if (question.includes('router.replace() instead of router.push()')) {
        reply += "`router.push()` pushes a new entry onto the browser's history stack. This allows the user to click their browser's 'Back' button to return to the previous page. `router.replace()` redirects the user by overwriting the current active history entry instead of adding a new one. This is ideal for post-login redirects, checkout completion screens, or unauthorized redirects, ensuring users cannot hit 'Back' to return to screens that are no longer relevant or secure."
      } else if (question.includes('reuse components on parameter changes')) {
        reply += "When navigating between different parameters of the same route path (e.g. from `/jobs/1` to `/jobs/2`), Vue Router reuses the already mounted view component instead of destroying it and building a new one from scratch to optimize rendering performance. This means standard lifecycle hooks like `onMounted()` will not execute again on parameter shifts. To run logic (such as fetching new data) when a parameter changes, you must watch the parameter: `watch(() => route.params.id, (newId) => { fetchJobData(newId) })`."
      } else if (question.includes('global guards and route guards')) {
        reply += "Global guards (like `router.beforeEach()`) are registered on the main router instance and run before every single route navigation in the entire application. They are ideal for app-wide logic like authentication checks or page progress indicators. Route-specific guards (like `beforeEnter`) are declared directly within individual route definitions. They only run when that specific route is matched, which is perfect for limiting code clutter and protecting isolated sections of your app like an admin console."
      } else if (question.includes('redirecting to login cause a loop')) {
        reply += "If your guard checks `if (!isLoggedIn) return '/login'`, it executes when the user tries to visit `/profile`, sees they are logged out, and redirects them to `/login`. However, when navigating to `/login`, the guard runs *again*. It checks if they are logged in, finds they are not, and tries to redirect them to `/login` again, repeating this cycle indefinitely. To prevent this infinite loop, you must ensure the destination route is not already the login page: `if (!isLoggedIn && to.path !== '/login') return '/login'`."
      } else if (question.includes('block backend API calls')) {
        reply += "No, frontend navigation guards cannot block backend API calls. They run entirely in the user's browser and only control which page view is rendered. A tech-savvy user can easily bypass these guards by modifying JavaScript code, accessing components directly via devtools, or using tools like Postman to query API endpoints directly. Therefore, navigation guards are strictly for User Experience (UX). Real security must be enforced on the backend by validating session tokens (like JWTs) or database roles on every API request."
      } else if (question.includes('Pinia solve in scaling applications')) {
        reply += "Pinia solves the problem of complex data flow (such as prop drilling) in large applications. When unrelated components (like a Navbar, an Admin Panel, and a Sidebar) all need access to the same shared data (such as user profile details or a shopping cart), passing data through multiple layers of layout props makes code fragile and bloated. Pinia establishes centralized global stores that any component can read from or write to directly, decoupled from the page layout tree."
      } else if (question.includes('difference between state, getters, and actions')) {
        reply += "State represents the **raw reactive data** of the store (equivalent to component data or `ref()`). Getters represent **computed properties** that evaluate and cache derived values based on the state (equivalent to `computed()`). Actions represent **methods** that contain synchronous or asynchronous logic (equivalent to component functions) to modify the store state. Encapsulating state modifications inside actions makes debugging and logging state transitions very easy."
      } else if (question.includes('destructuring a Pinia store directly break reactivity')) {
        reply += "A Pinia store is a reactive object wrapped in a JavaScript Proxy. When you destructure it directly (e.g. `const { count } = useCounterStore()`), you extract a local primitive reference which is no longer tracked by Vue's reactivity system. To destructure properties while keeping them reactive, you must wrap the store in the `storeToRefs()` helper: `const { count } = storeToRefs(store)`. Note that actions can be destructured directly, as they are static methods and do not need to be wrapped in `storeToRefs()`."
      } else if (question.includes('Option Stores and Setup Stores')) {
        reply += "Option Stores use an options object format with explicit `state`, `getters`, and `actions` blocks, similar to Vue's old Options API. Setup Stores pass a standard setup function returning states, getters, and actions, exactly like the Composition API. Setup Stores are preferred by modern teams because they allow you to write standard `ref()`, `computed()`, and custom composables inside the store, which feels natural and is highly flexible."
      } else if (question.includes('storeToRefs() vs normal destructuring')) {
        reply += "Use `storeToRefs(store)` when destructuring **reactive state properties** or **getters** from a store. This converts the fields into reactive refs so they remain bound to the store updates on the screen. Use **normal destructuring** (e.g. `const { login } = store`) when extracting **actions (functions)**. Actions do not hold primitive values and do not rely on Vue Proxy wrappers, so they can be destructured safely without any helpers."
      } else if (question.includes('Store Composition')) {
        reply += "Store Composition is the pattern of importing and using one Pinia store inside another store definition. This is highly useful in large applications where stores depend on each other. For example, a `useJobStore` action (`applyToJob`) can import `useAuthStore` to check if the current user is authenticated and pull their authorization bearer token before triggering a backend API network request."
      } else if (question.includes('JWT Authentication flow work')) {
        reply += "The JWT Authentication flow in Vue SPAs follows these steps: 1. The user logs in via a Form component, submitting their email/password. 2. The Form triggers an action in the Pinia Auth store. 3. The store action makes a POST API request. 4. The backend verifies the credentials and returns a signed JWT token and user info. 5. The store saves the token/user inside reactive state and writes them to `localStorage`. 6. Subsequent requests attach this token in the `Authorization: Bearer <token>` header to authenticate API calls."
      } else if (question.includes('storing passwords in localStorage a bad practice')) {
        reply += "Storing plaintext passwords in `localStorage` is a major security vulnerability because any JavaScript code running on your page (including third-party scripts, analytics tools, or CDN dependencies) can access `localStorage` via `window.localStorage`. This exposes user passwords to Cross-Site Scripting (XSS) attacks. Instead, you should only store the backend-issued JWT token and basic non-sensitive profile parameters (like username or display name). Passwords should only be collected in the form, sent directly over HTTPS, and immediately discarded from browser memory."
      } else if (question.includes('startup execution flow when initializing auth')) {
        reply += "When a Vue app opens, the correct initialization sequence is: 1. Create the Vue app and Pinia instances in `main.js`. 2. Instantiate the Auth store and invoke `authStore.restoreSession()` immediately to read cached tokens/user states from `localStorage`. 3. Register the router instance: `app.use(router)`. Registering the router *after* restoring sessions ensures that when the router runs its initial navigation guards, the Auth store already has the authenticated user details loaded, preventing race conditions or false redirects to `/login`."
      } else if (question.includes('service layer instead of calling APIs')) {
        reply += "A service layer decouples API endpoints from Vue components and Pinia stores. Without it, if you change an endpoint path (like `/jobs` to `/api/v2/jobs`), you have to edit dozens of component files. With a service layer, you only edit one service file (e.g. `jobService.js`). This keeps components completely focused on UI rendering and events, makes store actions simple, and makes API calls highly reusable and testable."
      } else if (question.includes('JWT token attachment and 401 error redirect')) {
        reply += "Both JWT token attachment and 401 redirect handling should happen inside a centralized **API Client** (`apiClient.js`). The API client intercepts all outgoing requests to append the active token from localStorage, and intercepts all incoming responses. If a response returns a `401 Unauthorized` status (indicating an expired or invalid token), the client intercepts it, clears the invalid token, and redirects the user to the `/login` view globally."
      } else if (question.includes('Refresh Tokens work inside API interceptors')) {
        reply += "Refresh Tokens are long-lived tokens stored in secure, HttpOnly cookies. Access tokens (the ones used for API requests) are short-lived (e.g., 15 minutes) for security. When an access token expires, a request returns a `401 Unauthorized`. A response interceptor detects this 401 error, pauses the request queue, makes a background request to the `/refresh` endpoint, retrieves a new access token, updates the store, and retries the original failed request seamlessly without the user noticing."
      } else if (question.includes('computed properties preferred over methods')) {
        reply += "Computed properties are cached based on their reactive dependencies. When a computed property is read, Vue records the reactive variables it depends on, and returns the cached result without running the getter function again unless those dependencies change. A normal method has no caching mechanism – it executes from scratch on every single component re-render, which degrades performance if it contains complex loops or calculations."
      } else if (question.includes('Virtual Scrolling and why does it improve')) {
        reply += "Virtual Scrolling is an optimization technique for rendering large lists. Instead of painting thousands of DOM nodes (which slows down the browser's layout engine), Virtual Scrolling renders only the items currently visible in the screen viewport (e.g. 30 rows) plus a small buffer. As the user scrolls, Vue recycles the existing DOM nodes and swaps the text content, keeping the DOM extremely light and maintaining 60 FPS scrolling."
      } else if (question.includes('Math.random() degrades list rendering')) {
        reply += "Using `:key=\"Math.random()\"` is dangerous because every time the component renders, a brand-new random key is generated for every list item. Vue uses keys to identify stable elements in the Virtual DOM diffing process. Because the keys change on every render, Vue thinks all items have been destroyed and replaced with new ones. It completely deletes and recreates all real DOM nodes on every update, causing severe rendering lags and breaking inputs."
      } else if (question.includes('simple terms')) {
        reply += "Think of `ref` as wrapping a value in an object so Vue can track when it changes. In the Composition API, we use it to declare reactive variables that immediately update the user interface when modified."
      } else {
        reply += "In Vue 3, using the Composition API (`<script setup>`) makes your code cleaner and easier to organize by features. It lets you bundle reactive state, computed values, and methods together instead of spreading them across options objects."
      }
    } else {
      reply += `In ${activeSubject.value.name}, understanding this concept is crucial for building robust applications. Do you have any specific code snippet you'd like to debug or refactor?`
    }
    
    aiMessages.value.push({ sender: 'tutor', text: reply })
    aiIsTyping.value = false
  }, 1000)
}

function sendCustomAiMessage() {
  if (!aiInput.value.trim()) return
  const msg = aiInput.value.trim()
  aiInput.value = ''
  askAiTutor(msg)
}

// ── Copy to Clipboard Helper ─────────────────────────────────────
const copiedIndex = ref<string | null>(null)
function copyCode(text: string, indexKey: string) {
  navigator.clipboard.writeText(text)
  copiedIndex.value = indexKey
  setTimeout(() => {
    copiedIndex.value = null
  }, 2000)
}

// Bookmark toggler
const bookmarkedSubjects = ref<Set<string>>(new Set(['linux', 'vue']))
function toggleBookmark(subjId: string) {
  if (bookmarkedSubjects.value.has(subjId)) {
    bookmarkedSubjects.value.delete(subjId)
  } else {
    bookmarkedSubjects.value.add(subjId)
  }
}

// Print Handler
function triggerPrint() {
  window.print()
}

// ── Subjects Database ──────────────────────────────────────────────
const subjects = ref([
  {
    id: 'linux',
    name: 'Linux System Commands',
    category: 'Systems',
    description: 'Deep dive into standard input/output streams, redirection pipelines, variables, and process lifecycle control.',
    icon: faTerminal,
    color: 'bg-sticker-sky border-sticker-sky/40 text-primary-active',
    textColor: 'text-primary-active',
    bgColor: 'bg-sticker-sky/15',
    pillColor: 'bg-sticker-sky/10 text-primary-active border border-sticker-sky/30',
    participants: [usersList[0], usersList[1], usersList[2]],
    updateDate: 'June 12, 2026',
    readTime: '12 min read',
    difficulty: 'Medium',
    progress: 75,
    chapters: [
      {
        id: 'linux_1',
        title: '1. File Descriptors & Streams',
        sections: [
          {
            type: 'paragraph',
            text: 'In Linux and Unix-like operating systems, **everything is treated as a file**. When you run a command, the operating system opens three default streams for the process, each represented by a non-negative integer known as a **File Descriptor (FD)**:'
          },
          {
            type: 'table',
            headers: ['File Descriptor', 'Stream Name', 'Default Device', 'Description'],
            rows: [
              ['0', 'stdin', 'Keyboard (Input)', 'The standard input stream where a command reads its input data.'],
              ['1', 'stdout', 'Screen (Output)', 'The standard output stream where a command writes normal output.'],
              ['2', 'stderr', 'Screen (Errors)', 'The standard error stream where error messages are output separately.']
            ]
          },
          {
            type: 'paragraph',
            text: 'By segregating normal output (stdout) from error notifications (stderr), Linux allows administrators to log errors separately while routing actual processed data through automated tooling.'
          },
          {
            type: 'visual_diagram',
            title: 'Visual Representation of Process Streams',
            diagramType: 'linux-streams'
          },
          {
            type: 'callout',
            title: 'Key Pro-Tip',
            text: 'You can test where file descriptors lead by inspecting `/proc/self/fd/` inside a running shell script or terminal process.'
          }
        ]
      },
      {
        id: 'linux_2',
        title: '2. Redirection Operators',
        sections: [
          {
            type: 'paragraph',
            text: 'Redirection allows you to route process input and output streams to or from physical files. The primary operators for directing output are:'
          },
          {
            type: 'paragraph',
            text: '`>` : Redirects the output (stdout) of a command to a file, **overwriting** any existing contents.'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Overwrite file content with echo message\necho "Initial Setup Completed" > status.log\ncat status.log'
          },
          {
            type: 'paragraph',
            text: '`>>` : Redirects output but **appends** to the target file instead of erasing it.'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Append status messages to status.log\necho "Running checks..." >> status.log\necho "All tests passed." >> status.log\ncat status.log'
          },
          {
            type: 'paragraph',
            text: '`2>` & `2>>` : Redirects standard errors (stderr) to a separate file, allowing you to log malfunctions without cluttering clean standard stdout pipelines.'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Redirect file search errors to a separate error log\nfind /etc -name "*.conf" > config_files.txt 2> search_errors.log'
          }
        ]
      },
      {
        id: 'linux_3',
        title: '3. Pipes & Command Chaining',
        sections: [
          {
            type: 'paragraph',
            text: 'Pipelines link the stdout of one process directly into the stdin of another, creating complex commands from basic building blocks:'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Filter files, sort them alphabetically, and fetch the top 5\nls -la /usr/bin | grep "git" | sort | head -n 5'
          },
          {
            type: 'paragraph',
            text: 'For executing multiple commands conditionally, use the chaining operators:'
          },
          {
            type: 'paragraph',
            text: '`&&` : Execute the next command **only if** the previous one returns an exit code of `0` (success).'
          },
          {
            type: 'paragraph',
            text: '`||` : Execute the next command **only if** the previous one returns a non-zero exit code (failure).'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Compile and run code only if compilation succeeds\ngcc server.c -o server && ./server || echo "Compilation failed!"'
          }
        ]
      },
      {
        id: 'linux_4',
        title: '4. Environment Variables',
        sections: [
          {
            type: 'paragraph',
            text: 'Environment variables contain system configurations shared across terminal shells and child sub-processes. Use `export` to make a local shell variable globally available.'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Set and export an API token\nAPI_URL="https://api.linuxmaster.dev"\nexport API_URL\n\n# Quick assignment fallback if unset\necho ${USER_ROLE:=Learner}'
          }
        ]
      }
    ]
  },
  {
    id: 'vue',
    name: 'Vue 3 Composition API',
    category: 'Frontend',
    description: 'Learn setup script syntax, ref vs reactive models, computed reactivity, watchers, and state stores.',
    icon: faLaptopCode,
    color: 'bg-sticker-pink border-sticker-pink/40 text-accent-pink',
    textColor: 'text-accent-pink',
    bgColor: 'bg-sticker-pink/15',
    pillColor: 'bg-sticker-pink/10 text-accent-pink border border-sticker-pink/30',
    participants: [usersList[1], usersList[2]],
    updateDate: 'June 10, 2026',
    readTime: '10 min read',
    difficulty: 'Easy',
    progress: 90,
    chapters: [
      {
        id: 'vue_0',
        title: '1. What is Vue?',
        sections: [
          {
            type: 'paragraph',
            text: 'Imagine you are building a website. Without a framework like Vue, you have to write verbose, imperative JavaScript to manually update the Document Object Model (DOM) and manage event listeners.'
          },
          {
            type: 'code',
            lang: 'html',
            code: '\x3cdiv id="app"\x3e\x3c/div\x3e\n\n\x3cscript\x3e\nconst app = document.getElementById(\'app\')\nlet count = 0\n\napp.innerHTML = `\x3cbutton\x3e${count}\x3c/button\x3e`\n\napp.addEventListener(\'click\', () => {\n  count++\n  app.innerHTML = `\x3cbutton\x3e${count}\x3c/button\x3e`\n})\n\x3c/script\x3e'
          },
          {
            type: 'callout',
            title: 'Problems with Vanilla JS',
            text: '• Manually updating the DOM is error-prone and tedious.<br>• Setting up and tearing down event listeners manually gets cluttered.<br>• The code quickly becomes messy and difficult to scale as complexity increases.'
          },
          {
            type: 'paragraph',
            text: 'Vue solves this by introducing a **declarative, reactive model**. Here is the exact same counter logic written in Vue:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst count = ref(0)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click="count++"\x3e\n    {{ count }}\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Vue automatically **tracks state changes**, **updates the DOM** in response, **handles events**, and **optimizes rendering** under the hood.'
          },
          {
            type: 'paragraph',
            text: '---'
          },
          {
            type: 'paragraph',
            text: '### Core Idea of Vue<br>A Vue application revolves around three main parts:'
          },
          {
            type: 'table',
            headers: ['Core Concept', 'Description', 'Code Example'],
            rows: [
              ['State', 'Data stored in memory that serves as the single source of truth.', 'const count = ref(0)'],
              ['Template', 'The UI representation describing what the interface should look like.', '<button>{{ count }}</button>'],
              ['Reactivity', 'The link that automatically updates the UI when state changes.', 'count.value++ updates button content']
            ]
          },
          {
            type: 'paragraph',
            text: '---'
          },
          {
            type: 'paragraph',
            text: '### How Vue Works Internally<br>When you write a Vue template, Vue compiles it into highly optimized JavaScript **render functions**.'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: `// Conceptually, Vue compiles templates into:\nrender() {\n  return h('h1', count.value)\n}`
          },
          {
            type: 'paragraph',
            text: 'Instead of mutating the real DOM directly for every single change (which is computationally expensive), Vue maintains a **Virtual DOM** in memory, diffs it against the previous state, and batched-updates only the changed elements in the real DOM.'
          },
          {
            type: 'visual_diagram',
            title: 'Vue Reactivity & Virtual DOM Flow',
            diagramType: 'vue-flow'
          },
          {
            type: 'paragraph',
            text: '---'
          },
          {
            type: 'paragraph',
            text: '### Single File Components (SFC)<br>In Vue, we write components using `.vue` files, which combine template markup, script logic, and scoped styles in a single file:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst name = \'Satyam\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1\x3eHello {{ name }}\x3c/h1\x3e\n\x3c/template\x3e\n\n\x3cstyle scoped\x3e\nh1 {\n  color: red;\n}\n\x3c/style\x3e'
          },
          {
            type: 'paragraph',
            text: '---'
          },
          {
            type: 'paragraph',
            text: '### Most Important Vue Concepts<br>These are the core concepts that you will master in this course:'
          },
          {
            type: 'table',
            headers: ['Category', 'Concepts'],
            rows: [
              ['Reactivity API', 'ref(), reactive(), computed(), watch()'],
              ['Components', 'props, emit, slots, custom components'],
              ['Ecosystem', 'router (Vue Router), pinia (State Management), composables']
            ]
          },
          {
            type: 'callout',
            title: 'Interview Q: Why use Vue instead of vanilla JS?',
            text: '• **Reactive UI**: Vue manages DOM synchronization automatically.<br>• **Component-Based**: Encapsulates structure, logic, and style into reusable blocks.<br>• **Organization**: Keeps projects maintainable as scale grows.<br>• **Performance**: High efficiency via compilation and Virtual DOM diffing.'
          },
          {
            type: 'code',
            lang: 'bash',
            code: `# Homework: Install Vue locally and explore the default project\nnpm create vue@latest`
          }
        ]
      },
      {
        id: 'vue_1',
        title: '2. Create a Vue Project',
        sections: [
          {
            type: 'paragraph',
            text: '# Step 1: Create a Vue Project\n\nRun:'
          },
          {
            type: 'code',
            lang: 'bash',
            code: 'npm create vue@latest'
          },
          {
            type: 'paragraph',
            text: 'You will see questions like:'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '✔ Project name:\n✔ Add TypeScript?\n✔ Add Vue Router?\n✔ Add Pinia?\n✔ Add ESLint?'
          },
          {
            type: 'paragraph',
            text: 'Choose:'
          },
          {
            type: 'code',
            lang: 'text',
            code: 'Project name: vue-mastery\n\nTypeScript: No\n\nJSX: No\n\nVue Router: Yes\n\nPinia: Yes\n\nVitest: No\n\nPlaywright: No\n\nESLint: Yes\n\nPrettier: Yes'
          },
          {
            type: 'paragraph',
            text: '---\n\n# What Actually Happened?\n\nYou might think:'
          },
          {
            type: 'code',
            lang: 'bash',
            code: 'npm create vue@latest'
          },
          {
            type: 'paragraph',
            text: 'simply creates files.\n\nWrong.\n\nInternally:'
          },
          {
            type: 'code',
            lang: 'text',
            code: 'npm\n  ↓\ndownloads create-vue\n  ↓\ngenerates project structure\n  ↓\ninstalls dependencies\n  ↓\nconfigures Vite\n  ↓\ncreates Vue application'
          },
          {
            type: 'paragraph',
            text: 'The CLI is generating hundreds of lines of code for you.\n\n---\n\n# What is Vite?\n\nModern Vue projects use:\n\nVite\n\nBefore Vite:\n\n`Webpack`\n\nProblems:\n\n- Slow startup\n- Slow rebuilds\n- Large configs\n\nVite solves this.'
          },
          {
            type: 'paragraph',
            text: '---\n\n## Traditional Bundlers\n\nOld flow:'
          },
          {
            type: 'code',
            lang: 'text',
            code: 'Start app\n    ↓\nBundle EVERYTHING\n    ↓\nServe app'
          },
          {
            type: 'paragraph',
            text: 'For 1000 files:\n\n`1000 files bundled first`\n\nCan take seconds.\n\n---\n\n## Vite Flow'
          },
          {
            type: 'code',
            lang: 'text',
            code: 'Start app\n    ↓\nServe file on demand'
          },
          {
            type: 'paragraph',
            text: 'Only files being used are loaded.\n\nResult:\n\n```\nCold start ~ instant\nHot reload ~ instant\n```\n\n---\n\n# Start the Development Server\n\nRun:'
          },
          {
            type: 'code',
            lang: 'bash',
            code: 'cd vue-mastery\nnpm install\nnpm run dev'
          },
          {
            type: 'paragraph',
            text: "You'll see:"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'Local:\nhttp://localhost:5173'
          },
          {
            type: 'paragraph',
            text: "Open it.\n\nYou should see the Vue starter page.\n\n---\n\n# How Does Vue Actually Start?\n\nLet's follow the chain.\n\n---\n\n## main.js\n\nOpen:\n\n`src/main.js`\n\nYou will see something like:"
          },
          {
            type: 'code',
            lang: 'javascript',
            code: "import './assets/main.css'\n\nimport { createApp } from 'vue'\nimport App from './App.vue'\n\ncreateApp(App).mount('#app')"
          },
          {
            type: 'paragraph',
            text: "This is the ENTRY POINT.\n\n---\n\n# Understanding createApp()\n\n`createApp(App)`\n\ncreates a Vue application instance.\n\nThink:"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'createApp()\n       ↓\ncreate Vue runtime\n       ↓\nload components\n       ↓\nprepare reactivity system'
          },
          {
            type: 'paragraph',
            text: "---\n\n# Understanding mount()\n\n`.mount('#app')`\n\nVue searches:\n\n`<div id=\"app\"></div>`\n\ninside:\n\n`index.html`\n\nand injects the application there.\n\n---\n\n# index.html\n\nOpen:\n\n`index.html`\n\nNotice:\n\n`<div id=\"app\"></div>`\n\nThis is the root container."
          },
          {
            type: 'code',
            lang: 'html',
            code: '<!DOCTYPE html>\n<html>\n<head>\n</head>\n<body>\n  <div id=\"app\"></div>\n\n  \x3cscript type="module" src="/src/main.js"\x3e\x3c/script\x3e\n</body>\n</html>'
          },
          {
            type: 'paragraph',
            text: "---\n\n# Flow of Execution"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'Browser opens\n       ↓\nLoads index.html\n       ↓\nLoads main.js\n       ↓\ncreateApp(App)\n       ↓\nmount(\'#app\')\n       ↓\nRender App.vue'
          },
          {
            type: 'paragraph',
            text: "---\n\n# Project Structure Deep Dive\n\nYou will see:"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'src/\n├── assets/\n├── components/\n├── router/\n├── stores/\n├── views/\n├── App.vue\n└── main.js'
          },
          {
            type: 'paragraph',
            text: "Let's understand every folder.\n\n---\n\n## assets/\n\nContains:\n\n`images`, `fonts`, `css`, `icons`\n\nExample:\n\n`logo.png`, `main.css`\n\n---\n\n## components/\n\nReusable UI pieces.\n\nExample:\n\n`Navbar.vue`, `Sidebar.vue`, `Button.vue`\n\nThink LEGO blocks.\n\n---\n\n## views/\n\nFull pages.\n\nExample:\n\n`HomeView.vue`, `AboutView.vue`, `ProfileView.vue`\n\nRouter loads these pages.\n\n---\n\n## router/\n\nContains `router/index.js`.\n\nExample:\n\n```javascript\nconst routes = [\n {\n   path: \'/\',\n   component: HomeView\n }\n]\n```\n\nControls navigation.\n\n---\n\n## stores/\n\nPinia stores live here.\n\nExample:\n\n`userStore.js`, `cartStore.js`, `authStore.js`\n\nGlobal state.\n\n---\n\n# Difference Between Components and Views\n\nMany beginners confuse these.\n\n### Component\n\n`Navbar`, `Footer`, `Card`, `Button` (Reusable).\n\n### View\n\n`Home Page`, `Profile Page`, `Settings Page` (Entire page).\n\nExample:"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'HomeView\n   ├── Navbar\n   ├── Hero\n   ├── ProductCard\n   └── Footer'
          },
          {
            type: 'paragraph',
            text: "---\n\n# What is App.vue?\n\nThis is the root component. Everything starts here.\n\nExample:\n\n```vue\n<template>\n  <h1>Hello Vue</h1>\n</template>\n```\n\nor later:\n\n```vue\n<template>\n  <RouterView />\n</template>\n```\n\n`App.vue` becomes the shell of the application.\n\n---\n\n# Understanding Component Tree\n\nSuppose:"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'App\n ├── Navbar\n ├── HomeView\n │    ├── ProductCard\n │    ├── ProductCard\n │    └── ProductCard\n └── Footer'
          },
          {
            type: 'paragraph',
            text: "Vue builds a tree internally called the **Component Tree**. Vue DevTools can show this tree.\n\n---\n\n# Install Vue DevTools\n\nUse: [Vue DevTools](https://devtools.vuejs.org/)\n\nThis is one of the most important tools for Vue developers.\n\nYou can inspect:\n- Components\n- Props\n- Pinia stores\n- Router state\n- Reactive variables\n\n---\n\n# What Happens When a Component Changes?\n\nExample:\n\n`const count = ref(0)`\n\nUser clicks:\n\n`count.value++`\n\nVue:"
          },
          {
            type: 'code',
            lang: 'text',
            code: 'Detects change\n      ↓\nMarks component dirty\n      ↓\nRuns render function\n      ↓\nUpdates Virtual DOM\n      ↓\nUpdates Real DOM'
          },
          {
            type: 'paragraph',
            text: "Only affected components re-render. Not the entire app.\n\n---\n\n# Industry Folder Structure\n\nLater for large apps:\n\n```\nsrc/\n├── assets/\n├── components/\n├── views/\n├── router/\n├── stores/\n├── composables/\n├── services/\n├── api/\n├── layouts/\n└── utils/\n```\n\nWe'll gradually introduce these folders.\n\n---\n\n# Mini Exercise\n\nCreate a new Vue project and answer:\n\n### Q1\n\nWhat file is the entry point?\n\n### Q2\n\nWhat does `createApp()` do?\n\n### Q3\n\nWhat does `.mount('#app')` do?\n\n### Q4\n\nDifference between `components/` and `views/`?\n\n### Q5\n\nWhat is the purpose of `router/` and `stores/`?"
          }
        ]
      },
      {
        id: 'vue_2',
        title: '3. What is a Template?',
        sections: [
          {
            type: 'paragraph',
            text: 'A template describes **what the UI should look like**.\n\nExample:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3ch1\x3eHello World\x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'You are not telling Vue:\n\n```javascript\ncreateElement(...)\nappendChild(...)\n```\n\nInstead you\'re describing:\n\n> "I want an h1 containing Hello World."\n\nThis is called **declarative programming**.\n\n---\n\n## Imperative vs Declarative\n\n### Vanilla JS (Imperative)'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'const h1 = document.createElement(\'h1\')\nh1.textContent = \'Hello World\'\n\ndocument.body.appendChild(h1)'
          },
          {
            type: 'paragraph',
            text: 'You\'re telling the browser HOW.\n\n---\n\n### Vue (Declarative)'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3ch1\x3eHello World\x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'You\'re telling Vue WHAT.\n\nVue figures out HOW.\n\n---\n\n# How Vue Compiles Templates\n\nWhen Vue sees:\n\n```vue\n\x3ctemplate\x3e\n  \x3ch1\x3eHello World\x3c/h1\x3e\n\x3c/template\x3e\n```\n\nIt doesn\'t send templates directly to the browser.\n\nVue compiles them into render functions.\n\nConceptually:\n\n```js\nrender() {\n  return h(\'h1\', \'Hello World\')\n}\n```\n\nwhere `h()` means: `Create Virtual DOM node`\n\nFlow:\n\n```text\nTemplate ➔ Compiler ➔ Render Function ➔ Virtual DOM ➔ Real DOM\n```\n\n---\n\n# Interpolation\n\nMost common Vue syntax:\n\n`{{ expression }}`\n\nExample:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst name = \'Satyam\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1\x3e{{ name }}\x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output:\n\n`<h1>Satyam</h1>`\n\n---\n\n# Why Double Curly Braces?\n\nCalled:\n\n**Mustache Syntax**\n\n`{{ variable }}`\n\nVue evaluates the expression and inserts the result.\n\n---\n\n## Multiple Variables'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst firstName = \'Satyam\'\nconst lastName = \'Kumar\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1\x3e\n    {{ firstName }} {{ lastName }}\n  \x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output:\n\n`<h1>Satyam Kumar</h1>`\n\n---\n\n# Expressions Inside Interpolation\n\nNot just variables.\n\nYou can write expressions.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst age = 20\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ age + 5 }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `25`\n\nAnother example:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst name = \'vue\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ name.toUpperCase() }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `VUE`\n\n---\n\n# Ternary Operators\n\nVery common in interviews.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst isLoggedIn = true\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ isLoggedIn ? \'Welcome\' : \'Login\' }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `Welcome`\n\n---\n\n# What You Cannot Do\n\nThis works: `{{ 5 + 10 }}`\n\nThis works: `{{ name.toUpperCase() }}`\n\nThis does NOT work: `{{ if (true) {} }}`\n\nReason: Interpolation only accepts **single JavaScript expressions**. Not statements.\n\n---\n\n## Expression vs Statement\n\n* **Expression**: `5 + 5` (Produces a value)\n* **Statement**: `if (x) {}` (Controls execution, no value returned)\n\n---\n\n# Method Calls Inside Templates\n\nExample:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nfunction greet() {\n  return \'Hello\'\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ greet() }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `Hello` (Works).\n\nBut be careful. Many beginners do:\n\n```vue\n\x3ctemplate\x3e\n  {{ expensiveFunction() }}\n\x3c/template\x3e\n```\n\nEvery render, the component re-renders and the function executes again. Can hurt performance.\n\nLater we\'ll learn `computed()` which solves this.\n\n---\n\n# Accessing Arrays'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst fruits = [\'Apple\', \'Mango\', \'Banana\']\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ fruits[0] }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `Apple`\n\n---\n\n# Accessing Objects'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst user = {\n  name: \'Satyam\',\n  age: 20\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ user.name }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `Satyam`\n\n---\n\n# HTML Escaping (VERY IMPORTANT)\n\nConsider:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst message = \'\x3ch1\x3eHello\x3c/h1\x3e\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ message }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<h1>Hello</h1>` displayed as text, NOT rendered as an actual heading. Vue automatically escapes HTML for security.\n\n---\n\n# XSS Attack Example\n\nSuppose user enters:\n\n```html\n\x3cscript\x3e\nalert(\'Hacked\')\n\x3c/script\x3e\n```\n\nWithout escaping, browser executes the script (bad!). Vue protects you automatically.\n\n---\n\n# Rendering Raw HTML\n\nVue provides `v-html`.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst html = \'\x3ch1\x3eHello Vue\x3c/h1\x3e\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv v-html=\"html\"\x3e\x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output:\n\n`<h1>Hello Vue</h1>` actually rendered.\n\n⚠️ Never use `v-html` on untrusted user input to avoid security vulnerabilities.\n\n---\n\n# Reactivity in Templates\n\nExample:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst count = ref(0)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ count }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Notice we write `{{ count }}` and NOT `{{ count.value }}` inside templates. Vue automatically unwraps refs in templates. Inside script block, `count.value` is required.\n\n---\n\n# Template Compilation Example\n\nYou write `<h1>{{ name }}</h1>`, Vue compiles to:\n\n```js\nrender() {\n  return h(\'h1\', name.value)\n}\n```\n\n---\n\n# Real Industry Example'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst user = ref({\n  name: \'Satyam\',\n  role: \'Developer\'\n})\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv\x3e\n    \x3ch2\x3e{{ user.name }}\x3c/h2\x3e\n    \x3cp\x3e{{ user.role }}\x3c/p\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '---\n\n# Common Beginner Mistakes\n\n* **Mistake 1**: `{{ const x = 5 }}` ❌ Invalid\n* **Mistake 2**: `{{ if (true) return \'Hello\' }}` ❌ Invalid\n* **Mistake 3**: `{{ count.value }}` inside template (Not needed, use `{{ count }}`)\n* **Mistake 4**: Using `v-html` everywhere (Avoid unless absolutely necessary)\n\n---\n\n# Mental Model\n\nWhenever you see `{{ something }}`, think:\n\n1. Evaluate JavaScript expression\n2. Convert result to text\n3. Insert into DOM\n\n---\n\n# Mini Challenge\n\nPredict the outputs:\n\n1. `{{ age * 2 }}` when `age = 20` ➔ `40`\n2. `{{ name.length }}` when `name = \'vue\'` ➔ `3`\n3. `{{ loggedIn ? \'Home\' : \'Login\' }}` when `loggedIn = false` ➔ `Login`\n4. `{{ fruits[1] }}` when `fruits = [\'Apple\', \'Mango\']` ➔ `Mango`\n5. `{{ count }}` when `count = ref(10)` ➔ `10`'
          }
        ]
      },
      {
        id: 'vue_3',
        title: '4. Dynamic Attributes',
        sections: [
          {
            type: 'paragraph',
            text: 'In Lesson 3, you learned how to put data **inside HTML content**:\n\n```vue\n<h1>{{ name }}</h1>\n```\n\nBut what if you want to put data inside HTML attributes?\n\nExample:\n\n```html\n<img src="logo.png">\n<a href="/about">About</a>\n<input disabled>\n```\n\nThe values of `src`, `href`, `disabled`, `id`, `class`, etc. are called **attributes**.\n\nTo make them dynamic, Vue uses:\n\n`v-bind`\n\n---\n\n# The Problem\n\nSuppose:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst imageUrl = \'/images/profile.jpg\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cimg src=\"imageUrl\"\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'What will happen? Vue treats `src="imageUrl"` as a string. It literally looks for `imageUrl`, not the variable. Wrong.\n\n---\n\n# v-bind\n\nCorrect way:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst imageUrl = \'/images/profile.jpg\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cimg v-bind:src=\"imageUrl\"\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Now Vue evaluates `imageUrl` and inserts its value.\n\nResult:\n\n`<img src="/images/profile.jpg">`\n\n---\n\n# Shorthand Syntax\n\nYou\'ll almost never see `v-bind:src` in production. Instead, use `:src`.\n\nExample:\n\n`<img :src="imageUrl">`\n\nThese are identical:\n\n* `v-bind:src="imageUrl"`\n* `:src="imageUrl"`\n\n---\n\n# Dynamic Links\n\nExample:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst website = \'https://vuejs.org\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ca :href=\"website\"\x3e\n    Vue Docs\n  \x3c/a\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Vue renders:\n\n`<a href="https://vuejs.org">`\n\n---\n\n# Binding Multiple Attributes'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst imageUrl = \'/logo.png\'\nconst altText = \'Vue Logo\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cimg\n    :src=\"imageUrl\"\n    :alt=\"altText\"\n  \x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output:\n\n`<img src="/logo.png" alt="Vue Logo">`\n\n---\n\n# Binding Boolean Attributes\n\nHTML has boolean attributes such as `disabled`, `checked`, `required`, `readonly`.\n\nExample:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst isDisabled = true\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton :disabled=\"isDisabled\"\x3e\n    Submit\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<button disabled>`\n\nIf `isDisabled = false`, the output is `<button>`, as the attribute is removed automatically.\n\n---\n\n# Dynamic IDs'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst userId = 101\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv :id=\"userId\"\x3e\n    User\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<div id="101">`\n\n---\n\n# Dynamic Classes\n\nThis is one of the most important Vue skills.\n\n---\n\n## String Class Binding'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst className = \'active\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton :class=\"className\"\x3e\n    Click\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<button class="active">`\n\n---\n\n## Multiple Classes'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst classes = \'btn primary\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton :class=\"classes\"\x3e\n    Save\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<button class="btn primary">`\n\n---\n\n## Object Class Binding\n\nMost common in real projects.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst isActive = true\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton\n    :class=\"{\n      active: isActive\n    }\"\n  \x3e\n    Save\n  \x3c/button\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Meaning: If `isActive` is true, add class `active`. Output is `<button class="active">`. If `isActive` is false, output is `<button>` (no class added).\n\n---\n\n## Multiple Conditional Classes'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst isActive = true\nconst isDisabled = false\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton\n    :class=\"{\n      active: isActive,\n      disabled: isDisabled\n    }\"\n  \x3e\n    Save\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Result: `<button class="active">`\n\n---\n\n## Array Class Binding\n\nUseful when combining classes.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst primary = \'btn\'\nconst secondary = \'rounded\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton\n    :class=\"[primary, secondary]\"\n  \x3e\n    Save\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<button class="btn rounded">`\n\n---\n\n## Real Industry Example'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst isLoggedIn = true\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton\n    :class=\"[\n      \'btn\',\n      isLoggedIn\n        ? \'success\'\n        : \'danger\'\n    ]\"\n  \x3e\n    Login\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '---\n\n# Dynamic Styles\n\nVue can bind inline styles too.\n\n---\n\n## String Style'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst color = \'red\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1 :style=\"\'color:\' + color\"\x3e\n    Hello\n  \x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Works but not recommended.\n\n---\n\n## Object Style Binding'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst color = \'red\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1\n    :style=\"{\n      color: color\n    }\"\n  \x3e\n    Hello\n  \x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Output: `<h1 style="color:red">`\n\n---\n\n## Multiple Styles'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst color = \'blue\'\nconst size = \'32px\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1\n    :style=\"{\n      color: color,\n      fontSize: size\n    }\"\n  \x3e\n    Vue\n  \x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Note that Vue styles use CamelCase (e.g. `fontSize`) rather than kebab-case (`font-size`) because it is a JavaScript object.\n\n---\n\n# Binding Entire Objects'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst user = {\n  id: 1,\n  class: \'active\'\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv v-bind=\"user\"\x3e\n    User\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Vue converts to: `<div id="1" class="active">`\n\n---\n\n# How Vue Updates Attributes\n\nSuppose:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst imageUrl = ref(\'cat.jpg\')\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cimg :src=\"imageUrl\"\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Later when you update: `imageUrl.value = \'dog.jpg\'`, Vue updates the Virtual DOM, and only the `src` attribute changes, not the whole page.\n\n---\n\n# Real Production Example'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst darkMode = ref(false)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv\n    :class=\"{\n      dark: darkMode\n    }\"\n  \x3e\n    Dashboard\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Used in: Dark mode, active navigation, validation states, error messages, and authentication UI daily in real projects.\n\n---\n\n# Common Beginner Mistakes\n\n* **Wrong**: `<img src="{{ imageUrl }}">` ❌ Vue doesn\'t support interpolation inside attributes. Correct is `<img :src="imageUrl">`.\n* **Wrong**: `<button class="{{ btn }}">` ❌ Correct is `<button :class="btn">`.\n* **Wrong**: `<div style="{{ styles }}">` ❌ Correct is `<div :style="styles">`.\n\n---\n\n# Mental Model\n\nWhenever you see `:attribute="expression"`, think: Evaluate JavaScript expression ➔ Take resulting value ➔ Bind it to HTML attribute.\n\n---\n\n# Mini Challenge\n\nPredict the outputs:\n1. `url = \'profile.png\'` inside `<img :src="url">` ➔ `src="profile.png"`\n2. `disabled = false` inside `<button :disabled="disabled">` ➔ The button is NOT disabled.\n3. `isActive = true` inside `<div :class="{ active: isActive }">` ➔ `class="active"`\n4. `color = \'green\'` inside `<h1 :style="{ color }">` ➔ Text color is green.'
          }
        ]
      },
      {
        id: 'vue_4',
        title: '5. Event Handling',
        sections: [
          {
            type: 'paragraph',
            text: 'So far, our UI can **display data**.\n\nBut users need to **interact** with the UI.\n\nExamples:\n* Clicking a button\n* Typing in an input\n* Submitting a form\n* Hovering over an element\n* Pressing keyboard keys\n\nAll of these are called **events**.'
          },
          {
            type: 'paragraph',
            text: '### What is an Event?\nAn event is simply: *Something that happened in the browser*.\n\nExamples:\n```text\nUser clicked\nUser typed\nUser scrolled\nUser submitted form\nUser pressed Enter\n```\nThe browser notifies JavaScript: "Hey! Something happened."'
          },
          {
            type: 'paragraph',
            text: '### Vanilla JavaScript Event Handling\nWithout Vue, event handling is imperative:'
          },
          {
            type: 'code',
            lang: 'html',
            code: '\x3cbutton id="btn"\x3e\n  Click\n\x3c/button\x3e\n\n\x3cscript\x3e\nconst btn = document.getElementById(\'btn\')\nbtn.addEventListener(\'click\', () => {\n  console.log(\'clicked\')\n})\n\x3c/script\x3e'
          },
          {
            type: 'callout',
            title: 'Vanilla JS Drawbacks',
            text: '• Manual DOM selection is required.<br>• Manual listener registration/removal is needed.<br>• It is hard to manage at scale.'
          },
          {
            type: 'paragraph',
            text: '### Vue Event Handling\nVue provides the `v-on` directive to register event listeners.\n\nExample:\n`\x3cbutton v-on:click=\"sayHello\"\x3eClick Me\x3c/button\x3e`\n\n### Shorthand Syntax\nJust like `v-bind:src` became `:src`, `v-on:click` becomes `@click`.\nProduction code uses `@click` almost always:\n`\x3cbutton @click=\"sayHello\"\x3eClick\x3c/button\x3e`'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nfunction greet() {\n  console.log(\'Hello\')\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"greet\"\x3e\n    Click Me\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Many beginners ask why we use `@click=\"greet\"` instead of `@click=\"greet()\"`.\nVue automatically calls the function. Both work, but `@click=\"greet\"` is cleaner and preferred.'
          },
          {
            type: 'paragraph',
            text: '### Updating Reactive State\nReal applications don\'t just log messages. They update state, and Vue automatically updates the UI in response:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst count = ref(0)\n\nfunction increment() {\n  count.value++\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"increment\"\x3e\n    {{ count }}\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Inline Event Handlers\nSmall actions can be written directly inside the directive:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst count = ref(0)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"count++\"\x3e\n    {{ count }}\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Passing Arguments\nYou can pass custom values directly in the template:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nfunction greet(name) {\n  console.log(name)\n}\nfunction add(a, b) {\n  console.log(a + b)\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"greet(\'Satyam\')\"\x3e\n    Click\n  \x3c/button\x3e\n  \x3cbutton @click=\"add(10, 20)\"\x3e\n    Add\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Event Object\nEvery browser event creates an event object. If you don\'t pass any arguments, Vue automatically forwards the event as the first parameter. If you need both custom arguments and the event object, pass the special `$event` variable:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nfunction greet(name, event) {\n  console.log(name)\n  console.log(event.type) // \'click\'\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"greet(\'Satyam\', $event)\"\x3e\n    Click\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Event Bubbling & Modifiers\nIn the DOM, events bubble upward from child to parent. Vue provides modifiers to control this and intercept default behavior easily:\n\n* `.stop` : Stops event propagation (bubbling).\n* `.prevent` : Prevents default browser behaviors, such as page reloads on form submit.\n* `.once` : Triggers the listener only once.\n* `.self` : Fires only if the event targets the element itself directly.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3c!-- Stops bubbling --\x3e\n  \x3cdiv @click=\"parent\"\x3e\n    \x3cbutton @click.stop=\"child\"\x3eClick\x3c/button\x3e\n  \x3c/div\x3e\n\n  \x3c!-- Prevents page reload --\x3e\n  \x3cform @submit.prevent=\"save\"\x3e\n    \x3cbutton type=\"submit\"\x3eSave\x3c/button\x3e\n  \x3c/form\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Keyboard & Mouse Events\nYou can listen for specific keys using keyboard modifiers:\n* `@keyup.enter` : Triggers only when Enter is pressed.\n* `@keyup.esc` : Triggers only when Escape is pressed.\n* Modifiers available: `.enter`, `.tab`, `.esc`, `.space`, `.delete`.\n\nMouse events: `@click`, `@dblclick`, `@mousedown`, `@mouseup`, `@mousemove`, `@mouseenter`, `@mouseleave`.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\n\nconst count = ref(0)\nfunction increment() { count.value++ }\nfunction decrement() { count.value-- }\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"decrement\"\x3e-\x3c/button\x3e\n  {{ count }}\n  \x3cbutton @click=\"increment\"\x3e+\x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Writing `@click="increment()"` when no arguments are needed. Cleaner is `@click="increment"`. <br>• **Mistake 2**: Forgetting `.prevent` on forms, causing page reloads and state loss. <br>• **Mistake 3**: Ignoring event bubbling in nested elements. Use `.stop` to prevent parent clicks.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. What is the value of `count` after clicking 3 times on `<button @click=\"count++\"\x3e`? ➔ `3`\n2. What does `.prevent` do in `\x3cform @submit.prevent=\"save\"\x3e`? ➔ Prevents default page refresh.\n3. What is the output order when clicking the button inside `\x3cdiv @click=\"parent\"\x3e\x3cbutton @click=\"child\"\x3eClick\x3c/button\x3e\x3c/div\x3e`? ➔ `child` then `parent`.'
          }
        ]
      },
      {
        id: 'vue_5',
        title: '6. Reactivity System',
        sections: [
          {
            type: 'paragraph',
            text: 'This is the single most important lesson in Vue. If you deeply understand reactivity, then components, forms, Pinia, computed logic, and watchers all become easy. Most beginners memorize Vue. Good developers understand **Vue\'s reactivity system**.'
          },
          {
            type: 'paragraph',
            text: '### The Problem Vue Solves\nImagine plain JavaScript:\n```javascript\nlet count = 0\nfunction increment() {\n  count++\n}\n```\nWhen `count` changes, the HTML does not automatically update because JavaScript variables are not connected to the DOM. Vue solves this by introducing **State Tracking** and **Automatic UI Updates**.'
          },
          {
            type: 'paragraph',
            text: '### What is Reactivity?\nReactivity means Vue can detect when data changes and automatically updates the DOM in response.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\nconst count = ref(0)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  {{ count }}\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### What Does ref() Return?\nWhen you write `const count = ref(0)`, Vue returns a reactive **Ref object** wrapping the value under a `.value` property. Behind the scenes, it looks like: `{ value: 0 }`. In script, you must write `count.value++` to update it. In templates, Vue automatically unwraps the ref, so you can write `{{ count }}` directly.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\nconst firstName = ref(\'Satyam\')\nconst age = ref(20)\n\n// Updating refs in JS:\nfirstName.value = \'Rahul\'\nage.value = 21\n\n// Refs can store objects and arrays too:\nconst user = ref({ name: \'Satyam\' })\nuser.value.name = \'Aarav\'\n\nconst fruits = ref([\'Apple\'])\nfruits.value.push(\'Mango\')\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Enter reactive()\nVue provides another reactive API: `reactive()`. Unlike `ref()`, which takes any value and wraps it, `reactive()` only accepts objects/arrays and makes them reactive directly without wrapping them in `.value`.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { reactive } from \'vue\'\n\nconst user = reactive({\n  name: \'Satyam\',\n  age: 20\n})\n\n// Update directly without .value:\nuser.name = \'Rahul\'\nuser.age = 21\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### When to Use ref() vs reactive()\n* Use `ref()` for primitive values like numbers, strings, booleans, or when you need to completely reassign arrays/objects.\n* Use `reactive()` for grouped state, large objects, forms, and states where you only mutate properties and never reassign the entire object.'
          },
          {
            type: 'table',
            headers: ['Feature', 'ref()', 'reactive()'],
            rows: [
              ['Argument Type', 'Any type (Primitive or Object)', 'Objects, Arrays, Map, Set only'],
              ['Access in Script', 'Requires .value property', 'Direct access (no .value)'],
              ['Access in Template', 'Automatically unwrapped', 'Direct access'],
              ['Reassignment', 'Can reassign entire .value', 'Cannot overwrite entire object (loses reactivity)']
            ]
          },
          {
            type: 'paragraph',
            text: '### How Reactivity Works Internally\nVue 3 uses JavaScript **Proxies** to intercept property accesses. When a component renders and reads a reactive variable, Vue records it as a dependency (getter interception). When the variable changes (setter interception), Vue notifies the component to re-render. Primitives cannot be proxied directly in JS, which is why Vue wraps them in a Ref object.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Forgetting `.value` in JavaScript: writing `count++` instead of `count.value++` for a ref. <br>• **Mistake 2**: Writing `user.value.name` for a reactive object created with `reactive()`. Reactive objects do not have `.value`. <br>• **Mistake 3**: Reassigning a reactive object completely (e.g. `user = reactive({ ... })`). This breaks Vue\'s proxy connection.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the output:\n1. If `count = ref(5)` and you run `count.value++`, what is the value? ➔ `6`\n2. If `user = reactive({ age: 20 })` and you run `user.age += 5`, what is `user.age`? ➔ `25`\n3. Does reactive support primitive variables like `reactive(0)`? ➔ No, it requires an object or array.'
          }
        ]
      },
      {
        id: 'vue_6',
        title: '7. Conditional Rendering',
        sections: [
          {
            type: 'paragraph',
            text: 'One of the most common requirements in any application is showing or hiding UI elements based on conditions. For example: showing a dashboard only to logged-in users, displaying a spinner while loading, or hiding admin panels from normal users. This is called **Conditional Rendering**.'
          },
          {
            type: 'paragraph',
            text: '### v-if, v-else-if, and v-else\nVue provides directives to render elements conditionally:\n* `v-if` : Renders the element only if the condition evaluates to truthy.\n* `v-else-if` : Adds an else-if block for multiple conditions.\n* `v-else` : Adds a fallback block when all previous conditions fail.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst role = \'admin\'\nconst isLoggedIn = true\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1 v-if=\"role === \'admin\'\"\x3e\n    Admin Panel\n  \x3c/h1\x3e\n  \x3ch1 v-else-if=\"role === \'manager\'\"\x3e\n    Manager Panel\n  \x3c/h1\x3e\n  \x3ch1 v-else\x3e\n    User Panel\n  \x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### What Happens Internally with v-if?\nWhen the condition on `v-if` is false, Vue completely removes the element from the DOM. It does not exist in the page structure at all. When the condition becomes true, Vue dynamically compiles and inserts the element.'
          },
          {
            type: 'paragraph',
            text: '### v-show\nVue provides another directive: `v-show`. Example:\n`\x3ch1 v-show=\"visible\"\x3eHello Vue\x3c/h1\x3e`\nIt looks very similar to `v-if`, but behaves differently under the hood.'
          },
          {
            type: 'paragraph',
            text: '### Difference Between v-if and v-show\n* **v-if**: Dynamically creates/destroys the DOM element. If false, element is not in DOM.\n* **v-show**: Keeps the element in the DOM but toggles the CSS `display` property. If false, element has `style=\"display: none\"`.'
          },
          {
            type: 'table',
            headers: ['Directive', 'DOM Presence (when false)', 'Initial Render Cost', 'Toggle Performance Cost', 'Ideal Use Case'],
            rows: [
              ['v-if', 'Removed from DOM', 'Low (doesn\'t compile if false)', 'High (re-creates/destroys)', 'Rarely changing conditions (e.g. auth blocks)'],
              ['v-show', 'Stays in DOM (display:none)', 'High (always compiles/creates)', 'Low (only changes CSS)', 'Frequently toggled elements (e.g. dropdowns, modals)']
            ]
          },
          {
            type: 'paragraph',
            text: '### Using <template> wrapper\nIf you want to apply a single condition to multiple sibling elements without adding a wrapper `div` to the HTML, you can wrap them in a `\x3ctemplate\x3e` tag with `v-if`:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate v-if=\"showDetails\"\x3e\n  \x3ch3\x3eProduct details\x3c/h3\x3e\n  \x3cp\x3eIn stock: yes\x3c/p\x3e\n\x3c/template\x3e'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Using assignment inside condition (e.g., `v-if=\"count = 5\"` instead of `v-if=\"count === 5\"`). <br>• **Mistake 2**: Using `v-else` without a preceding `v-if` or `v-else-if` sibling. <br>• **Mistake 3**: Using `v-if` for extremely frequent toggle animations (like mouse hover dropdowns), which can degrade performance. Use `v-show` instead.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the output:\n1. If `visible = false` and you inspect the DOM, will an element with `v-show=\"visible\"` be present? ➔ Yes, with `style=\"display: none\"`. \n2. Which directive is better for a Sidebar Toggle? ➔ `v-show`, because sidebars are toggled frequently. \n3. Can a `v-else` tag be placed inside a different parent than its sibling `v-if`? ➔ No, they must be adjacent siblings.'
          }
        ]
      },
      {
        id: 'vue_7',
        title: '8. List Rendering',
        sections: [
          {
            type: 'paragraph',
            text: 'One of the most heavily used features in Vue is rendering lists of repeating data elements. Think of YouTube showing a list of videos, Spotify showing songs, or Amazon showing products. This pattern involves taking a **Data Array** and **rendering multiple UI elements**.'
          },
          {
            type: 'paragraph',
            text: '### The Problem\nSuppose you have a list of fruits:\n`const fruits = [\'Apple\', \'Mango\', \'Banana\']`\nWithout loops, you would have to manually write out an element for each, which is impossible if you have 10,000 items from an API. Vue solves this with the `v-for` directive.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst fruits = [\'Apple\', \'Mango\', \'Banana\']\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cp v-for=\"fruit in fruits\"\x3e\n    {{ fruit }}\n  \x3c/p\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### How It Works\nThe syntax `fruit in fruits` tells Vue to take each item from `fruits`, store it temporarily in `fruit`, and render the template tag for that iteration. You can also access the current iteration index:\n\n`v-for=\"(fruit, index) in fruits\"`'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3cul\x3e\n    \x3cli v-for=\"(fruit, index) in fruits\"\x3e\n      {{ index }} - {{ fruit }}\n    \x3c/li\x3e\n  \x3c/ul\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Rendering Objects and Lists of Objects\nReal APIs usually return arrays of objects. Vue can iterate over them easily. You can also loop through the properties of a single object using `v-for=\"(value, key) in object\"`.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst users = [\n  { id: 1, name: \'Satyam\', age: 21 },\n  { id: 2, name: \'Rahul\', age: 25 }\n]\n\nconst profile = {\n  name: \'Satyam\',\n  city: \'Ranchi\'\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3c!-- Array of Objects --\x3e\n  \x3cdiv v-for=\"user in users\"\x3e\n    \x3ch3\x3e{{ user.name }}\x3c/h3\x3e\n    \x3cp\x3eAge: {{ user.age }}\x3c/p\x3e\n  \x3c/div\x3e\n\n  \x3c!-- Single Object properties --\x3e\n  \x3cp v-for=\"(val, key) in profile\"\x3e\n    {{ key }}: {{ val }}\n  \x3c/p\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Looping a Number Range\nYou can also iterate over a range of numbers directly. Note that Vue range loops start from 1, not 0:\n\n`v-for=\"n in 5\"` renders 1, 2, 3, 4, 5.'
          },
          {
            type: 'paragraph',
            text: '### The Most Important Topic: Keys\nWhen rendering lists, Vue requires a `:key` attribute containing a unique identifier for each item. This enables Vue\'s Virtual DOM diffing engine to track item identities. If items are added, removed, or reordered, Vue can reuse existing DOM elements instead of recreating everything from scratch.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3cdiv\n    v-for=\"user in users\"\n    :key=\"user.id\"\n  \x3e\n    {{ user.name }}\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'callout',
            title: 'NEVER Use Index as Key',
            text: 'Avoid binding `:key=\"index\"`. If you insert an item at the beginning of the list, all array indexes shift. Vue will get confused, thinking every single element has changed, which hurts performance and breaks local element states (such as form inputs).'
          },
          {
            type: 'paragraph',
            text: '### Filtering Lists\nAvoid using `v-if` and `v-for` on the same element. Instead, filter the list first using a computed property:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { computed } from \'vue\'\nconst users = [\n  { id: 1, name: \'Satyam\', age: 21 },\n  { id: 2, name: \'Rahul\', age: 17 }\n]\nconst adults = computed(() => users.filter(u => u.age \x3e= 18))\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cli v-for=\"user in adults\" :key=\"user.id\"\x3e\n    {{ user.name }}\n  \x3c/li\x3e\n\x3c/template\x3e'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Missing the `:key` attribute entirely. <br>• **Mistake 2**: Using `:key=\"index\"` for dynamic lists where items can be reordered or inserted. <br>• **Mistake 3**: Combining `v-if` and `v-for` on the same tag (can lead to performance overhead and warning messages). <br>• **Mistake 4**: Using non-unique keys like `user.name` which could clash if two users share a name.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the output:\n1. What is the output of `\x3cspan v-for=\"n in 3\"\x3e{{ n }}\x3c/span\x3e`? ➔ `123` \n2. Why should we avoid `:key=\"index\"`? ➔ It degrades performance and breaks component state if items are reordered or inserted at the start. \n3. How does Vue loop through a single object? ➔ By extracting its keys and values using `v-for=\"(value, key) in object\"`.'
          }
        ]
      },
      {
        id: 'vue_8',
        title: '9. Two-Way Data Binding',
        sections: [
          {
            type: 'paragraph',
            text: 'Forms are one of the most vital parts of any application, from login pages to profile creation or complex settings screens. Vue simplifies form handling by using the `v-model` directive to bind input values and reactive state.'
          },
          {
            type: 'paragraph',
            text: '### The Problem\nIn vanilla JavaScript, getting value out of an input requires selecting the element and binding event listeners manually:'
          },
          {
            type: 'code',
            lang: 'html',
            code: '\x3cinput id=\"username\"\x3e\n\n\x3cscript\x3e\nconst input = document.getElementById(\'username\')\ninput.addEventListener(\'input\', (e) => {\n  console.log(e.target.value)\n})\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Vue Solution: v-model\nVue\'s `v-model` directive sets up **Two-Way Data Binding**, linking the template input value and the reactive JavaScript state. When the state changes, the input field updates; when the user types in the input field, the state updates automatically.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\nconst name = ref(\'\')\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cinput v-model=\"name\" placeholder=\"Enter name\"\x3e\n  \x3cp\x3eYour name: {{ name }}\x3c/p\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### How v-model Works Internally\nWhen you write `v-model=\"name\"`, Vue compiles it under the hood to a property binding and an input event listener:\n\n`\x3cinput :value=\"name\" @input=\"name = $event.target.value\"\x3e`\n\n* **Value Binding**: passes the state into the input value.\n* **Input Event**: listens for keystrokes and assigns the target input value back to the state.'
          },
          {
            type: 'paragraph',
            text: '### Binding Different Input Types\n`v-model` behaves differently depending on the input element type:\n\n* **Text / Textarea**: Binds to string values.\n* **Checkbox**: Binds to a boolean for a single checkbox (true/false) or to an array for multiple checkboxes.\n* **Radio Buttons**: Binds to a string value matching the checked option\'s `value` attribute.\n* **Select Dropdown**: Binds to a string representing the selected option\'s value (or array for multi-selects).'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\nconst accepted = ref(false)\nconst gender = ref(\'\')\nconst country = ref(\'\')\nconst skills = ref([])\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3c!-- Single Checkbox --\x3e\n  \x3clabel\x3e\n    \x3cinput type=\"checkbox\" v-model=\"accepted\"\x3e Accept terms\n  \x3c/label\x3e\n\n  \x3c!-- Radio --\x3e\n  \x3cinput type=\"radio\" value=\"Male\" v-model=\"gender\"\x3e Male\n  \x3cinput type=\"radio\" value=\"Female\" v-model=\"gender\"\x3e Female\n\n  \x3c!-- Dropdown --\x3e\n  \x3cselect v-model=\"country\"\x3e\n    \x3coption value=\"India\"\x3eIndia\x3c/option\x3e\n    \x3coption value=\"USA\"\x3eUSA\x3c/option\x3e\n  \x3c/select\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Form State with reactive()\nFor larger forms with multiple fields, instead of creating dozens of separate refs, it is best practice to group them into a single reactive object:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { reactive } from \'vue\'\n\nconst form = reactive({\n  email: \'\',\n  password: \'\',\n  rememberMe: false\n})\n\nfunction submitForm() {\n  console.log(\'Sending values:\', form)\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cform @submit.prevent=\"submitForm\"\x3e\n    \x3cinput type=\"email\" v-model=\"form.email\"\x3e\n    \x3cinput type=\"password\" v-model=\"form.password\"\x3e\n    \x3cbutton type=\"submit\"\x3eSubmit\x3c/button\x3e\n  \x3c/form\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### v-model Modifiers\nVue provides modifiers to sanitize or tweak user inputs:\n* `.trim` : Automatically strips leading and trailing whitespaces.\n* `.number` : Automatically casts string values to numbers under the hood.\n* `.lazy` : Updates state on `change` events (i.e., when leaving focus) rather than every `input` keystroke.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3c!-- Numbers cast automatically --\x3e\n  \x3cinput v-model.number=\"age\" type=\"number\"\x3e\n\n  \x3c!-- Whitespace trimmed automatically --\x3e\n  \x3cinput v-model.trim=\"username\"\x3e\n\x3c/template\x3e'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Writing `v-model=\"count.value\"` in the template. Just write `v-model=\"count\"`; Vue automatically unwraps it. <br>• **Mistake 2**: Binding `v-model` to non-reactive values (like plain objects). Ensure target state is initialized with `ref()` or `reactive()`. <br>• **Mistake 3**: Forgetting `.prevent` on submit, causing page reloads and clearing inputs.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If `name = ref(\"\")` and user enters \"Vue\" inside `\x3cinput v-model=\"name\"\x3e`, what is `name.value`? ➔ `"Vue"` \n2. What modifier casts input string values to real numbers? ➔ `.number` \n3. Why is using `reactive()` preferred for forms? ➔ It groups variables into a single object wrapper for clean organization.'
          }
        ]
      },
      {
        id: 'vue_9',
        title: '10. Computed Properties',
        sections: [
          {
            type: 'paragraph',
            text: 'As your applications grow, you will often need values calculated from other reactive states. For instance, computing a full name from first and last name variables, calculating shopping cart totals, or filtering a list of jobs in a placement portal. These are called **Derived States**, and Vue manages them efficiently using **Computed Properties**.'
          },
          {
            type: 'paragraph',
            text: '### The Problem\nImagine you have first and last name variables and want to render the full name on the page in multiple places. If you write `{{ firstName + \' \' + lastName }}` directly in the template, you repeat calculations and clutter the template code. Vue solves this with the `computed()` API.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, computed } from \'vue\'\nconst firstName = ref(\'Satyam\')\nconst lastName = ref(\'Kumar\')\n\nconst fullName = computed(() => {\n  return firstName.value + \' \' + lastName.value\n})\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch1\x3e{{ fullName }}\x3c/h1\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Why Not Use a Normal Function?\nWhy use `computed()` instead of a standard JavaScript function like `fullName()`? The answer is **Caching**. Computed properties are cached based on their reactive dependencies. A computed property will only re-evaluate when some of its reactive dependencies change. If the dependencies do not change, accessing the computed property returns the cached result immediately, which is crucial for expensive list-filtering and sorting operations.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, computed } from \'vue\'\nconst count = ref(0)\n\n// Computed is cached. Only runs once when accessed multiple times:\nconst doubleCount = computed(() => {\n  console.log(\'computed running\')\n  return count.value * 2\n})\n\n// Method version. Runs every single render:\nfunction getDoubleCount() {\n  console.log(\'method running\')\n  return count.value * 2\n}\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### How Computed Knows When to Recalculate\nVue automatically tracks which reactive variables are accessed inside the computed getter function. If one of those variables (e.g. `count.value`) updates, Vue invalidates the cached value and triggers a recalculation the next time the computed property is read.'
          },
          {
            type: 'paragraph',
            text: '### Common Use Cases\n* **Search Filtering**: Reactively filtering list arrays based on search inputs.\n* **Shopping Carts**: Summing pricing items to show cart totals.\n* **Writable Computed**: Creating two-way computed properties by defining both a `get` and a `set` method (e.g., parsing a full name back into first and last name components).'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, computed } from \'vue\'\nconst search = ref(\'\')\nconst users = ref([\'Satyam\', \'Rahul\', \'Aman\'])\n\n// Search filtering computed property\nconst filteredUsers = computed(() => {\n  return users.value.filter(u => \n    u.toLowerCase().includes(search.value.toLowerCase())\n  )\n})\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cinput v-model=\"search\" placeholder=\"Search...\"\x3e\n  \x3cli v-for=\"u in filteredUsers\" :key=\"u\"\x3e{{ u }}\x3c/li\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Writable Computed Example\nAlthough computed properties are read-only by default, they can be made writable by providing both `get` and `set` options:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, computed } from \'vue\'\nconst firstName = ref(\'Satyam\')\nconst lastName = ref(\'Kumar\')\n\nconst fullName = computed({\n  get() {\n    return firstName.value + \' \' + lastName.value\n  },\n  set(newValue) {\n    const parts = newValue.split(\' \')\n    firstName.value = parts[0]\n    lastName.value = parts[1] || \'\'\n  }\n})\n\n// Triggers set() and updates firstName/lastName:\nfullName.value = \'Rahul Sharma\'\n\x3c/script\x3e'
},
          {
            type: 'table',
            headers: ['Aspect', 'Computed Properties', 'Watchers (watch)'],
            rows: [
              ['Purpose', 'Derive state values from other reactive states', 'Perform side-effects in response to state changes'],
              ['Return Value', 'Must return a value (sync)', 'Returns nothing (handles actions)'],
              ['Caching', 'Yes, cached until dependencies change', 'No, executes side effects directly'],
              ['Examples', 'Cart totals, filtered lists, formatted strings', 'API requests, writing to localStorage, analytics tracking']
            ]
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Performing side-effects inside computed properties (e.g. making API calls or updating localStorage). Computed properties should only be pure functions returning derived state. Use watchers for side effects. <br>• **Mistake 2**: Mutating computed properties directly (e.g. `doubleCount.value = 10`) when they are read-only. <br>• **Mistake 3**: Calling the computed property like a function in templates (e.g. writing `{{ fullName() }}`). Access them as values: `{{ fullName }}`.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If `count = ref(5)` and `doubleCount = computed(() => count.value * 2)`, what is the value? ➔ `10` \n2. What is the main performance benefit of computed properties over methods? ➔ Caching (they only recalculate when dependencies change). \n3. Which is better for updating local storage after a state changes: computed or watch? ➔ Watch, because updating local storage is a side-effect.'
          }
        ]
      },
      {
        id: 'vue_10',
        title: '11. Watchers',
        sections: [
          {
            type: 'paragraph',
            text: 'While computed properties are ideal for deriving values, you will often need to perform **side effects** (actions) in response to state changes. Examples include making an API call when search query changes, saving settings to local storage, routing paths, or logging analytics. In Vue, these tasks are handled by **Watchers**.'
          },
          {
            type: 'paragraph',
            text: '### The Problem\nImagine you have a search box input linked to a reactive search string. Whenever the user types, you want to query a database. If you use a computed property, you are executing side effects inside a getter, which can cause performance loops and violates standard reactive rules. Vue solves this with the `watch()` API.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, watch } from \'vue\'\nconst count = ref(0)\n\n// A basic watcher listening for count changes\nwatch(count, (newValue, oldValue) => {\n  console.log(`Count changed from ${oldValue} to ${newValue}`)\n})\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Watching Multiple Sources or Computed Values\nYou can watch multiple reactive variables simultaneously by passing an array of sources. You can also watch computed properties directly:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, watch } from \'vue\'\nconst firstName = ref(\'Satyam\')\nconst lastName = ref(\'Kumar\')\n\nwatch([firstName, lastName], ([newFirst, newLast], [oldFirst, oldLast]) => {\n  console.log(`First name: ${oldFirst} -> ${newFirst}`)\n  console.log(`Last name: ${oldLast} -> ${newLast}`)\n})\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Watching Reactive Object Properties\nIf you watch a property of a reactive object (e.g. `user.name`), you cannot pass it directly because it is a string/primitive and not a reactive source. Instead, you must pass a **getter function** returning the property value:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { reactive, watch } from \'vue\'\nconst user = reactive({ name: \'Satyam\', age: 20 })\n\n// Correct way: using a getter function\nwatch(() => user.name, (newName) => {\n  console.log(`Name changed to: ${newName}`)\n})\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Deep and Immediate Options\nBy default, watchers only trigger when the watched source is replaced and do not run on initial load. You can configure this behavior with options:\n\n* `deep: true` : Recursively watches nested properties of reactive objects.\n* `immediate: true` : Executes the watcher callback immediately when the component mounts, rather than waiting for the first state modification.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, watch } from \'vue\'\nconst userId = ref(1)\n\nasync function fetchUser(id) {\n  const res = await fetch(`/api/users/${id}`)\n  console.log(await res.json())\n}\n\n// Runs immediately on mount and whenever userId changes:\nwatch(userId, (newId) => fetchUser(newId), { immediate: true })\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### watchEffect()\nVue provides a simplified watcher called `watchEffect()`. Unlike `watch()`, you do not specify the source to watch. Instead, Vue automatically tracks any reactive variables accessed inside the callback function and executes the callback immediately on mount and whenever those variables change.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref, watchEffect } from \'vue\'\nconst count = ref(0)\nconst theme = ref(\'light\')\n\n// Runs immediately, registers dependencies automatically:\nwatchEffect(() => {\n  console.log(`Current state: count=${count.value}, theme=${theme.value}`)\n})\n\x3c/script\x3e'
          },
          {
            type: 'table',
            headers: ['Feature', 'watch()', 'watchEffect()'],
            rows: [
              ['Explicit Dependencies', 'Yes, must pass source(s) as first parameter', 'No, auto-detected inside callback'],
              ['Initial Run', 'Only runs on change (unless immediate:true is set)', 'Always runs immediately on mount'],
              ['Access to Old Value', 'Yes, passed as callback parameter', 'No access to previous values'],
              ['Complexity', 'Better for precise dependency control', 'Better for simple immediate effects tracking multiple variables']
            ]
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Using a watcher when a computed property is more appropriate. Derived values (e.g. fullName) should be computed properties. <br>• **Mistake 2**: Attempting to watch primitive object fields directly (e.g. `watch(user.name, ...)`) without wrapping in a getter function. <br>• **Mistake 3**: Putting async actions/fetch requests inside computed properties instead of watchers.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. Which hook should be used to fetch initial list data when opening a page? ➔ `onMounted()` \n2. What happens to a `setInterval` timer if a component is unmounted without clearing it? ➔ It keeps running in the background, causing a memory leak. \n3. Arrange the hooks in chronological order: `onUpdated`, `onMounted`, `setup`, `onUnmounted`. ➔ `setup` ➔ `onMounted` ➔ `onUpdated` ➔ `onUnmounted`.'
          }
        ]
      },
      {
        id: 'vue_12',
        title: '13. Vue Components',
        sections: [
          {
            type: 'paragraph',
            text: 'Everything in a Vue application is built out of **Components**. Instead of writing one massive, monolithic HTML page, component-based thinking involves breaking down your user interface into small, encapsulated, reusable pieces containing their own template markup, scripts, and styling rules.'
          },
          {
            type: 'paragraph',
            text: '### The Problem\nImagine building YouTube without components: you would have to write duplicate markup blocks for hundreds of different video recommendations. If you need to tweak the design of a video card, you would have to update it in a hundred places. Vue solves this by organizing applications into **Component Trees**.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- src/components/UserCard.vue (Child) --\x3e\n\x3cscript setup\x3e\n// Custom child component logic\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv class=\"user-card\"\x3e\n    \x3ch3\x3eUser Card\x3c/h3\x3e\n  \x3c/div\x3e\n\x3c/template\x3e\n\n\x3cstyle scoped\x3e\n.user-card {\n  border: 1px solid #ccc;\n  padding: 10px;\n}\n\x3c/style\x3e'
          },
          {
            type: 'paragraph',
            text: '### Importing and Using Components\nTo use a component inside another component (e.g. inside `App.vue`), you import the `.vue` file and render it like a custom HTML tag:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport UserCard from \'./components/UserCard.vue\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3c!-- Reusable component instances --\x3e\n  \x3cUserCard /\x3e\n  \x3cUserCard /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Component Relationships\nComponents build a hierarchy known as the **Component Tree**. A component that renders another is the **Parent**, and the rendered component is the **Child**. Each child component instance maintains its own independent state and lifecycle.'
          },
          {
            type: 'paragraph',
            text: '### Naming and Syntax Conventions\n* **PascalCase**: Component filenames and template tags should use PascalCase (e.g. `FighterCard.vue` and `\x3cFighterCard /\x3e`), making them easily distinguishable from standard HTML5 tags.\n* **Self-Closing Tags**: Use self-closing tags (e.g. `\x3cUserCard /\x3e`) for child components that do not receive nested slot elements.\n* **Scoped Styles**: Use the `scoped` attribute on the component `<style>` tag to ensure CSS rules do not bleed out and affect parents or siblings.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport FighterCard from \'./components/FighterCard.vue\'\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3c!-- PascalCase self-closing fighter tags --\x3e\n  \x3cFighterCard /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'callout',
            title: 'Components vs Functions',
            text: '• **Functions** receive arguments, perform operations, and return output values. <br>• **Components** are much richer: they compile to Virtual DOM render structures, maintain reactive local state, run custom lifecycle hooks (like `onMounted`), receive styles, and emit custom events.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Putting the entire application structure in a single massive file (e.g., `App.vue` or `notes.vue`!). Split pages into components. <br>• **Mistake 2**: Creating tiny two-line components too early; not every minor markup block needs its own separate component. <br>• **Mistake 3**: Duplicating identical UI sections instead of refactoring them into a single reusable component.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a component page has a Navbar, Sidebar, FighterCard lists, and a Footer, what represents the parent component? ➔ The main page component container. \n2. What is the standard casing convention for Vue components? ➔ PascalCase. \n3. How do you ensure that component style rules do not bleed out to other files? ➔ Use the `<style scoped>` attribute tag.'
          }
        ]
      },
      {
        id: 'vue_13',
        title: '14. Component Props',
        sections: [
          {
            type: 'paragraph',
            text: 'While components let us modularize our UI, they need to display different data in different places. This is achieved using **Props**, which are custom attributes passed from a parent component down to a child component. Props establish a **One-Way Data Flow** from parent to child.'
          },
          {
            type: 'paragraph',
            text: '### What Are Props?\nProps are data parameters passed down the component tree. Think of ordering food: the restaurant (Parent) sends an order list down to the chef (Child). The child doesn\'t decide what elements go on the plate; they receive the orders as static parameters.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- src/components/UserCard.vue (Child) --\x3e\n\x3cscript setup\x3e\n// defineProps is a compiler macro (no import needed)\nconst props = defineProps({\n  name: String,\n  age: Number\n})\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv class=\"card\"\x3e\n    \x3ch2\x3e{{ props.name }}\x3c/h2\n    \x3cp\x3eAge: {{ props.age }}\x3c/p\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Parent Component Usage\nThe parent component passes props using either static HTML attributes or dynamic reactive bindings with the `:` (shorthand for `v-bind`) directive:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport UserCard from \'./UserCard.vue\'\nconst activeAge = 21\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3c!-- Static prop --\x3e\n  \x3cUserCard name=\"Satyam\" :age=\"21\" /\x3e\n\n  \x3c!-- Dynamic binding --\x3e\n  \x3cUserCard name=\"Aman\" :age=\"activeAge\" /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Props Are Read-Only\nThis is a critical rule: a child component must **never mutate** its props directly (e.g. `props.name = \'Rahul\'`). Doing so violates the one-way data flow model and triggers a Vue warning. If the child needs to edit the value locally, it should copy the prop to a local ref variable: `const localName = ref(props.name)`.'
          },
          {
            type: 'paragraph',
            text: '### Prop Validation & Default Values\nYou can enforce types, make props mandatory, or define fallback default values inside the child component:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nconst props = defineProps({\n  name: {\n    type: String,\n    required: true\n  },\n  title: {\n    type: String,\n    default: \'Learner\'\n  }\n})\n\x3c/script\x3e'
          },
          {
            type: 'table',
            headers: ['Aspect', 'Static Attribute', 'V-Bind (:) Attribute'],
            rows: [
              ['Example Syntax', 'name="Satyam"', ':age="21" or :user="userObj"'],
              ['Evaluation', 'Passed literally as a raw string value', 'Evaluated as a JavaScript expression'],
              ['Data Types', 'Strings only', 'Numbers, Booleans, Objects, Arrays, or variables']
            ]
          },
          {
            type: 'callout',
            title: 'What is Prop Drilling?',
            text: 'Passing the same prop through multiple layers of components (e.g., App ➔ Page ➔ List ➔ Card ➔ Avatar) is called **Prop Drilling**. It clutters intermediate components that do not actually need the data. As application complexity grows, prop drilling should be replaced with global state stores like **Pinia**.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Attempting to modify a prop inside child components: `props.name = "Arav"` triggers runtime console warnings. <br>• **Mistake 2**: Forgetting the `:` colon for numbers or booleans (e.g. `<UserCard age="21">` passes the string `"21"`, not the number `21`). <br>• **Mistake 3**: Importing `defineProps` from Vue. It is a compiler macro and is globally available without imports.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If you pass `age="25"` to a child component, what data type will it have inside the child? ➔ String. \n2. Can a child component modify its own props directly? ➔ No, props are read-only. \n3. What is the role of `required: true`? ➔ It throws a console warning if the parent component fails to supply that specific prop attribute.'
          }
        ]
      },
      {
        id: 'vue_14',
        title: '15. Component Emits',
        sections: [
          {
            type: 'paragraph',
            text: 'Props let parents send data down to children, establishing a one-way flow. But what if a child needs to communicate back up to its parent? For instance, clicking a delete button inside a list item should tell the parent to remove that item. Since child components cannot directly modify parent state, Vue solves this using **Emits** via `defineEmits()`.'
          },
          {
            type: 'paragraph',
            text: '### Props vs Emits: The Communication Loop\nThink of props as instructions flowing downward, and emits as notifications rising upward:\n\n```text\nParent\n  ↓ props (data down)\nChild\n  ↑ emits (events up)\nParent\n```'
          },
          {
            type: 'paragraph',
            text: '### Your First Emit\nTo send a custom event up, define it in the child component using `defineEmits()`. This is a compiler macro, meaning you don\'t need to import it.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- CounterButton.vue (Child) --\x3e\n\x3cscript setup\x3e\n// Define custom events this component can broadcast\nconst emit = defineEmits([\'increment\'])\n\nfunction handleClick() {\n  emit(\'increment\') // Broadcast event\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"handleClick\"\x3e\n    Increment\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'In the parent component, listen to the custom event using `@` (shorthand for `v-on`), just like a native browser event:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- App.vue (Parent) --\x3e\n\x3cscript setup\x3e\nimport { ref } from \'vue\'\nimport CounterButton from \'./CounterButton.vue\'\n\nconst count = ref(0)\nfunction increment() {\n  count.value++\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3ch2\x3eCount: {{ count }}\x3c/h2\x3e\n  \x3c!-- Listen to the custom increment event --\x3e\n  \x3cCounterButton @increment=\"increment\" /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Passing Data (Payloads) with Emits\nMost real-world events carry a payload. You can pass any JavaScript variable, object, or array as additional parameters to the `emit()` function:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Child Component --\x3e\n\x3cscript setup\x3e\nconst emit = defineEmits([\'save\'])\n\nfunction saveUser() {\n  emit(\'save\', { id: 1, name: \'Satyam\' }) // Event with payload object\n}\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: 'The parent component automatically receives the payload as the first parameter of the event handler method:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Parent Component --\x3e\n\x3cscript setup\x3e\nfunction handleSave(user) {\n  console.log(\'Saved user:\', user.name) // Logs "Satyam"\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cUserForm @save=\"handleSave\" /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Props and Emits Together\nCombining props and emits is the absolute standard for building interactive child components. For example, in a Todo List, the parent passes the todo details down via props, and the child signals when to delete it via emits.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- TodoItem.vue (Child) --\x3e\n\x3cscript setup\x3e\nconst props = defineProps({\n  todo: Object\n})\nconst emit = defineEmits([\'delete\'])\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv\x3e\n    \x3cspan\x3e{{ todo.text }}\x3c/span\x3e\n    \x3cbutton @click=\"emit(\'delete\', todo.id)\"\x3e\n      Delete\n    \x3c/button\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'In the parent, you render lists of child components, listening to each instance\'s events:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- TodoList.vue (Parent) --\x3e\n\x3cscript setup\x3e\nimport { ref } from \'vue\'\nimport TodoItem from \'./TodoItem.vue\'\n\nconst todos = ref([\n  { id: 1, text: \'Learn Vue Props\' },\n  { id: 2, text: \'Learn Vue Emits\' }\n])\n\nfunction removeTodo(id) {\n  todos.value = todos.value.filter(t => t.id !== id)\n}\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cTodoItem \n    v-for=\"todo in todos\" \n    :key=\"todo.id\" \n    :todo=\"todo\"\n    @delete=\"removeTodo\"\n  /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Real-World Case Study: Placement Portal & UFC App\nIn production, UI elements like a fighter card or job listing are encapsulated child components. Clicking "Apply" or "Add to Favorites" passes the item ID up to update parent arrays.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- FighterCard.vue (Child) --\x3e\n\x3cscript setup\x3e\nconst props = defineProps({ fighter: Object })\nconst emit = defineEmits([\'favorite\'])\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv\x3e\n    \x3ch3\x3e{{ fighter.name }}\x3c/h3\x3e\n    \x3cbutton @click=\"emit(\'favorite\', fighter.id)\"\x3e\n      ⭐ Favorite\n    \x3c/button\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'table',
            headers: ['Communication Channel', 'Direction', 'Mechanism', 'State Ownership'],
            rows: [
              ['Props', 'Parent ➔ Child', 'Passed as attributes (`:name=\"val\"`)', 'Parent (Read-only for Child)'],
              ['Emits', 'Child ➔ Parent', 'Triggered via `emit(\'eventName\', payload)`', 'Parent (Parent decides updates)'],
              ['Pinia Store', 'Global (Any Component)', 'Central state store access via store action methods', 'Centralized Store']
            ]
          },
          {
            type: 'callout',
            title: 'Event Naming Conventions',
            text: 'Keep event names short, lowercase, and simple. Standard verbs are preferred:\n* `save`, `delete`, `submit`, `update`, `close`, `open`, `favorite`, `login`, `logout`'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Mutating parent props directly (e.g. `props.count++`) instead of emitting a request event up. <br>• **Mistake 2**: Importing `defineEmits` from Vue. Just like `defineProps`, it is a compiler macro available globally. <br>• **Mistake 3**: Using emits to pass data across deeply nested sibling components (prop drilling in reverse). For global messaging, use **Pinia**.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a child emits `emit(\'delete\', 10)` and parent has `@delete=\"removeUser\"`, what value does `removeUser(id)` receive? ➔ `10` \n2. Why should child components not mutate props directly? ➔ It breaks one-way data flow, making state changes unpredictable and hard to track. \n3. Fill in the blanks: Parent passes data down using _____, Child notifies parent upwards using _____. ➔ Props, Emits.'
          }
        ]
      },
      {
        id: 'vue_15',
        title: '16. Component Slots',
        sections: [
          {
            type: 'paragraph',
            text: 'While props let us pass data parameters down to custom child components, we often need to pass rich HTML markup, layouts, or other component structures instead of plain data values. Vue solves this using **Slots**, defined via the `<slot />` element.'
          },
          {
            type: 'paragraph',
            text: '### The Problem\nImagine building a reusable button component: `\x3cBaseButton /\x3e`. If you hardcode the word "Save" inside the button template, you cannot reuse it for "Delete", "Login", or "Cancel". While you could pass the button text as a string prop, this approach is extremely limiting if you want to include icons, loading spinners, or formatted text. Slots allow parents to inject dynamic UI content between component tags.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- BaseButton.vue (Child) --\x3e\n\x3ctemplate\x3e\n  \x3cbutton class=\"btn\"\x3e\n    \x3c!-- Content from the parent will be injected here --\x3e\n    \x3cslot /\x3e\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Now, when utilizing this component, the parent inserts any desired HTML structure or text inside the tags:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Parent Usage --\x3e\n\x3ctemplate\x3e\n  \x3c!-- Simple Text --\x3e\n  \x3cBaseButton\x3eSave\x3c/BaseButton\x3e\n\n  \x3c!-- Rich content with custom icons --\x3e\n  \x3cBaseButton\x3e\n    \x3cIcon name=\"trash\" /\x3e Delete\n  \x3c/BaseButton\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Default (Fallback) Slot Content\nYou can define placeholder content inside the `<slot>` element. If the parent component does not supply any content between the tag container, the fallback content renders automatically:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- BaseButton.vue (Child) --\x3e\n\x3ctemplate\x3e\n  \x3cbutton\x3e\n    \x3cslot\x3eClick Me\x3c/slot\x3e\n  \x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Named Slots\nFor complex layouts (like modular widgets or custom modals), you often need multiple content insertion points. You can define multiple slot elements and give them distinct `name` attributes. Unnamed slots are automatically given the name `default`.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- BaseCard.vue (Child) --\x3e\n\x3ctemplate\x3e\n  \x3cdiv class=\"card\"\x3e\n    \x3cheader class=\"card-header\"\x3e\n      \x3cslot name=\"header\" /\x3e\n    \x3c/header\x3e\n    \x3cmain class=\"card-body\"\x3e\n      \x3cslot /\x3e\n    \x3c/main\x3e\n    \x3cfooter class=\"card-footer\"\x3e\n      \x3cslot name=\"footer\" /\x3e\n    \x3c/footer\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'In the parent component, you target these specific slots using `<template #slotName>` (where `#` is the shorthand for `v-slot:`):'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Parent Usage --\x3e\n\x3ctemplate\x3e\n  \x3cBaseCard\x3e\n    \x3ctemplate #header\x3e\n      \x3ch2\x3eUFC Fighter Profile\x3ch2\x3e\n    \x3c/template\x3e\n\n    \x3cp\x3eFighter: Islam Makhachev\x3c/p\x3e\n    \x3cp\x3eDivision: Lightweight\x3c/p\n\n    \x3ctemplate #footer\x3e\n      \x3cbutton\x3eView Full Stats\x3c/button\x3e\n    \x3c/template\x3e\n  \x3c/BaseCard\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Scoped Slots\nBy default, parent slot templates cannot access the child component\'s local reactive state variables. **Scoped Slots** solve this by allowing the child to bind local attributes to the slot element, exposing them back up to the parent:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- UserProvider.vue (Child) --\x3e\n\x3cscript setup\x3e\nconst user = { name: \'Satyam\', role: \'Admin\' }\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3c!-- Bind local user object to slot attributes --\x3e\n  \x3cslot :user=\"user\" /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'The parent component receives this bound state object using destructuring parameters in the `#default` slot directive:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Parent Usage --\x3e\n\x3ctemplate\x3e\n  \x3cUserProvider\x3e\n    \x3ctemplate #default=\"{ user }\"\x3e\n      \x3ch3\x3eWelcome, {{ user.name }} ({{ user.role }})\x3c/h3\x3e\n    \x3c/template\x3e\n  \x3c/UserProvider\x3e\n\x3c/template\x3e'
          },
          {
            type: 'table',
            headers: ['Feature', 'Props', 'Slots'],
            rows: [
              ['Core Purpose', 'Pass data values (strings, arrays, objects) from parent to child', 'Pass structural template markup (HTML, icons, components)'],
              ['Casing / Syntax', 'Attributes: `:disabled=\"flag\"`', 'Nested tags: `\x3cslot\x3e` or `\x3ctemplate #header\x3e`'],
              ['Flexibility', 'Low (limited to static types supported by JS)', 'High (supports arbitrary custom layouts and component nodes)'],
              ['Best Used For', 'Component configuration settings, form states, raw textual content', 'Card layouts, dashboard widgets widgets, generic lists, data tables']
            ]
          },
          {
            type: 'callout',
            title: 'Mental Model of Component Communication',
            text: 'Think of Vue components as modular layout chips:\n* **Props**: Inputs to modify component data configuration.\n* **Slots**: Inputs to customize nested markup layout structure.\n* **Emits**: Output alerts notifying parents of actions.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Attempting to pass HTML blocks via a prop string (e.g. `<Card title="<h1>Title</h1>">`). Use slots for HTML. <br>• **Mistake 2**: Forgetting the `#` symbol or using invalid template names when targeting named slots. <br>• **Mistake 3**: Confusing scoped slot props with parent variables. Always verify parameter names in the `#default="{ key }"` destructuring expression.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a child component has `<button><slot>Save</slot></button>` and parent uses `<BaseButton>Cancel</BaseButton>`, what text is rendered? ➔ `Cancel` \n2. What is the shorthand syntax for `v-slot:header`? ➔ `#header` \n3. Which slot type allows children to pass internal state back to parent slot templates? ➔ Scoped Slots.'
          }
        ]
      },
      {
        id: 'vue_16',
        title: '17. Provide / Inject',
        sections: [
          {
            type: 'paragraph',
            text: 'As applications scale, you will encounter scenarios where deeply nested child components need data from high-level ancestors. For example, rendering an user avatar inside a header navigation bar that sits inside a dashboard. Passing this user data down through every intermediate component (Prop Drilling) makes components brittle and clutters code. Vue solves this using **Provide / Inject**.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Prop Drilling\nImagine a deep hierarchy where only the leaf node needs a `theme` parameter, yet every parent along the way must receive and re-forward it:\n\n```text\nApp (has state: theme)\n  ↓ theme prop\nNavbar\n  ↓ theme prop\nUserMenu\n  ↓ theme prop\nAvatar (uses: theme)\n```\nThis requires useless boilerplate at every intermediate layer. With Provide/Inject, the ancestor makes data available to all its descendants, allowing them to pull it directly.'
          },
          {
            type: 'paragraph',
            text: '### Your First Provide & Inject\nThe ancestor component uses the `provide()` function to register data. The key is typically a string, and the second parameter is the data value:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- App.vue (Ancestor) --\x3e\n\x3cscript setup\x3e\nimport { provide } from \'vue\'\nimport Navbar from \'./Navbar.vue\'\n\n// Provide a username string with key \'username\'\nprovide(\'username\', \'Satyam\')\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cNavbar /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Any descendant component, regardless of how deep it sits, can access this value using the `inject()` function:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Avatar.vue (Deep Descendant) --\x3e\n\x3cscript setup\x3e\nimport { inject } from \'vue\'\n\n// Inject username using the same key\nconst username = inject(\'username\')\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cspan\x3e{{ username }}\x3c/span\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Reactive Provide\nBy default, providing a plain primitive value (like a number or string) is not reactive. If the ancestor modifies the variable, the descendants will not receive updates. To establish a reactive link, you must wrap the data in a `ref()` or `reactive()` object before providing it:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Parent.vue --\x3e\n\x3cscript setup\x3e\nimport { ref, provide } from \'vue\'\n\nconst theme = ref(\'light\')\n// Provide the reactive ref wrapper\nprovide(\'theme\', theme)\n\nfunction toggleTheme() {\n  theme.value = theme.value === \'light\' ? \'dark\' : \'light\'\n}\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: 'In the descendant, the injected property resolves to the same reactive ref, so the template updates automatically whenever the parent toggles the theme:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Child.vue --\x3e\n\x3cscript setup\x3e\nimport { inject } from \'vue\'\nconst theme = inject(\'theme\')\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv :class=\"theme\"\x3e\n    Current Theme: {{ theme }}\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Providing Objects & Fallback Defaults\nProviding reactive objects is very common. You can also define default fallback values in `inject()` to prevent application crashes if a provider is missing:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// In Child Component:\n// If no ancestor provides \'theme\', fallback to \'light\'\nconst theme = inject(\'theme\', \'light\')'
          },
          {
            type: 'paragraph',
            text: '### Using Symbol Keys for Large Apps\nIn large applications with many features, separate packages might accidentally overwrite string keys. To prevent key collisions, define keys using JavaScript Symbols:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// keys.js\nexport const USER_KEY = Symbol(\'user\')\n\n// Parent.vue\nimport { USER_KEY } from \'./keys\'\nprovide(USER_KEY, userRef)\n\n// Child.vue\nimport { USER_KEY } from \'./keys\'\nconst user = inject(USER_KEY)'
          },
          {
            type: 'table',
            headers: ['State Mechanism', 'Scope', 'Best Use Cases', 'Limitation'],
            rows: [
              ['Props', 'Direct Parent-to-Child only', 'Configuring local widget details, passing variables one level down', 'Becomes cluttered when drilling deep'],
              ['Provide / Inject', 'Ancestor-to-Descendant subtree', 'Theme styling, Form layout contexts, plugin configuration dependencies', 'Restricted to component tree hierarchy'],
              ['Pinia Store', 'Global (Any Component anywhere)', 'User authorization, shopping cart items, cross-page global states', 'Adds slight configuration overhead for simple apps']
            ]
          },
          {
            type: 'callout',
            title: 'Provide/Inject vs Pinia',
            text: '• **Provide/Inject** is restricted to subtrees. Sibling components (like a Sidebar and a Header Navbar) cannot share state via Provide/Inject unless they wrap them inside a common parent shell. <br>• **Pinia** is completely decoupled from the component layout tree. Any component can access the store directly.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Providing a raw primitive instead of a `ref` (e.g. `provide(\'key\', value)` where value is a string). <br>• **Mistake 2**: Trying to inject data inside a sibling component that doesn\'t descend from the provider. <br>• **Mistake 3**: Typos in string keys. String keys are case-sensitive (\'theme\' !== \'Theme\').'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. Can a sibling component inject data provided by its sister sibling? ➔ No, it must descend from the provider. \n2. What is the value of an injected key if no ancestor provides it and no default fallback is set? ➔ `undefined`. \n3. How do large apps prevent naming collisions on keys? ➔ By using JavaScript Symbols.'
          }
        ]
      },
      {
        id: 'vue_17',
        title: '18. Dynamic Components & KeepAlive',
        sections: [
          {
            type: 'paragraph',
            text: 'In rich interactive applications, you will often need to switch between different views, tabs, or settings panels on the same page. While using multiple `v-if` branches works for small projects, it quickly becomes unmaintainable as panels grow. Vue provides a dedicated `<component :is=\"...\" />` helper for **Dynamic Component Swapping**, which can be paired with `<KeepAlive>` to cache inactive state values.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Naive v-if Tabs\nSuppose you are building a dashboard tab system with a Profile Tab, Settings Tab, and Security Tab. A standard approach using `v-if` looks like this:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Naive tab structure --\x3e\n\x3ctemplate\x3e\n  \x3cProfilePanel v-if=\"tab === \'profile\'\" /\x3e\n  \x3cSettingsPanel v-if=\"tab === \'settings\'\" /\x3e\n  \x3cSecurityPanel v-if=\"tab === \'security\'\" /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'While this works, it becomes repetitive and cluttered if you have 10 or 20 tabs. Dynamic components resolve this boilerplate.'
          },
          {
            type: 'paragraph',
            text: '### Dynamic Components via component tag\nVue provides a special `<component>` tag with an `:is` binding. You pass the imported component constructor variable or a string (like \'div\' or \'span\') directly to `:is`:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\nimport ProfilePanel from \'./ProfilePanel.vue\'\nimport SettingsPanel from \'./SettingsPanel.vue\'\n\n// Store the component definition reference directly in a ref\nconst currentTab = ref(ProfilePanel)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"currentTab = ProfilePanel\"\x3eProfile\x3c/button\x3e\n  \x3cbutton @click=\"currentTab = SettingsPanel\"\x3eSettings\x3c/button\x3e\n\n  \x3c!-- Renders whichever component is currently stored in currentTab --\x3e\n  \x3ccomponent :is=\"currentTab\" /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Swapping String HTML Elements\nYou can also pass standard HTML tag strings to `:is` to conditionally toggle element node containers dynamically:\n\n`\x3ccomponent :is=\"\'div\'\"\x3eHello\x3c/component\x3e` renders `\x3cdiv\x3eHello\x3c/div\x3e`.'
          },
          {
            type: 'paragraph',
            text: '### The State Destruction Catch\nWhen switching dynamic components (e.g. from `ProfilePanel` to `SettingsPanel`), Vue completely **destroys** the old component instance. If the user typed input text or filled out fields in the Profile Panel, switching tabs and returning resets the component, erasing all entries. Vue solves this UX issue with `<KeepAlive>`.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Wrap dynamic components to preserve state --\x3e\n\x3ctemplate\x3e\n  \x3cKeepAlive\x3e\n    \x3ccomponent :is=\"currentTab\" /\x3e\n  \x3c/KeepAlive\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'With `<KeepAlive>`, instead of being destroyed, inactive components are **cached in memory** and deactivated. When the user switches back, Vue restores the active instance exactly as it was left.'
          },
          {
            type: 'paragraph',
            text: '### Cached Component Lifecycles: onActivated & onDeactivated\nBecause cached components are not destroyed or rebuilt when switching, standard hooks like `onMounted` and `onUnmounted` do not execute on swaps. Vue provides two dedicated hooks for KeepAlive components:\n\n* `onActivated()` : Triggers whenever the component is retrieved from the cache and shown on the page.\n* `onDeactivated()` : Triggers whenever the component is swapped out and placed back in the cache.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { onActivated, onDeactivated } from \'vue\'\n\nonActivated(() => {\n  console.log(\'Profile component is now visible\')\n})\nonDeactivated(() => {\n  console.log(\'Profile component is cached in background\')\n})\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Configuring Cache Limits: Include, Exclude, and Max\nYou can fine-tune caching behavior using attributes:\n* `include` : List of components to cache (comma-separated string or regex).\n* `exclude` : List of components to never cache.\n* `:max` : Limit the maximum number of component instances kept in memory (oldest cached components are destroyed when the limit is exceeded).'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cKeepAlive :max=\"5\" exclude=\"SecurityPanel\"\x3e\n  \x3ccomponent :is=\"currentTab\" /\x3e\n\x3c/KeepAlive\x3e'
          },
          {
            type: 'table',
            headers: ['Mechanism', 'Primary Use Case', 'Routing / History', 'Ideal Layout Scenarios'],
            rows: [
              ['Dynamic Components', 'Toggling views on the same page', 'No browser URL change or history tracking', 'Tab systems, dashboard panels, multi-step form wizards'],
              ['Vue Router', 'Navigating between separate pages', 'Updates browser URL, supports back/forward history navigation', 'Authentication flows, separate main dashboard pages, user profile routes']
            ]
          },
          {
            type: 'callout',
            title: 'When to Use KeepAlive',
            text: 'Use KeepAlive to cache user form entries (e.g. multi-step registration forms), active document tabs, search filters, or heavy charts that should not reload from scratch. Avoid caching static components to conserve device memory.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Caching everything using KeepAlive, which wastes system memory on static, lightweight views. <br>• **Mistake 2**: Using dynamic components for main site pages instead of Vue Router (which breaks browser back-navigation). <br>• **Mistake 3**: Expecting standard `onMounted()` to run on every tab click inside KeepAlive. Use `onActivated()` instead.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. Does a dynamic component inside `<KeepAlive>` trigger `onUnmounted()` when swapped out? ➔ No, it triggers `onDeactivated()`. \n2. What attribute limits the maximum number of components KeepAlive holds in cache? ➔ `max` (e.g., `:max=\"5\"`). \n3. Which mechanism should be used for a multi-step registration wizard where clicking \"Back\" must preserve fields? ➔ Dynamic Components + KeepAlive.'
          }
        ]
      },
      {
        id: 'vue_18',
        title: '19. Async Components & Code Splitting',
        sections: [
          {
            type: 'paragraph',
            text: 'As your applications grow in complexity, the size of your JavaScript bundles increases. If a single page needs large charting libraries or formatting engines, standard import chains force users to download the entire application code on initial startup—even if they only visit a simple login page. Senior frontend engineers optimize performance by utilizing **Async Components** to achieve **Code Splitting**.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Monolithic Bundles\nWhen you compile a standard Vue application, the bundler (Vite) compiles all `.vue` and `.js` source files into a few highly compressed output files (bundles). If you have pages like `/admin` or `/analytics` with heavy components, their large size degrades initial load speeds for regular users who never visit those pages.'
          },
          {
            type: 'paragraph',
            text: '### The Solution: defineAsyncComponent()\nVue solves this via `defineAsyncComponent()`, which instructs Vue to lazy-load the component file over the network only when it is actually rendered on screen.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { defineAsyncComponent } from \'vue\'\n\n// Normal import: loaded immediately at startup\n// import HeavyChart from \'./HeavyChart.vue\'\n\n// Async import: loaded only when rendered\nconst HeavyChart = defineAsyncComponent(() => \n  import(\'./HeavyChart.vue\') // Dynamic import\n)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cHeavyChart /\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Managing Loading and Error States\nBecause downloading files takes time, users need visual feedback. `defineAsyncComponent()` supports options to display spinners, show fallback error states, set delays, or trigger timeouts:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'const HeavyChart = defineAsyncComponent({\n  // The loader function returning a dynamic import promise\n  loader: () => import(\'./HeavyChart.vue\'),\n\n  // Component to display while loading (e.g. LoadingSpinner.vue)\n  loadingComponent: LoadingSpinner,\n\n  // Component to display if download fails (e.g. ErrorMessage.vue)\n  errorComponent: ErrorMessage,\n\n  // Delay before showing loadingComponent (default: 200ms)\n  delay: 200,\n\n  // Timeout limit in milliseconds. If exceeded, errorComponent renders (default: Infinity)\n  timeout: 5000\n})'
          },
          {
            type: 'paragraph',
            text: '### Route-Based Code Splitting\nRoute-based splitting is the most impactful way to optimize performance. In your routing configuration, replace static imports with dynamic arrow imports. Vite automatically splits these files into separate chunks that download on demand:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// router.js\nconst routes = [\n  {\n    path: \'/\',\n    component: () => import(\'./Home.vue\') // Lazy loaded chunk\n  },\n  {\n    path: \'/admin\',\n    component: () => import(\'./Admin.vue\') // Split chunk loaded on demand\n  }\n]'
          },
          {
            type: 'table',
            headers: ['Optimization Method', 'Primary Purpose', 'Vite Bundle Output', 'Ideal Scenarios'],
            rows: [
              ['Normal Import', 'Load core elements immediately', 'Combined into main bundle chunk (app.js)', 'Navbar, Sidebar, primary login views, lightweight widgets'],
              ['Async Component', 'Lazy-load views inside a single page', 'Split into a separate on-demand chunk', 'Heavy analytics maps, document editors, rare charts'],
              ['Router Code Splitting', 'Lazy-load separate route pages', 'Split into route-based chunks (e.g. admin.chunk.js)', 'All subpage views (/jobs, /profile, /admin)']
            ]
          },
          {
            type: 'callout',
            title: 'Vite and Code Splitting',
            text: 'You do not need to configure complex Webpack rules. When Vite detects the `import(\'...\')` syntax, it automatically handles code splitting, generating optimized asset chunks during production build output.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Async-loading tiny, basic components (like `BaseButton.vue`), which increases network requests and degrades performance. <br>• **Mistake 2**: Leaving heavy views statically imported, bloating the main initial bundle. <br>• **Mistake 3**: Not configuring fallback loading components, causing a blank layout flash during page loads.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. When does Vue download the code for a component declared with `defineAsyncComponent`? ➔ When it is first rendered on screen. \n2. Which tool automatically splits code when it detects dynamic imports? ➔ Vite (or your bundler). \n3. Arrange in order of loading speed (best to worst): monolithic bundle, route-split bundle. ➔ Route-split bundle ➔ Monolithic bundle.'
          }
        ]
      },
      {
        id: 'vue_19',
        title: '20. Component Teleport',
        sections: [
          {
            type: 'paragraph',
            text: 'Sometimes, parts of a component\'s template logically belong inside the component, but visually need to be rendered elsewhere in the DOM tree. The classic example is a full-screen confirmation modal or alert toast. If nested inside layout elements, parent rules (like `overflow: hidden` or `z-index` stacking context) can clip or hide it. Vue solves this layout problem using the **Teleport** component.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Trapped Modal Containers\nConsider a deep UI component tree structure where a delete confirmation modal sits inside a user card element on a dashboard page:\n\n```text\nApp (has layouts)\n └── Dashboard (has CSS: overflow: hidden)\n      └── UserCard (has CSS: z-index: 1)\n           └── DeleteModal (should cover full screen!)\n```\nBecause HTML rendering follows parent stacking constraints, the modal is trapped inside the UserCard container, getting cut off by the Dashboard\'s `overflow` boundaries. Teleport relocates the DOM nodes to escape this constraint.'
          },
          {
            type: 'paragraph',
            text: '### Teleporting DOM Elements\nWrap your template elements in `<Teleport>` and pass a target query selector (like `to=\"body\"` or `to=\"#modal-container\"`):'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- UserCard.vue (Parent Component) --\x3e\n\x3ctemplate\x3e\n  \x3cdiv class=\"user-card\"\x3e\n    \x3ch3\x3eUser profile\x3c/h3\x3e\n\n    \x3c!-- Renders inside body tag directly, escaping user-card constraints --\x3e\n    \x3cTeleport to=\"body\"\x3e\n      \x3cdiv class=\"modal-overlay\"\x3e\n        \x3ch2\x3eDelete Confirmation\x3ch2\x3e\n      \x3c/div\x3e\n    \x3c/Teleport\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: 'Vue renders the modal markup as a direct child of the HTML `<body>` element, freeing it from the parent card\'s styles, while maintaining the component\'s logical position in the Vue Virtual DOM tree.'
          },
          {
            type: 'paragraph',
            text: '### Logical Covenants Preserved\nTeleport only alters the **physical DOM render location**. It does **NOT** break Vue\'s virtual component tree relationships. This means:\n* **Props** and **Emits** pass normally between parent and child.\n* **Provide / Inject** contexts propagate down successfully.\n* Component reactive state and lifecycles function as if rendered in place.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { ref } from \'vue\'\nconst show = ref(false)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"show = true\"\x3eOpen Dialog\x3c/button\x3e\n\n  \x3cTeleport to=\"body\"\x3e\n    \x3cdiv v-if=\"show\" class=\"dialog\"\x3e\n      \x3cp\x3eAre you sure?\x3c/p\x3e\n      \x3c!-- Emitting normal custom event close to parent --\x3e\n      \x3cbutton @click=\"show = false\"\x3eClose\x3c/button\x3e\n    \x3c/div\x3e\n  \x3c/Teleport\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Targeting Specific DOM Nodes\nYou can target elements other than body, such as custom notification portals. Ensure the target element exists in the HTML page source before the Teleport component mounts:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- HTML container index.html --\x3e\n\x3cdiv id=\"toast-notifications\"\x3e\x3c/div\x3e\n\n\x3c!-- Vue Component --\x3e\n\x3cTeleport to=\"#toast-notifications\"\x3e\n  \x3cdiv class=\"toast-alert\"\x3eSaved successfully!\x3c/div\x3e\n\x3c/Teleport\x3e'
          },
          {
            type: 'paragraph',
            text: '### Disabling Teleport\nYou can conditionally disable teleporting using the `:disabled` prop. When disabled, the template renders in its original placement inside the parent component, which is highly useful for responsive designs or testing:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- Render inline on mobile, but teleport to body on desktop --\x3e\n\x3cTeleport to=\"body\" :disabled=\"isMobile\"\x3e\n  \x3cdiv class=\"popup\"\x3eOverlay Content\x3c/div\x3e\n\x3c/Teleport\x3e'
          },
          {
            type: 'table',
            headers: ['Aspect', 'Standard Render', 'Teleport Render'],
            rows: [
              ['DOM Placement', 'Nested inline within the parent component element container', 'Moved directly to targeted selector (e.g. `body`, `#modals`)'],
              ['CSS Inheritance', 'Inherits constraints, bounds, margins, and overflow values of parent', 'Escapes parent stacking contexts to follow target element rules'],
              ['Props & Emits', 'Fully functional', 'Fully functional (logical hierarchy is completely preserved)'],
              ['Best Used For', 'Normal widgets, tables, card listings, lists, inline form inputs', 'Confirmation modals, overlay popups, toast notifications, floating tooltips']
            ]
          },
          {
            type: 'callout',
            title: 'Multiple Teleport Elements',
            text: 'You can teleport multiple components to the same target container (like `#toast-notifications`). Vue will append them sequentially in the DOM in chronological mount order.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Teleporting to a query selector target that doesn\'t exist in the HTML DOM structure, throwing console reference errors. <br>• **Mistake 2**: Teleporting normal, basic page elements that can be styled correctly with standard CSS. Use Teleport only for overlays escaping parent container bounds. <br>• **Mistake 3**: Assuming props/emits break because the DOM elements moved. Rest assured, the Virtual DOM relationship is untouched.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. Where will a component inside `<Teleport to=\"body\">` render in the DOM? ➔ Direct child of the HTML `<body>` element. \n2. Can a teleported component access parent state variables via Provide / Inject? ➔ Yes, the logical component tree remains unchanged. \n3. What prop disables a Teleport, causing it to render inline? ➔ `:disabled=\"true\"`.'
          }
        ]
      },
      {
        id: 'vue_20',
        title: '21. Composables',
        sections: [
          {
            type: 'paragraph',
            text: 'One of the most revolutionary updates in Vue 3\'s Composition API is the ability to easily reuse stateful logic. In older Vue 2 applications, developers struggled with copy-pasting, giant monolithic components, or messy mixins. Composition API introduces **Composables**, which allow you to package reactive states and methods into clean, explicit, and highly reusable function containers.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Stateful Logic Duplication\nImagine a student Profile Page and a Dashboard Page, both needing to pull database records over the network. Both components define identical loading indicators, data structures, and lifecycle handlers to coordinate API fetches. Copy-pasting this logic results in bloated, difficult-to-maintain files. Composables solve this by extracting the logic.'
          },
          {
            type: 'paragraph',
            text: '### What is a Composable?\nA composable is a function that utilizes Vue\'s Reactivity APIs (like `ref`, `computed`, or lifecycle hooks) to manage state. By convention, composables use camelCase names starting with the prefix `use` (e.g., `useFetch`, `useAuth`, `useCounter`):'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/composables/useCounter.js\nimport { ref } from \'vue\'\n\nexport function useCounter() {\n  const count = ref(0)\n  const increment = () => count.value++\n  const decrement = () => count.value--\n\n  // Return reactive states and methods for the component to use\n  return { count, increment, decrement }\n}'
          },
          {
            type: 'paragraph',
            text: 'In your Vue component, import the composable function and destructure the returned properties to use them directly in scripts and templates:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { useCounter } from \'@/composables/useCounter\'\n\nconst { count, increment, decrement } = useCounter()\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cbutton @click=\"decrement\"\x3e-\x3c/button\x3e\n  \x3cspan\x3e{{ count }}\x3c/span\x3e\n  \x3cbutton @click=\"increment\"\x3e+\x3c/button\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Real-World Composable: useFetch\nHere is a complete, production-ready example of extracting network request flows (loading flags, actual records, and error handlers) into a single reusable helper function:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/composables/useFetch.js\nimport { ref, onMounted } from \'vue\'\n\nexport function useFetch(url) {\n  const data = ref(null)\n  const loading = ref(false)\n  const error = ref(null)\n\n  const fetchData = async () => {\n    try {\n      loading.value = true\n      const res = await fetch(url)\n      data.value = await res.json()\n    } catch (err) {\n      error.value = err\n    } finally {\n      loading.value = false\n    }\n  }\n\n  onMounted(fetchData)\n  return { data, loading, error, fetchData }\n}'
          },
          {
            type: 'paragraph',
            text: '### Independent Caching vs Shared State\nEvery time you call a composable function, a **new independent state container** is created in memory. If two different components call `useCounter()`, they get separate counters. If you want to share a single state globally (like user auth or shopping carts), declare the reactive ref *outside* the function container in the composable file:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// Global shared state (similar to a tiny Pinia store)\nconst user = ref(null)\n\nexport function useAuth() {\n  const login = async (credentials) => { /* ... */ }\n  const logout = () => { user.value = null }\n  return { user, login, logout }\n}'
          },
          {
            type: 'table',
            headers: ['Aspect', 'Components', 'Composables'],
            rows: [
              ['Core Purpose', 'Define visual interface layout structure + local logic widget behavior', 'Define and encapsulate reusable stateful logic routines (no UI template)'],
              ['Casing Convention', 'PascalCase tags (e.g. `\x3cUserCard /\x3e`)', 'camelCase prefix starting with `use` (e.g. `useFetch()`)'],
              ['Visual Layout', 'Contains `\x3ctemplate\x3e` markup and styles', 'Contains only JavaScript/TypeScript variables, functions, and hooks'],
              ['Best Used For', 'Navigation menus, page cards, charts, popups, inputs', 'API fetching, screen width tracking, forms, local storage syncing']
            ]
          },
          {
            type: 'callout',
            title: 'Using Lifecycle Hooks inside Composables',
            text: 'Composables can safely register lifecycle hooks (like `onMounted`, `onUnmounted`, `watch`). These hooks bind automatically to the active component instance invoking the composable, making them ideal for registering window resize listeners or background interval syncs.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Putting HTML tags or UI templates inside composables. Composables handle logic only. <br>• **Mistake 2**: Forgetting to return values at the end of the composable function, making them inaccessible. <br>• **Mistake 3**: Misunderstanding state instances. Remember that calling `useCounter()` in two places generates separate, independent counters by default.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If Component A and Component B both invoke `const { count } = useCounter()`, are their counts shared? ➔ No, they are independent local states. \n2. What is the standard naming convention prefix for Vue composables? ➔ `use` (e.g., `useAuth`). \n3. Where should you declare a ref inside a composable file to share a single state globally? ➔ Outside of the exported function definition.'
          }
        ]
      },
      {
        id: 'vue_21',
        title: '22. Vue Router',
        sections: [
          {
            type: 'paragraph',
            text: 'Until now, all our components and panels loaded on a single view sheet inside `App.vue`. However, real-world web applications need separate routes (such as a Home Page, Student Profile, and Job Dashboard). Switch between pages dynamically without full browser reloads using **Vue Router**, the official routing library for Vue.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Full Page Reloads\nOn traditional multi-page websites, clicking a link forces the browser to request a new HTML document from the server. The screen flashes blank, assets download again, and all local JavaScript state is destroyed. Vue Router solves this by establishing a Single Page Application (SPA) structure: only a single HTML file is loaded, and routing is handled dynamically.'
          },
          {
            type: 'paragraph',
            text: '### Setting Up Route Paths\nIn your project, declare routes inside a `router/index.js` configuration file. A route map links a URL path to a specific page View Component:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/router/index.js\nimport { createRouter, createWebHistory } from \'vue-router\'\nimport HomeView from \'../views/HomeView.vue\'\nimport ProfileView from \'../views/ProfileView.vue\'\n\nconst routes = [\n  { path: \'/\', component: HomeView },\n  { path: \'/profile\', component: ProfileView }\n]\n\nconst router = createRouter({\n  history: createWebHistory(), // Uses HTML5 history for clean URLs without hashes (#)\n  routes\n})\n\nexport default router'
          },
          {
            type: 'paragraph',
            text: '### Router Integration in main.js\nRegister the router instance within the main application configuration before mounting to active HTML containers:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'import { createApp } from \'vue\'\nimport App from \'./App.vue\'\nimport router from \'./router\'\n\ncreateApp(App)\n  .use(router) // Register router plugin\n  .mount(\'#app\')'
          },
          {
            type: 'paragraph',
            text: '### Rendering Route Views: RouterView\nInside your root component `App.vue`, render the active page view using the `<RouterView />` tag. When the URL matches a route path, the corresponding view component dynamically renders inside this container:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3c!-- App.vue --\x3e\n\x3ctemplate\x3e\n  \x3cnav\x3e\n    \x3ch1\x3ePlacement Portal\x3ch1\x3e\n  \x3c/nav\x3e\n\n  \x3c!-- Swapped dynamically by Vue Router --\x3e\n  \x3cRouterView /\x3e\n\x3ctemplate\x3e'
          },
          {
            type: 'paragraph',
            text: '### Routing Navigation: RouterLink\nTo navigate without reloading the page, replace traditional anchor tags (`\x3ca href\x3e`) with `<RouterLink to=\"/path\">`. Vue Router intercepts clicks and updates components instantly:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3c!-- Correct SPA navigation --\x3e\n  \x3cRouterLink to=\"/\"\x3eHome\x3c/RouterLink\x3e\n  \x3cRouterLink to=\"/profile\"\x3eProfile\x3c/RouterLink\x3e\n\x3c/template\x3e'
          },
          {
            type: 'table',
            headers: ['Feature', 'HTML Anchor (a href)', 'Vue Router Link (RouterLink)'],
            rows: [
              ['Navigation Behavior', 'Forces full browser reload and resets state', 'Swaps components dynamically via JS (no reload)'],
              ['Performance Speed', 'Slow (re-downloads stylesheet and script assets)', 'Instantaneous (only swapping content markup)'],
              ['State Retention', 'State is completely lost', 'All reactive states and store variables are fully preserved'],
              ['Best Used For', 'External links out of the application domain', 'Internal subpages inside the Vue SPA application']
            ]
          },
          {
            type: 'callout',
            title: 'Views vs Components Casing',
            text: '• **Views** represent full pages or route destinations (like `HomeView.vue`, `JobsView.vue`, `AdminView.vue`). Store them inside the `views/` folder. <br>• **Components** are reusable, modular UI widgets (like `Navbar.vue`, `JobCard.vue`, `BaseButton.vue`). Store them in the `components/` folder.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Using standard `<a href="/profile">` links inside the SPA, causing slow page reloads. <br>• **Mistake 2**: Forgetting to add `<RouterView />` in `App.vue`, resulting in a blank viewport where views never render. <br>• **Mistake 3**: Placing reusable component files inside the page-level `views/` folder structure.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. What container element does Vue Router use to inject matching view components? ➔ `<RouterView />`. \n2. Why is `<RouterLink>` preferred over standard anchor links? ➔ It prevents full page refreshes and preserves reactive states. \n3. In which folder should full route landing pages be placed? ➔ The `views/` folder.'
          }
        ]
      },
      {
        id: 'vue_22',
        title: '23. Dynamic Routing & Navigation',
        sections: [
          {
            type: 'paragraph',
            text: 'In Lesson 22, we mapped static URLs to views (e.g. `/profile` to `ProfileView`). However, real-world applications need dynamic path patterns to render varying data collections (such as rendering different jobs using the exact same detail layout). Vue Router solves this by utilizing **Dynamic Path Segments** (parameters prefixed with a colon `:`), and exposes routing tools via Vue hooks.'
          },
          {
            type: 'paragraph',
            text: '### Declaring Dynamic Route Parameters\nTo configure a route parameter, prefix the parameter name segment with a colon (`:`) in the router configuration path:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/router/index.js\nconst routes = [\n  {\n    path: \'/jobs/:id\',\n    component: JobDetailsView\n  }\n]'
          },
          {
            type: 'paragraph',
            text: 'This route now dynamically matches requests like `/jobs/101`, `/jobs/102`, and `/jobs/999` using the exact same `JobDetailsView` component.'
          },
          {
            type: 'paragraph',
            text: '### Accessing Route Parameters inside components: useRoute()\nTo read active parameters, query variables, or paths inside a component setup context, invoke the `useRoute()` hook:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { useRoute } from \'vue-router\'\n\nconst route = useRoute()\n\n// Access route.params to read parameter values\nconsole.log(route.params.id)\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv\x3eViewing Job details for ID: {{ route.params.id }}\x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Multiple Parameter Segments\nVue Router allows multiple parameter identifiers in a single route path pattern:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// Matches: /users/5/posts/99\n{\n  path: \'/users/:userId/posts/:postId\',\n  component: PostView\n}'
          },
          {
            type: 'paragraph',
            text: 'Accessing parameters yields: `route.params.userId // "5"` and `route.params.postId // "99"`.'
          },
          {
            type: 'paragraph',
            text: '### Programmatic Navigation: useRouter()\nWhile `<RouterLink>` manages user click navigation declaratively, you often need to navigate programmatically inside JavaScript handlers (e.g. redirecting users to the dashboard after a successful form submit). Vue Router provides the `useRouter()` hook for programmatic navigation actions:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { useRouter } from \'vue-router\'\n\nconst router = useRouter()\n\nfunction navigateToDashboard() {\n  // Push a new route path onto the navigation stack\n  router.push(\'/dashboard\')\n}\n\nfunction redirectSafely() {\n  // Overwrite history so users cannot hit \"Back\" to return here\n  router.replace(\'/dashboard\')\n}\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Query Parameters\nQuery parameters sit after a question mark in the URL (e.g. `/search?q=vue&page=2`). Access them via `route.query`:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { useRoute } from \'vue-router\'\nconst route = useRoute()\n\n// For url: /search?q=vue\nconsole.log(route.query.q) // \"vue\"\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Nested Routes\nFor nested dashboard layouts where sidebar elements remain but inner sub-panels toggle, define sub-routes under the `children` array of a parent route:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '{\n  path: \'/settings\',\n  component: SettingsLayout,\n  children: [\n    { path: \'profile\', component: ProfileSettings },\n    { path: \'security\', component: SecuritySettings }\n  ]\n}'
          },
          {
            type: 'paragraph',
            text: 'Ensure the parent component (`SettingsLayout.vue`) contains a nested `<RouterView />` container where child views can render.'
          },
          {
            type: 'paragraph',
            text: '### Catch-All 404 Page\nTo handle non-existent URLs, declare a wild-card route parameter using custom pattern matching. Always append this catch-all route at the very end of your routes array list:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '{\n  path: \'/:pathMatch(.*)*\',\n  component: NotFoundView\n}'
          },
          {
            type: 'paragraph',
            text: '### Reacting to Param Updates via Route Watchers\nWhen navigating between paths that map to the same component layout structure (e.g., from `/jobs/1` to `/jobs/2`), Vue reuses the already mounted component instance instead of re-creating it from scratch. Consequently, standard hooks like `onMounted()` will not execute again on route parameter changes. To react to parameter updates, define a watcher:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { useRoute } from \'vue-router\'\nimport { watch } from \'vue\'\n\nconst route = useRoute()\n\n// Watch route params object for changes\nwatch(\n  () => route.params.id,\n  (newId) => {\n    // Fetch new data updates based on updated ID\n    fetchJobDetails(newId)\n  }\n)\n\x3c/script\x3e'
          },
          {
            type: 'table',
            headers: ['Aspect / Hook', 'useRoute()', 'useRouter()'],
            rows: [
              ['Core Purpose', 'Inspects active route properties (read-only)', 'Executes routing navigation actions'],
              ['Key Properties', 'path, params, query, meta, hash', 'push(), replace(), go(), back()'],
              ['Reactivity', 'Fully reactive data object', 'Static callable navigation actions class API'],
              ['Best Used For', 'Fetching item details, reading search query filters, checking tags', 'Handling post-login redirects, user logout actions, routing back']
            ]
          },
          {
            type: 'callout',
            title: 'Route Parameter Casing Rules',
            text: '• **Params** represent structural parts of the route URL path (e.g. `/jobs/101`). Access them via `route.params.id`. <br>• **Query Params** represent additional filters appended after the path query string separator (e.g. `/jobs?page=2`). Access them via `route.query.page`.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Attempting to query route parameters via `route.query.id` for dynamic paths like `/jobs/101`. Always use `route.params.id`. <br>• **Mistake 2**: Expecting lifecycle hooks (like `onMounted()`) to trigger on dynamic parameter transitions. You must use a watcher to monitor changes. <br>• **Mistake 3**: Confusing hooks usage by invoking `useRouter().params.id` instead of `useRoute().params.id`.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If the current path is `/jobs/123?page=2`, what does `route.params.id` contain? ➔ `123` \n2. Which hook provides methods for executing dynamic redirects in scripts? ➔ `useRouter()`. \n3. Why do standard component mounts not execute when switching from `/jobs/1` to `/jobs/2`? ➔ Vue reuses the mounted component instance to optimize rendering speeds.'
          }
        ]
      },
      {
        id: 'vue_23',
        title: '24. Navigation Guards',
        sections: [
          {
            type: 'paragraph',
            text: 'Now that we can transition across dynamic pages, managing user visibility and access permissions becomes essential. For example, stopping users from loading the `/admin` dashboard unless they are authenticated admins. Vue Router provides **Navigation Guards** to validate, permit, or redirect routing transitions dynamically.'
          },
          {
            type: 'paragraph',
            text: '### The Problem: Pages Traversal Protection\nIn standard Multi-Page Applications, authorization is checked on the server on every request. In Single Page Applications (SPAs), pages run completely in the browser via JavaScript. If you do not secure routes, users can manually enter URLs in the address bar to view page structures. Centralizing navigation control via Guards ensures pages are blocked and routed appropriately.'
          },
          {
            type: 'paragraph',
            text: '### Global beforeEach Guards\nGlobal guards run before every single route navigation in your application. Register them on the main router instance in `router/index.js` using `beforeEach`:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/router/index.js\nrouter.beforeEach((to, from) => {\n  // to: Destination route object user is trying to reach\n  // from: Source route object user is leaving from\n  console.log(\'Navigating to:\', to.path)\n})'
          },
          {
            type: 'paragraph',
            text: '### Attaching Route Metadata: meta fields\nTo avoid hardcoding path validations directly in guard files, attach custom attributes to individual routes using the `meta` configuration block:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'const routes = [\n  {\n    path: \'/profile\',\n    component: ProfileView,\n    meta: { requiresAuth: true }\n  },\n  {\n    path: \'/admin\',\n    component: AdminView,\n    meta: { requiresAuth: true, requiresAdmin: true }\n  }\n]'
          },
          {
            type: 'paragraph',
            text: '### Evaluating Meta in Global Guards\nCheck route meta attributes inside the `beforeEach` guard to trigger conditional redirects:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'router.beforeEach((to, from) => {\n  const isLoggedIn = isAuthenticated()\n  const user = getCurrentUser()\n\n  // Check if destination path requires authentication\n  if (to.meta.requiresAuth && !isLoggedIn) {\n    return \'/login\' // Redirect unauthenticated users\n  }\n\n  // Check if destination requires admin permissions\n  if (to.meta.requiresAdmin && user.role !== \'admin\') {\n    return \'/\' // Redirect to home if unauthorized\n  }\n})'
          },
          {
            type: 'paragraph',
            text: '### The Redirection Loop Trap\nWhen redirecting unauthenticated users to `/login`, you must verify that their target destination is not already the login page. Failing to check this target results in an infinite redirection loop crash:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// WRONG (Triggers infinite loop if logged out):\nrouter.beforeEach((to) => {\n  if (!isLoggedIn) return \'/login\'\n})\n\n// CORRECT (Prevents loop):\nrouter.beforeEach((to) => {\n  if (!isLoggedIn && to.path !== \'/login\') {\n    return \'/login\'\n  }\n})'
          },
          {
            type: 'paragraph',
            text: '### Redirecting Logged-in Users\nSimilarly, you can block already logged-in users from accessing the login or signup views by routing them to the dashboard:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'router.beforeEach((to) => {\n  const loggedIn = isAuthenticated()\n  if (to.path === \'/login\' && loggedIn) {\n    return \'/dashboard\'\n  }\n})'
          },
          {
            type: 'paragraph',
            text: '### Route-Specific Guards: beforeEnter\nInstead of checking conditions globally for all views, configure guard logic directly on targeted route definitions using `beforeEnter`:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '{\n  path: \'/admin\',\n  component: AdminView,\n  beforeEnter: (to, from) => {\n    if (!isAdmin()) {\n      return \'/\'\n    }\n  }\n}'
          },
          {
            type: 'table',
            headers: ['Guard Type', 'Registration Method', 'Execution Scope', 'Ideal Use Cases'],
            rows: [
              ['Global Guard', 'router.beforeEach()', 'Triggers on every single route change in the app', 'Authentication checks, tracking page views, global progress bars'],
              ['Route-Specific Guard', 'beforeEnter property inside Route object', 'Triggers only when matching that specific path', 'Restricting dashboard access by feature flags or specific roles']
            ]
          },
          {
            type: 'callout',
            title: 'Frontend vs Backend Security Rules',
            text: '• Frontend guards are strictly for **User Experience (UX)**. They prevent UI flashes, hide menu options, and help redirect user flows. <br>• They do **NOT** replace backend authentication. Always validate session tokens (like JWTs) and roles on the backend for every API endpoint.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Triggering complex database query API requests on every route transition in global guards, which degrades routing speeds. <br>• **Mistake 2**: Forgetting to exclude the login path in redirection blocks, causing infinite loading loop crashes. <br>• **Mistake 3**: Relying on client-side state flags to completely secure sensitive data pages without backend database role checks.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a logged-out user tries to access a path with `meta: { requiresAuth: true }`, where does the correct guard redirect them? ➔ `\'/login\'` \n2. What is the execution difference between `beforeEach` and `beforeEnter`? ➔ `beforeEach` checks all route paths globally; `beforeEnter` runs only when matching its specific route definition. \n3. Why are client-side navigation guards insufficient for securing application data? ➔ Because client-side Javascript runs in the browser and can be bypassed; real authorization must be validated on the backend API.'
          }
        ]
      },
      {
        id: 'vue_24',
        title: '25. Pinia Global State Management',
        sections: [
          {
            type: 'paragraph',
            text: 'When applications scale and component trees grow, passing data between deeply nested or completely unrelated components becomes complex. Standard Vue techniques like Prop Drilling (passing props down multiple layers) or Provide/Inject (limited to subtree ancestors) add unnecessary boilerplate. **Pinia** is Vue\'s official, type-safe global state management library, establishing a centralized memory store in the browser that any component can read, update, or listen to directly.'
          },
          {
            type: 'paragraph',
            text: '### The Anatomy of a Pinia Store\nA Pinia store is composed of three primary blocks:\n* **State** : The reactive source data of your application store (equivalent to component `ref()` or `reactive()`).\n* **Getters** : Derived, cached value properties computed directly from store states (equivalent to component `computed()`).\n* **Actions** : Synchronous or asynchronous method functions containing logic to update states (equivalent to component functions).'
          },
          {
            type: 'paragraph',
            text: '### Registering Pinia in main.js\nBefore using Pinia stores, you must create a Pinia plugin instance and register it in the entry file:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/main.js\nimport { createApp } from \'vue\'\nimport { createPinia } from \'pinia\'\nimport App from \'./App.vue\'\n\nconst app = createApp(App)\napp.use(createPinia()) // Register the Pinia plugin\napp.mount(\'#app\')'
          },
          {
            type: 'paragraph',
            text: '### Creating a Pinia Store using defineStore()\nDefine stores inside `src/stores/` using the `defineStore()` function. Each store requires a unique string ID to identify it:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/stores/counter.js\nimport { defineStore } from \'pinia\'\n\nexport const useCounterStore = defineStore(\'counter\', {\n  // State must be a function returning the initial state object\n  state: () => ({\n    count: 0,\n    name: \'Satyam\'\n  }),\n  getters: {\n    // Getters receive the state as the first parameter\n    doubleCount: (state) => state.count * 2\n  },\n  actions: {\n    // Actions use \'this\' to access and modify state properties directly\n    increment() {\n      this.count++\n    }\n  }\n})'
          },
          {
            type: 'paragraph',
            text: '### Using the Store inside Vue Components\nTo access states, getters, and trigger actions inside templates and setup scripts, invoke the store\'s hook function:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { useCounterStore } from \'@/stores/counter\'\n\nconst store = useCounterStore()\n\x3c/script\x3e\n\n\x3ctemplate\x3e\n  \x3cdiv\x3e\n    \x3cp\x3eCount: {{ store.count }}\x3c/p\x3e\n    \x3cp\x3eDouble Count: {{ store.doubleCount }}\x3c/p\x3e\n    \x3cbutton @click=\"store.increment\"\x3eIncrement\x3c/button\x3e\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Global Authentication Store Example\nA classic use case for global state management is tracking user sessions. If the user state changes in the auth store, every component using the store (e.g. Header Navbars, User Profiles, Sidebars) immediately updates:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/stores/auth.js\nimport { defineStore } from \'pinia\'\n\nexport const useAuthStore = defineStore(\'auth\', {\n  state: () => ({\n    user: null,\n    loggedIn: false\n  }),\n  getters: {\n    isAuthenticated: (state) => !!state.user\n  },\n  actions: {\n    login(userData) {\n      this.user = userData\n      this.loggedIn = true\n    },\n    logout() {\n      this.user = null\n      this.loggedIn = false\n    }\n  }\n})'
          },
          {
            type: 'table',
            headers: ['Concept', 'Vue Component equivalent', 'Pinia Store equivalent', 'Primary Role'],
            rows: [
              ['Reactive Data', 'ref() / reactive() variables', 'state: () => ({ ... })', 'Declares the source state parameters of the store'],
              ['Computed Properties', 'computed(() => value)', 'getters: { double() { ... } }', 'Caches derived calculations based on store states'],
              ['Methods', 'function run() { ... }', 'actions: { run() { ... } }', 'Encapsulates synchronous or asynchronous logic to update states']
            ]
          },
          {
            type: 'callout',
            title: 'Communication Methods choice guide',
            text: '• **Props / Emits**: Best for direct parent-to-child or child-to-parent communications.<br>• **Provide / Inject**: Best for passing data down a single branch subtree layout.<br>• **Pinia Store**: Best for global states that unrelated components (e.g. Navbar vs Sidebar) need to access simultaneously.'
          },
          {
            type: 'callout',
            title: 'Common Beginner Mistakes',
            text: '• **Mistake 1**: Destructuring store properties directly (e.g. `const { count } = useCounterStore()`). This breaks Vue\'s reactivity proxy tracking. Use `storeToRefs(store)` for properties. <br>• **Mistake 2**: Storing local UI toggle variables (e.g. whether a modal is open) in global stores. Keep local UI states inside components. <br>• **Mistake 3**: Putting all variables into one huge monolithic store. Divide logic into small, focused store files.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a store has state `count: 5` and a getter `doubleCount` returning `state.count * 2`, what does `store.doubleCount` evaluate to? ➔ `10` \n2. What Pinia helper enables safe destructuring of reactive state properties in components? ➔ `storeToRefs()`. \n3. Where should you define global states like user authorization sessions? ➔ Centralized Pinia Stores.'
          }
        ]
      },
      {
        id: 'vue_25',
        title: '26. Setup Stores & Async Patterns',
        sections: [
          {
            type: 'paragraph',
            text: 'While Option Stores configure states, getters, and actions inside options object blocks (matching options APIs), modern Vue teams prefer **Setup Stores** using a setup function. This format allows you to write standard `ref()` variables, `computed()` properties, and helper functions—exactly like writing component setup blocks—which provides maximum flexibility and integrates naturally with Vue\'s Composition API.'
          },
          {
            type: 'paragraph',
            text: '### Defining a Setup Store\nTo declare a Setup Store, pass a setup function mapping your store state and methods as the second argument to `defineStore()`:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/stores/counter.js\nimport { defineStore } from \'pinia\'\nimport { ref, computed } from \'vue\'\n\nexport const useCounterStore = defineStore(\'counter\', () => {\n  const count = ref(0)\n\n  // Getter: defined using computed()\n  const doubleCount = computed(() => count.value * 2)\n\n  // Action: defined as a standard function\n  function increment() {\n    count.value++\n  }\n\n  // CRITICAL: You must return all reactive values and methods\n  return { count, doubleCount, increment }\n})'
          },
          {
            type: 'paragraph',
            text: '### Managing Asynchronous Requests & Status Indicators\nIn production, actions are the ideal boundary for managing asynchronous operations (like network API requests). It is highly recommended to declare loading and error status refs inside your store to automatically update components during data fetches:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/stores/jobs.js\nimport { defineStore } from \'pinia\'\nimport { ref } from \'vue\'\n\nexport const useJobStore = defineStore(\'jobs\', () => {\n  const jobs = ref([])\n  const loading = ref(false)\n  const error = ref(null)\n\n  async function fetchJobs() {\n    loading.value = true\n    error.value = null\n    try {\n      const response = await fetch(\'/api/jobs\')\n      if (!response.ok) throw new Error(\'Failed to fetch jobs data\')\n      jobs.value = await response.json()\n    } catch (err) {\n      error.value = err.message\n    } finally {\n      loading.value = false\n    }\n  }\n\n  return { jobs, loading, error, fetchJobs }\n})'
          },
          {
            type: 'paragraph',
            text: '### Safe Destructuring: storeToRefs()\nDestructuring store state directly (e.g. `const { jobs } = jobStore`) breaks Vue\'s reactivity because JavaScript extracts property references as static variables. To safely destructure properties without breaking reactivity, wrap the store instance in the `storeToRefs()` helper utility:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3cscript setup\x3e\nimport { storeToRefs } from \'pinia\'\nimport { useJobStore } from \'@/stores/jobs\'\n\nconst jobStore = useJobStore()\n\n// Destructure state and getters reactively via storeToRefs\nconst { jobs, loading, error } = storeToRefs(jobStore)\n\n// Actions are normal functions and do not require storeToRefs\nconst { fetchJobs } = jobStore\n\x3c/script\x3e'
          },
          {
            type: 'paragraph',
            text: '### Store Composition\nPinia allows stores to import and call other stores inside their setup definitions, enabling simple cross-store dependencies (such as reading active user auth tokens inside request headers):'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'import { useAuthStore } from \'./auth\'\n\nexport const useJobStore = defineStore(\'jobs\', () => {\n  const authStore = useAuthStore()\n\n  async function applyToJob(jobId) {\n    if (!authStore.isAuthenticated) {\n      throw new Error(\'User must be logged in to apply!\')\n    }\n    // Trigger API call using authStore.user.token...\n  }\n})'
          },
          {
            type: 'paragraph',
            text: '### Persisting Store State in Local Storage\nBecause stores reside in browser memory, page refreshes reset them back to initial parameters. You can watch store variables and automatically sync updates to client storage to maintain user login sessions:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'import { ref, watch } from \'vue\'\n\n// Retrieve session from local storage on load\nconst storedSession = localStorage.getItem(\'session\')\nconst user = ref(storedSession ? JSON.parse(storedSession) : null)\n\n// Watch state and sync updates automatically\nwatch(user, (newUser) => {\n  if (newUser) {\n    localStorage.setItem(\'session\', JSON.stringify(newUser))\n  } else {\n    localStorage.removeItem(\'session\')\n  }\n}, { deep: true })'
          },
          {
            type: 'table',
            headers: ['Aspect / Options', 'Option Store Format', 'Setup Store Format', 'Composition Analogy'],
            rows: [
              ['Syntax Layout', 'Options configuration object', 'Function setup block', 'Options API vs Composition API'],
              ['State Variables', 'state: () => ({ count: 0 })', 'const count = ref(0)', 'ref() or reactive() definitions'],
              ['Getters Properties', 'getters: { doubleCount() { ... } }', 'const doubleCount = computed(...)', 'computed(() => value) properties'],
              ['Actions Methods', 'actions: { run() { ... } }', 'function run() { ... }', 'Standard JS / TS functions']
            ]
          },
          {
            type: 'callout',
            title: 'Pinia Stores vs Custom Composables',
            text: '• **Composables** (like `useFetch`) encapsulate stateful *logic routines* to reuse code. Every component calling it gets an isolated data container instance. <br>• **Pinia Stores** (like `useAuthStore`) encapsulate *shared global states*. Every component calling it shares the exact same reactive variables.'
          },
          {
            type: 'callout',
            title: 'Common Setup Store Pitfalls',
            text: '• **Mistake 1**: Forgetting to return state properties or actions at the bottom of the setup function block. Unreturned fields will be undefined to components. <br>• **Mistake 2**: Attempting to destructure store states directly without utilizing `storeToRefs()`, breaking reactivity. <br>• **Mistake 3**: Calling endpoints directly inside component lifecycle hooks instead of centralizing async requests inside actions.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a store has state `const count = ref(10)` and getter `const doubleCount = computed(() => count.value * 2)`, what does `doubleCount.value` contain? ➔ `20` \n2. Why can actions be destructured directly (e.g. `const { login } = store`) while state cannot? ➔ Actions are functions, which do not rely on Proxy getters to notify Vue on changes. \n3. Where should you place async network requests (fetching data) in clean architectures? ➔ Centralized Store Actions.'
          }
        ]
      },
      {
        id: 'vue_26',
        title: '27. Authentication System Integration',
        sections: [
          {
            type: 'paragraph',
            text: 'In modern client-side architectures, authentication connects multiple layers together: templates and inputs (Vue Components), session memory (Pinia Stores), client caching (Local Storage), page access protections (Router Guards), and backend validations (JWT API requests). We will combine all of these into a production-ready JWT Authentication pipeline.'
          },
          {
            type: 'paragraph',
            text: '### High-Level Authentication Lifecycle\nA standard Single Page Application authentication workflow follows this pipeline:\n1. User enters email/password in a login form component. \n2. Click triggers a login action inside the Pinia Auth Store. \n3. Store action triggers a POST API network request to the backend. \n4. Backend verifies credentials and issues a signed JSON Web Token (JWT). \n5. Store records token and user info inside reactive state and saves them to `localStorage`. \n6. The browser attaches the JWT inside the headers of every subsequent API network call.'
          },
          {
            type: 'paragraph',
            text: '### Centralized Auth Store Implementation\nCreate a Setup Store to centralize authentication state variables, credentials caching, network indicators, session restoration, and user sign-out behaviors:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/stores/auth.js\nimport { defineStore } from \'pinia\'\nimport { ref, computed } from \'vue\'\n\nexport const useAuthStore = defineStore(\'auth\', () => {\n  const user = ref(null)\n  const token = ref(null)\n  const loading = ref(false)\n  const error = ref(null)\n\n  const isAuthenticated = computed(() => !!token.value)\n\n  async function login(email, password) {\n    loading.value = true\n    error.value = null\n    try {\n      const res = await fetch(\'/api/login\', {\n        method: \'POST\',\n        headers: { \'Content-Type\': \'application/json\' },\n        body: JSON.stringify({ email, password })\n      })\n      if (!res.ok) throw new Error(\'Invalid email or password\')\n      const data = await res.json()\n\n      token.value = data.token\n      user.value = data.user\n\n      // Persist auth status\n      localStorage.setItem(\'token\', data.token)\n      localStorage.setItem(\'user\', JSON.stringify(data.user))\n    } catch (err) {\n      error.value = err.message\n    } finally {\n      loading.value = false\n    }\n  }\n\n  function logout() {\n    token.value = null\n    user.value = null\n    localStorage.removeItem(\'token\')\n    localStorage.removeItem(\'user\')\n  }\n\n  function restoreSession() {\n    const storedToken = localStorage.getItem(\'token\')\n    const storedUser = localStorage.getItem(\'user\')\n    if (storedToken && storedUser) {\n      token.value = storedToken\n      user.value = JSON.parse(storedUser)\n    }\n  }\n\n  return { user, token, loading, error, isAuthenticated, login, logout, restoreSession }\n})'
          },
          {
            type: 'paragraph',
            text: '### Restoring Cached Sessions on Application Startup\nTo prevent users from getting logged out on browser refreshes, retrieve data from local storage when initializing Vue in the main entry file before registering the router instance:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/main.js\nimport { createApp } from \'vue\'\nimport { createPinia } from \'pinia\'\nimport App from \'./App.vue\'\nimport router from \'./router\'\nimport { useAuthStore } from \'./stores/auth\'\n\nconst app = createApp(App)\napp.use(createPinia())\n\n// Restore session from localStorage BEFORE router loading\nconst authStore = useAuthStore()\nauthStore.restoreSession()\n\napp.use(router)\napp.mount(\'#app\')'
          },
          {
            type: 'paragraph',
            text: '### Enforcing Role-Based Access Control (RBAC) in Guards\nVue Router checks the auth store within global route navigation loops, guarding both guest access and role-restricted pages (like blocking students from access to the admin page):'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/router/index.js\nimport { createRouter, createWebHistory } from \'vue-router\'\nimport { useAuthStore } from \'../stores/auth\'\n\nconst routes = [\n  {\n    path: \'/profile\',\n    component: () => import(\'../views/ProfileView.vue\'),\n    meta: { requiresAuth: true }\n  },\n  {\n    path: \'/admin\',\n    component: () => import(\'../views/AdminView.vue\'),\n    meta: { requiresAuth: true, requiresAdmin: true }\n  }\n]\n\nconst router = createRouter({\n  history: createWebHistory(),\n  routes\n})\n\nrouter.beforeEach((to) => {\n  const authStore = useAuthStore()\n\n  // Redirect guests to login\n  if (to.meta.requiresAuth && !authStore.isAuthenticated) {\n    return { path: \'/login\', query: { redirect: to.fullPath } }\n  }\n\n  // Redirect non-admins to home\n  if (to.meta.requiresAdmin && authStore.user?.role !== \'admin\') {\n    return \'/\'\n  }\n})'
          },
          {
            type: 'paragraph',
            text: '### Responsive Auth UI Integration\nConnect header menus directly to store states to conditionally show login options or display user profile names automatically:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3cnav class=\"navbar\"\x3e\n    \x3cdiv v-if=\"authStore.isAuthenticated\" class=\"menu-group\"\x3e\n      \x3cspan\x3eHello, {{ authStore.user?.name }}\x3c/span\x3e\n      \x3cbutton @click=\"handleLogout\"\x3eLogout\x3c/button\x3e\n    \x3c/div\x3e\n    \x3cRouterLink v-else to=\"/login\"\x3eLogin\x3c/RouterLink\x3e\n  \x3c/nav\x3e\n\x3c/template\x3e\n\n\x3cscript setup\x3e\nimport { useAuthStore } from \'@/stores/auth\'\nimport { useRouter } from \'vue-router\'\n\nconst authStore = useAuthStore()\nconst router = useRouter()\n\nfunction handleLogout() {\n  authStore.logout()\n  router.push(\'/login\')\n}\n\x3c/script\x3e'
          },
          {
            type: 'table',
            headers: ['Architectural Layer', 'Primary Responsibility', 'Tech / Code representation', 'Security trust level'],
            rows: [
              ['Frontend View Component', 'Collect user credentials, show loaders and error fields', 'LoginView.vue (v-model, loading, error)', 'None (strictly display logic)'],
              ['Pinia Auth Store', 'Initiate fetch requests, manage user/token session memory', 'stores/auth.js (login(), restoreSession())', 'Medium (orchestrates browser memory)'],
              ['Vue Router Guards', 'Centralize client page restrictions and role-based redirects', 'router.beforeEach() & route.meta', 'Medium (guards UI traversal routes)'],
              ['Backend Database API', 'Verify password hashes, generate JWT tokens, validate roles', 'Node / Flask API (JSON Web Tokens)', 'Absolute (ultimate data gatekeeper)']
            ]
          },
          {
            type: 'callout',
            title: 'Frontend Auth vs Backend Security',
            text: '• Frontend auth systems are meant for **User Experience (UX)**. They hide restricted UI widgets, prevent blank layout page flashes, and route users cleanly. <br>• They do **NOT** establish security. A malicious user can bypass router guards. Real security is enforced exclusively on the backend: every API request must attach an `Authorization: Bearer token` header, which the backend database validates for every database query.'
          },
          {
            type: 'callout',
            title: 'Common Security Pitfalls',
            text: '• **Mistake 1**: Storing sensitive plaintext user passwords inside localStorage or Pinia stores. Store only tokens and basic profile parameters. <br>• **Mistake 2**: Forgetting to call `restoreSession()` on app creation, logging users out every time they hit refresh. <br>• **Mistake 3**: Trusting the client role (e.g. `user.role === \'admin\'`) for backend mutations without token role validation on the server.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a store has token `token.value = \'abc123\'`, what does `authStore.isAuthenticated` resolve to? ➔ `true` \n2. Why is calling `restoreSession()` during app initialization critical? ➔ It retrieves stored sessions from localStorage, preventing user logouts on page refreshes. \n3. Where is the redirection target typically stored when a guest is redirected from `/profile` to `/login`? ➔ In the route query params (e.g. `?redirect=/profile`), allowing redirection back after successful login.'
          }
        ]
      },
      {
        id: 'vue_27',
        title: '28. Production API Architecture',
        sections: [
          {
            type: 'paragraph',
            text: 'In production-grade client-side applications, triggering raw endpoints directly inside view page lifecycles or store actions leads to duplicated headers, hard-coded URLs, scattered error triggers, and rigid testing blocks. High-quality Vue applications structure networking into a **Separated Layer Pipeline**:'
          },
          {
            type: 'paragraph',
            text: '### Layered Pipeline Responsibilities\n1. **Component (UI Layer)**: Stays completely focused on styling layouts, displaying fields, and binding user click events. \n2. **Pinia Store (State Layer)**: Manages global reactive variables, page loading indicators, error objects, and client caching. \n3. **Service Layer (Data Layer)**: Organizes API endpoints logically by domain (e.g., `jobService.js`) to completely decouple URL structures from stores. \n4. **API Client (Network Layer)**: Establizes a single network wrapper instance to manage base URLs, request/response headers, and global interceptors.'
          },
          {
            type: 'paragraph',
            text: '### Implementing the Centralized API Client (Network Layer)\nCreate a client configuration module (typically using Fetch or Axios wrappers) to attach headers and catch errors globally:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/services/apiClient.js\nconst BASE_URL = \'/api\'\n\nasync function request(endpoint, options = {}) {\n  const token = localStorage.getItem(\'token\')\n  const headers = {\n    \'Content-Type\': \'application/json\',\n    ...options.headers\n  }\n\n  if (token) {\n    headers[\'Authorization\'] = `Bearer ${token}` // Auto-attach token header\n  }\n\n  const response = await fetch(`${BASE_URL}${endpoint}`, {\n    ...options,\n    headers\n  })\n\n  // Response Interceptor: Catch unauthorized responses\n  if (response.status === 401) {\n    localStorage.removeItem(\'token\')\n    window.location.href = \'/login\' // Force redirect to login page\n  }\n\n  if (!response.ok) {\n    const errorData = await response.json().catch(() => ({}))\n    throw new Error(errorData.message || \'An API error occurred\')\n  }\n\n  return response.json()\n}\n\nexport const apiClient = {\n  get: (url, options) => request(url, { ...options, method: \'GET\' }),\n  post: (url, data, options) => request(url, { ...options, method: \'POST\', body: JSON.stringify(data) })\n}'
          },
          {
            type: 'paragraph',
            text: '### Organizing Feature Endpoint Sets: The Service Layer\nGroup related API endpoint definitions together inside a feature service file, isolating URL strings from global state code:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/services/jobService.js\nimport { apiClient } from \'./apiClient\'\n\nexport const jobService = {\n  async getJobs() {\n    return apiClient.get(\'/jobs\')\n  },\n  async getJobDetails(id) {\n    return apiClient.get(`/jobs/${id}`)\n  },\n  async applyToJob(jobId, payload) {\n    return apiClient.post(`/jobs/${jobId}/apply`, payload)\n  }\n}'
          },
          {
            type: 'paragraph',
            text: '### Triggering Services in the Pinia Store\nThe store action executes service methods directly, allowing it to focus exclusively on mutating loading status flags and managing application state:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: '// src/stores/jobs.js\nimport { defineStore } from \'pinia\'\nimport { ref } from \'vue\'\nimport { jobService } from \'../services/jobService\'\n\nexport const useJobStore = defineStore(\'jobs\', () => {\n  const jobs = ref([])\n  const loading = ref(false)\n  const error = ref(null)\n\n  async function loadJobs() {\n    loading.value = true\n    error.value = null\n    try {\n      // The store has no knowledge of how JWT headers are attached or what base URL is used\n      jobs.value = await jobService.getJobs()\n    } catch (err) {\n      error.value = err.message\n    } finally {\n      loading.value = false\n    }\n  }\n\n  return { jobs, loading, error, loadJobs }\n})'
          },
          {
            type: 'paragraph',
            text: '### Advanced: Interceptors and Refresh Tokens\nProduction applications utilize custom interceptor loops (such as Axios request/response interceptors) to intercept outgoing payloads and incoming responses. A common pattern is utilizing **Refresh Tokens** to keep users authenticated automatically: when a short-lived access token expires and an API call returns a 401 error code, the response interceptor catches the 401, calls a refresh endpoint using a long-lived HTTP-only cookie, caches the new access token, and retries the original failed request seamlessly behind the scenes.'
          },
          {
            type: 'table',
            headers: ['Layer Name', 'Primary Responsibility', 'Project Directory', 'Key Syntax Signature'],
            rows: [
              ['Component (UI)', 'Render grids and layouts, bind user event inputs', 'src/views/JobListView.vue', 'store.loadJobs() method triggers'],
              ['Pinia Store (State)', 'Orchestrate global reactive variables, loading and error status states', 'src/stores/jobsStore.js', 'loading.value = true state updates'],
              ['Service (Data)', 'Map endpoint paths and coordinate feature payload structures', 'src/services/jobService.js', 'apiClient.get(\'/jobs\') URL definitions'],
              ['API Client (Network)', 'Centralize API domain URLs, headers, and request/response interceptors', 'src/services/apiClient.js', 'fetch(endpoint, options) network wrappers']
            ]
          },
          {
            type: 'callout',
            title: 'Maintenance and Testing Benefits',
            text: '• If a backend developer changes a URL route path (e.g. from `/jobs` to `/api/v2/jobs`), you only modify the Service file. All stores and views remain unchanged. <br>• If you swap the underlying HTTP client library (e.g. from standard Fetch to Axios), you only edit the API Client wrapper file. The rest of the codebase stays intact.'
          },
          {
            type: 'callout',
            title: 'Common Architectural Mistakes',
            text: '• **Mistake 1**: Executing raw fetch() calls directly inside UI view templates. This duplicates configurations across dozens of page scripts. <br>• **Mistake 2**: Putting endpoint paths (like `/api/v1/jobs`) inside Pinia store files, merging network configurations with state updates. <br>• **Mistake 3**: Hardcoding authorization token checks inside every individual service request wrapper instead of centralizing it in the API Client.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. If a backend developer changes `/jobs` to `/api/v2/jobs`, which layer needs to be modified? ➔ The Service Layer (`jobService.js`). \n2. In which layer should the JWT authorization headers be automatically attached? ➔ The API Client (`apiClient.js`). \n3. What status code prompts response interceptors to automatically trigger logout functions? ➔ `401 Unauthorized`.'
          }
        ]
      },
      {
        id: 'vue_28',
        title: '29. Performance Optimization Principles',
        sections: [
          {
            type: 'paragraph',
            text: 'Building a functioning Vue application is simple, but building a highly performant application requires understanding how Vue schedules template updates. When data updates, Vue initiates a fast updates cycle: Data Change ➔ Proxy Setter ➔ Render Effect Triggers ➔ Virtual DOM Recalculations ➔ Tree Diffing ➔ Real DOM Patches. Optimization is simply: **reducing the execution work at each stage of this cycle**.'
          },
          {
            type: 'paragraph',
            text: '### Static Layout Optimizations: v-once and v-memo\nUse `v-once` for visual components that never change (like static logos, headers, or descriptions) to compile them once and skip diffing entirely. Use `v-memo` inside large loops to skip updates unless specific dependencies update:'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3c!-- Render once and skip tracking --\x3e\n  \x3ch1 v-once\x3ePlacement Portal\x3c/h1\n\n  \x3c!-- Skip re-rendering user card details unless name or role updates --\x3e\n  \x3cdiv v-for=\"user in users\" :key=\"user.id\" v-memo=\"[user.name, user.role]\"\x3e\n    {{ user.name }} - {{ user.role }}\n  \x3c/div\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Computed Caching vs template Methods\nNever invoke plain methods directly in text interpolations (e.g. `{{ calculateTotal() }}`). Since Vue runs template functions on every single render cycle, calculations will execute repeatedly. Use `computed()` properties instead, which cache results and only recalculate when their reactive dependencies change.'
          },
          {
            type: 'paragraph',
            text: '### Rendering Large lists: Virtual Scrolling & Stable Keys\nIn huge datasets, rendering lists with thousands of items (like 50,000 jobs) freezes browsers due to heavy DOM loads. Instead of rendering them all, use **Virtual Scrolling** to render only visible rows (e.g. 30 items) and recycle DOM containers. Always supply stable, unique `:key` attributes (like `item.id`) – never use array indexes or `Math.random()`, which force complete node rebuilds.'
          },
          {
            type: 'code',
            lang: 'vue',
            code: '\x3ctemplate\x3e\n  \x3c!-- WRONG (destroys and rebuilds elements on every re-render) --\x3e\n  \x3cli v-for=\"item in items\" :key=\"Math.random()\"\x3e{{ item.name }}\x3c/li\x3e\n\n  \x3c!-- CORRECT (highly optimized diffing) --\x3e\n  \x3cli v-for=\"item in items\" :key=\"item.id\"\x3e{{ item.name }}\x3c/li\x3e\n\x3c/template\x3e'
          },
          {
            type: 'paragraph',
            text: '### Skipping Reactivity: Object.freeze()\nVue recursively wraps objects in proxies to track edits. For massive datasets that are strictly read-only (like static country tables or historical logs), skip proxy creation to save device memory and boost speeds by freezing objects with `Object.freeze()`:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'import { ref } from \'vue\'\n\n// Vue will skip proxy tracking, saving memory and boot speeds\nconst rawConfig = Object.freeze({\n  apiUrl: \'https://api.site.com\',\n  features: { chat: true, analytics: false }\n})\nconst config = ref(rawConfig)'
          },
          {
            type: 'paragraph',
            text: '### Debouncing Search Inputs\nAutocomplete search inputs that trigger network API calls on every keystroke overload servers. Delay request execution using **Debouncing** to wait until a user pauses typing before firing the API request:'
          },
          {
            type: 'code',
            lang: 'javascript',
            code: 'import { ref, watch } from \'vue\'\nimport { debounce } from \'lodash-es\'\n\nconst search = ref(\'\')\n\n// Wait 300ms after the last keypress before triggering the fetch\nconst debouncedFetch = debounce((query) => {\n  fetchResults(query)\n}, 300)\n\nwatch(search, (newQuery) => {\n  debouncedFetch(newQuery)\n})'
          },
          {
            type: 'table',
            headers: ['Optimization Method', 'Primary Win Area', 'Estimated Win Impact', 'Best Applied For'],
            rows: [
              ['Code Splitting', 'Initial bundle size and download speed', 'Extremely High', 'Route-based views and heavy modular pages'],
              ['Virtual Scrolling', 'Browser DOM element counts and memory loads', 'Extremely High', 'Lists containing over 500 nodes (e.g. jobs lists)'],
              ['Computed Caching', 'Calculation redundancy', 'High', 'Data aggregations, totals, and formatting filters'],
              ['Debouncing Inputs', 'API requests count and server query loads', 'Medium to High', 'Autocomplete searches, window resize handlers'],
              ['v-once / v-memo', 'Virtual DOM diffing speeds', 'Low to Medium', 'Static landing layouts, massive complex tables']
            ]
          },
          {
            type: 'callout',
            title: 'Measuring Performance First',
            text: 'Never optimize code blindly based on guesses. Always profile your application first using Chrome DevTools (Performance tab), Vue DevTools, and Lighthouse reports to identify where actual bottlenecks occur before applying complex architectural changes.'
          },
          {
            type: 'callout',
            title: 'Common Optimization Pitfalls',
            text: '• **Mistake 1**: Using dynamic keys like `Math.random()` in lists, which forces Vue to delete and recreate the entire DOM list on every single minor state update. <br>• **Mistake 2**: Putting heavy API fetching actions inside expensive watchers that trigger repeatedly. <br>• **Mistake 3**: Wrapping massive static, read-only configuration tables in reactive refs instead of freezing them with `Object.freeze()`.'
          },
          {
            type: 'paragraph',
            text: '### Mini Challenge\nPredict the outputs:\n1. Why is placing a method like `{{ getSummary() }}` inside a template interpolation inefficient? ➔ Because it executes on every re-render, whereas computed properties cache results. \n2. What is the browser impact of rendering 50,000 DOM nodes in a simple list? ➔ The browser UI thread freezes, causing scrolling lags and high memory footprint. \n3. What HTML attribute should be added to images to defer loading until they enter the viewport? ➔ `loading=\"lazy\"`.'
          }
        ]
      }
    ]
  },
  {
    id: 'git',
    name: 'Git & GitHub Workflows',
    category: 'Git',
    description: 'Master version control mechanisms, branches, staged assets, conflict resolution markers, and rebasing.',
    icon: faGithub,
    color: 'bg-sticker-purple border-sticker-purple/40 text-sticker-purple-deep',
    textColor: 'text-sticker-purple-deep',
    bgColor: 'bg-sticker-purple/15',
    pillColor: 'bg-sticker-purple/10 text-sticker-purple border border-sticker-purple/20',
    participants: [usersList[0], usersList[2], usersList[3]],
    updateDate: 'June 09, 2026',
    readTime: '8 min read',
    difficulty: 'Medium',
    progress: 40,
    chapters: [
      {
        id: 'git_1',
        title: '1. Basic Git Workflow',
        sections: [
          {
            type: 'paragraph',
            text: 'Git operates on three main areas: the **Working Directory**, the **Staging Area (Index)**, and the **Local Repository**.'
          },
          {
            type: 'code',
            lang: 'bash',
            code: '# Check staging status\ngit status\n\n# Stage specific files\ngit add index.html style.css\n\n# Commit files with descriptive message\ngit commit -m "feat: design custom layout sidebar"'
          }
        ]
      }
    ]
  },
  {
    id: 'python',
    name: 'Python Data Structures',
    category: 'Python',
    description: 'Learn decorators, generators, list/dict comprehensions, sets, dictionaries, and collections.',
    icon: faPython,
    color: 'bg-sticker-green border-sticker-green/40 text-accent-green',
    textColor: 'text-accent-green',
    bgColor: 'bg-sticker-green/15',
    pillColor: 'bg-sticker-green/10 text-accent-green border border-sticker-green/20',
    participants: [usersList[2], usersList[3]],
    updateDate: 'May 28, 2026',
    readTime: '9 min read',
    difficulty: 'Easy',
    progress: 50,
    chapters: [
      {
        id: 'python_1',
        title: '1. Advanced Data Structures',
        sections: [
          {
            type: 'paragraph',
            text: 'Python has built-in structures optimized for specific tasks. For example, `set` provides constant-time $O(1)$ lookup speeds and unique mathematical operators.'
          },
          {
            type: 'code',
            lang: 'python',
            code: '# Quick set operations\nadmin_roles = {"write", "delete", "edit"}\nuser_roles = {"read", "edit"}\n\n# Intersection (common items)\ncan_edit = admin_roles.intersection(user_roles)  # {"edit"}'
          }
        ]
      }
    ]
  },
  {
    id: 'sql',
    name: 'SQL Aggregations & Joins',
    category: 'Databases',
    description: 'Write complex JOIN pipelines, aggregations, window functions (RANK, ROW_NUMBER), and CTE expressions.',
    icon: faDatabase,
    color: 'bg-sticker-orange border-sticker-orange/40 text-accent-orange-deep',
    textColor: 'text-accent-orange-deep',
    bgColor: 'bg-sticker-orange/15',
    pillColor: 'bg-sticker-orange/10 text-accent-orange border border-sticker-orange/20',
    participants: [usersList[0], usersList[3]],
    updateDate: 'June 01, 2026',
    readTime: '15 min read',
    difficulty: 'Hard',
    progress: 15,
    chapters: [
      {
        id: 'sql_1',
        title: '1. Join Variations',
        sections: [
          {
            type: 'paragraph',
            text: 'Joins allow tables to link based on matching keys. A `LEFT JOIN` returns all rows from the left table, and the matched rows from the right table.'
          },
          {
            type: 'code',
            lang: 'sql',
            code: 'SELECT u.username, a.score, a.completed_at\nFROM users u\nLEFT JOIN attempts a ON u.id = a.user_id\nORDER BY a.score DESC;'
          }
        ]
      }
    ]
  },
  {
    id: 'ml',
    name: 'Machine Learning Basics',
    category: 'AI & Data Science',
    description: 'Understand linear regression, classification accuracy, Lasso L1 regularizations, and loss metrics.',
    icon: faRobot,
    color: 'bg-sticker-teal border-sticker-teal/40 text-accent-teal',
    textColor: 'text-accent-teal',
    bgColor: 'bg-sticker-teal/15',
    pillColor: 'bg-sticker-teal/10 text-accent-teal border border-sticker-teal/25',
    participants: [usersList[1], usersList[2]],
    updateDate: 'May 15, 2026',
    readTime: '20 min read',
    difficulty: 'Expert',
    progress: 0,
    chapters: [
      {
        id: 'ml_1',
        title: '1. Supervised Learning Models',
        sections: [
          {
            type: 'paragraph',
            text: 'Supervised machine learning algorithms learn mapping functions from input variables to outputs based on labeled datasets.'
          },
          {
            type: 'code',
            lang: 'python',
            code: 'from sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import Ridge\n\n# Split training datasets\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n\n# Fit regularized Ridge regression\nmodel = Ridge(alpha=1.0)\nmodel.fit(X_train, y_train)'
          }
        ]
      }
    ]
  }
])

// Filter and search logic
const filteredSubjects = computed(() => {
  return subjects.value.filter(s => {
    // Category filter
    const matchesCategory = selectedCategory.value === 'All' || s.category === selectedCategory.value
    
    // Bookmark filter
    const matchesBookmark = !showBookmarkedOnly.value || bookmarkedSubjects.value.has(s.id)
    
    // Search query filter
    const matchesSearch = s.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          s.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          s.category.toLowerCase().includes(searchQuery.value.toLowerCase())
                          
    return matchesCategory && matchesBookmark && matchesSearch
  }).sort((a, b) => {
    if (sortBy.value === 'alphabetical') {
      return a.name.localeCompare(b.name)
    } else if (sortBy.value === 'difficulty') {
      const diffOrder = ['Easy', 'Medium', 'Hard', 'Expert']
      return diffOrder.indexOf(a.difficulty) - diffOrder.indexOf(b.difficulty)
    } else {
      // default: latest (simulated sorting using progress or ID)
      return b.progress - a.progress
    }
  })
})

const categories = ['All', 'Systems', 'Git', 'Frontend', 'Python', 'Databases', 'AI & Data Science']

function openNote(subj: any) {
  activeSubject.value = subj
  activeChapterIndex.value = 0
  
  // Reset AI Tutor Chat with tailored greeting
  aiMessages.value = [
    { sender: 'tutor', text: `Hi! I am your AI Tutor. Let's study **${subj.name}**. What questions do you have about the first chapter?` }
  ]
}

function selectChapter(idx: number) {
  activeChapterIndex.value = idx
}

function closeNote() {
  activeSubject.value = null
}
</script>

<template>
  <div class="min-h-screen bg-canvas-soft select-text pb-12">
    
    <!-- ══════════════════ LOBBY GRID VIEW ══════════════════ -->
    <div v-if="!activeSubject" class="max-w-6xl mx-auto px-6 py-8">
      <!-- Heading & Stats Summary -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 class="text-3xl font-extrabold text-ink tracking-tight flex items-center gap-2">
            <span v-html="getFaIcon(faBookOpen)" class="text-primary w-8 h-8 flex items-center justify-center"></span>
            Study Notes & Guides
          </h1>
          <p class="text-sm text-ink-muted mt-1.5">Notion-style study guides, code libraries, and references with integrated AI tutoring.</p>
        </div>
        
        <div class="flex items-center gap-3">
          <button @click="showBookmarkedOnly = !showBookmarkedOnly" 
            :class="['px-3 py-1.5 rounded-full text-xs font-semibold border flex items-center gap-1.5 transition-all cursor-pointer',
                     showBookmarkedOnly ? 'bg-sticker-purple/10 text-sticker-purple-deep border-sticker-purple/30 shadow-sm' : 'bg-surface text-ink-secondary border-hairline hover:bg-canvas-soft']">
            <span v-html="getFaIcon(faBookmark)" :class="showBookmarkedOnly ? 'text-sticker-purple-deep' : 'text-ink-faint'"></span>
            Bookmarked ({{ bookmarkedSubjects.size }})
          </button>
        </div>
      </div>

      <!-- Filters Toolbar -->
      <div class="bg-surface border border-hairline rounded-xl p-4 shadow-notion-soft mb-8 flex flex-col lg:flex-row gap-4 items-center justify-between">
        <!-- Search -->
        <div class="w-full lg:w-96 relative">
          <span v-html="getFaIcon(faSearch)" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-faint w-4 h-4 pointer-events-none flex items-center justify-center"></span>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search notes by name, tag..." 
            class="w-full pl-9.5 pr-4 py-2 bg-canvas-soft border border-hairline rounded-md text-sm text-ink focus:outline-none focus:ring-1 focus:ring-primary focus:bg-surface transition-all"
          />
        </div>

        <!-- Category Pills -->
        <div class="flex flex-wrap items-center gap-1.5 w-full lg:w-auto overflow-x-auto py-1">
          <button 
            v-for="cat in categories" 
            :key="cat"
            @click="selectedCategory = cat"
            :class="['px-3.5 py-1.5 rounded-full text-xs font-semibold border transition-all cursor-pointer whitespace-nowrap',
                     selectedCategory === cat 
                       ? 'bg-ink text-white border-ink shadow-sm' 
                       : 'bg-canvas-soft text-ink-muted border-hairline hover:bg-surface hover:text-ink']"
          >
            {{ cat }}
          </button>
        </div>

        <!-- Sort dropdown -->
        <div class="flex items-center gap-2 shrink-0 self-end lg:self-auto">
          <span class="text-xs text-ink-muted font-medium">Sort by</span>
          <select 
            v-model="sortBy" 
            class="bg-canvas-soft border border-hairline rounded-md text-xs font-semibold px-2.5 py-1.5 text-ink-secondary focus:outline-none focus:ring-1 focus:ring-primary cursor-pointer"
          >
            <option value="latest">Status / Progress</option>
            <option value="alphabetical">Alphabetical</option>
            <option value="difficulty">Difficulty Level</option>
          </select>
        </div>
      </div>

      <!-- Notes Grid -->
      <div v-if="filteredSubjects.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="subj in filteredSubjects" 
          :key="subj.id" 
          class="notion-card cursor-pointer group flex flex-col h-full hover:shadow-notion-soft hover:scale-[1.01] transition-all duration-300 relative border border-hairline overflow-hidden"
          @click="openNote(subj)"
        >
          <!-- Decorative Top Bar -->
          <div class="h-2" :class="subj.color.split(' ')[0]"></div>
          
          <div class="p-6 flex-1 flex flex-col">
            <!-- Header Tag -->
            <div class="flex items-center justify-between mb-4">
              <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xxs font-bold uppercase tracking-wider" :class="subj.pillColor">
                • {{ subj.category }}
              </span>
              <div class="flex items-center gap-1">
                <!-- Difficulty -->
                <span class="text-xxs font-bold text-ink-muted px-1.5 py-0.5 rounded bg-canvas-soft border border-hairline">
                  {{ subj.difficulty }}
                </span>
                <!-- Bookmark -->
                <button @click.stop="toggleBookmark(subj.id)" class="text-ink-faint hover:text-sticker-purple transition-colors p-1 flex items-center justify-center border-0 bg-transparent">
                  <span v-html="getFaIcon(faBookmark)" :class="bookmarkedSubjects.has(subj.id) ? 'text-sticker-purple fill-sticker-purple' : 'text-ink-faint'"></span>
                </button>
              </div>
            </div>

            <!-- Subject Title -->
            <h3 class="text-lg font-bold text-ink group-hover:text-primary transition-colors flex items-center gap-2 mb-2">
              <span v-html="getFaIcon(subj.icon)" class="w-5 h-5 flex items-center justify-center shrink-0" :class="subj.textColor"></span>
              {{ subj.name }}
            </h3>

            <!-- Description -->
            <p class="text-xs text-ink-muted leading-relaxed line-clamp-3 mb-5 flex-1 font-normal">
              {{ subj.description }}
            </p>

            <!-- Progress Bar -->
            <div class="mb-5 bg-canvas-soft p-3 rounded-lg border border-hairline">
              <div class="flex justify-between items-center text-xxs font-bold text-ink-muted mb-1.5">
                <span>Completed</span>
                <span>{{ subj.progress }}%</span>
              </div>
              <div class="w-full bg-canvas h-1.5 rounded-full overflow-hidden border border-hairline relative">
                <div class="bg-primary h-full transition-all duration-500" :style="{ width: `${subj.progress}%` }"></div>
              </div>
            </div>

            <!-- Card Footer -->
            <div class="border-t border-hairline pt-4 flex items-center justify-between mt-auto">
              <!-- Authors Avatars -->
              <div class="flex -space-x-1.5 overflow-hidden">
                <div 
                  v-for="(p, pi) in subj.participants" 
                  :key="pi" 
                  :title="`${p.name} (${p.role})`"
                  class="w-6 h-6 rounded-full border border-surface flex items-center justify-center text-[9px] font-extrabold uppercase hover:z-10 hover:scale-110 transition-all cursor-help"
                  :class="p.color"
                >
                  {{ p.initials }}
                </div>
              </div>
              
              <!-- Reading Time / Date -->
              <span class="text-xxs text-ink-faint font-medium flex items-center gap-1">
                <span v-html="getFaIcon(faClock)" class="w-3 h-3 flex items-center justify-center shrink-0"></span>
                {{ subj.readTime }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="bg-surface border border-hairline rounded-xl p-16 text-center shadow-notion-soft">
        <span v-html="getFaIcon(faBookOpen)" class="text-4xl text-ink-faint mb-3 inline-block w-12 h-12 flex items-center justify-center mx-auto"></span>
        <h3 class="text-lg font-bold text-ink mb-1">No notes match your filters</h3>
        <p class="text-sm text-ink-muted max-w-sm mx-auto">Try clearing your search query or switching the category pill to All.</p>
        <button @click="searchQuery = ''; selectedCategory = 'All'; showBookmarkedOnly = false" class="btn-utility mt-4 cursor-pointer">
          Reset Filters
        </button>
      </div>
    </div>

    <!-- ══════════════════ SPLIT DETAIL VIEW ══════════════════ -->
    <div v-else class="h-[calc(100vh-3.5rem)] flex flex-col overflow-hidden">
      <!-- ── View Toolbar (Interactive Top Bar) ── -->
      <div class="bg-surface border-b border-hairline h-12 flex-shrink-0 flex items-center justify-between px-6 shadow-sm select-none print:hidden">
        <div class="flex items-center gap-3">
          <button @click="closeNote" class="flex items-center gap-1.5 text-xs font-semibold text-ink-secondary hover:text-ink hover:bg-canvas-soft border border-hairline rounded px-2.5 py-1.5 bg-surface transition-all cursor-pointer">
            <span v-html="getFaIcon(faArrowLeft)" class="w-3 h-3 flex items-center justify-center"></span>
            Back to Guides
          </button>
          <div class="w-px h-4 bg-hairline"></div>
          <span class="text-xs text-ink-muted font-medium flex items-center gap-1.5">
            <span v-html="getFaIcon(activeSubject.icon)" class="w-3.5 h-3.5 flex items-center justify-center shrink-0" :class="activeSubject.textColor"></span>
            {{ activeSubject.name }}
          </span>
        </div>

        <div class="flex items-center gap-2">
          <!-- Bookmark -->
          <button @click="toggleBookmark(activeSubject.id)" class="text-xs font-semibold text-ink-secondary hover:text-ink hover:bg-canvas-soft border border-hairline rounded px-2.5 py-1.5 bg-surface transition-all cursor-pointer">
            <span v-html="getFaIcon(faBookmark)" :class="bookmarkedSubjects.has(activeSubject.id) ? 'text-sticker-purple fill-sticker-purple mr-1.5' : 'text-ink-faint mr-1.5'"></span>
            {{ bookmarkedSubjects.has(activeSubject.id) ? 'Bookmarked' : 'Bookmark' }}
          </button>
          
          <!-- Print/PDF Button -->
          <button @click="triggerPrint" class="flex items-center gap-1.5 text-xs font-semibold text-ink-secondary hover:text-ink hover:bg-canvas-soft border border-hairline rounded px-2.5 py-1.5 bg-surface transition-all cursor-pointer">
            <span v-html="getFaIcon(faPrint)" class="w-3 h-3 flex items-center justify-center text-ink-muted"></span>
            Print PDF
          </button>
        </div>
      </div>

      <!-- ── Three Pane Container ── -->
      <div class="flex-1 flex overflow-hidden min-w-0">
        
        <!-- Left Pane: Chapter Selector Navigation (Image 2 style) -->
        <aside :style="{ width: leftSidebarWidth + 'px' }" class="bg-canvas border-r border-hairline flex flex-col h-full flex-shrink-0 print:hidden overflow-y-auto select-none">
          <div class="p-4 border-b border-hairline">
            <h4 class="text-xxs font-bold text-ink-muted uppercase tracking-wider">Note Sections</h4>
          </div>
          <nav class="p-2 space-y-0.5 flex-1">
            <button 
              v-for="(ch, idx) in activeSubject.chapters" 
              :key="ch.id"
              @click="selectChapter(idx)"
              :class="['w-full text-left px-3 py-2.5 rounded text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer border border-transparent',
                       activeChapterIndex === idx 
                         ? 'bg-canvas-soft border-hairline text-ink' 
                         : 'text-ink-secondary hover:bg-canvas-soft/60 hover:text-ink']"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="activeSubject.color.split(' ')[0]"></span>
              <span class="truncate">{{ ch.title }}</span>
            </button>
          </nav>
        </aside>

        <!-- Left Drag Handle -->
        <div 
          @mousedown="startResizeLeft"
          @dblclick="leftSidebarWidth = 256"
          :class="['w-1 hover:w-1.5 bg-hairline cursor-col-resize h-full select-none shrink-0 print:hidden z-10 relative transition-all duration-150',
                   isResizingLeft ? 'bg-primary w-1.5' : 'hover:bg-primary/50']"
          title="Drag to resize, double-click to reset"
        ></div>

        <!-- Center Pane: Clean Document Sheet (Full-page style) -->
        <main class="flex-1 overflow-y-auto bg-surface p-8 md:p-12 lg:p-16 print:p-0">
          <article class="w-full min-w-0 bg-surface relative print:p-0 print:w-full">
            <!-- Header elements -->
            <div class="border-b border-hairline pb-6 mb-8">
              <h2 class="text-2xl md:text-3xl font-extrabold text-ink leading-tight tracking-tight mb-4 flex items-center gap-2.5">
                <span v-html="getFaIcon(activeSubject.icon)" class="w-8 h-8 flex items-center justify-center shrink-0" :class="activeSubject.textColor"></span>
                {{ activeSubject.chapters[activeChapterIndex].title }}
              </h2>
              
              <!-- Author metadata & profiles -->
              <div class="flex flex-wrap items-center justify-between gap-4 mt-2">
                <div class="flex items-center gap-3">
                  <div class="flex -space-x-1.5 overflow-hidden">
                    <div 
                      v-for="(p, pi) in activeSubject.participants" 
                      :key="pi"
                      class="w-7 h-7 rounded-full border-2 border-surface flex items-center justify-center text-[10px] font-extrabold uppercase hover:z-10 hover:scale-110 transition-all cursor-help"
                      :class="p.color"
                    >
                      {{ p.initials }}
                    </div>
                  </div>
                  <div class="text-[11px] text-ink-muted font-medium">
                    Contributors: <span class="text-ink font-semibold">{{ activeSubject.participants.map((p: any) => p.name.split(' ')[0]).join(', ') }}</span>
                  </div>
                </div>

                <div class="flex items-center gap-2 text-xxs text-ink-faint font-semibold">
                  <span class="flex items-center gap-1">
                    <span v-html="getFaIcon(faCalendarDays)" class="w-3 h-3 flex items-center justify-center text-ink-faint text-xs"></span>
                    Updated: {{ activeSubject.updateDate }}
                  </span>
                  <span>•</span>
                  <span class="flex items-center gap-1">
                    <span v-html="getFaIcon(faClock)" class="w-3 h-3 flex items-center justify-center text-ink-faint text-xs"></span>
                    {{ activeSubject.readTime }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Document content -->
            <div class="space-y-6 text-ink-secondary leading-relaxed font-sans text-sm md:text-[15px]">
              
              <div v-for="(sec, sidx) in activeSubject.chapters[activeChapterIndex].sections" :key="sidx">
                
                <!-- PARAGRAPH -->
                <div v-if="sec.type === 'paragraph'" v-html="renderMarkdown(sec.text)" class="mb-4 text-ink-secondary font-normal markdown-content"></div>

                <!-- CODE BLOCK -->
                <div v-else-if="sec.type === 'code'" class="group relative w-full max-w-full bg-canvas-soft border border-hairline rounded-lg overflow-hidden my-6 font-mono text-xs md:text-sm text-ink-secondary">
                  <div class="bg-surface border-b border-hairline px-4 py-1.5 flex justify-between items-center text-xxs text-ink-faint select-none">
                    <span>{{ sec.lang?.toUpperCase() }}</span>
                    <button 
                      @click="copyCode(sec.code, `${activeChapterIndex}_${sidx}`)" 
                      class="flex items-center gap-1 hover:text-ink transition-colors cursor-pointer px-1.5 py-0.5 rounded border border-transparent hover:bg-canvas-soft"
                    >
                      <span v-html="getFaIcon(copiedIndex === `${activeChapterIndex}_${sidx}` ? faCheck : faCopy)" class="w-2.5 h-2.5 flex items-center justify-center"></span>
                      <span>{{ copiedIndex === `${activeChapterIndex}_${sidx}` ? 'Copied' : 'Copy' }}</span>
                    </button>
                  </div>
                  <pre class="p-4 w-full max-w-full overflow-x-auto whitespace-pre-wrap leading-normal font-mono"><code v-html="highlightCode(sec.code, sec.lang)"></code></pre>
                </div>

                <!-- CALLOUT -->
                <div v-else-if="sec.type === 'callout'" class="bg-sticker-sky/10 border-l-4 border-primary text-ink-secondary p-4 rounded-r-lg flex gap-3 items-start my-6 shadow-sm">
                  <span v-html="getFaIcon(faInfoCircle)" class="w-4 h-4 text-primary mt-0.5 shrink-0 flex items-center justify-center"></span>
                  <div>
                    <h5 class="text-xs font-bold text-primary uppercase tracking-wide mb-1">{{ sec.title }}</h5>
                    <div v-html="renderMarkdown(sec.text)" class="text-xs leading-relaxed font-normal markdown-content"></div>
                  </div>
                </div>

                <!-- TABLE -->
                <div v-else-if="sec.type === 'table'" class="overflow-x-auto border border-hairline rounded-lg my-6 shadow-sm bg-surface">
                  <table class="w-full text-left border-collapse text-xs md:text-sm">
                    <thead>
                      <tr class="bg-canvas-soft border-b border-hairline">
                        <th v-for="h in sec.headers" :key="h" class="p-3 font-semibold text-ink uppercase tracking-wider text-xxs border-r border-hairline last:border-r-0">
                          {{ h }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, ri) in sec.rows" :key="ri" class="border-b border-hairline last:border-0 hover:bg-canvas-soft/30 transition-colors">
                        <td v-for="(cell, ci) in row" :key="ci" class="p-3 text-ink-secondary border-r border-hairline last:border-r-0 font-medium">
                          <code v-if="ci === 0" class="px-1.5 py-0.5 rounded bg-canvas-soft text-xxs font-mono border border-hairline text-ink">{{ cell }}</code>
                          <span v-else class="font-normal">{{ cell }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- CUSTOM VISUAL DIAGRAM -->
                <div v-else-if="sec.type === 'visual_diagram'" class="border border-hairline rounded-lg p-5 bg-canvas-soft/30 shadow-sm my-6 select-none">
                  <h5 class="text-xxs font-bold text-ink-muted uppercase tracking-wider mb-4 flex items-center gap-1.5 justify-center">
                    <span>💡 DIAGRAM: {{ sec.title }}</span>
                  </h5>
                  
                  <!-- Stream Redirection Layout -->
                  <div v-if="sec.diagramType === 'linux-streams'" class="flex flex-col items-center gap-4 py-2 font-mono">
                    <div class="flex gap-12 justify-center items-center w-full max-w-lg">
                      <!-- Input Device -->
                      <div class="flex flex-col items-center gap-1 bg-surface border border-hairline shadow-sm px-4 py-2.5 rounded-lg w-28 text-center">
                        <span class="text-xs font-bold text-ink">Keyboard</span>
                        <span class="text-[9px] text-ink-faint border border-hairline px-1 rounded bg-canvas-soft">Device</span>
                      </div>
                      
                      <!-- Line/Arrow -->
                      <div class="flex-1 h-px bg-hairline relative flex items-center justify-center">
                        <span class="absolute text-[10px] text-primary bg-surface border border-hairline rounded px-1.5 -top-3.5">stdin (FD 0)</span>
                        <div class="absolute right-0 w-1.5 h-1.5 border-t border-r border-hairline rotate-45 transform"></div>
                      </div>
                      
                      <!-- Active Process -->
                      <div class="flex flex-col items-center gap-1 bg-sticker-purple/10 border border-sticker-purple/30 text-sticker-purple-deep shadow-sm px-4 py-2.5 rounded-lg w-28 text-center font-bold">
                        <span class="text-xs font-semibold">Process</span>
                        <span class="text-[9px] bg-sticker-purple/20 px-1 rounded border border-sticker-purple/30 font-normal">grep / cat</span>
                      </div>
                    </div>

                    <!-- Flow Divergence -->
                    <div class="w-full flex justify-center items-stretch h-20 max-w-lg mt-1 relative">
                      <!-- Left Divergence -->
                      <div class="w-1/2 border-r border-hairline relative">
                        <!-- Diagonal lines via borders/positions -->
                        <div class="absolute right-0 top-0 h-full w-px bg-hairline"></div>
                        <div class="absolute -right-3 top-1/2 -translate-y-1/2 text-[9px] text-sticker-green font-semibold bg-surface border border-hairline px-1 rounded">FD 1</div>
                      </div>
                      <!-- Right Divergence -->
                      <div class="w-1/2 relative">
                        <div class="absolute -left-3 top-1/2 -translate-y-1/2 text-[9px] text-sticker-orange-deep font-semibold bg-surface border border-hairline px-1 rounded">FD 2</div>
                      </div>
                    </div>

                    <div class="flex gap-12 justify-center items-center w-full max-w-lg">
                      <!-- stdout target -->
                      <div class="flex flex-col items-center gap-1 bg-surface border border-hairline shadow-sm px-4 py-2.5 rounded-lg w-32 text-center">
                        <span class="text-xs font-bold text-sticker-green">stdout</span>
                        <span class="text-[9px] text-ink-faint border border-hairline px-1 rounded bg-canvas-soft font-normal">Screen / File</span>
                      </div>
                      <!-- spacer -->
                      <div class="w-8 shrink-0"></div>
                      <!-- stderr target -->
                      <div class="flex flex-col items-center gap-1 bg-surface border border-hairline shadow-sm px-4 py-2.5 rounded-lg w-32 text-center">
                        <span class="text-xs font-bold text-sticker-orange-deep">stderr</span>
                        <span class="text-[9px] text-ink-faint border border-hairline px-1 rounded bg-canvas-soft font-normal">Screen / ErrLog</span>
                      </div>
                    </div>
                  </div>

                  <!-- Vue Reactivity & VDOM Flow Layout -->
                  <div v-else-if="sec.diagramType === 'vue-flow'" class="flex flex-col items-center gap-4 py-2 font-mono">
                    <div class="flex flex-wrap md:flex-nowrap gap-3 justify-center items-center w-full max-w-2xl text-[11px]">
                      <!-- Step 1: State Change -->
                      <div class="flex flex-col items-center gap-1 bg-surface border border-hairline shadow-sm px-2.5 py-2 rounded-lg w-28 text-center">
                        <span class="font-bold text-ink">State Change</span>
                        <span class="text-[9px] text-ink-faint border border-hairline px-1 rounded bg-canvas-soft">count++</span>
                      </div>
                      
                      <div class="text-primary font-bold text-xs select-none">➔</div>
                      
                      <!-- Step 2: Reactive System -->
                      <div class="flex flex-col items-center gap-1 bg-sticker-pink/10 border border-sticker-pink/30 text-accent-pink shadow-sm px-2.5 py-2 rounded-lg w-28 text-center">
                        <span class="font-semibold">Reactivity</span>
                        <span class="text-[9px] bg-sticker-pink/20 px-1 rounded border border-sticker-pink/30 font-normal">Proxy Track</span>
                      </div>
                      
                      <div class="text-primary font-bold text-xs select-none">➔</div>

                      <!-- Step 3: Render Function -->
                      <div class="flex flex-col items-center gap-1 bg-surface border border-hairline shadow-sm px-2.5 py-2 rounded-lg w-28 text-center">
                        <span class="font-bold text-ink">Virtual DOM</span>
                        <span class="text-[9px] text-ink-faint border border-hairline px-1 rounded bg-canvas-soft">h('button')</span>
                      </div>

                      <div class="text-primary font-bold text-xs select-none">➔</div>

                      <!-- Step 4: Diffing -->
                      <div class="flex flex-col items-center gap-1 bg-sticker-purple/10 border border-sticker-purple/30 text-sticker-purple-deep shadow-sm px-2.5 py-2 rounded-lg w-28 text-center">
                        <span class="font-semibold">Diffing</span>
                        <span class="text-[9px] bg-sticker-purple/20 px-1 rounded border border-sticker-purple/30 font-normal">Compare trees</span>
                      </div>

                      <div class="text-primary font-bold text-xs select-none">➔</div>

                      <!-- Step 5: Real DOM Update -->
                      <div class="flex flex-col items-center gap-1 bg-sticker-green/10 border border-sticker-green/30 text-ink-secondary shadow-sm px-2.5 py-2 rounded-lg w-28 text-center">
                        <span class="font-bold text-sticker-green-deep">Real DOM</span>
                        <span class="text-[9px] bg-sticker-green/20 px-1 rounded border border-sticker-green/30 font-normal">Patch UI</span>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            <!-- Was this guide helpful? Reactions row -->
            <div class="mt-12 pt-6 border-t border-hairline flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 select-none print:hidden">
              <div>
                <h4 class="text-xs font-bold text-ink">Was this guide helpful?</h4>
                <p class="text-xxs text-ink-muted mt-0.5 font-normal">React to let the contributors know!</p>
              </div>
              <div class="flex flex-wrap items-center gap-2">
                <button 
                  v-for="emoji in ['👍', '💡', '🎉', '❤️']"
                  :key="emoji"
                  @click="toggleChapterReaction(emoji)"
                  :class="['px-3 py-1.5 rounded-full text-xs font-semibold border flex items-center gap-1.5 transition-all cursor-pointer',
                           hasChapterReaction(emoji) ? 'bg-primary/10 border-primary text-primary shadow-sm' : 'bg-surface border-hairline text-ink-secondary hover:bg-canvas-soft']"
                >
                  <span>{{ emoji }}</span>
                  <span class="text-xxs font-bold">{{ getChapterReactionCount(emoji) }}</span>
                </button>
              </div>
            </div>

          </article>
        </main>

        <!-- Right Drag Handle -->
        <div 
          @mousedown="startResizeRight"
          @dblclick="rightSidebarWidth = 320"
          :class="['w-1 hover:w-1.5 bg-hairline cursor-col-resize h-full select-none shrink-0 print:hidden z-10 relative transition-all duration-150',
                   isResizingRight ? 'bg-primary w-1.5' : 'hover:bg-primary/50']"
          title="Drag to resize, double-click to reset"
        ></div>

        <!-- Right Sidebar: Comments Discussion & AI Tutor Panel (Image 1 style) -->
        <aside :style="{ width: rightSidebarWidth + 'px' }" class="bg-canvas border-l border-hairline flex flex-col h-full flex-shrink-0 print:hidden overflow-hidden">
          <!-- Contributors Profile / Overview -->
          <div class="p-4 border-b border-hairline select-none flex-shrink-0">
            <h4 class="text-xxs font-bold text-ink-muted uppercase tracking-wider mb-2.5">Active Study Session</h4>
            <div class="flex items-center gap-2">
              <!-- Inline Avatars -->
              <div class="flex -space-x-1.5 overflow-hidden">
                <div 
                  v-for="(p, pi) in activeSubject.participants" 
                  :key="pi"
                  class="w-6 h-6 rounded-full border border-surface flex items-center justify-center text-[9px] font-extrabold uppercase"
                  :class="p.color"
                >
                  {{ p.initials }}
                </div>
              </div>
              <span class="text-[11px] font-bold text-ink-secondary">{{ activeSubject.participants.length }} studying now</span>
              <span class="w-1.5 h-1.5 rounded-full bg-sticker-green animate-pulse"></span>
            </div>
          </div>

          <!-- Tab Selector for Tutor vs Comments -->
          <div class="flex border-b border-hairline text-xs font-bold bg-canvas-soft select-none flex-shrink-0">
            <button 
              @click="showTutorTab = true"
              :class="['flex-1 py-2.5 text-center border-b-2 cursor-pointer transition-all',
                       showTutorTab ? 'border-primary text-primary bg-canvas' : 'border-transparent text-ink-muted hover:text-ink']"
            >
              <span class="flex items-center justify-center gap-1.5">
                <span v-html="getFaIcon(faRobot)" class="w-3.5 h-3.5 flex items-center justify-center"></span>
                AI Tutor
              </span>
            </button>
            <button 
              @click="showTutorTab = false"
              :class="['flex-1 py-2.5 text-center border-b-2 cursor-pointer transition-all',
                       !showTutorTab ? 'border-primary text-primary bg-canvas' : 'border-transparent text-ink-muted hover:text-ink']"
            >
              <span class="flex items-center justify-center gap-1.5">
                <span v-html="getFaIcon(faComment)" class="w-3.5 h-3.5 flex items-center justify-center"></span>
                Discussion ({{ comments[activeSubject.chapters[activeChapterIndex].id]?.length || 0 }})
              </span>
            </button>
          </div>

          <!-- Tabs Body -->
          <div class="flex-1 overflow-y-auto p-4 min-h-0">
            
            <!-- AI TUTOR TAB -->
            <div v-if="showTutorTab" class="flex flex-col h-full">
              <!-- Chat Logs -->
              <div class="flex-1 space-y-3 mb-4 overflow-y-auto">
                <div 
                  v-for="(msg, mi) in aiMessages" 
                  :key="mi"
                  :class="['p-3 rounded-lg text-xs leading-relaxed max-w-[90%] border shadow-sm',
                           msg.sender === 'tutor' 
                             ? 'bg-canvas-soft border-hairline text-ink-secondary self-start' 
                             : 'bg-primary/5 border-primary/20 text-ink-secondary ml-auto border-r-4 border-r-primary']"
                >
                  <div class="flex items-center gap-1 font-bold mb-1 text-xxs select-none uppercase tracking-wider"
                    :class="msg.sender === 'tutor' ? 'text-primary' : 'text-ink-muted'">
                    <span v-if="msg.sender === 'tutor'" v-html="getFaIcon(faRobot)" class="w-3.5 h-3.5 flex items-center justify-center shrink-0"></span>
                    <span>{{ msg.sender === 'tutor' ? 'AI Tutor' : 'You' }}</span>
                  </div>
                  <div v-html="renderMarkdown(msg.text)" class="markdown-content"></div>
                </div>

                <!-- Typing indicator -->
                <div v-if="aiIsTyping" class="bg-canvas-soft border border-hairline p-3 rounded-lg text-xs text-ink-faint self-start max-w-[90%] flex items-center gap-1.5 shadow-sm">
                  <span v-html="getFaIcon(faRobot)" class="w-3.5 h-3.5 flex items-center justify-center animate-bounce text-primary shrink-0"></span>
                  <span>AI Tutor is thinking...</span>
                </div>
              </div>

              <!-- Quick Questions Pills -->
              <div class="mb-3 select-none">
                <div class="text-[10px] font-bold text-ink-muted uppercase tracking-wider mb-1.5">Quick Questions</div>
                <div class="flex flex-col gap-1">
                  <button 
                    v-for="q in quickQuestions" 
                    :key="q"
                    @click="askAiTutor(q)"
                    class="text-[11px] text-ink-secondary hover:text-ink hover:bg-canvas-soft bg-surface border border-hairline rounded px-2 py-1 text-left w-full transition-all cursor-pointer truncate font-semibold"
                    :title="q"
                  >
                    {{ q }}
                  </button>
                </div>
              </div>

              <!-- Input Area -->
              <div class="mt-auto border-t border-hairline pt-3 flex gap-2">
                <input 
                  v-model="aiInput" 
                  @keyup.enter="sendCustomAiMessage"
                  type="text" 
                  placeholder="Ask a question..." 
                  class="flex-1 bg-canvas-soft border border-hairline rounded px-3 py-1.5 text-xs text-ink focus:outline-none focus:ring-1 focus:ring-primary focus:bg-surface"
                />
                <button 
                  @click="sendCustomAiMessage"
                  class="bg-primary text-white p-2.5 rounded hover:bg-primary-active transition-colors cursor-pointer flex items-center justify-center shrink-0 border-0"
                >
                  <span v-html="getFaIcon(faPaperPlane)" class="w-3.5 h-3.5 flex items-center justify-center"></span>
                </button>
              </div>
            </div>

            <!-- COMMENTS TAB -->
            <div v-else class="flex flex-col h-full">
              <!-- Comment List -->
              <div class="flex-1 space-y-4 mb-4 overflow-y-auto font-normal">
                <div v-if="comments[activeSubject.chapters[activeChapterIndex].id] && comments[activeSubject.chapters[activeChapterIndex].id].length > 0" class="space-y-4">
                  <div 
                    v-for="(cmt, ci) in comments[activeSubject.chapters[activeChapterIndex].id]" 
                    :key="ci" 
                    class="border-b border-hairline last:border-0 pb-3"
                  >
                    <div class="flex items-center justify-between mb-1 text-xs select-none">
                      <div class="flex items-center gap-1.5">
                        <div class="w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-extrabold uppercase shrink-0 font-sans" :class="cmt.color">
                          {{ cmt.initials }}
                        </div>
                        <span class="font-bold text-ink font-sans">{{ cmt.author }}</span>
                      </div>
                      <span class="text-xxs text-ink-faint font-semibold">{{ cmt.time }}</span>
                    </div>
                    <div v-html="renderMarkdown(cmt.text)" class="text-xs text-ink-secondary pl-6 leading-relaxed markdown-content"></div>
                    
                    <!-- Comment Reactions -->
                    <div class="flex items-center gap-1.5 pl-6 mt-2 select-none">
                      <button 
                        v-for="(count, emoji) in (cmt.reactions || { '👍': 0, '❤️': 0, '🎉': 0, '💡': 0 })"
                        :key="emoji"
                        @click="toggleCommentReaction(activeSubject.chapters[activeChapterIndex].id, ci, emoji)"
                        :class="['px-2 py-0.5 rounded-full text-[10px] font-semibold border flex items-center gap-1 transition-all cursor-pointer',
                                 hasCommentReaction(activeSubject.chapters[activeChapterIndex].id, ci, emoji)
                                   ? 'bg-primary/10 border-primary text-primary shadow-sm' 
                                   : 'bg-surface border-hairline text-ink-muted hover:bg-canvas-soft hover:text-ink']"
                      >
                        <span>{{ emoji }}</span>
                        <span v-if="count > 0" class="text-[9px] font-bold">{{ count }}</span>
                      </button>
                    </div>
                  </div>
                </div>

                <div v-else class="text-center py-12 select-none">
                  <span v-html="getFaIcon(faComment)" class="w-10 h-10 text-ink-faint flex items-center justify-center mx-auto mb-2 opacity-50"></span>
                  <h5 class="text-xs font-bold text-ink-secondary">No comments yet</h5>
                  <p class="text-[11px] text-ink-faint mt-0.5">Start the discussion by writing below.</p>
                </div>
              </div>

              <!-- Comment Input Area -->
              <div class="mt-auto border-t border-hairline pt-3">
                <textarea 
                  v-model="newCommentText" 
                  rows="3" 
                  placeholder="Post an update or query..." 
                  class="w-full bg-canvas-soft border border-hairline rounded p-2.5 text-xs text-ink focus:outline-none focus:ring-1 focus:ring-primary focus:bg-surface resize-none mb-2"
                ></textarea>
                <button 
                  @click="submitComment(activeSubject.chapters[activeChapterIndex].id)"
                  class="btn-utility w-full justify-center flex items-center gap-1 py-2 cursor-pointer bg-surface hover:bg-canvas-soft text-xs font-semibold"
                >
                  <span v-html="getFaIcon(faComment)" class="w-3.5 h-3.5 flex items-center justify-center text-ink-muted"></span>
                  Comment
                </button>
              </div>
            </div>

          </div>
        </aside>

      </div>
    </div>

  </div>
</template>

<style scoped>
.text-xxs {
  font-size: 0.65rem;
}
.text-[9px] {
  font-size: 0.56rem;
}
.text-[10px] {
  font-size: 0.62rem;
}
.text-[11px] {
  font-size: 0.68rem;
}
.pl-9\.5 {
  padding-left: 2.375rem;
}

:deep(.markdown-content p) {
  margin-bottom: 0.5rem;
}
:deep(.markdown-content p:last-child) {
  margin-bottom: 0;
}
:deep(.markdown-content code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background-color: var(--color-canvas-soft, #f4f4f5);
  padding: 0.1rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.85em;
  color: var(--color-primary-active, #0072f5);
  border: 1px solid var(--color-hairline, #e4e4e7);
}
:deep(.markdown-content ul) {
  list-style-type: disc;
  padding-left: 1.25rem;
  margin-bottom: 0.75rem;
  margin-top: 0.25rem;
}
:deep(.markdown-content ol) {
  list-style-type: decimal;
  padding-left: 1.25rem;
  margin-bottom: 0.75rem;
  margin-top: 0.25rem;
}
:deep(.markdown-content li) {
  margin-bottom: 0.25rem;
}
:deep(.markdown-content strong) {
  font-weight: 700;
  color: inherit;
}
:deep(.markdown-content em) {
  font-style: italic;
}
:deep(.markdown-content a) {
  color: var(--color-primary, #0072f5);
  text-decoration: underline;
}
:deep(.markdown-content pre) {
  background-color: var(--color-canvas-soft, #f4f4f5);
  border: 1px solid var(--color-hairline, #e4e4e7);
  padding: 0.75rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0.75rem 0;
}
:deep(.markdown-content pre code) {
  background-color: transparent;
  border: none;
  padding: 0;
  color: inherit;
  font-size: 0.9em;
  font-weight: 400 !important;
}
:deep(.markdown-content code),
:deep(.markdown-content pre),
:deep(pre),
:deep(code),
:deep(.font-mono) {
  font-weight: 400 !important;
}

/* Printing Specific styles for PDF conversion */
@media print {
  body {
    background-color: #ffffff !important;
    color: #000000 !important;
  }
  /* Hide sidebars, buttons and headers */
  aside, 
  header, 
  select,
  input,
  button,
  .print\:hidden {
    display: none !important;
  }
  
  /* Make the central document sheet occupy full width and have no border/shadows */
  main {
    background: transparent !important;
    padding: 0 !important;
    overflow: visible !important;
  }
  
  article {
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    min-height: auto !important;
  }
}
</style>
