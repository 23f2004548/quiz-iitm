<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { icon } from '@fortawesome/fontawesome-svg-core'
import {
  faChevronLeft, faChevronRight, faPlus, faXmark,
  faMagnifyingGlass, faCalendarDays, faGripVertical,
  faSquare, faMinus, faExpand, faCompress,
  faTrash, faGraduationCap, faBell, faFlag
} from '@fortawesome/free-solid-svg-icons'

const fi = (d: any) => icon(d).html[0]

// ── Props / emits ──────────────────────────────────────────────
const emit = defineEmits<{ close: [] }>()

// ── Panel window state ─────────────────────────────────────────
const DEFAULT_W = 860
const DEFAULT_H = 580
const MIN_W     = 420
const MIN_H     = 320

const panelX      = ref(Math.max(80, (window.innerWidth  - DEFAULT_W) / 2))
const panelY      = ref(Math.max(60, (window.innerHeight - DEFAULT_H) / 2))
const panelW      = ref(DEFAULT_W)
const panelH      = ref(DEFAULT_H)
const isMaximized = ref(false)
const isMinimized = ref(false)

// Pre-max snapshot
let snapX = 0, snapY = 0, snapW = 0, snapH = 0

function toggleMaximize() {
  if (isMaximized.value) {
    panelX.value = snapX; panelY.value = snapY
    panelW.value = snapW; panelH.value = snapH
    isMaximized.value = false
  } else {
    snapX = panelX.value; snapY = panelY.value
    snapW = panelW.value; snapH = panelH.value
    panelX.value = 0; panelY.value = 0
    panelW.value = window.innerWidth; panelH.value = window.innerHeight
    isMaximized.value = true
  }
}

// ── DRAG (title bar) ───────────────────────────────────────────
let dragOffX = 0, dragOffY = 0

function startDrag(e: MouseEvent) {
  if (isMaximized.value) return
  e.preventDefault()
  dragOffX = e.clientX - panelX.value
  dragOffY = e.clientY - panelY.value
  document.addEventListener('mousemove', onDrag, { passive: true })
  document.addEventListener('mouseup', stopDrag)
}
function onDrag(e: MouseEvent) {
  panelX.value = Math.max(0, Math.min(e.clientX - dragOffX, window.innerWidth  - panelW.value))
  panelY.value = Math.max(0, Math.min(e.clientY - dragOffY, window.innerHeight - panelH.value))
}
function stopDrag() {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup',   stopDrag)
}

// ── RESIZE (8 handles) ─────────────────────────────────────────
type ResizeDir = 'n'|'s'|'e'|'w'|'ne'|'nw'|'se'|'sw'

let resDir: ResizeDir = 'se'
let resStartX = 0, resStartY = 0
let resStartW = 0, resStartH = 0
let resStartPX = 0, resStartPY = 0

function startResize(e: MouseEvent, dir: ResizeDir) {
  e.preventDefault()
  e.stopPropagation()
  resDir = dir
  resStartX  = e.clientX;  resStartY  = e.clientY
  resStartW  = panelW.value; resStartH = panelH.value
  resStartPX = panelX.value; resStartPY = panelY.value
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onResize, { passive: true })
  document.addEventListener('mouseup',   stopResize)
}
function onResize(e: MouseEvent) {
  const dx = e.clientX - resStartX
  const dy = e.clientY - resStartY
  let nx = resStartPX, ny = resStartPY, nw = resStartW, nh = resStartH

  if (resDir.includes('e')) nw = Math.max(MIN_W, resStartW + dx)
  if (resDir.includes('s')) nh = Math.max(MIN_H, resStartH + dy)
  if (resDir.includes('w')) {
    nw = Math.max(MIN_W, resStartW - dx)
    nx = resStartPX + (resStartW - nw)
  }
  if (resDir.includes('n')) {
    nh = Math.max(MIN_H, resStartH - dy)
    ny = resStartPY + (resStartH - nh)
  }

  panelX.value = nx; panelY.value = ny
  panelW.value = nw; panelH.value = nh
}
function stopResize() {
  document.body.style.userSelect = ''
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup',   stopResize)
}

// ══ CALENDAR LOGIC ═════════════════════════════════════════════
interface CalEvent {
  id: string; title: string; date: string
  startTime: string; endTime: string
  calendar: string; description?: string; allDay?: boolean
}
type ViewMode = 'week'|'day'|'month'

const view       = ref<ViewMode>('week')
const anchor     = ref(new Date())
const searchQ    = ref('')

