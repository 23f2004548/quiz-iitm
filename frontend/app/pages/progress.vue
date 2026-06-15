<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { icon } from '@fortawesome/fontawesome-svg-core'
import {
  faBolt, faFire, faTrophy, faClock, faCheckCircle,
  faChartLine, faCalendar, faArrowUp, faMedal,
  faBookOpen, faCircleCheck
} from '@fortawesome/free-solid-svg-icons'

const authStore = useAuthStore()

// ── Icon helper ─────────────────────────────────────────────────────────────
function getFaIcon(def: any) { return icon(def).html[0] }

// ── State ───────────────────────────────────────────────────────────────────
const timeFilter   = ref<'daily' | 'weekly' | 'monthly'>('daily')
const analytics    = ref<any>(null)
const ranking      = ref<any>(null)
const loading      = ref(true)
const error        = ref<string | null>(null)

// ── Chart canvas refs ────────────────────────────────────────────────────────
const questionsChartRef = ref<HTMLCanvasElement | null>(null)
const hoursChartRef     = ref<HTMLCanvasElement | null>(null)
const subjectChartRef   = ref<HTMLCanvasElement | null>(null)

let questionsChart: any = null
let hoursChart: any     = null
let subjectChart: any   = null

// ── Design tokens matching DESIGN.md ────────────────────────────────────────
const COLORS = {
  primary:   '#0075de',
  sky:       '#62aef0',
  purple:    '#d6b6f6',
  pink:      '#ff64c8',
  orange:    '#dd5b00',
  teal:      '#2a9d99',
  green:     '#1aae39',
  hairline:  '#e6e6e6',
  inkMuted:  '#615d59',
  inkFaint:  '#a39e98',
  canvas:    '#f6f5f4',
}

const SUBJECT_PALETTE = [
  COLORS.primary, COLORS.teal, COLORS.orange, COLORS.purple,
  COLORS.green,   COLORS.sky,  COLORS.pink,   '#523410',
]

// ── Computed: filtered series ────────────────────────────────────────────────
const activeSeries = computed(() => {
  if (!analytics.value) return []
  if (timeFilter.value === 'daily')   return analytics.value.daily   ?? []
  if (timeFilter.value === 'weekly')  return analytics.value.weekly  ?? []
  if (timeFilter.value === 'monthly') return analytics.value.monthly ?? []
  return []
})

const seriesLabels = computed(() => {
  return activeSeries.value.map((e: any) =>
    timeFilter.value === 'daily'   ? formatDate(e.date)  :
    timeFilter.value === 'weekly'  ? e.week               :
    e.month
  )
})

const totalStats = computed(() => analytics.value?.totals ?? {
  attempted: 0, correct: 0, accuracy: 0, hours: 0,
  streak: 0, longest_streak: 0, xp: 0, level: 1
})

const subjects = computed(() => analytics.value?.subjects ?? [])

// ── Heatmap: build 90-cell grid from daily data ──────────────────────────────
const heatmapCells = computed(() => {
  const daily: any[] = analytics.value?.daily ?? []
  return daily.map((d: any) => ({
    date: d.date,
    count: d.attempted,
    level: d.attempted === 0 ? 0 :
           d.attempted < 5  ? 1 :
           d.attempted < 10 ? 2 :
           d.attempted < 20 ? 3 : 4
  }))
})

// ── Format helpers ───────────────────────────────────────────────────────────
function formatDate(iso: string) {
  const d = new Date(iso)
  return d.toLocaleDateString('en', { month: 'short', day: 'numeric' })
}

function heatCellClass(level: number) {
  return [
    'rounded-sm transition-all duration-200 cursor-default',
    level === 0 ? 'bg-hairline'             :
    level === 1 ? 'bg-primary/20'           :
    level === 2 ? 'bg-primary/45'           :
    level === 3 ? 'bg-primary/70'           :
                  'bg-primary',
  ].join(' ')
}

