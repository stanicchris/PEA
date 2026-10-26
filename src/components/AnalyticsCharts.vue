<template>
  <div class="liquid-glass-card rounded-32 p-5 sm:p-7 flex flex-col justify-between h-full relative overflow-hidden group specular-highlight">
    <!-- Top Row: Title + Chart Type Toggle + Timeframe Selector -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-4">
      <div>
        <div class="flex items-center gap-2 mb-2 flex-wrap">
          <h3 class="text-white font-bold text-lg tracking-tight">Évolution Patrimoniale</h3>
          <span
            class="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold shadow-[0_0_8px_rgba(163,230,53,0.15)] border"
            :class="periodGain >= 0 ? 'text-neonLime bg-neonLime/10 border-neonLime/20' : 'text-roseAcc bg-roseAcc/10 border-roseAcc/20'"
          >
            {{ periodGain >= 0 ? '+' : '' }}{{ periodGain.toFixed(2) }}% ({{ activePeriodLabel }})
          </span>
        </div>

        <!-- Mode Courbe (Valeur vs Investi) OR Layer Filters -->
        <div class="flex items-center gap-1.5 text-xs flex-wrap">
          <!-- Chart Style Switcher -->
          <div class="flex items-center bg-black/40 p-0.5 rounded-full border border-white/10 mr-1">
            <button
              @click="chartStyle = 'area'"
              :class="chartStyle === 'area' ? 'bg-neonLime/20 text-neonLime border-neonLime/30 font-bold' : 'text-white/50 hover:text-white'"
              class="px-2.5 py-0.5 rounded-full text-[11px] border border-transparent transition-all cursor-pointer"
              title="Courbe Valeur Totale vs Capital Investi (Style Finary)"
            >
              📈 Courbe
            </button>
            <button
              @click="chartStyle = 'bars'"
              :class="chartStyle === 'bars' ? 'bg-neonPurple/25 text-lavender border-neonPurple/40 font-bold' : 'text-white/50 hover:text-white'"
              class="px-2.5 py-0.5 rounded-full text-[11px] border border-transparent transition-all cursor-pointer"
              title="Barres empilées par poche (Actions / ETFs / Cash)"
            >
              📊 Poches
            </button>
          </div>

          <template v-if="chartStyle === 'bars'">
            <button
              @click="toggleLayer('stocks')"
              :class="visibleLayers.stocks ? 'bg-neonPurple/20 border-neonPurple/40 text-lavender' : 'liquid-glass-subtle text-white/30 border-white/[0.04]'"
              class="flex items-center gap-1 px-2 py-0.5 rounded-full border text-[11px] transition-all cursor-pointer active:scale-95"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="visibleLayers.stocks ? 'bg-neonPurple' : 'bg-white/20'"></span>
              <span>Actions</span>
            </button>

            <button
              @click="toggleLayer('etfs')"
              :class="visibleLayers.etfs ? 'bg-cyanAcc/20 border-cyanAcc/40 text-cyan-200' : 'liquid-glass-subtle text-white/30 border-white/[0.04]'"
              class="flex items-center gap-1 px-2 py-0.5 rounded-full border text-[11px] transition-all cursor-pointer active:scale-95"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="visibleLayers.etfs ? 'bg-cyanAcc' : 'bg-white/20'"></span>
              <span>ETFs</span>
            </button>

            <button
              @click="toggleLayer('cash')"
              :class="visibleLayers.cash ? 'bg-neonLime/20 border-neonLime/40 text-neonLime' : 'liquid-glass-subtle text-white/30 border-white/[0.04]'"
              class="flex items-center gap-1 px-2 py-0.5 rounded-full border text-[11px] transition-all cursor-pointer active:scale-95"
            >
              <span class="w-1.5 h-1.5 rounded-full" :class="visibleLayers.cash ? 'bg-neonLime' : 'bg-white/20'"></span>
              <span>Cash</span>
            </button>
          </template>
          <template v-else>
            <span class="inline-flex items-center gap-1.5 text-[11px] text-white/60 px-2">
              <span class="w-2 h-2 rounded-full bg-neonLime"></span>Valeur PEA
              <span class="w-2 h-0.5 bg-lavender ml-1.5"></span>Versements cumulés
            </span>
          </template>
        </div>
      </div>

      <!-- Timeframe selector: Semaine, Mois, Année, Tout -->
      <div class="flex items-center gap-1 liquid-glass-subtle p-1 rounded-full border border-white/10 text-xs self-start sm:self-auto shadow-inner">
        <button
          v-for="p in timePeriods"
          :key="p.key"
          @click="activePeriod = p.key"
          :class="activePeriod === p.key ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
          class="px-2.5 py-1 rounded-full transition-all cursor-pointer active:scale-95"
          :title="`Affichage par ${p.label}`"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Chart Canvas -->
    <div class="relative w-full h-56 mt-auto">
      <div v-if="isLoading" class="absolute inset-0 rounded-2xl skeleton-shimmer"></div>
      <v-chart v-else class="w-full h-full" :option="chartOption" autoresize />

      <!-- Floating Milestone Price Tags -->
      <div
        v-if="!isLoading"
        class="hidden sm:block absolute left-[6%] bottom-[18%] text-[10px] font-mono font-bold text-lavender bg-[#121418]/90 backdrop-blur-md px-2.5 py-1 rounded-lg border border-white/10 shadow-lg pointer-events-none"
      >
        Investi : {{ formatMilestone(investedVal) }}
      </div>
      <div
        v-if="!isLoading"
        class="hidden sm:block absolute right-[6%] top-[8%] text-[10px] font-mono font-bold text-neonLime bg-[#121418]/90 backdrop-blur-md px-2.5 py-1 rounded-lg border border-neonLime/40 shadow-lg pointer-events-none"
      >
        Total : {{ formatMilestone(totalVal) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useAppStore } from '../stores/app'

use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent])