const CALENDARS = [
  { id: 'study',    label: 'Study',    color: '#0075de' },
  { id: 'exam',     label: 'Exams',    color: '#dd5b00' },
  { id: 'personal', label: 'Personal', color: '#1aae39' },
  { id: 'team',     label: 'Team',     color: '#7c3aed' },
  { id: 'holiday',  label: 'Holidays', color: '#ff64c8' },
]
const visCals = ref(new Set(CALENDARS.map(c => c.id)))
const toggleCal = (id: string) => {
  if (visCals.value.has(id)) visCals.value.delete(id)
  else visCals.value.add(id)
  visCals.value = new Set(visCals.value)
}

const events   = ref<CalEvent[]>([])
const calColor = (id: string) => CALENDARS.find(c => c.id === id)?.color ?? '#0075de'

function loadEvents() {
  try { events.value = JSON.parse(localStorage.getItem('lm_cal_v2') || '[]') }
  catch { events.value = [] }
}
function saveEvt() { localStorage.setItem('lm_cal_v2', JSON.stringify(events.value)) }

const visible = computed(() =>
  events.value.filter(e => visCals.value.has(e.calendar))
)

// Navigation
const goToday   = ()  => { anchor.value = new Date() }
const goBack    = ()  => {
  const d = new Date(anchor.value)
  view.value === 'day' ? d.setDate(d.getDate()-1) : view.value === 'week' ? d.setDate(d.getDate()-7) : d.setMonth(d.getMonth()-1)
  anchor.value = d
}
const goFwd     = ()  => {
  const d = new Date(anchor.value)
  view.value === 'day' ? d.setDate(d.getDate()+1) : view.value === 'week' ? d.setDate(d.getDate()+7) : d.setMonth(d.getMonth()+1)
  anchor.value = d
}

const isoDate  = (d: Date) => d.toISOString().slice(0,10)
const todayIso = computed(() => isoDate(new Date()))
const isToday  = (d: Date) => isoDate(d) === todayIso.value

const weekDays = computed(() => {
  const a = new Date(anchor.value)
  const dow = a.getDay()
  const mon = new Date(a); mon.setDate(a.getDate() + (dow === 0 ? -6 : 1 - dow))
  return Array.from({length:7},(_,i)=>{ const d=new Date(mon); d.setDate(mon.getDate()+i); return d })
})

const headerLabel = computed(() => {
  const d = anchor.value
  if (view.value==='day')   return d.toLocaleDateString('en',{weekday:'long',month:'long',day:'numeric',year:'numeric'})
  if (view.value==='week') {
    const [f,l] = [weekDays.value[0], weekDays.value[6]]
    return f.getMonth()===l.getMonth()
      ? f.toLocaleDateString('en',{month:'long',year:'numeric'})
      : `${f.toLocaleDateString('en',{month:'short'})} – ${l.toLocaleDateString('en',{month:'short',year:'numeric'})}`
  }
  return d.toLocaleDateString('en',{month:'long',year:'numeric'})
})

// Time grid
const HOURS       = Array.from({length:24},(_,i)=>i)
const CELL_H      = 48  // px per hour

const now       = ref(new Date())
let   nowTimer: any
onMounted(() => {
  now.value = new Date()
  nowTimer  = setInterval(() => { now.value = new Date() }, 30000)
  loadEvents(); seedDemo()
  nextTick(() => { if (gridEl.value) gridEl.value.scrollTop = CELL_H * 7 })
})
onUnmounted(() => clearInterval(nowTimer))

const nowTop = computed(() => (now.value.getHours() + now.value.getMinutes()/60) * CELL_H)
const nowInView = computed(() => {
  if (view.value==='day')  return isoDate(anchor.value)===todayIso.value
  if (view.value==='week') return weekDays.value.some(d=>isoDate(d)===todayIso.value)
  return true
})

const timeToMin = (t: string) => { const [h,m]=t.split(':').map(Number); return h*60+m }
const minToPx   = (m: number) => (m/60)*CELL_H
const eventsFor = (date: string) => visible.value.filter(e=>e.date===date&&!e.allDay)
const allDayFor = (date: string) => visible.value.filter(e=>e.date===date&&e.allDay)

function evStyle(ev: CalEvent) {
  const start = timeToMin(ev.startTime), end = timeToMin(ev.endTime)
  const h = Math.max(end-start, 15)
  const color = calColor(ev.calendar)
  return { top:`${minToPx(start)}px`, height:`${minToPx(h)}px`,
    backgroundColor:`${color}22`, borderLeft:`3px solid ${color}`, color }
}

function fmtTime(t: string) {
  const [h,m] = t.split(':').map(Number)
  const p = h>=12?'PM':'AM', h12 = h%12||12
  return m===0 ? `${h12}${p}` : `${h12}:${String(m).padStart(2,'0')}${p}`
}