// ── Fetch data ───────────────────────────────────────────────────────────────
async function fetchData() {
  loading.value = true
  error.value   = null
  try {
    const [aRes, rRes] = await Promise.all([
      authStore.api.get('/api/quizzes/analytics'),
      authStore.api.get('/api/quizzes/ranking'),
    ])
    analytics.value = aRes.data
    ranking.value   = rRes.data
  } catch (e: any) {
    error.value = e?.response?.data?.error ?? 'Failed to load analytics'
  } finally {
    loading.value = false
    await nextTick()
    renderCharts()
  }
}

// ── Chart.js rendering ───────────────────────────────────────────────────────
async function renderCharts() {
  const { Chart, registerables } = await import('chart.js')
  Chart.register(...registerables)

  const labels   = seriesLabels.value
  const attempted = activeSeries.value.map((e: any) => e.attempted)
  const correct   = activeSeries.value.map((e: any) => e.correct)
  const hours     = activeSeries.value.map((e: any) => e.hours)

  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, labels: { color: COLORS.inkMuted, font: { family: 'Inter', size: 12 } } },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { ticks: { color: COLORS.inkFaint, font: { size: 11 }, maxRotation: 45 }, grid: { color: COLORS.hairline } },
      y: { ticks: { color: COLORS.inkFaint, font: { size: 11 } }, grid: { color: COLORS.hairline }, beginAtZero: true }
    }
  }

  // ── Questions Chart ──
  if (questionsChartRef.value) {
    if (questionsChart) questionsChart.destroy()
    questionsChart = new Chart(questionsChartRef.value, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Attempted',
            data: attempted,
            backgroundColor: `${COLORS.primary}55`,
            borderColor: COLORS.primary,
            borderWidth: 2,
            borderRadius: 4,
          },
          {
            label: 'Correct',
            data: correct,
            backgroundColor: `${COLORS.teal}55`,
            borderColor: COLORS.teal,
            borderWidth: 2,
            borderRadius: 4,
          }
        ]
      },
      options: { ...baseOptions, interaction: { mode: 'index' } }
    })
  }

  // ── Hours Chart ──
  if (hoursChartRef.value) {
    if (hoursChart) hoursChart.destroy()
    hoursChart = new Chart(hoursChartRef.value, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Study Hours',
          data: hours,
          borderColor: COLORS.orange,
          backgroundColor: `${COLORS.orange}20`,
          borderWidth: 2.5,
          pointRadius: timeFilter.value === 'daily' ? 0 : 4,
          pointHoverRadius: 6,
          fill: true,
          tension: 0.4,
        }]
      },
      options: { ...baseOptions }
    })
  }

  // ── Subject Bar Chart ──
  if (subjectChartRef.value && subjects.value.length > 0) {
    if (subjectChart) subjectChart.destroy()
    const subLabels    = subjects.value.map((s: any) => s.subject)
    const subAttempted = subjects.value.map((s: any) => s.attempted)
    const subAccuracy  = subjects.value.map((s: any) => s.accuracy)

    subjectChart = new Chart(subjectChartRef.value, {
      type: 'bar',
      data: {
        labels: subLabels,
        datasets: [
          {
            label: 'Questions Attempted',
            data: subAttempted,
            backgroundColor: SUBJECT_PALETTE.map(c => `${c}66`),
            borderColor: SUBJECT_PALETTE,
            borderWidth: 2,
            borderRadius: 6,
            yAxisID: 'y',
          },
          {
            label: 'Accuracy %',
            data: subAccuracy,
            type: 'line' as const,
            borderColor: COLORS.pink,
            backgroundColor: 'transparent',
            borderWidth: 2.5,
            pointRadius: 5,
            pointHoverRadius: 7,
            yAxisID: 'y1',
            tension: 0.3,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true, labels: { color: COLORS.inkMuted, font: { family: 'Inter', size: 12 } } }
        },
        scales: {
          x: { ticks: { color: COLORS.inkFaint, font: { size: 11 } }, grid: { color: COLORS.hairline } },
          y: {
            type: 'linear', position: 'left', beginAtZero: true,
            ticks: { color: COLORS.inkFaint, font: { size: 11 } },
            grid: { color: COLORS.hairline },
            title: { display: true, text: 'Questions', color: COLORS.inkMuted }
          },
          y1: {
            type: 'linear', position: 'right', min: 0, max: 100,
            ticks: { color: COLORS.inkFaint, font: { size: 11 }, callback: (v: any) => `${v}%` },
            grid: { drawOnChartArea: false },
            title: { display: true, text: 'Accuracy %', color: COLORS.inkMuted }
          }
        }
      }
    })
  }
}