const store = useAppStore()

const props = defineProps({
  history: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  positions: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

const chartStyle = ref('area') // Default to Finary-style smooth Area Chart (Valorisation vs Investi)

const timePeriods = [
  { key: '1S', label: '7J' },
  { key: '1M', label: '1M' },
  { key: '1A', label: '1A' },
  { key: 'ALL', label: 'Max' }
]

const activePeriod = ref('ALL')

const activePeriodLabel = computed(() => {
  const found = timePeriods.find((p) => p.key === activePeriod.value)
  return found ? found.label : activePeriod.value
})

const visibleLayers = ref({
  stocks: true,
  etfs: true,
  cash: true
})

const toggleLayer = (layer) => {
  visibleLayers.value[layer] = !visibleLayers.value[layer]
}

const totalVal = computed(() => {
  if (props.summary?.total_value) return Number(props.summary.total_value)
  const titres = (props.positions || []).reduce((sum, p) => sum + p.quantity * p.current_price, 0)
  return titres + Number(props.summary?.cash || 0)
})

const investedVal = computed(() => {
  if (props.summary?.total_invested) return Number(props.summary.total_invested)
  return (props.positions || []).reduce((sum, p) => sum + p.quantity * p.pru, 0)
})

const etfsVal = computed(() => {
  return (props.positions || [])
    .filter(
      (p) =>
        (p.sector && p.sector.toLowerCase().includes('etf')) ||
        (p.name &&
          (p.name.toUpperCase().includes('ETF') ||
            p.name.toUpperCase().includes('CW8') ||
            p.name.toUpperCase().includes('STOXX')))
    )
    .reduce((sum, p) => sum + p.quantity * p.current_price, 0)
})

const stocksVal = computed(() => {
  const allTitres = (props.positions || []).reduce((sum, p) => sum + p.quantity * p.current_price, 0)
  return Math.max(0, allTitres - etfsVal.value)
})

const cashVal = computed(() => {
  return Number(props.summary?.cash || 0)
})

const formatMilestone = (val) => {
  if (store.isDiscreteMode) return '••• €'
  return (val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' €'
}

const periodGain = computed(() => {
  const invested = investedVal.value
  const total = totalVal.value
  if (!invested || invested <= 0) return props.summary?.global_performance_pct || 0
  return ((total - invested) / invested) * 100
})

const chartOption = computed(() => {
  let categories = []
  let sData = []
  let eData = []
  let cData = []
  let totalSeriesData = []
  let investedData = []

  const parseSnapDate = (dStr) => {
    if (!dStr) return new Date()
    const s = String(dStr).replace(' ', 'T')
    const d = new Date(s)
    return isNaN(d.getTime()) ? new Date() : d
  }

  const allSnapshots = Array.isArray(props.history) ? [...props.history] : []
  const sortedSnapshots = allSnapshots.sort((a, b) => parseSnapDate(a.snapshot_date) - parseSnapDate(b.snapshot_date))

  const now = new Date()
  let filtered = sortedSnapshots

  if (activePeriod.value === '1S') {
    const limitDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    filtered = sortedSnapshots.filter((h) => parseSnapDate(h.snapshot_date) >= limitDate)
  } else if (activePeriod.value === '1M') {
    const limitDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    filtered = sortedSnapshots.filter((h) => parseSnapDate(h.snapshot_date) >= limitDate)
  } else if (activePeriod.value === '1A') {
    const limitDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
    filtered = sortedSnapshots.filter((h) => parseSnapDate(h.snapshot_date) >= limitDate)
  }

  const totalTitresNow = stocksVal.value + etfsVal.value
  const stocksRatio = totalTitresNow > 0 ? stocksVal.value / totalTitresNow : 0.7
  const etfsRatio = totalTitresNow > 0 ? etfsVal.value / totalTitresNow : 0.3

  if (filtered.length >= 2) {
    categories = filtered.map((h) => {
      const d = parseSnapDate(h.snapshot_date)
      if (activePeriod.value === '1S') {
        return d.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric' })
      } else if (activePeriod.value === '1M') {
        return d.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' })
      } else if (activePeriod.value === '1A') {
        return d.toLocaleDateString('fr-FR', { month: 'short' })
      }
      return d.toLocaleDateString('fr-FR', { month: 'short', year: '2-digit' })
    })

    sData = filtered.map((h) => {
      if (!visibleLayers.value.stocks) return 0
      const valTitres = Number(h.valeur_titres) || Math.max(0, (Number(h.total_valeur) || 0) - (Number(h.cash) || 0))
      return Math.round(valTitres * stocksRatio)
    })

    eData = filtered.map((h) => {
      if (!visibleLayers.value.etfs) return 0
      const valTitres = Number(h.valeur_titres) || Math.max(0, (Number(h.total_valeur) || 0) - (Number(h.cash) || 0))
      return Math.round(valTitres * etfsRatio)
    })

    cData = filtered.map((h) => {
      if (!visibleLayers.value.cash) return 0
      return Math.round(Number(h.cash) || Number(props.summary?.cash) || 0)
    })

    totalSeriesData = filtered.map((h) => Math.round(Number(h.total_valeur) || totalVal.value))
    investedData = filtered.map((h) => Math.round((Number(h.cout_investi) || investedVal.value) + (Number(h.cash) || 0)))
  } else {
    const labelsMap = {
      '1S': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', "Auj."],
      '1M': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', "Auj."],
      '1A': ['T1', 'T2', 'T3', 'M-2', 'M-1', "Auj."],
      ALL: ['Début', 'Étape 1', 'Étape 2', 'Étape 3', 'Actuel']
    }
    categories = labelsMap[activePeriod.value] || labelsMap.ALL
    const steps = categories.length
    sData = categories.map((_, i) => (visibleLayers.value.stocks ? Math.round(stocksVal.value * (0.85 + (0.15 * i) / (steps - 1))) : 0))
    eData = categories.map((_, i) => (visibleLayers.value.etfs ? Math.round(etfsVal.value * (0.88 + (0.12 * i) / (steps - 1))) : 0))
    cData = categories.map(() => (visibleLayers.value.cash ? Math.round(cashVal.value) : 0))
    totalSeriesData = categories.map((_, i) => {
      const base = investedVal.value + cashVal.value
      const diff = totalVal.value - base
      return Math.round(base + diff * Math.pow(i / (steps - 1), 1.1))
    })
    investedData = categories.map((_, i) => Math.round((investedVal.value + cashVal.value) * (0.9 + (0.1 * i) / (steps - 1))))
  }

  if (chartStyle.value === 'area') {
    const minVal = Math.min(...investedData, ...totalSeriesData)
    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#12161E',
        borderColor: 'rgba(255,255,255,0.12)',
        textStyle: { color: '#F8FAFC', fontFamily: 'JetBrains Mono', fontSize: 11 },
        formatter: (params) => {
          if (store.isDiscreteMode) return 'Mode Discret Actif (••• €)'
          const pVal = params.find((p) => p.seriesName === 'Valeur PEA')?.value || 0
          const pInv = params.find((p) => p.seriesName === 'Capital Investi')?.value || 0
          const gain = pVal - pInv
          const gainPct = pInv > 0 ? ((gain / pInv) * 100).toFixed(1) : '0.0'
          return `
            <div class="font-bold border-b border-white/10 pb-1 mb-1 font-sans">${params[0].axisValue}</div>
            <div class="flex justify-between gap-4 text-xs"><span class="text-neonLime">Valeur PEA:</span><b>${pVal.toLocaleString('fr-FR')} €</b></div>
            <div class="flex justify-between gap-4 text-xs text-white/60"><span>Investi + Cash:</span><b>${pInv.toLocaleString('fr-FR')} €</b></div>
            <div class="border-t border-white/10 pt-1 mt-1 flex justify-between gap-4 text-xs ${gain >= 0 ? 'text-neonLime' : 'text-roseAcc'}">
              <span>Plus-Value:</span><b>${gain >= 0 ? '+' : ''}${gain.toLocaleString('fr-FR')} € (${gain >= 0 ? '+' : ''}${gainPct}%)</b>
            </div>
          `
        }
      },
      grid: { left: '2%', right: '2%', bottom: '4%', top: '12%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: categories,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#64748B', fontFamily: 'JetBrains Mono', fontSize: 10, margin: 12 }
      },
      yAxis: {
        type: 'value',
        min: Math.max(0, Math.floor(minVal * 0.92)),
        show: false,
        splitLine: { show: false }
      },
      series: [
        {
          name: 'Valeur PEA',
          type: 'line',
          smooth: 0.35,
          showSymbol: false,
          lineStyle: { color: '#A3E635', width: 3 },
          itemStyle: { color: '#A3E635' },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(163, 230, 53, 0.32)' },
                { offset: 1, color: 'rgba(163, 230, 53, 0.0)' }
              ]
            }
          },
          data: totalSeriesData
        },
        {
          name: 'Capital Investi',
          type: 'line',
          smooth: 0.25,
          showSymbol: false,
          lineStyle: { color: '#A78BFA', width: 2, type: 'dashed' },
          itemStyle: { color: '#A78BFA' },
          data: investedData
        }
      ]
    }
  }

  // Stacked Bars mode
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#16191E',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC', fontFamily: 'JetBrains Mono' },
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        if (store.isDiscreteMode) return 'Mode Discret Actif (••• €)'
        let total = 0
        let res = `<div class="font-bold border-b border-white/10 pb-1 mb-1 font-sans">${params[0].name}</div>`
        params.forEach((p) => {
          total += p.value || 0
          res += `<div class="flex justify-between gap-4 text-xs"><span>${p.seriesName}:</span><span class="font-bold font-mono">${(p.value || 0).toLocaleString('fr-FR')} €</span></div>`
        })
        res += `<div class="border-t border-white/10 pt-1 mt-1 font-bold text-neonLime flex justify-between gap-4 font-mono"><span>Total Valeur:</span><span>${total.toLocaleString('fr-FR')} €</span></div>`
        return res
      }
    },
    grid: { left: '2%', right: '2%', bottom: '5%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#64748B', fontFamily: 'JetBrains Mono', fontSize: 10, margin: 14 }
    },
    yAxis: {
      type: 'value',
      show: false,
      splitLine: { show: false }
    },
    series: [
      {
        name: 'Actions',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: { color: '#8B5CF6', borderRadius: [0, 0, 12, 12] },
        data: sData
      },
      {
        name: 'ETFs',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: { color: '#38BDF8' },
        data: eData
      },
      {
        name: 'Liquidités',
        type: 'bar',
        stack: 'total',
        barWidth: '50%',
        itemStyle: { color: '#A3E635', borderRadius: [12, 12, 0, 0] },
        data: cData
      }
    ]
  }
})
</script>