// Month grid
const monthGrid = computed(() => {
  const y=anchor.value.getFullYear(), mo=anchor.value.getMonth()
  const first=new Date(y,mo,1), startDay=(first.getDay()+6)%7
  const total=new Date(y,mo+1,0).getDate()
  const cells: {iso:string;day:number;isThis:boolean}[] = []
  const prevT=new Date(y,mo,0).getDate()
  for(let i=startDay-1;i>=0;i--){ const pm=mo===0?12:mo,py=mo===0?y-1:y; cells.push({iso:`${py}-${String(pm).padStart(2,'0')}-${String(prevT-i).padStart(2,'0')}`,day:prevT-i,isThis:false}) }
  for(let d=1;d<=total;d++) cells.push({iso:`${y}-${String(mo+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`,day:d,isThis:true})
  let nm=mo+2,ny=y; if(nm>12){nm=1;ny++}
  let nx=1; while(cells.length%7) cells.push({iso:`${ny}-${String(nm).padStart(2,'0')}-${String(nx).padStart(2,'0')}`,day:nx++,isThis:false})
  return cells
})

// Mini calendar
const miniOff  = ref(0)
const miniDate = computed(()=>{ const d=new Date(); d.setDate(1); d.setMonth(d.getMonth()+miniOff.value); return d })
const miniLbl  = computed(()=>miniDate.value.toLocaleDateString('en',{month:'short',year:'numeric'}))
const miniGrid = computed(()=>{
  const y=miniDate.value.getFullYear(),m=miniDate.value.getMonth()
  const first=new Date(y,m,1),start=(first.getDay()+6)%7
  const total=new Date(y,m+1,0).getDate()
  const c:(number|null)[]=[...Array(start).fill(null)]
  for(let d=1;d<=total;d++) c.push(d)
  while(c.length%7) c.push(null)
  return c
})
function miniIso(d:number|null){ if(!d) return null; const y=miniDate.value.getFullYear(),m=miniDate.value.getMonth(); return `${y}-${String(m+1).padStart(2,'0')}-${String(d).padStart(2,'0')}` }
function miniHasEv(d:number|null){ const iso=miniIso(d); return iso?visible.value.some(e=>e.date===iso):false }
function miniClick(d:number|null){ if(!d) return; const y=miniDate.value.getFullYear(),m=miniDate.value.getMonth(); anchor.value=new Date(y,m,d); if(view.value==='month') view.value='week' }

// Seed demo
function seedDemo(){
  if(events.value.length>0) return
  const t=new Date(), y=t.getFullYear(), m=String(t.getMonth()+1).padStart(2,'0'), d=String(t.getDate()).padStart(2,'0')
  const tom=new Date(t); tom.setDate(t.getDate()+1)
  const ty=tom.getFullYear(),tm=String(tom.getMonth()+1).padStart(2,'0'),td=String(tom.getDate()).padStart(2,'0')
  events.value=[
    {id:'d1',title:'Linux Midterm Exam',date:`${y}-${m}-${d}`,startTime:'10:00',endTime:'12:00',calendar:'exam'},
    {id:'d2',title:'Study Session: Git',date:`${y}-${m}-${d}`,startTime:'14:00',endTime:'16:00',calendar:'study'},
    {id:'d3',title:'Team Stand-up',date:`${y}-${m}-${d}`,startTime:'09:00',endTime:'09:30',calendar:'team'},
    {id:'d4',title:'Python Assignment Due',date:`${ty}-${tm}-${td}`,startTime:'11:00',endTime:'12:00',calendar:'exam'},
    {id:'d5',title:'SQL Practice Quiz',date:`${ty}-${tm}-${td}`,startTime:'15:00',endTime:'16:30',calendar:'study'},
  ]
  saveEvt()
}

// Add/edit modal
const showModal = ref(false)
const editId    = ref<string|null>(null)
const form      = ref({title:'',date:'',startTime:'09:00',endTime:'10:00',calendar:'study',description:'',allDay:false})

function openNew(date=todayIso.value, startTime='09:00'){
  editId.value=null
  const endH=String(Number(startTime.split(':')[0])+1).padStart(2,'0')
  form.value={title:'',date,startTime,endTime:`${endH}:00`,calendar:'study',description:'',allDay:false}
  showModal.value=true
}
function openEdit(ev:CalEvent){
  editId.value=ev.id
  form.value={title:ev.title,date:ev.date,startTime:ev.startTime,endTime:ev.endTime,calendar:ev.calendar,description:ev.description??'',allDay:ev.allDay??false}
  showModal.value=true
}
function saveEvent(){
  if(!form.value.title.trim()) return
  if(editId.value){
    const i=events.value.findIndex(e=>e.id===editId.value)
    if(i!==-1) events.value[i]={...events.value[i],...form.value}
  } else {
    events.value.push({id:`${Date.now()}-${Math.random().toString(36).slice(2)}`,...form.value})
  }
  saveEvt(); showModal.value=false
}
function deleteEvent(id:string){ events.value=events.value.filter(e=>e.id!==id); saveEvt(); showModal.value=false }

