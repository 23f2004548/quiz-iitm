<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useVirtualTerminal } from '~/composables/useVirtualTerminal'
import { icon } from '@fortawesome/fontawesome-svg-core'
import {
  faTerminal,
  faDatabase,
  faPlay,
  faRotateLeft,
  faTrash,
  faEye,
  faTable,
  faCode,
  faChevronRight,
  faCheck,
  faInfoCircle,
  faBug
} from '@fortawesome/free-solid-svg-icons'
import {
  faPython,
  faJs,
  faHtml5,
  faCss3Alt,
  faRust,
  faJava,
  faLinux
} from '@fortawesome/free-brands-svg-icons'

// Programmatic FontAwesome SVG helper
function getFaIcon(iconDef: any) {
  return icon(iconDef).html[0]
}

const languages = [
  { id: 'ubuntu', name: 'Ubuntu', icon: faLinux, isBrand: true, ext: '.sh', desc: 'Interactive Ubuntu terminal' },
  { id: 'gitbash', name: 'GitBash', icon: faTerminal, isBrand: false, ext: '.sh', desc: 'Interactive shell terminal' },
  { id: 'jupyter', name: 'Jupyter', icon: faTerminal, isBrand: false, ext: '.ipynb', desc: 'Interactive Python Notebook' },
  { id: 'python', name: 'Python', icon: faPython, isBrand: true, ext: '.py', desc: 'Client-side execution' },
  { id: 'sql', name: 'SQL Query', icon: faDatabase, isBrand: false, ext: '.sql', desc: 'Mock database engine' },
  { id: 'javascript', name: 'JavaScript', icon: faJs, isBrand: true, ext: '.js', desc: 'Safe JS sandbox eval' },
  { id: 'html_css', name: 'HTML & CSS', icon: faHtml5, isBrand: true, ext: '.html', desc: 'Live iframe preview' },
  { id: 'java', name: 'Java', icon: faJava, isBrand: true, ext: '.java', desc: 'Simulated compiler logs' },
  { id: 'cpp', name: 'C++', icon: faCode, isBrand: false, ext: '.cpp', desc: 'Simulated compiler logs' },
  { id: 'rust', name: 'Rust', icon: faRust, isBrand: true, ext: '.rs', desc: 'Simulated compiler logs' }
]

const activeLang = ref('ubuntu')
const activeWebTab = ref<'html' | 'css'>('html')
const activeOutputTab = ref<'console' | 'preview' | 'db'>('console')

// Terminal state (for GitBash)
const terminal = useVirtualTerminal()
const currentInput = ref('')
const commandHistory = ref<string[]>([])
const historyIndex = ref(-1)
const terminalBodyRef = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

// Templates
const defaultTemplates: Record<string, string> = {
  python: `# Python Sandbox\n\ndef greet(name):\n    print(f"Hello, {name}!")\n\ngreet("Antigravity Learner")\n\n# Try writing a loop:\nfor i in range(1, 6):\n    print(f"Index: {i}, Square: {i * i}")\n`,
  sql: `-- SQL Sandbox\n-- Available Tables: users, subjects, leaderboard\n\nSELECT * FROM users WHERE level > 1;\n\n-- Try another select:\n-- SELECT name, topics FROM subjects;\n-- SELECT * FROM leaderboard ORDER BY xp DESC;\n`,
  javascript: `// JavaScript Sandbox\n\nconst greet = (name) => {\n    console.log(\`Hello, \${name}!\`);\n};\n\ngreet("Antigravity Learner");\n\n// Try creating an array and reducing it\nconst list = [10, 20, 30, 40];\nconst sum = list.reduce((total, val) => total + val, 0);\nconsole.log("Sum is:", sum);\n`,
  java: `// Java Sandbox\n\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java!");\n        \n        int count = 5;\n        for (int i = 0; i < count; i++) {\n            System.out.println("Running iteration: " + i);\n        }\n    }\n}\n`,
  cpp: `// C++ Sandbox\n#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello C++!" << endl;\n    \n    int factor = 7;\n    for (int i = 1; i <= 5; ++i) {\n        cout << i << " * " << factor << " = " << (i * factor) << endl;\n    }\n    return 0;\n}\n`,
  rust: `// Rust Sandbox\n\nfn main() {\n    println!("Hello from Rust!");\n    \n    let msg = "learning sandboxes";\n    println!("Status: {}", msg);\n    \n    for i in 1..4 {\n        println!("Iteration #{}", i);\n    }\n}\n`
}

const defaultHtml = `<!-- HTML Sandbox -->\n<div class="card">\n  <h2>Web Sandbox</h2>\n  <p>Modify HTML & CSS to see real-time preview updates!</p>\n  <button onclick="changeColor()">Click Me</button>\n</div>\n\n<` + `script>\nfunction changeColor() {\n  const card = document.querySelector('.card');\n  const colors = ['#62aef0', '#d6b6f6', '#ff64c8', '#dd5b00', '#2a9d99', '#1aae39'];\n  const rand = colors[Math.floor(Math.random() * colors.length)];\n  card.style.borderColor = rand;\n  alert('Border color randomized to ' + rand);\n}\n</` + `script>\n`

const defaultCss = `/* CSS Stylesheet */\nbody {\n  font-family: system-ui, sans-serif;\n  display: flex;\n  justify-content: center;\n  align-items: center;\n  min-height: 100vh;\n  margin: 0;\n  background: #09090b;\n  color: #e4e4e7;\n}\n\n.card {\n  background: #18181b;\n  border: 2px solid #27272a;\n  border-radius: 12px;\n  padding: 2rem;\n  text-align: center;\n  max-width: 350px;\n  box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);\n  transition: all 0.3s ease;\n}\n\n.card:hover {\n  transform: translateY(-4px);\n  box-shadow: 0 20px 30px -10px rgba(0,0,0,0.7);\n}\n\nh2 {\n  margin-top: 0;\n  color: #1aae39;\n}\n\np {\n  font-size: 0.9rem;\n  color: #a1a1aa;\n  line-height: 1.5;\n  margin-bottom: 1.5rem;\n}\n\nbutton {\n  background: #0075de;\n  color: white;\n  border: none;\n  padding: 0.5rem 1.25rem;\n  border-radius: 6px;\n  font-weight: 500;\n  cursor: pointer;\n  transition: opacity 0.2s;\n}\n\nbutton:hover {\n  opacity: 0.9;\n}\n`