// Re-render charts when time filter changes
watch(timeFilter, async () => {
  await nextTick()
  renderCharts()
})

onMounted(fetchData)
</script>

<template>
  <div class="min-h-full bg-canvas-soft">
    <div class="max-w-7xl mx-auto px-6 py-8">

      <!-- ── Page Header ─────────────────────────────────────────────── -->
      <div class="mb-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <p class="text-xs font-semibold text-primary uppercase tracking-widest mb-1">Analytics</p>
          <h1 class="text-3xl font-bold text-ink tracking-tight">
            Your Progress
          </h1>
          <p class="text-sm text-ink-muted mt-1">Track your learning journey, streaks, and performance across all subjects.</p>
        </div>

        <!-- Time filter pill tabs -->
        <div class="flex items-center bg-surface border border-hairline rounded-full p-1 gap-0.5 shadow-sm">
          <button v-for="tab in (['daily', 'weekly', 'monthly'] as const)" :key="tab"
            @click="timeFilter = tab"
            :class="['px-4 py-1.5 rounded-full text-xs font-semibold capitalize transition-all duration-200',
              timeFilter === tab
                ? 'bg-primary text-white shadow-sm'
                : 'text-ink-muted hover:text-ink hover:bg-canvas-soft']">
            {{ tab }}
          </button>
        </div>
      </div>

      <!-- ── Loading state ───────────────────────────────────────────── -->
      <div v-if="loading" class="flex flex-col items-center justify-center h-64 gap-4">
        <div class="w-10 h-10 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
        <p class="text-sm text-ink-muted">Loading analytics…</p>
      </div>

      <!-- ── Error state ─────────────────────────────────────────────── -->
      <div v-else-if="error" class="flex flex-col items-center justify-center h-64 gap-3">
        <div class="text-4xl">⚠️</div>
        <p class="text-sm text-red-500 font-medium">{{ error }}</p>
        <button @click="fetchData" class="px-4 py-2 bg-primary text-white text-xs font-semibold rounded-full hover:bg-primary-active transition-colors">Retry</button>
      </div>

      <!-- ── Main Content ────────────────────────────────────────────── -->
      <template v-else-if="analytics">

        <!-- ══ ROW 1: Hero stat cards ══ -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
          <!-- XP -->
          <div class="bg-surface rounded-xl border border-hairline p-4 flex flex-col gap-1 hover:shadow-notion-soft transition-all duration-300 group">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider">Total XP</span>
              <span v-html="getFaIcon(faBolt)" class="w-3.5 h-3.5 text-sticker-sky"></span>
            </div>
            <span class="text-2xl font-bold text-ink tracking-tight">{{ totalStats.xp.toLocaleString() }}</span>
            <span class="text-[10px] text-ink-muted">Level {{ totalStats.level }}</span>
          </div>

          <!-- Questions Solved -->
          <div class="bg-surface rounded-xl border border-hairline p-4 flex flex-col gap-1 hover:shadow-notion-soft transition-all duration-300">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider">Solved</span>
              <span v-html="getFaIcon(faCheckCircle)" class="w-3.5 h-3.5 text-sticker-green"></span>
            </div>
            <span class="text-2xl font-bold text-ink tracking-tight">{{ totalStats.correct.toLocaleString() }}</span>
            <span class="text-[10px] text-ink-muted">of {{ totalStats.attempted }} attempted</span>
          </div>

          <!-- Accuracy -->
          <div class="bg-surface rounded-xl border border-hairline p-4 flex flex-col gap-1 hover:shadow-notion-soft transition-all duration-300">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider">Accuracy</span>
              <span v-html="getFaIcon(faArrowUp)" class="w-3.5 h-3.5 text-primary"></span>
            </div>
            <span class="text-2xl font-bold text-ink tracking-tight">{{ totalStats.accuracy }}%</span>
            <div class="w-full bg-canvas-soft h-1.5 rounded-full overflow-hidden mt-1">
              <div class="bg-primary h-full rounded-full transition-all duration-700" :style="{ width: `${totalStats.accuracy}%` }"></div>
            </div>
          </div>

          <!-- Study Hours -->
          <div class="bg-surface rounded-xl border border-hairline p-4 flex flex-col gap-1 hover:shadow-notion-soft transition-all duration-300">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider">Hours</span>
              <span v-html="getFaIcon(faClock)" class="w-3.5 h-3.5 text-sticker-orange"></span>
            </div>
            <span class="text-2xl font-bold text-ink tracking-tight">{{ totalStats.hours }}h</span>
            <span class="text-[10px] text-ink-muted">study time (est.)</span>
          </div>

          <!-- Streak -->
          <div class="bg-surface rounded-xl border border-hairline p-4 flex flex-col gap-1 hover:shadow-notion-soft transition-all duration-300">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider">Streak</span>
              <span v-html="getFaIcon(faFire)" class="w-3.5 h-3.5 text-sticker-orange animate-pulse"></span>
            </div>
            <span class="text-2xl font-bold text-ink tracking-tight">{{ totalStats.streak }}</span>
            <span class="text-[10px] text-ink-muted">days in a row</span>
          </div>

          <!-- Global Rank -->
          <div class="bg-surface rounded-xl border border-hairline p-4 flex flex-col gap-1 hover:shadow-notion-soft transition-all duration-300">
            <div class="flex items-center justify-between mb-1">
              <span class="text-[10px] font-semibold text-ink-faint uppercase tracking-wider">Rank</span>
              <span v-html="getFaIcon(faTrophy)" class="w-3.5 h-3.5 text-sticker-orange"></span>
            </div>
            <span class="text-2xl font-bold text-ink tracking-tight">#{{ ranking?.rank ?? '—' }}</span>
            <span class="text-[10px] text-ink-muted">of {{ ranking?.total_users ?? '—' }} users</span>
          </div>
        </div>

        <!-- ══ ROW 2: Activity Heatmap + Streak Panel ══ -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">

          <!-- Heatmap -->
          <div class="lg:col-span-2 bg-surface rounded-xl border border-hairline p-5 hover:shadow-notion-soft transition-shadow duration-300">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h2 class="text-sm font-bold text-ink">Activity Heatmap</h2>
                <p class="text-xs text-ink-muted mt-0.5">Last 90 days of question activity</p>
              </div>
              <span v-html="getFaIcon(faCalendar)" class="w-4 h-4 text-ink-faint"></span>
            </div>

            <!-- Grid: 90 cells, 18 columns × 5 rows -->
            <div class="grid gap-1" style="grid-template-columns: repeat(18, minmax(0, 1fr))">
              <div v-for="cell in heatmapCells" :key="cell.date"
                :class="heatCellClass(cell.level)"
                :title="`${cell.date}: ${cell.count} questions`"
                style="aspect-ratio: 1">
              </div>
            </div>

            <!-- Legend -->
            <div class="flex items-center gap-2 mt-3 justify-end">
              <span class="text-[10px] text-ink-faint">Less</span>
              <div v-for="l in [0,1,2,3,4]" :key="l" :class="['w-3 h-3 rounded-sm', heatCellClass(l)]"></div>
              <span class="text-[10px] text-ink-faint">More</span>
            </div>
          </div>

          <!-- Streak + Badges panel -->
          <div class="bg-surface rounded-xl border border-hairline p-5 flex flex-col gap-4 hover:shadow-notion-soft transition-shadow duration-300">
            <!-- Current streak big display -->
            <div class="text-center pb-4 border-b border-hairline">
              <div class="w-16 h-16 mx-auto rounded-full bg-sticker-orange/10 border-2 border-sticker-orange flex items-center justify-center mb-2 shadow-sm">
                <span v-html="getFaIcon(faFire)" class="w-7 h-7 text-sticker-orange"></span>
              </div>
              <div class="text-4xl font-bold text-ink tracking-tight">{{ totalStats.streak }}</div>
              <div class="text-xs font-semibold text-ink-muted uppercase tracking-wide mt-0.5">Day Streak</div>
            </div>

            <!-- Streak stats -->
            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <span class="text-xs text-ink-muted flex items-center gap-1.5">
                  <span v-html="getFaIcon(faMedal)" class="w-3 h-3 text-sticker-sky"></span>
                  Current Streak
                </span>
                <span class="text-sm font-bold text-ink">{{ totalStats.streak }} days</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-ink-muted flex items-center gap-1.5">
                  <span v-html="getFaIcon(faTrophy)" class="w-3 h-3 text-sticker-orange"></span>
                  Best Streak
                </span>
                <span class="text-sm font-bold text-ink">{{ totalStats.longest_streak }} days</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-ink-muted flex items-center gap-1.5">
                  <span v-html="getFaIcon(faBookOpen)" class="w-3 h-3 text-primary"></span>
                  Subjects Covered
                </span>
                <span class="text-sm font-bold text-ink">{{ subjects.length }}</span>
              </div>
            </div>

            <!-- Weekly streak dots -->
            <div>
              <div class="text-[10px] font-semibold text-ink-faint uppercase tracking-widest mb-2">This Week</div>
              <div class="flex gap-1.5">
                <div v-for="(day, i) in ['M','T','W','T','F','S','S']" :key="i"
                  class="flex-1 aspect-square rounded-md flex items-center justify-center text-[9px] font-bold transition-all duration-300"
                  :class="i < Math.min(totalStats.streak % 7 || 7, 7)
                    ? 'bg-sticker-orange text-white shadow-sm'
                    : 'bg-canvas-soft text-ink-faint border border-hairline'">
                  {{ day }}
                </div>
              </div>
            </div>

            <!-- Ranking badge -->
            <div v-if="ranking" class="bg-canvas-soft rounded-lg p-3 border border-hairline">
              <div class="flex items-center gap-2">
                <div class="w-9 h-9 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm shadow-sm">
                  #{{ ranking.rank }}
                </div>
                <div>
                  <div class="text-xs font-bold text-ink">Global Rank</div>
                  <div class="text-[10px] text-ink-muted">Top {{ ranking.total_users ? Math.round((ranking.rank / ranking.total_users) * 100) : 0 }}% of all learners</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ══ ROW 3: Questions Solved chart ══ -->
        <div class="bg-surface rounded-xl border border-hairline p-5 mb-6 hover:shadow-notion-soft transition-shadow duration-300">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-sm font-bold text-ink">Questions Solved</h2>
              <p class="text-xs text-ink-muted mt-0.5 capitalize">{{ timeFilter }} breakdown — attempted vs. correct</p>
            </div>
            <span v-html="getFaIcon(faChartLine)" class="w-4 h-4 text-primary"></span>
          </div>
          <div style="height: 220px; position: relative">
            <canvas ref="questionsChartRef"></canvas>
          </div>
        </div>

        <!-- ══ ROW 4: Study Hours chart ══ -->
        <div class="bg-surface rounded-xl border border-hairline p-5 mb-6 hover:shadow-notion-soft transition-shadow duration-300">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-sm font-bold text-ink">Study Hours</h2>
              <p class="text-xs text-ink-muted mt-0.5">Estimated time spent (1.5 min/question)</p>
            </div>
            <span v-html="getFaIcon(faClock)" class="w-4 h-4 text-sticker-orange"></span>
          </div>
          <div style="height: 200px; position: relative">
            <canvas ref="hoursChartRef"></canvas>
          </div>
        </div>

        <!-- ══ ROW 5: Subject Performance ══ -->
        <div class="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-6">

          <!-- Subject chart -->
          <div class="lg:col-span-3 bg-surface rounded-xl border border-hairline p-5 hover:shadow-notion-soft transition-shadow duration-300">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h2 class="text-sm font-bold text-ink">Subject Performance</h2>
                <p class="text-xs text-ink-muted mt-0.5">Questions attempted & accuracy per subject</p>
              </div>
              <span v-html="getFaIcon(faBookOpen)" class="w-4 h-4 text-ink-faint"></span>
            </div>
            <div v-if="subjects.length > 0" style="height: 260px; position: relative">
              <canvas ref="subjectChartRef"></canvas>
            </div>
            <div v-else class="flex items-center justify-center h-48 text-sm text-ink-muted">
              No subject data yet. Complete some quizzes!
            </div>
          </div>

          <!-- Subject accuracy cards -->
          <div class="lg:col-span-2 bg-surface rounded-xl border border-hairline p-5 hover:shadow-notion-soft transition-shadow duration-300">
            <h2 class="text-sm font-bold text-ink mb-4">Per-Subject Accuracy</h2>
            <div v-if="subjects.length > 0" class="space-y-3 overflow-y-auto max-h-72">
              <div v-for="(sub, idx) in subjects" :key="sub.subject" class="group">
                <div class="flex items-center justify-between mb-1">
                  <div class="flex items-center gap-2">
                    <div class="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      :style="{ backgroundColor: SUBJECT_PALETTE[idx % SUBJECT_PALETTE.length] }"></div>
                    <span class="text-xs font-medium text-ink truncate max-w-24">{{ sub.subject }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-[10px] text-ink-faint">{{ sub.attempted }}q</span>
                    <span class="text-xs font-bold"
                      :class="sub.accuracy >= 80 ? 'text-sticker-green' : sub.accuracy >= 60 ? 'text-sticker-orange' : 'text-red-500'">
                      {{ sub.accuracy }}%
                    </span>
                  </div>
                </div>
                <div class="w-full bg-canvas-soft h-1.5 rounded-full overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-700"
                    :style="{ width: `${sub.accuracy}%`, backgroundColor: SUBJECT_PALETTE[idx % SUBJECT_PALETTE.length] }">
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center justify-center h-48 text-sm text-ink-muted">
              Complete quizzes to see subject breakdown.
            </div>
          </div>
        </div>

        <!-- ══ ROW 6: Recent activity summary ══ -->
        <div class="bg-surface rounded-xl border border-hairline p-5 hover:shadow-notion-soft transition-shadow duration-300">
          <h2 class="text-sm font-bold text-ink mb-4">Last 7 Days at a Glance</h2>
          <div class="grid grid-cols-7 gap-2">
            <div v-for="entry in (analytics.daily ?? []).slice(-7)" :key="entry.date"
              class="flex flex-col items-center gap-1.5">
              <div class="text-[9px] font-semibold text-ink-faint uppercase">
                {{ new Date(entry.date).toLocaleDateString('en', { weekday: 'short' }) }}
              </div>
              <div class="w-full aspect-square rounded-lg flex items-center justify-center text-sm font-bold transition-all duration-300 hover:scale-105"
                :class="entry.attempted > 0 ? 'bg-primary/10 text-primary border border-primary/20' : 'bg-canvas-soft text-ink-faint border border-hairline'">
                {{ entry.attempted }}
              </div>
              <div class="text-[9px] text-ink-muted">
                {{ entry.attempted > 0 ? `${entry.correct}✓` : '—' }}
              </div>
            </div>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<style scoped>
.shadow-notion-soft {
  box-shadow:
    rgba(0,0,0,0.01) 0 0.175px 1.041px,
    rgba(0,0,0,0.02) 0 0.8px 2.925px,
    rgba(0,0,0,0.027) 0 2.025px 7.847px,
    rgba(0,0,0,0.04) 0 4px 18px;
}

.bg-hairline { background-color: #e6e6e6; }
.bg-sticker-orange { background-color: #dd5b00; }
.text-sticker-orange { color: #dd5b00; }
.text-sticker-green { color: #1aae39; }
.text-sticker-sky { color: #62aef0; }
.bg-sticker-orange\/10 { background-color: rgb(221 91 0 / 0.1); }
.border-sticker-orange { border-color: #dd5b00; }
.text-primary { color: #0075de; }
.bg-primary { background-color: #0075de; }
.bg-primary\/10 { background-color: rgb(0 117 222 / 0.1); }
.bg-primary\/20 { background-color: rgb(0 117 222 / 0.2); }
.bg-primary\/45 { background-color: rgb(0 117 222 / 0.45); }
.bg-primary\/70 { background-color: rgb(0 117 222 / 0.7); }
.border-primary\/20 { border-color: rgb(0 117 222 / 0.2); }
.hover\:bg-primary-active:hover { background-color: #005bab; }
</style>