function slotClick(dateStr:string, hour:number){ openNew(dateStr,`${String(hour).padStart(2,'0')}:00`) }

const gridEl = ref<HTMLElement|null>(null)
const leftW  = ref(168)  // resizable left panel width inside calendar

// Left panel drag resize
let lpStart = 0, lpStartW = 0
function startLpResize(e:MouseEvent){
  e.preventDefault()
  lpStart=e.clientX; lpStartW=leftW.value
  document.addEventListener('mousemove', onLpResize, {passive:true})
  document.addEventListener('mouseup', stopLpResize)
}
function onLpResize(e:MouseEvent){ leftW.value=Math.min(260,Math.max(120,lpStartW+(e.clientX-lpStart))) }
function stopLpResize(){ document.removeEventListener('mousemove',onLpResize); document.removeEventListener('mouseup',stopLpResize) }
</script>

<template>
  <Teleport to="body">
    <!-- Click-outside backdrop -->
    <div
      class="fixed inset-0 z-[8887]"
      @click="$emit('close')"
    ></div>

    <!-- Panel -->
    <div
      class="calendar-panel fixed z-[8888] flex flex-col bg-white rounded-2xl overflow-hidden select-none"
      :class="[isMaximized ? 'rounded-none' : 'shadow-[0_32px_80px_rgba(0,0,0,0.18)] border border-hairline']"
      :style="{
        left:   `${panelX}px`,
        top:    `${panelY}px`,
        width:  `${panelW}px`,
        height: `${panelH}px`,
        transition: 'border-radius 150ms ease'
      }"
    >
      <!-- ── Title bar (drag target) ── -->
      <div
        class="flex-shrink-0 flex items-center justify-between px-4 h-10 bg-canvas-soft border-b border-hairline cursor-grab active:cursor-grabbing"
        style="font-family:'Inter',sans-serif"
        @mousedown="startDrag"
      >
        <!-- Left: traffic-light buttons -->
        <div class="flex items-center gap-1.5" @mousedown.stop>
          <!-- Close -->
          <button @click="$emit('close')"
            class="w-3 h-3 rounded-full bg-[#ff5f57] hover:bg-[#e0433b] transition-colors flex items-center justify-center group cursor-pointer">
            <span v-html="fi(faXmark)" class="w-1.5 h-1.5 text-[#7a1000] opacity-0 group-hover:opacity-100 pointer-events-none flex items-center justify-center"></span>
          </button>
          <!-- Minimize -->
          <button @click="isMinimized = !isMinimized"
            class="w-3 h-3 rounded-full bg-[#febc2e] hover:bg-[#e0a020] transition-colors flex items-center justify-center group cursor-pointer">
            <span v-html="fi(faMinus)" class="w-1.5 h-1.5 text-[#7a5400] opacity-0 group-hover:opacity-100 pointer-events-none flex items-center justify-center"></span>
          </button>
          <!-- Maximize -->
          <button @click="toggleMaximize"
            class="w-3 h-3 rounded-full bg-[#28c840] hover:bg-[#1ea832] transition-colors flex items-center justify-center group cursor-pointer">
            <span v-html="fi(isMaximized ? faCompress : faExpand)" class="w-1.5 h-1.5 text-[#003d00] opacity-0 group-hover:opacity-100 pointer-events-none flex items-center justify-center"></span>
          </button>
        </div>

        <!-- Centre: title -->
        <div class="flex items-center gap-1.5 absolute left-1/2 -translate-x-1/2 pointer-events-none">
          <span v-html="fi(faCalendarDays)" class="w-3.5 h-3.5 text-primary flex items-center justify-center"></span>
          <span class="text-xs font-semibold text-ink-secondary">Calendar</span>
        </div>

        <!-- Right: explicit close button + grip -->
        <div class="flex items-center gap-2" @mousedown.stop>
          <button
            @click="$emit('close')"
            class="w-6 h-6 rounded-md flex items-center justify-center text-ink-faint hover:text-red-500 hover:bg-red-50 transition-all duration-150 cursor-pointer"
            title="Close calendar"
          >
            <span v-html="fi(faXmark)" class="w-3 h-3 flex items-center justify-center pointer-events-none"></span>
          </button>
          <span v-html="fi(faGripVertical)" class="w-3 h-3 flex items-center justify-center opacity-30"></span>
        </div>
      </div>

      <!-- ── Body (hidden when minimized) ── -->
      <div v-show="!isMinimized" class="flex flex-1 min-h-0 overflow-hidden">

        <!-- ─── LEFT PANEL ─── -->
        <div class="flex-shrink-0 flex flex-col border-r border-hairline bg-canvas-soft overflow-y-auto"
          :style="{ width: `${leftW}px` }">

          <!-- New event -->
          <div class="p-2.5 border-b border-hairline">
            <button @click="openNew()"
              class="w-full flex items-center justify-center gap-1.5 py-1.5 bg-primary text-white text-xs font-semibold rounded-full hover:bg-[#005bab] transition-colors shadow-sm cursor-pointer">
              <span v-html="fi(faPlus)" class="w-3 h-3 flex items-center justify-center pointer-events-none shrink-0"></span>
              New event
            </button>
          </div>

          <!-- Mini calendar -->
          <div class="px-2.5 py-2.5">
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-[11px] font-bold text-ink">{{ miniLbl }}</span>
              <div class="flex gap-0.5">
                <button @click="miniOff--" class="w-5 h-5 flex items-center justify-center rounded text-ink-faint hover:bg-hairline cursor-pointer">
                  <span v-html="fi(faChevronLeft)" class="w-2 h-2 pointer-events-none flex items-center justify-center"></span>
                </button>
                <button @click="miniOff++" class="w-5 h-5 flex items-center justify-center rounded text-ink-faint hover:bg-hairline cursor-pointer">
                  <span v-html="fi(faChevronRight)" class="w-2 h-2 pointer-events-none flex items-center justify-center"></span>
                </button>
              </div>
            </div>
            <div class="grid grid-cols-7 mb-0.5">
              <div v-for="d in ['S','M','T','W','T','F','S']" :key="d+Math.random()" class="text-center text-[8px] font-semibold text-ink-faint py-0.5">{{ d }}</div>
            </div>
            <div class="grid grid-cols-7 gap-y-0.5">
              <button v-for="(day,i) in miniGrid" :key="i"
                @click="miniClick(day)"
                :class="['relative h-5 w-full flex items-center justify-center text-[10px] rounded-full transition-all',
                  day===null ? 'pointer-events-none' : 'cursor-pointer hover:bg-primary/10',
                  miniIso(day)===todayIso ? 'bg-primary text-white font-bold' : 'text-ink']">
                {{ day }}
                <span v-if="day && miniHasEv(day) && miniIso(day)!==todayIso"
                  class="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-primary pointer-events-none"></span>
              </button>
            </div>
          </div>

          <!-- Calendars -->
          <div class="px-2.5 py-1.5 border-t border-hairline">
            <div class="text-[9px] font-bold text-ink-faint uppercase tracking-widest mb-1.5">My Calendars</div>
            <div class="space-y-0.5">
              <label v-for="cal in CALENDARS" :key="cal.id"
                class="flex items-center gap-2 px-1 py-1 rounded-md hover:bg-surface cursor-pointer transition-colors">
                <div class="w-3 h-3 rounded flex-shrink-0 flex items-center justify-center border-2 transition-all"
                  :style="visCals.has(cal.id) ? { backgroundColor:cal.color, borderColor:cal.color } : { backgroundColor:'transparent', borderColor:cal.color }"
                  @click.prevent="toggleCal(cal.id)">
                  <span v-if="visCals.has(cal.id)" class="text-white text-[6px] font-bold pointer-events-none">✓</span>
                </div>
                <span class="text-[11px] text-ink-secondary select-none" @click="toggleCal(cal.id)">{{ cal.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- Left-panel resize divider -->
        <div class="w-1 flex-shrink-0 cursor-col-resize hover:bg-primary/30 active:bg-primary/50 transition-colors relative z-10"
          @mousedown.stop="startLpResize">
          <div class="absolute inset-y-0 left-0 w-px bg-hairline"></div>
        </div>

        <!-- ─── MAIN CALENDAR AREA ─── -->
        <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

          <!-- Toolbar -->
          <div class="flex-shrink-0 h-11 flex items-center justify-between px-4 border-b border-hairline bg-canvas gap-3">
            <div class="flex items-center gap-2">
              <button @click="goToday" class="px-3 py-1 border border-hairline rounded-full text-[11px] font-semibold text-ink hover:bg-canvas-soft transition-colors cursor-pointer">Today</button>
              <button @click="goBack"  class="w-6 h-6 flex items-center justify-center rounded-full text-ink-muted hover:bg-canvas-soft transition-colors cursor-pointer">
                <span v-html="fi(faChevronLeft)"  class="w-2.5 h-2.5 flex items-center justify-center pointer-events-none"></span>
              </button>
              <button @click="goFwd"   class="w-6 h-6 flex items-center justify-center rounded-full text-ink-muted hover:bg-canvas-soft transition-colors cursor-pointer">
                <span v-html="fi(faChevronRight)" class="w-2.5 h-2.5 flex items-center justify-center pointer-events-none"></span>
              </button>
              <span class="text-sm font-bold text-ink tracking-tight">{{ headerLabel }}</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="relative">
                <span v-html="fi(faMagnifyingGlass)" class="absolute left-2 top-1/2 -translate-y-1/2 w-2.5 h-2.5 text-ink-faint flex items-center justify-center pointer-events-none"></span>
                <input v-model="searchQ" placeholder="Search" class="pl-6 pr-2.5 py-1 text-[11px] bg-canvas-soft border border-hairline rounded-full w-28 text-ink placeholder-ink-faint focus:outline-none focus:border-primary transition-all"/>
              </div>
              <div class="flex items-center bg-canvas-soft border border-hairline rounded-full p-0.5">
                <button v-for="v in [['day','Day'],['week','Week'],['month','Month']]" :key="v[0]"
                  @click="view = v[0] as ViewMode"
                  :class="['px-2.5 py-0.5 rounded-full text-[10px] font-semibold transition-all cursor-pointer',
                    view===v[0] ? 'bg-white shadow-sm text-ink border border-hairline' : 'text-ink-muted hover:text-ink']">
                  {{ v[1] }}
                </button>
              </div>
            </div>
          </div>

          <!-- ── WEEK / DAY VIEW ── -->
          <template v-if="view==='week'||view==='day'">
            <!-- Day headers -->
            <div class="flex-shrink-0 border-b border-hairline bg-canvas" style="padding-left:44px">
              <div class="flex">
                <div v-for="day in (view==='week' ? weekDays : [anchor])" :key="isoDate(day)"
                  class="flex-1 py-1.5 text-center border-l border-hairline first:border-l-0">
                  <div class="text-[9px] font-bold text-ink-faint uppercase tracking-wide">{{ day.toLocaleDateString('en',{weekday:'short'}) }}</div>
                  <div class="mt-0.5 flex justify-center">
                    <div :class="['w-7 h-7 flex items-center justify-center rounded-full text-xs font-bold cursor-pointer transition-all',
                      isToday(day) ? 'bg-primary text-white shadow-sm' : 'text-ink hover:bg-canvas-soft']"
                      @click="anchor=new Date(day); view='day'">
                      {{ day.getDate() }}
                    </div>
                  </div>
                  <div v-if="allDayFor(isoDate(day)).length" class="px-0.5 mt-0.5 space-y-px">
                    <div v-for="ev in allDayFor(isoDate(day))" :key="ev.id"
                      @click.stop="openEdit(ev)"
                      class="text-[8px] font-semibold px-1 py-px rounded-sm truncate text-white cursor-pointer hover:opacity-80"
                      :style="{ backgroundColor: calColor(ev.calendar) }">
                      {{ ev.title }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Time grid -->
            <div ref="gridEl" class="flex-1 overflow-y-auto relative">
              <div class="flex relative" :style="{ minHeight: `${CELL_H*24}px` }">
                <!-- Hour labels -->
                <div class="flex-shrink-0 relative select-none" style="width:44px">
                  <div v-for="h in HOURS" :key="h"
                    class="absolute right-1.5 text-[9px] text-ink-faint font-medium"
                    :style="{ top:`${h*CELL_H-6}px` }">
                    {{ h===0?'':(h<12?`${h}a`:h===12?'12p':`${h-12}p`) }}
                  </div>
                </div>

                <!-- Day columns -->
                <div class="flex flex-1 relative">
                  <div v-for="day in (view==='week'?weekDays:[anchor])" :key="isoDate(day)"
                    class="flex-1 relative border-l border-hairline first:border-l-0"
                    :class="isToday(day) ? 'bg-primary/[0.015]' : ''">

                    <div v-for="h in HOURS" :key="h"
                      class="absolute left-0 right-0 border-t border-hairline/60 cursor-pointer hover:bg-primary/5 transition-colors group/slot"
                      :style="{ top:`${h*CELL_H}px`, height:`${CELL_H}px` }"
                      @click="slotClick(isoDate(day),h)">
                      <div class="absolute inset-x-0 border-t border-hairline/25" :style="{ top:`${CELL_H/2}px` }"></div>
                    </div>

                    <div v-for="ev in eventsFor(isoDate(day))" :key="ev.id"
                      @click.stop="openEdit(ev)"
                      class="absolute left-0.5 right-0.5 rounded px-1 py-0.5 cursor-pointer hover:opacity-90 hover:shadow-md transition-all z-10 overflow-hidden"
                      :style="evStyle(ev)">
                      <div class="text-[10px] font-semibold truncate leading-tight">{{ ev.title }}</div>
                      <div v-if="timeToMin(ev.endTime)-timeToMin(ev.startTime)>=45" class="text-[8px] opacity-75 mt-px">
                        {{ fmtTime(ev.startTime) }}–{{ fmtTime(ev.endTime) }}
                      </div>
                    </div>
                  </div>

                  <!-- Current time indicator -->
                  <div v-if="nowInView" class="absolute left-0 right-0 z-20 pointer-events-none flex items-center" :style="{ top:`${nowTop}px` }">
                    <div class="w-2 h-2 rounded-full bg-red-500 -ml-1 flex-shrink-0 shadow-sm"></div>
                    <div class="h-px bg-red-500 flex-1 opacity-70"></div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- ── MONTH VIEW ── -->
          <template v-else>
            <div class="flex-shrink-0 border-b border-hairline bg-canvas">
              <div class="grid grid-cols-7">
                <div v-for="d in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']" :key="d"
                  class="py-1.5 text-center text-[9px] font-semibold text-ink-faint uppercase tracking-wide border-r border-hairline last:border-r-0">{{ d }}</div>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto">
              <div class="grid grid-cols-7 h-full" style="grid-auto-rows:minmax(72px,1fr)">
                <div v-for="cell in monthGrid" :key="cell.iso"
                  class="border-r border-b border-hairline p-1 cursor-pointer hover:bg-canvas-soft/50 transition-colors"
                  :class="!cell.isThis ? 'opacity-40' : ''"
                  @click="openNew(cell.iso)">
                  <div class="flex justify-end mb-0.5">
                    <div :class="['w-5 h-5 flex items-center justify-center rounded-full text-[10px] font-semibold',
                      cell.iso===todayIso ? 'bg-primary text-white' : 'text-ink hover:bg-canvas-soft']">
                      {{ cell.day }}
                    </div>
                  </div>
                  <div class="space-y-px">
                    <div v-for="ev in visible.filter(e=>e.date===cell.iso).slice(0,2)" :key="ev.id"
                      @click.stop="openEdit(ev)"
                      class="text-[8px] font-semibold px-1 py-px rounded-sm truncate text-white cursor-pointer hover:opacity-80"
                      :style="{ backgroundColor: calColor(ev.calendar) }">
                      {{ ev.title }}
                    </div>
                    <div v-if="visible.filter(e=>e.date===cell.iso).length>2" class="text-[8px] text-ink-muted px-1">
                      +{{ visible.filter(e=>e.date===cell.iso).length-2 }} more
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- ── 8 resize handles ── -->
      <template v-if="!isMaximized">
        <!-- Edges -->
        <div class="resize-handle resize-n"  @mousedown.stop="startResize($event,'n')"></div>
        <div class="resize-handle resize-s"  @mousedown.stop="startResize($event,'s')"></div>
        <div class="resize-handle resize-e"  @mousedown.stop="startResize($event,'e')"></div>
        <div class="resize-handle resize-w"  @mousedown.stop="startResize($event,'w')"></div>
        <!-- Corners -->
        <div class="resize-handle resize-ne" @mousedown.stop="startResize($event,'ne')"></div>
        <div class="resize-handle resize-nw" @mousedown.stop="startResize($event,'nw')"></div>
        <div class="resize-handle resize-se" @mousedown.stop="startResize($event,'se')"></div>
        <div class="resize-handle resize-sw" @mousedown.stop="startResize($event,'sw')"></div>
      </template>
    </div>

    <!-- ── Add/Edit modal (inside Teleport, above panel) ── -->
    <Transition name="modal-fade">
      <div v-if="showModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4" @click.self="showModal=false">
        <div class="absolute inset-0 bg-black/20 backdrop-blur-[2px]"></div>
        <div class="relative bg-white rounded-2xl shadow-[0_24px_64px_rgba(0,0,0,0.18)] w-full max-w-md overflow-hidden border border-hairline">
          <div class="h-1 w-full" :style="{ backgroundColor: calColor(form.calendar) }"></div>
          <div class="px-6 pt-5 pb-3 flex items-start justify-between">
            <div>
              <h3 class="text-sm font-bold text-ink">{{ editId ? 'Edit Event' : 'New Event' }}</h3>
              <p class="text-[11px] text-ink-faint mt-0.5">
                {{ new Date(form.date+'T00:00').toLocaleDateString('en',{weekday:'long',month:'long',day:'numeric'}) }}
              </p>
            </div>
            <button @click="showModal=false" class="w-7 h-7 rounded-full bg-canvas-soft flex items-center justify-center text-ink-faint hover:text-ink hover:bg-hairline transition-all cursor-pointer ml-4 flex-shrink-0">
              <span v-html="fi(faXmark)" class="w-3 h-3 flex items-center justify-center pointer-events-none"></span>
            </button>
          </div>
          <div class="px-6 pb-2 space-y-4">
            <input v-model="form.title" placeholder="Add title"
              class="w-full text-xl font-bold text-ink border-0 border-b-2 border-hairline focus:border-primary focus:outline-none pb-1.5 bg-transparent placeholder-ink-faint/50 transition-colors"
              @keydown.enter="saveEvent" autofocus />

            <label class="flex items-center gap-2 cursor-pointer">
              <div class="relative w-7 h-3.5 rounded-full transition-colors flex-shrink-0 cursor-pointer"
                :class="form.allDay ? 'bg-primary' : 'bg-hairline'"
                @click="form.allDay=!form.allDay">
                <div class="absolute top-0.5 w-2.5 h-2.5 bg-white rounded-full shadow transition-all" :class="form.allDay?'left-[14px]':'left-0.5'"></div>
              </div>
              <span class="text-xs font-medium text-ink-secondary select-none">All day</span>
            </label>

            <div class="grid gap-3" :class="form.allDay?'grid-cols-1':'grid-cols-3'">
              <div :class="form.allDay?'':'col-span-1'">
                <label class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider block mb-1">Date</label>
                <input v-model="form.date" type="date" class="w-full px-3 py-1.5 text-xs border border-hairline rounded-lg bg-canvas-soft text-ink focus:outline-none focus:border-primary transition-colors"/>
              </div>
              <template v-if="!form.allDay">
                <div>
                  <label class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider block mb-1">Start</label>
                  <input v-model="form.startTime" type="time" class="w-full px-3 py-1.5 text-xs border border-hairline rounded-lg bg-canvas-soft text-ink focus:outline-none focus:border-primary transition-colors"/>
                </div>
                <div>
                  <label class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider block mb-1">End</label>
                  <input v-model="form.endTime" type="time" class="w-full px-3 py-1.5 text-xs border border-hairline rounded-lg bg-canvas-soft text-ink focus:outline-none focus:border-primary transition-colors"/>
                </div>
              </template>
            </div>

            <div>
              <label class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider block mb-1.5">Calendar</label>
              <div class="flex flex-wrap gap-1.5">
                <button v-for="cal in CALENDARS" :key="cal.id"
                  @click="form.calendar=cal.id"
                  :class="['flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold border transition-all cursor-pointer',
                    form.calendar===cal.id ? 'text-white border-transparent' : 'bg-canvas-soft border-hairline text-ink-secondary hover:border-ink-faint']"
                  :style="form.calendar===cal.id ? { backgroundColor:cal.color, borderColor:cal.color } : {}">
                  <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="{ backgroundColor:form.calendar===cal.id?'rgba(255,255,255,0.8)':cal.color }"></span>
                  {{ cal.label }}
                </button>
              </div>
            </div>

            <div>
              <label class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider block mb-1">Notes</label>
              <textarea v-model="form.description" placeholder="Add notes…" rows="2"
                class="w-full px-3 py-2 text-xs border border-hairline rounded-lg bg-canvas-soft text-ink placeholder-ink-faint focus:outline-none focus:border-primary transition-colors resize-none"/>
            </div>
          </div>
          <div class="px-6 py-4 flex items-center justify-between">
            <button v-if="editId" @click="deleteEvent(editId!)"
              class="flex items-center gap-1.5 text-xs font-medium text-red-500 hover:text-red-600 cursor-pointer px-2 py-1 rounded-lg hover:bg-red-50 transition-colors">
              <span v-html="fi(faTrash)" class="w-3 h-3 flex items-center justify-center pointer-events-none"></span> Delete
            </button>
            <div v-else class="flex-1"></div>
            <div class="flex gap-2 ml-auto">
              <button @click="showModal=false" class="px-4 py-1.5 border border-hairline rounded-xl text-xs font-medium text-ink-muted hover:bg-canvas-soft transition-colors cursor-pointer">Cancel</button>
              <button @click="saveEvent" :disabled="!form.title.trim()"
                class="px-4 py-1.5 text-white rounded-xl text-xs font-semibold transition-colors cursor-pointer disabled:opacity-40 shadow-sm"
                :style="{ backgroundColor: calColor(form.calendar) }">
                {{ editId ? 'Save' : 'Create' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* ── Resize handles ── */
.resize-handle { position: absolute; z-index: 50; }

.resize-n  { top:-4px;    left:12px;  right:12px; height:8px; cursor:n-resize;  }
.resize-s  { bottom:-4px; left:12px;  right:12px; height:8px; cursor:s-resize;  }
.resize-e  { right:-4px;  top:12px;   bottom:12px; width:8px; cursor:e-resize;  }
.resize-w  { left:-4px;   top:12px;   bottom:12px; width:8px; cursor:w-resize;  }
.resize-ne { top:-6px;    right:-6px;  width:14px; height:14px; cursor:ne-resize; border-radius:0 8px 0 0; }
.resize-nw { top:-6px;    left:-6px;   width:14px; height:14px; cursor:nw-resize; border-radius:8px 0 0 0; }
.resize-se { bottom:-6px; right:-6px;  width:14px; height:14px; cursor:se-resize; border-radius:0 0 8px 0; }
.resize-sw { bottom:-6px; left:-6px;   width:14px; height:14px; cursor:sw-resize; border-radius:0 0 0 8px; }

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 180ms ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #e6e6e6; border-radius: 9999px; }
::-webkit-scrollbar-thumb:hover { background: #a39e98; }
</style>