// In-Memory Database Tables for SQL Mock
const mockDb = {
  users: [
    { id: 1, username: 'studious_coder', email: 'learner@iitm.ac.in', xp: 140, level: 2, streak: 4 },
    { id: 2, username: 'command_master', email: 'cmd@linux.org', xp: 520, level: 6, streak: 12 },
    { id: 3, username: 'py_wizard', email: 'pythonista@dev.com', xp: 290, level: 3, streak: 7 }
  ],
  subjects: [
    { id: 1, name: 'Linux System Commands', topics: 'Basic Commands, Filesystem, Permissions' },
    { id: 2, name: 'Git & GitHub', topics: 'Branching & Merging' },
    { id: 3, name: 'Python', topics: 'Data Structures' },
    { id: 4, name: 'SQL', topics: 'Aggregations' }
  ],
  leaderboard: [
    { id: 1, username: 'command_master', xp: 520, badge: 'Gold' },
    { id: 2, username: 'py_wizard', xp: 290, badge: 'Silver' },
    { id: 3, username: 'studious_coder', xp: 140, badge: 'Bronze' }
  ]
}

const codes = ref<Record<string, string>>({
  python: defaultTemplates.python,
  sql: defaultTemplates.sql,
  javascript: defaultTemplates.javascript,
  java: defaultTemplates.java,
  cpp: defaultTemplates.cpp,
  rust: defaultTemplates.rust,
  html: defaultHtml,
  css: defaultCss
})

const consoleLogs = ref<{ type: 'info' | 'output' | 'error'; text: string }[]>([])
const sqlResult = ref<{ headers: string[]; rows: any[][]; message?: string; error?: boolean } | null>(null)
const iframeHtml = ref('')

const editorRef = ref<HTMLTextAreaElement | null>(null)
const gutterRef = ref<HTMLDivElement | null>(null)

const activeCode = computed({
  get() {
    if (activeLang.value === 'html_css') {
      return activeWebTab.value === 'html' ? codes.value.html : codes.value.css
    }
    return codes.value[activeLang.value] || ''
  },
  set(val: string) {
    if (activeLang.value === 'html_css') {
      if (activeWebTab.value === 'html') {
        codes.value.html = val
      } else {
        codes.value.css = val
      }
    } else {
      codes.value[activeLang.value] = val
    }
  }
})

const lineCount = computed(() => {
  return (activeCode.value || '').split('\n').length
})

function handleScroll() {
  if (editorRef.value && gutterRef.value) {
    gutterRef.value.scrollTop = editorRef.value.scrollTop
  }
}

const isTerminalMode = computed(() => {
  return activeLang.value === 'gitbash' || activeLang.value === 'ubuntu'
})

// Focus input for terminal sandboxes
function focusTerminal() {
  if (isTerminalMode.value) {
    inputRef.value?.focus()
  }
}

onMounted(() => {
  focusTerminal()
})

// Switch Language handler
function selectLanguage(langId: string) {
  activeLang.value = langId
  if (langId === 'html_css') {
    activeOutputTab.value = 'preview'
    nextTick(() => runCode())
  } else if (langId === 'sql') {
    activeOutputTab.value = 'console'
  } else {
    activeOutputTab.value = 'console'
  }
  nextTick(() => {
    focusTerminal()
  })
}

// Reset code template
function resetCode() {
  if (activeLang.value === 'html_css') {
    codes.value.html = defaultHtml
    codes.value.css = defaultCss
    activeWebTab.value = 'html'
  } else {
    codes.value[activeLang.value] = defaultTemplates[activeLang.value] || ''
  }
  nextTick(() => runCode())
}

// Clear outputs
function clearLogs() {
  consoleLogs.value = []
  sqlResult.value = null
}

// GitBash key handlers
function handleEnter() {
  const cmd = currentInput.value.trim()
  if (!cmd) return

  commandHistory.value.push(cmd)
  historyIndex.value = commandHistory.value.length

  const output = terminal.executeCommand(cmd)
  currentInput.value = ''

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

// Python / JS helper scopes
function getSandboxHelpers() {
  return {
    range: (start: number, end?: number, step = 1) => {
      let s = start
      let e = end
      if (e === undefined) {
        e = start
        s = 0
      }
      const arr = []
      for (let i = s; i < e; i += step) {
        arr.push(i)
      }
      return arr
    },
    len: (obj: any) => {
      if (obj && obj.length !== undefined) return obj.length
      if (obj && typeof obj === 'object') return Object.keys(obj).length
      return 0
    }
  }
}

// Global Python-to-JS transpiler
function transpilePythonToJs(code: string): string {
  let jsCode = ""
  const lines = code.split('\n')
  let indentLevels: number[] = []

  for (let line of lines) {
    const trimmed = line.trim()
    if (!trimmed) {
      jsCode += "\n"
      continue
    }

    if (trimmed.startsWith('#')) {
      jsCode += "//" + line.substring(line.indexOf('#') + 1) + "\n"
      continue
    }

    const indent = line.length - line.trimStart().length
    while (indentLevels.length > 0 && indentLevels[indentLevels.length - 1] > indent) {
      jsCode += " ".repeat(indentLevels[indentLevels.length - 1]) + "}\n"
      indentLevels.pop()
    }

    let processed = trimmed

    if (processed.startsWith('def ') && processed.endsWith(':')) {
      const funcSig = processed.slice(4, -1)
      processed = `function ${funcSig} {`
      indentLevels.push(indent)
    } else if (processed.startsWith('if ') && processed.endsWith(':')) {
      const cond = processed.slice(3, -1)
      processed = `if (${cond}) {`
      indentLevels.push(indent)
    } else if (processed.startsWith('elif ') && processed.endsWith(':')) {
      const cond = processed.slice(5, -1)
      processed = `else if (${cond}) {`
      indentLevels.push(indent)
    } else if (processed === 'else:') {
      processed = `else {`
      indentLevels.push(indent)
    } else if (processed.startsWith('for ') && processed.endsWith(':')) {
      const forSig = processed.slice(4, -1)
      const parts = forSig.split(' in ')
      if (parts.length === 2) {
        const iterVar = parts[0].trim()
        const iterable = parts[1].trim()
        processed = `for (let ${iterVar} of ${iterable}) {`
        indentLevels.push(indent)
      }
    } else if (processed.startsWith('while ') && processed.endsWith(':')) {
      const cond = processed.slice(6, -1)
      processed = `while (${cond}) {`
      indentLevels.push(indent)
    }

    // Translate f-string printing: print(f"...") or print(...)
    if (processed.startsWith('print(') && processed.endsWith(')')) {
      let inner = processed.slice(6, -1)
      if ((inner.startsWith('f"') && inner.endsWith('"')) || (inner.startsWith("f'") && inner.endsWith("'"))) {
        inner = '`' + inner.slice(2, -1).replace(/\{([^}]+)\}/g, '${$1}') + '`'
      }
      processed = `console.log(${inner});`
    }

    processed = processed
      .replace(/\bTrue\b/g, 'true')
      .replace(/\bFalse\b/g, 'false')
      .replace(/\bNone\b/g, 'null')
      .replace(/\band\b/g, '&&')
      .replace(/\bor\b/g, '||')
      .replace(/\bnot\b/g, '!')

    jsCode += " ".repeat(indent) + processed + "\n"
  }

  while (indentLevels.length > 0) {
    jsCode += " ".repeat(indentLevels[indentLevels.length - 1]) + "}\n"
    indentLevels.pop()
  }

  return jsCode
}

// Jupyter Notebook structures & states
interface NotebookCell {
  id: string
  type: 'code' | 'markdown'
  source: string
  output: { type: 'output' | 'error'; text: string }[]
  executionCount: number | null
  isEditingMarkdown: boolean
}

const notebookCells = ref<NotebookCell[]>([
  {
    id: 'c1',
    type: 'markdown',
    source: '# Jupyter Notebook Sandbox\nWelcome! This is an interactive client-side Jupyter Notebook. \n- Double-click any Markdown cell to edit it.\n- Press **Shift + Enter** or click the Play button to execute a Code cell.\n- Variables and functions persist between cells!',
    output: [],
    executionCount: null,
    isEditingMarkdown: false
  },
  {
    id: 'c2',
    type: 'code',
    source: '# Define a variable\nmessage = "Jupyter Notebook is running client-side!"\nx = 12\ny = 30\nprint(message)\nprint(f"x + y = {x + y}")',
    output: [],
    executionCount: null,
    isEditingMarkdown: false
  },
  {
    id: 'c3',
    type: 'code',
    source: '# Use variables from previous cell executions!\nprint(f"Triple of x is {x * 3}")\n\ndef cuboid_volume(l, w, h):\n    return l * w * h\n\nprint(f"Volume = {cuboid_volume(x, y, 2)}")',
    output: [],
    executionCount: null,
    isEditingMarkdown: false
  }
])

const focusedCellIndex = ref<number | null>(null)
let executionCounter = 1

async function runNotebookCell(index: number) {
  const cell = notebookCells.value[index]
  if (cell.type !== 'code') return

  cell.executionCount = null
  cell.output = []
  await nextTick()

  const logs: { type: 'output' | 'error'; text: string }[] = []
  const originalLog = console.log
  console.log = (...args) => {
    logs.push({
      type: 'output',
      text: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' ')
    })
  }

  try {
    let combinedJs = ""
    
    // Setup helper range/len
    combinedJs += "const range = helpers.range;\nconst len = helpers.len;\n"

    // Execute previous code cells silently to populate context variables
    if (index > 0) {
      combinedJs += "const originalLog = console.log;\nconsole.log = () => {};\n"
      for (let i = 0; i < index; i++) {
        const prevCell = notebookCells.value[i]
        if (prevCell.type === 'code') {
          combinedJs += transpilePythonToJs(prevCell.source) + "\n"
        }
      }
      combinedJs += "console.log = originalLog;\n"
    }

    // Execute active cell code
    combinedJs += transpilePythonToJs(cell.source)

    const helpers = getSandboxHelpers()
    const runner = new Function('helpers', combinedJs)
    runner(helpers)

    cell.output = logs
    cell.executionCount = executionCounter++
  } catch (err: any) {
    cell.output = [{ type: 'error', text: 'Traceback (most recent call last):\nRuntimeError: ' + err.message }]
    cell.executionCount = executionCounter++
  } finally {
    console.log = originalLog
  }
}

function addNotebookCell(type: 'code' | 'markdown', index?: number) {
  const newCell: NotebookCell = {
    id: 'c_' + Math.random().toString(36).substring(2, 9),
    type,
    source: type === 'code' ? '# Write code here\n' : 'Double-click to edit markdown...\n',
    output: [],
    executionCount: null,
    isEditingMarkdown: type === 'markdown'
  }
  if (index !== undefined) {
    notebookCells.value.splice(index + 1, 0, newCell)
  } else {
    notebookCells.value.push(newCell)
  }
}

function deleteNotebookCell(index: number) {
  notebookCells.value.splice(index, 1)
  if (notebookCells.value.length === 0) {
    addNotebookCell('code')
  }
}

function moveNotebookCell(index: number, direction: 'up' | 'down') {
  if (direction === 'up' && index > 0) {
    const temp = notebookCells.value[index]
    notebookCells.value[index] = notebookCells.value[index - 1]
    notebookCells.value[index - 1] = temp
  } else if (direction === 'down' && index < notebookCells.value.length - 1) {
    const temp = notebookCells.value[index]
    notebookCells.value[index] = notebookCells.value[index + 1]
    notebookCells.value[index + 1] = temp
  }
}

async function runAllNotebookCells() {
  for (let i = 0; i < notebookCells.value.length; i++) {
    if (notebookCells.value[i].type === 'code') {
      await runNotebookCell(i)
    }
  }
}

function clearAllNotebookOutputs() {
  executionCounter = 1
  notebookCells.value.forEach(cell => {
    cell.output = []
    cell.executionCount = null
  })
}

function parseSimpleMarkdown(md: string) {
  if (!md || !md.trim()) return '<p class="text-neutral-500 italic">Empty markdown cell. Double-click to edit.</p>'
  
  let escaped = md
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  escaped = escaped.replace(/^### (.*?)$/gm, '<h3 class="text-sm font-bold text-ink mt-3 mb-1 font-sans">$1</h3>')
  escaped = escaped.replace(/^## (.*?)$/gm, '<h2 class="text-base font-bold text-ink mt-4 mb-2 font-sans">$1</h2>')
  escaped = escaped.replace(/^# (.*?)$/gm, '<h1 class="text-lg font-bold text-ink mt-5 mb-3 border-b border-hairline pb-1 font-sans">$1</h1>')

  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>')
  escaped = escaped.replace(/`([^`]+)`/g, '<code class="bg-canvas-soft border border-hairline px-1.5 py-0.5 rounded font-mono text-xxs text-primary">$1</code>')
  escaped = escaped.replace(/^- (.*?)$/gm, '<li class="ml-4 list-disc text-xs text-ink-secondary mb-1">$1</li>')

  const paragraphs = escaped.split('\n\n')
  return paragraphs.map(p => {
    const trimmed = p.trim()
    if (!trimmed) return ''
    if (trimmed.startsWith('<h') || trimmed.startsWith('<li')) return trimmed
    return `<p class="text-xs text-ink-secondary leading-relaxed mb-2 font-sans">${trimmed.replace(/\n/g, '<br/>')}</p>`
  }).join('')
}

// Main Execution Router
function runCode() {
  const codeText = activeCode.value
  const lang = activeLang.value

  if (lang === 'html_css') {
    // Compile live visual preview
    iframeHtml.value = `
      <!DOCTYPE html>
      <html>
        <head>
          <meta charset="utf-8">
          <style>${codes.value.css}</style>
        </head>
        <body>
          ${codes.value.html}
        </body>
      </html>
    `
    consoleLogs.value = [{ type: 'info', text: 'HTML & CSS live preview rendered.' }]
    return
  }

  // Clear previous execution state
  consoleLogs.value = []
  sqlResult.value = null

  if (lang === 'javascript') {
    consoleLogs.value.push({ type: 'info', text: 'Running JavaScript...\n' })
    const logs: string[] = []
    const originalLog = console.log
    console.log = (...args) => {
      logs.push(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '))
    }

    try {
      const runner = new Function(codes.value.javascript)
      runner()
      logs.forEach(l => consoleLogs.value.push({ type: 'output', text: l }))
      consoleLogs.value.push({ type: 'info', text: '\nProcess finished with exit code 0.' })
    } catch (err: any) {
      consoleLogs.value.push({ type: 'error', text: 'TypeError: ' + err.message })
    } finally {
      console.log = originalLog
    }
  } 
  else if (lang === 'python') {
    consoleLogs.value.push({ type: 'info', text: 'python3 main.py...\n' })
    const logs: string[] = []
    const originalLog = console.log
    console.log = (...args) => {
      logs.push(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '))
    }

    try {
      const jsCode = transpilePythonToJs(codes.value.python)
      const helpers = getSandboxHelpers()
      const runner = new Function('range', 'len', jsCode)
      runner(helpers.range, helpers.len)

      logs.forEach(l => consoleLogs.value.push({ type: 'output', text: l }))
      consoleLogs.value.push({ type: 'info', text: '\nProcess finished with exit code 0.' })
    } catch (err: any) {
      consoleLogs.value.push({ type: 'error', text: 'SyntaxError/RuntimeError: ' + err.message })
    } finally {
      console.log = originalLog
    }
  } 
  else if (lang === 'sql') {
    consoleLogs.value.push({ type: 'info', text: 'Evaluating SQL query...\n' })
    const result = runSql(codes.value.sql)
    sqlResult.value = result
    
    if (result.error) {
      consoleLogs.value.push({ type: 'error', text: result.message || 'Error executing query' })
    } else {
      consoleLogs.value.push({ type: 'info', text: result.message || 'Query successful.' })
      activeOutputTab.value = 'preview' // switch to preview table tab automatically for SQL results
    }
  } 
  else if (lang === 'java') {
    consoleLogs.value.push({ type: 'info', text: 'javac Main.java\njava Main\n' })
    consoleLogs.value.push({ type: 'info', text: 'Compiling Main.java...' })
    consoleLogs.value.push({ type: 'info', text: 'Compilation successful. Executing bytecode...\n' })
    
    try {
      const mainMatch = codes.value.java.match(/public static void main\s*\(String\s*\[\s*\]\s*args\)\s*\{([\s\S]*)\}\s*\}\s*$/)
      if (mainMatch) {
        let body = mainMatch[1]
        body = body
          .replace(/System\.out\.println\((.*?)\);/g, 'console.log($1);')
          .replace(/System\.out\.print\((.*?)\);/g, 'console.log($1);')
          .replace(/\bint\b/g, 'let')
          .replace(/\bdouble\b/g, 'let')
          .replace(/\bfloat\b/g, 'let')
          .replace(/\bString\b/g, 'let')
          .replace(/\bboolean\b/g, 'let')
          
        const logs: string[] = []
        const originalLog = console.log
        console.log = (...args) => {
          logs.push(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '))
        }
        
        try {
          new Function(body)()
          logs.forEach(l => consoleLogs.value.push({ type: 'output', text: l }))
          consoleLogs.value.push({ type: 'info', text: '\nProcess finished with exit code 0.' })
        } catch(e: any) {
          consoleLogs.value.push({ type: 'error', text: 'Java Runtime Exception: ' + e.message })
        } finally {
          console.log = originalLog
        }
      } else {
        consoleLogs.value.push({ type: 'error', text: 'Error: Could not find main method: public static void main(String[] args)' })
      }
    } catch(e: any) {
      consoleLogs.value.push({ type: 'error', text: 'Compiler Exception: ' + e.message })
    }
  } 
  else if (lang === 'cpp') {
    consoleLogs.value.push({ type: 'info', text: 'g++ -o main main.cpp\n./main\n' })
    consoleLogs.value.push({ type: 'info', text: 'Compiling main.cpp...' })
    consoleLogs.value.push({ type: 'info', text: 'Compilation successful. Launching main...\n' })
    
    try {
      const mainMatch = codes.value.cpp.match(/int main\s*\(\)\s*\{([\s\S]*)return\s+0\s*;\s*\}\s*$/) || codes.value.cpp.match(/int main\s*\(\)\s*\{([\s\S]*)\}\s*$/)
      if (mainMatch) {
        let body = mainMatch[1]
        body = body
          .replace(/cout\s*<<\s*endl\s*;/g, 'console.log("");')
          .replace(/cout\s*<<\s*([\s\S]*?)\s*<<\s*endl\s*;/g, 'console.log($1);')
          .replace(/cout\s*<<\s*([\s\S]*?);/g, 'console.log($1);')
          .replace(/\bint\b/g, 'let')
          .replace(/\bdouble\b/g, 'let')
          .replace(/\bfloat\b/g, 'let')
          .replace(/\bstring\b/g, 'let')
          .replace(/\bbool\b/g, 'let')
          .replace(/<<\s*/g, '+ ')
          
        const logs: string[] = []
        const originalLog = console.log
        console.log = (...args) => {
          logs.push(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '))
        }
        
        try {
          new Function(body)()
          logs.forEach(l => consoleLogs.value.push({ type: 'output', text: l }))
          consoleLogs.value.push({ type: 'info', text: '\nProcess finished with exit code 0.' })
        } catch(e: any) {
          consoleLogs.value.push({ type: 'error', text: 'C++ SegFault/Runtime Exception: ' + e.message })
        } finally {
          console.log = originalLog
        }
      } else {
        consoleLogs.value.push({ type: 'error', text: 'Error: Could not find main function: int main()' })
      }
    } catch(e: any) {
      consoleLogs.value.push({ type: 'error', text: 'Compiler Exception: ' + e.message })
    }
  } 
  else if (lang === 'rust') {
    consoleLogs.value.push({ type: 'info', text: 'cargo run\n' })
    consoleLogs.value.push({ type: 'info', text: 'Compiling main.rs...' })
    consoleLogs.value.push({ type: 'info', text: 'Compilation successful. Executing target/debug/main...\n' })
    
    try {
      const mainMatch = codes.value.rust.match(/fn main\s*\(\)\s*\{([\s\S]*)\}\s*$/)
      if (mainMatch) {
        let body = mainMatch[1]
        
        body = body.replace(/println!\s*\(\s*"(.*?)"\s*,\s*(.*?)\s*\)\s*;/g, (match, str, vars) => {
          const jsStr = str.replace(/{}/g, '%s')
          return `console.log("${jsStr}".replace('%s', ${vars}));`
        })
        body = body.replace(/println!\s*\(\s*"(.*?)"\s*\)\s*;/g, 'console.log("$1");')
        body = body.replace(/for\s+([a-zA-Z_0-9]+)\s+in\s+([0-9]+)\.\.([0-9]+)\s*\{/g, 'for (let $1 = $2; $1 < $3; $1++) {')
        body = body.replace(/let\s+mut\s+/g, 'let ')
        
        const logs: string[] = []
        const originalLog = console.log
        console.log = (...args) => {
          logs.push(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : String(arg)).join(' '))
        }
        
        try {
          new Function(body)()
          logs.forEach(l => consoleLogs.value.push({ type: 'output', text: l }))
          consoleLogs.value.push({ type: 'info', text: '\nProcess finished with exit code 0.' })
        } catch(e: any) {
          consoleLogs.value.push({ type: 'error', text: 'Rust Panic: ' + e.message })
        } finally {
          console.log = originalLog
        }
      } else {
        consoleLogs.value.push({ type: 'error', text: 'Error: Could not find main function: fn main()' })
      }
    } catch(e: any) {
      consoleLogs.value.push({ type: 'error', text: 'Compiler Exception: ' + e.message })
    }
  }
}

// SQL Query parser logic
function runSql(queryText: string): { headers: string[]; rows: any[][]; message?: string; error?: boolean } {
  const q = queryText.trim().toLowerCase().replace(/;$/, '')
  if (!q) {
    return { headers: [], rows: [], message: 'No query entered.' }
  }

  if (q.startsWith('select')) {
    const selectRegex = /^select\s+([\s\S]+?)\s+from\s+([a-zA-Z_0-9]+)(?:\s+where\s+([\s\S]+?))?(?:\s+order\s+by\s+([a-zA-Z_0-9]+)(?:\s+(asc|desc))?)?$/
    const match = q.match(selectRegex)
    
    if (!match) {
      if (q.includes('from users')) {
        return { headers: ['id', 'username', 'email', 'xp', 'level', 'streak'], rows: mockDb.users.map(u => [u.id, u.username, u.email, u.xp, u.level, u.streak]), message: 'Syntax Alert: Executed standard SELECT on users' }
      } else if (q.includes('from subjects')) {
        return { headers: ['id', 'name', 'topics'], rows: mockDb.subjects.map(s => [s.id, s.name, s.topics]), message: 'Syntax Alert: Executed standard SELECT on subjects' }
      } else if (q.includes('from leaderboard')) {
        return { headers: ['id', 'username', 'xp', 'badge'], rows: mockDb.leaderboard.map(l => [l.id, l.username, l.xp, l.badge]), message: 'Syntax Alert: Executed standard SELECT on leaderboard' }
      }
      return { headers: [], rows: [], error: true, message: 'Syntax Error: Support is limited to SELECT queries on users, subjects, leaderboard.' }
    }

    const colsStr = match[1].trim()
    const tableName = match[2].trim()
    const whereStr = match[3] ? match[3].trim() : null
    const orderByCol = match[4] ? match[4].trim() : null
    const orderByDir = match[5] ? match[5].trim() : 'asc'

    if (tableName !== 'users' && tableName !== 'subjects' && tableName !== 'leaderboard') {
      return { headers: [], rows: [], error: true, message: `Error: Table '${tableName}' does not exist.` }
    }

    let dataList = [...mockDb[tableName as keyof typeof mockDb]]

    // WHERE
    if (whereStr) {
      const condRegex = /^([a-zA-Z_0-9]+)\s*([>=<]+)\s*(.*?)$/
      const condMatch = whereStr.match(condRegex)
      if (condMatch) {
        const col = condMatch[1].trim()
        const op = condMatch[2].trim()
        const rawVal = condMatch[3].trim().replace(/['"]/g, '')

        dataList = dataList.filter((row: any) => {
          const rowVal = row[col]
          if (rowVal === undefined) return false

          if (!isNaN(Number(rawVal)) && typeof rowVal === 'number') {
            const numVal = Number(rawVal)
            if (op === '=') return rowVal === numVal
            if (op === '>') return rowVal > numVal
            if (op === '<') return rowVal < numVal
            if (op === '>=') return rowVal >= numVal
            if (op === '<=') return rowVal <= numVal
          } else {
            if (op === '=') return String(rowVal).toLowerCase() === rawVal.toLowerCase()
          }
          return false
        })
      }
    }

    // ORDER BY
    if (orderByCol) {
      dataList.sort((a: any, b: any) => {
        const valA = a[orderByCol]
        const valB = b[orderByCol]
        if (valA === undefined || valB === undefined) return 0

        if (typeof valA === 'number' && typeof valB === 'number') {
          return orderByDir === 'desc' ? valB - valA : valA - valB
        } else {
          return orderByDir === 'desc'
            ? String(valB).localeCompare(String(valA))
            : String(valA).localeCompare(String(valB))
        }
      })
    }

    // Selected columns
    let headers: string[] = []
    if (colsStr === '*') {
      if (tableName === 'users') headers = ['id', 'username', 'email', 'xp', 'level', 'streak']
      else if (tableName === 'subjects') headers = ['id', 'name', 'topics']
      else headers = ['id', 'username', 'xp', 'badge']
    } else {
      headers = colsStr.split(',').map(s => s.trim().toLowerCase())
    }

    const rows = dataList.map((row: any) => {
      return headers.map(h => row[h] !== undefined ? row[h] : null)
    })

    return { headers, rows, message: `Query successful: ${rows.length} rows returned.` }
  }

  return { headers: [], rows: [], message: 'Mock SQL Engine: Query executed successfully (0 rows affected).' }
}
</script>

<template>
  <div class="flex flex-col lg:flex-row h-full min-h-[500px] border border-hairline bg-surface rounded-xl overflow-hidden shadow-notion-soft select-none">
    
    <!-- Left Panel: Language Selection Sidebar -->
    <div class="w-full lg:w-48 bg-canvas-soft border-b lg:border-b-0 lg:border-r border-hairline flex flex-row lg:flex-col overflow-x-auto lg:overflow-x-visible lg:overflow-y-auto shrink-0 select-none scrollbar-thin">
      <button v-for="lang in languages" :key="lang.id"
              @click="selectLanguage(lang.id)"
              class="flex-1 lg:flex-initial text-left px-4 py-3 flex items-center gap-2.5 transition-all text-xs font-semibold select-none border-b lg:border-b-0 lg:border-r-2"
              :class="activeLang === lang.id
                ? 'bg-surface text-primary border-primary lg:border-r-primary'
                : 'text-ink-muted hover:text-ink hover:bg-canvas-soft/40 border-transparent lg:border-r-transparent'">
        <!-- Custom Jupyter Logo SVG -->
        <span v-if="lang.id === 'jupyter'" class="w-3.5 h-3.5 flex items-center justify-center shrink-0"
              :class="activeLang === 'jupyter' ? 'text-orange-500' : 'text-ink-faint'">
          <svg viewBox="0 0 100 100" class="w-4 h-4 fill-none" stroke="currentColor">
            <ellipse cx="50" cy="50" rx="42" ry="12" stroke-width="8" transform="rotate(-30 50 50)" />
            <circle cx="35" cy="35" r="9" fill="currentColor" />
            <circle cx="65" cy="65" r="6" fill="currentColor" />
            <circle cx="50" cy="50" r="17" fill="currentColor" />
          </svg>
        </span>
        <span v-else v-html="getFaIcon(lang.icon)" 
              class="w-3.5 h-3.5 flex items-center justify-center shrink-0"
              :class="activeLang === lang.id ? 'text-primary' : 'text-ink-faint'"></span>
        <div class="hidden sm:block">
          <span class="block truncate">{{ lang.name }}</span>
          <span class="hidden lg:block text-[9px] text-ink-faint font-normal truncate mt-0.5">{{ lang.desc }}</span>
        </div>
      </button>
    </div>

    <!-- Right Workspace Area -->
    <div class="flex-1 flex flex-col min-w-0 h-full">
      
      <!-- Interactive Terminal Layout (Ubuntu / GitBash) -->
      <div v-if="isTerminalMode" class="flex-1 flex flex-col h-full bg-neutral-950 overflow-hidden relative" @click="focusTerminal">
        <!-- Title Bar -->
        <div class="bg-neutral-900 border-b border-neutral-800 px-4 py-2 flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-green-500"></span>
            <span class="text-xxs text-neutral-400 ml-2 font-mono uppercase font-bold">Sandbox ({{ activeLang }})</span>
          </div>
          <button @click.stop="terminal.resetFs()" class="text-[10px] bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 px-2 py-0.5 rounded transition-all font-mono">
            🔄 Reset FS
          </button>
        </div>

        <!-- Terminal Output -->
        <div ref="terminalBodyRef" class="flex-1 p-4 overflow-y-auto space-y-2 select-text font-mono text-xs">
          <!-- Ubuntu banner -->
          <div v-if="activeLang === 'ubuntu'" class="text-neutral-400 mb-2 leading-relaxed">
            Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0-generic x86_64)<br/>
            * Documentation:  https://help.ubuntu.com<br/>
            * Management:     https://landscape.canonical.com<br/>
            * Support:        https://ubuntu.com/advantage<br/><br/>
            Type 'help' to see list of commands. Filesystem changes are stored in-memory.
          </div>
          <!-- GitBash banner -->
          <div v-else class="text-neutral-500 mb-2">
            LinuxMaster Virtual Shell v1.0.0 (GitBash Sandbox)<br/>
            Type 'help' to see list of commands. Filesystem changes are stored in-memory.
          </div>
          
          <div v-for="(line, idx) in terminal.history.value" :key="idx">
            <div class="flex items-center gap-1.5 text-neutral-400">
              <span class="text-emerald-500 font-bold" v-if="activeLang === 'ubuntu'">learner@ubuntu:~{{ terminal.currentDir.value }}$</span>
              <span class="text-emerald-500 font-bold" v-else>learner@linux:~{{ terminal.currentDir.value }}#</span>
              <span>{{ line.command }}</span>
            </div>
            <div class="whitespace-pre-wrap mt-0.5 leading-relaxed" :class="line.error ? 'text-red-400' : 'text-neutral-300'">
              {{ line.output }}
            </div>
          </div>

          <!-- Active Input Line -->
          <div class="flex items-center gap-1.5">
            <span class="text-emerald-500 font-bold flex-shrink-0" v-if="activeLang === 'ubuntu'">learner@ubuntu:~{{ terminal.currentDir.value }}$</span>
            <span class="text-emerald-500 font-bold flex-shrink-0" v-else>learner@linux:~{{ terminal.currentDir.value }}#</span>
            <input ref="inputRef" v-model="currentInput" type="text"
                   class="flex-1 bg-transparent border-none outline-none focus:ring-0 p-0 m-0 text-neutral-200 font-mono caret-primary text-xs"
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

      <!-- Jupyter Notebook Layout -->
      <div v-else-if="activeLang === 'jupyter'" class="flex-1 flex flex-col h-full bg-canvas-soft overflow-hidden select-none">
        <!-- Notebook Toolbar -->
        <div class="bg-surface border-b border-hairline px-4 py-2 flex items-center justify-between select-none">
          <div class="flex items-center gap-1.5 font-mono text-xs text-ink-muted">
            <svg viewBox="0 0 100 100" class="w-4 h-4 text-orange-500" fill="none">
              <ellipse cx="50" cy="50" rx="42" ry="12" stroke="currentColor" stroke-width="8" transform="rotate(-30 50 50)" />
              <circle cx="35" cy="35" r="9" fill="currentColor" />
              <circle cx="65" cy="65" r="6" fill="currentColor" />
              <circle cx="50" cy="50" r="17" fill="currentColor" />
            </svg>
            <span class="font-bold">workspace.ipynb</span>
          </div>
          
          <div class="flex gap-2">
            <button @click="runAllNotebookCells" class="text-[10px] font-semibold bg-neutral-800 hover:bg-neutral-700 text-neutral-200 px-3 py-1.5 rounded transition-all flex items-center gap-1.5 cursor-pointer">
              <span v-html="getFaIcon(faPlay)" class="w-2.5 h-2.5 flex items-center text-sticker-green"></span>
              <span>Run All</span>
            </button>
            <button @click="addNotebookCell('code')" class="text-[10px] font-semibold bg-surface hover:bg-canvas-soft text-ink border border-hairline px-3 py-1.5 rounded transition-all cursor-pointer">
              + Code
            </button>
            <button @click="addNotebookCell('markdown')" class="text-[10px] font-semibold bg-surface hover:bg-canvas-soft text-ink border border-hairline px-3 py-1.5 rounded transition-all cursor-pointer">
              + Markdown
            </button>
            <button @click="clearAllNotebookOutputs" class="text-[10px] font-semibold bg-surface hover:bg-canvas-soft text-ink-muted border border-hairline px-3 py-1.5 rounded transition-all cursor-pointer">
              Clear Outputs
            </button>
          </div>
        </div>
        
        <!-- Notebook Cells Scroll Area -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4 select-text scrollbar-thin">
          <div v-for="(cell, cIdx) in notebookCells" :key="cell.id" 
               class="bg-surface rounded-lg border border-hairline overflow-hidden shadow-xxs transition-all relative group"
               :class="focusedCellIndex === cIdx ? 'border-primary shadow-sm' : 'hover:border-neutral-300'"
               @click="focusedCellIndex = cIdx">
            
            <!-- Cell Header Actions -->
            <div class="absolute right-2 top-2 hidden group-hover:flex gap-1 bg-surface border border-hairline shadow-sm rounded p-0.5 z-10 select-none">
              <button @click.stop="moveNotebookCell(cIdx, 'up')" :disabled="cIdx === 0" class="p-1 hover:bg-canvas-soft rounded text-ink-muted disabled:opacity-30">▲</button>
              <button @click.stop="moveNotebookCell(cIdx, 'down')" :disabled="cIdx === notebookCells.length - 1" class="p-1 hover:bg-canvas-soft rounded text-ink-muted disabled:opacity-30">▼</button>
              <button @click.stop="deleteNotebookCell(cIdx)" class="p-1 hover:bg-red-50 text-red-500 rounded">✕</button>
            </div>

            <div class="flex items-stretch select-text">
              <!-- Left Gutter -->
              <div class="w-16 bg-canvas-soft/40 border-r border-hairline flex flex-col items-center pt-3 select-none shrink-0 font-mono text-[10px]">
                <button v-if="cell.type === 'code'" @click.stop="runNotebookCell(cIdx)" 
                        class="p-1 hover:bg-primary/10 rounded-full text-primary hover:text-primary-active mb-1">
                  <span v-html="getFaIcon(faPlay)" class="w-2.5 h-2.5 flex items-center"></span>
                </button>
                <span v-if="cell.type === 'code'" class="text-ink-faint">
                  {{ cell.executionCount === null ? 'In [*]:' : `In [${cell.executionCount}]:` }}
                </span>
              </div>
              
              <!-- Editor/Content Area -->
              <div class="flex-1 min-w-0 p-3 select-text">
                <!-- Markdown Cell -->
                <div v-if="cell.type === 'markdown'" class="select-text">
                  <textarea v-if="cell.isEditingMarkdown" v-model="cell.source" 
                            @blur="cell.isEditingMarkdown = false" 
                            class="w-full bg-canvas-soft border border-hairline p-3 font-mono text-xs rounded focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed whitespace-pre-wrap resize-y select-text"
                            rows="4" autofocus></textarea>
                  <div v-else @dblclick="cell.isEditingMarkdown = true" 
                       v-html="parseSimpleMarkdown(cell.source)"
                       class="prose prose-sm max-w-none select-text cursor-text min-h-[1.5rem]"></div>
                </div>
                
                <!-- Code Cell -->
                <div v-else class="select-text">
                  <textarea v-model="cell.source" 
                            class="w-full bg-neutral-950 text-neutral-200 border border-neutral-800 p-3 font-mono text-xs rounded focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed whitespace-pre select-text resize-y"
                            rows="4" spellcheck="false"></textarea>
                </div>
              </div>
            </div>

            <!-- Cell Output -->
            <div v-if="cell.type === 'code' && cell.output.length > 0" class="border-t border-hairline bg-canvas-soft/30 p-3 font-mono text-[11px] select-text">
              <div v-for="(out, oIdx) in cell.output" :key="oIdx" 
                   class="whitespace-pre-wrap leading-relaxed select-text"
                   :class="out.type === 'error' ? 'text-red-600 font-bold' : 'text-ink-secondary'">
                {{ out.text }}
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- Code Sandbox Editor & Console Output split-layout -->
      <div v-else class="flex-1 flex flex-col md:flex-row overflow-hidden h-full items-stretch">
        
        <!-- Editor Left Split -->
        <div class="flex-1 flex flex-col border-b md:border-b-0 md:border-r border-hairline bg-neutral-950 overflow-hidden h-full">
          <!-- Editor Title Bar -->
          <div class="bg-neutral-900 border-b border-neutral-800 px-4 py-2 flex items-center justify-between text-neutral-300 select-none">
            <div class="flex items-center gap-1.5 font-mono text-xs">
              <span class="w-2.5 h-2.5 rounded-full bg-red-500"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-yellow-500"></span>
              <span class="w-2.5 h-2.5 rounded-full bg-green-500"></span>
              <span class="text-xxs text-neutral-400 ml-2 font-mono uppercase font-bold">Sandbox ({{ activeLang }})</span>
            </div>
            
            <!-- Tab switches for HTML/CSS mode -->
            <div v-if="activeLang === 'html_css'" class="flex bg-neutral-800 p-0.5 rounded border border-neutral-700">
              <button @click="activeWebTab = 'html'" 
                      class="px-2 py-0.5 text-[10px] font-mono rounded transition-colors"
                      :class="activeWebTab === 'html' ? 'bg-neutral-600 text-white font-bold' : 'text-neutral-400 hover:text-white'">
                index.html
              </button>
              <button @click="activeWebTab = 'css'" 
                      class="px-2 py-0.5 text-[10px] font-mono rounded transition-colors"
                      :class="activeWebTab === 'css' ? 'bg-neutral-600 text-white font-bold' : 'text-neutral-400 hover:text-white'">
                style.css
              </button>
            </div>
            
            <div class="text-[10px] text-neutral-500 font-mono">
              Main{{ languages.find(l => l.id === activeLang)?.ext }}
            </div>
          </div>

          <!-- Code Entry Space -->
          <div class="flex-1 flex overflow-hidden relative font-mono text-xs bg-neutral-950">
            <!-- Line-number Gutter -->
            <div ref="gutterRef" class="w-10 bg-neutral-900 border-r border-neutral-800 py-3 text-right pr-2 text-neutral-600 select-none overflow-hidden leading-6">
              <div v-for="n in lineCount" :key="n" class="h-6">{{ n }}</div>
            </div>
            <!-- Interactive Textarea -->
            <textarea ref="editorRef" v-model="activeCode" 
                      class="flex-1 bg-transparent border-none outline-none resize-none p-3 text-neutral-200 font-mono text-xs leading-6 focus:ring-0 whitespace-pre overflow-auto scrollbar-thin select-text"
                      placeholder="Write your code here..."
                      @scroll="handleScroll"
                      spellcheck="false"></textarea>
          </div>

          <!-- Bottom Action Bar -->
          <div class="bg-neutral-900 border-t border-neutral-800 px-4 py-2.5 flex items-center justify-between">
            <div class="flex gap-2">
              <button @click="resetCode" class="text-[10px] font-semibold bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 px-3 py-1.5 rounded transition-all flex items-center gap-1.5">
                <span v-html="getFaIcon(faRotateLeft)" class="w-2.5 h-2.5 flex items-center text-neutral-400"></span>
                <span>Reset Template</span>
              </button>
              <button @click="clearLogs" class="text-[10px] font-semibold bg-neutral-800 hover:bg-neutral-700 text-neutral-300 border border-neutral-700 px-3 py-1.5 rounded transition-all flex items-center gap-1.5">
                <span v-html="getFaIcon(faTrash)" class="w-2.5 h-2.5 flex items-center text-neutral-400"></span>
                <span>Clear Outputs</span>
              </button>
            </div>
            
            <button @click="runCode" class="text-xs font-bold bg-sticker-green hover:bg-green-600 text-white px-5 py-1.5 rounded-full transition-all flex items-center gap-1.5 active:scale-95 shadow-md">
              <span v-html="getFaIcon(faPlay)" class="w-2.5 h-2.5 flex items-center text-white"></span>
              <span>Run Code</span>
            </button>
          </div>
        </div>

        <!-- Output Pane Right Split -->
        <div class="flex-1 flex flex-col overflow-hidden h-full items-stretch bg-canvas-soft">
          <!-- Output tab header -->
          <div class="flex border-b border-hairline bg-surface select-none font-sans text-xs">
            <button @click="activeOutputTab = 'console'"
                    class="px-4 py-2 font-bold border-r border-hairline transition-colors flex items-center gap-1.5"
                    :class="activeOutputTab === 'console' ? 'bg-canvas-soft text-ink border-b-2 border-b-primary' : 'text-ink-muted hover:text-ink'">
              <span v-html="getFaIcon(faTerminal)" class="w-3 h-3 text-ink-faint flex items-center"></span>
              <span>Console Log</span>
            </button>
            
            <button v-if="activeLang === 'html_css'" @click="activeOutputTab = 'preview'"
                    class="px-4 py-2 font-bold border-r border-hairline transition-colors flex items-center gap-1.5"
                    :class="activeOutputTab === 'preview' ? 'bg-canvas-soft text-ink border-b-2 border-b-primary' : 'text-ink-muted hover:text-ink'">
              <span v-html="getFaIcon(faEye)" class="w-3 h-3 text-ink-faint flex items-center"></span>
              <span>Live Preview</span>
            </button>
            
            <button v-if="activeLang === 'sql'" @click="activeOutputTab = 'preview'"
                    class="px-4 py-2 font-bold border-r border-hairline transition-colors flex items-center gap-1.5"
                    :class="activeOutputTab === 'preview' ? 'bg-canvas-soft text-ink border-b-2 border-b-primary' : 'text-ink-muted hover:text-ink'">
              <span v-html="getFaIcon(faTable)" class="w-3 h-3 text-ink-faint flex items-center"></span>
              <span>Query Results</span>
            </button>
            
            <button v-if="activeLang === 'sql'" @click="activeOutputTab = 'db'"
                    class="px-4 py-2 font-bold border-r border-hairline transition-colors flex items-center gap-1.5"
                    :class="activeOutputTab === 'db' ? 'bg-canvas-soft text-ink border-b-2 border-b-primary' : 'text-ink-muted hover:text-ink'">
              <span v-html="getFaIcon(faDatabase)" class="w-3 h-3 text-ink-faint flex items-center"></span>
              <span>Database Tables</span>
            </button>
          </div>

          <!-- Output Body -->
          <div class="flex-1 overflow-y-auto p-4 select-text h-full">
            
            <!-- Output Console Logs -->
            <div v-if="activeOutputTab === 'console'" class="font-mono text-xs space-y-1 select-text">
              <div v-if="consoleLogs.length === 0" class="text-ink-faint select-none p-4 text-center">
                <span v-html="getFaIcon(faBug)" class="w-6 h-6 mx-auto mb-2 text-ink-faint/40 flex items-center justify-center"></span>
                <p>Run your script to view runtime details here.</p>
              </div>
              <div v-for="(log, idx) in consoleLogs" :key="idx" 
                   class="whitespace-pre-wrap leading-relaxed select-text"
                   :class="log.type === 'info' ? 'text-primary' : log.type === 'error' ? 'text-red-500 font-bold' : 'text-ink-secondary'">
                {{ log.text }}
              </div>
            </div>

            <!-- SQL Query Results Table Viewer -->
            <div v-else-if="activeOutputTab === 'preview' && activeLang === 'sql'" class="h-full">
              <div v-if="!sqlResult" class="text-center p-8 text-ink-muted font-sans text-xs select-none">
                <p>Write an SQL query and click "Run Code" to view rows here.</p>
              </div>
              <div v-else-if="sqlResult.error" class="bg-red-50 border border-red-200 text-red-700 p-4 rounded font-mono text-xs select-text">
                {{ sqlResult.message }}
              </div>
              <div v-else class="space-y-3">
                <p class="text-[10px] text-ink-muted font-mono">{{ sqlResult.message }}</p>
                <div class="overflow-x-auto border border-hairline bg-surface rounded-lg select-text shadow-xxs">
                  <table class="w-full text-left border-collapse font-sans text-xs">
                    <thead>
                      <tr class="bg-canvas-soft border-b border-hairline text-ink font-bold font-mono text-[10px] uppercase">
                        <th v-for="h in sqlResult.headers" :key="h" class="p-2.5 border-r border-hairline/60">{{ h }}</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-hairline">
                      <tr v-for="(row, rIdx) in sqlResult.rows" :key="rIdx" class="hover:bg-canvas-soft/30 transition-colors">
                        <td v-for="(cell, cIdx) in row" :key="cIdx" class="p-2.5 border-r border-hairline/60 font-mono text-ink-secondary">{{ cell }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- HTML/CSS live preview rendering inside a sandboxed Iframe -->
            <div v-else-if="activeOutputTab === 'preview' && activeLang === 'html_css'" class="w-full h-full min-h-[300px] bg-white rounded-lg border border-hairline shadow-inner overflow-hidden select-none">
              <iframe v-if="iframeHtml" :srcdoc="iframeHtml" sandbox="allow-scripts allow-modals" class="w-full h-full border-none"></iframe>
              <div v-else class="text-center p-12 text-ink-faint font-sans text-xs select-none">
                Click "Run Code" to load visual output.
              </div>
            </div>

            <!-- SQL In-Memory Table Viewer Schema -->
            <div v-else-if="activeOutputTab === 'db' && activeLang === 'sql'" class="space-y-6">
              <div class="bg-surface border border-hairline rounded-lg p-4 shadow-xxs">
                <h4 class="text-xs font-bold text-ink uppercase tracking-wider mb-3 flex items-center gap-1.5 select-none">
                  <span v-html="getFaIcon(faDatabase)" class="w-3.5 h-3.5 text-primary flex items-center"></span>
                  <span>Database Schema (Mock Engine)</span>
                </h4>
                <p class="text-xxs text-ink-muted mb-4 font-sans leading-relaxed">
                  These standard tables are seeded in memory for testing SELECT statement aggregations and conditions:
                </p>
                
                <div class="space-y-4">
                  <!-- Users Table -->
                  <div class="border-t border-hairline pt-3">
                    <span class="font-mono text-xs font-bold text-primary">users</span>
                    <div class="text-[10px] text-ink-muted font-mono mt-1">Columns: id (INT), username (TEXT), email (TEXT), xp (INT), level (INT), streak (INT)</div>
                  </div>
                  
                  <!-- Subjects Table -->
                  <div class="border-t border-hairline pt-3">
                    <span class="font-mono text-xs font-bold text-primary">subjects</span>
                    <div class="text-[10px] text-ink-muted font-mono mt-1">Columns: id (INT), name (TEXT), topics (TEXT)</div>
                  </div>

                  <!-- Leaderboard Table -->
                  <div class="border-t border-hairline pt-3">
                    <span class="font-mono text-xs font-bold text-primary">leaderboard</span>
                    <div class="text-[10px] text-ink-muted font-mono mt-1">Columns: id (INT), username (TEXT), xp (INT), badge (TEXT)</div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>

    </div>

  </div>
</template>

<style scoped>
textarea {
  tab-size: 4;
}
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: rgba(163, 158, 152, 0.4);
}
</style>
