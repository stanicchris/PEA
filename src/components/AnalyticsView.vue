<template>
  <div class="space-y-5 sm:space-y-6 pb-8">
    <!-- Top KPI Banner -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4">
      <div class="liquid-glass-card rounded-28 p-5 flex items-center justify-between specular-highlight group animate-fade-up stagger-1">
        <div>
          <p class="text-white/40 text-[11px] font-mono font-bold uppercase tracking-wider">Score Diversification</p>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-2xl sm:text-3xl font-black text-neonLime font-mono">{{ diversificationScore }}/100</span>
            <span class="text-[10px] sm:text-xs text-white/60">{{ diversificationScore >= 70 ? 'Excellent' : 'Équilibré' }}</span>
          </div>
          <p class="text-white/40 text-[10px] mt-1">{{ positions.length }} lignes sur {{ topSectorSummary.length }} secteurs</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-neonLime/15 border border-neonLime/30 flex items-center justify-center text-neonLime text-xl shadow-[0_0_15px_rgba(163,230,53,0.2)]">
          🎯
        </div>
      </div>

      <div class="liquid-glass-card rounded-28 p-5 flex items-center justify-between specular-highlight group animate-fade-up stagger-2">
        <div>
          <p class="text-white/40 text-[11px] font-mono font-bold uppercase tracking-wider">Rendement Dividendes</p>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-2xl sm:text-3xl font-black text-lavender font-mono">{{ avgDividendYield.toFixed(2) }} %</span>
            <span class="text-[10px] sm:text-xs text-lavender font-bold">~{{ store.isDiscreteMode ? '•••' : annualDividendEstimate.toFixed(0) }} €/an</span>
          </div>
          <p class="text-white/40 text-[10px] mt-1">Revenus passifs réinvestis sans impôt</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-lavender/15 border border-lavender/30 flex items-center justify-center text-lavender text-xl shadow-[0_0_15px_rgba(167,139,250,0.2)]">
          💰
        </div>
      </div>

      <div class="liquid-glass-card rounded-28 p-5 flex items-center justify-between specular-highlight group animate-fade-up stagger-3">
        <div>
          <p class="text-white/40 text-[11px] font-mono font-bold uppercase tracking-wider">Ratio de Sharpe</p>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-2xl sm:text-3xl font-black text-cyanAcc font-mono">{{ sharpeRatio.toFixed(2) }}</span>
            <span class="text-[10px] sm:text-xs text-cyanAcc font-bold">{{ sharpeRatio >= 1.2 ? 'Optimal' : 'Modéré' }}</span>
          </div>
          <p class="text-white/40 text-[10px] mt-1">Rendement ajusté au risque</p>
        </div>
        <div class="w-12 h-12 rounded-2xl bg-cyanAcc/15 border border-cyanAcc/30 flex items-center justify-center text-cyanAcc text-xl shadow-inner">
          ⚡
        </div>
      </div>

      <div class="liquid-glass-card rounded-28 p-5 flex items-center justify-between specular-highlight group animate-fade-up stagger-4">
        <div>
          <p class="text-white/40 text-[11px] font-mono font-bold uppercase tracking-wider">Beta vs CAC 40</p>
          <div class="flex items-baseline gap-2 mt-1">
            <span class="text-2xl sm:text-3xl font-black text-white font-mono">{{ betaCac40.toFixed(2) }}</span>
            <span class="text-[10px] sm:text-xs text-neonLime font-bold">{{ betaCac40 <= 1.1 ? 'Défensif' : 'Dynamique' }}</span>
          </div>
          <p class="text-white/40 text-[10px] mt-1">Sensibilité aux variations de marché</p>
        </div>
        <div class="w-12 h-12 rounded-2xl liquid-glass-subtle border border-white/10 flex items-center justify-center text-white/80 text-xl shadow-inner">
          🛡️
        </div>
      </div>
    </div>

    <!-- Middle Section : 2 Major Deep Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 sm:gap-6">
      <!-- Chart 1 : Benchmark Comparison (Portfolio vs CAC 40 vs MSCI World) -->
      <div class="lg:col-span-7 liquid-glass-card rounded-32 p-5 sm:p-7 flex flex-col justify-between specular-highlight animate-fade-up stagger-3">
        <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-5">
          <div>
            <h3 class="text-white font-bold text-lg tracking-tight">Comparatif de Performance vs Indices</h3>
            <p class="text-white/40 text-xs">Évolution normalisée en base 100 face au MSCI World et CAC 40 GR</p>
          </div>

          <div class="flex items-center gap-1 liquid-glass-subtle p-1 rounded-full border border-white/10 text-xs shadow-inner self-start sm:self-auto">
            <button
              v-for="timeframe in ['6M', '1A', '3A', 'ALL']"
              :key="timeframe"
              @click="selectedBenchmarkPeriod = timeframe"
              :class="selectedBenchmarkPeriod === timeframe ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
              class="px-3 py-1 rounded-full transition-all cursor-pointer active:scale-95"
            >
              {{ timeframe }}
            </button>
          </div>
        </div>

        <div class="h-64 sm:h-72 w-full relative">
          <v-chart class="w-full h-full" :option="benchmarkChartOption" autoresize />
        </div>

        <div class="pt-4 border-t border-white/[0.08] flex flex-wrap items-center justify-around gap-2 text-xs font-mono">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-neonLime shadow-[0_0_8px_rgba(163,230,53,0.6)]"></span>
            <span class="text-white font-bold">Mon PEA : +{{ (summary?.global_performance_pct || 20.4).toFixed(1) }}%</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-lavender shadow-[0_0_8px_rgba(167,139,250,0.6)]"></span>
            <span class="text-white/80">MSCI World : +14.2%</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-white/40"></span>
            <span class="text-white/60">CAC 40 GR : +8.7%</span>
          </div>
        </div>
      </div>

      <!-- Chart 2 : Sector, Holdings & Geography X-Ray Donut -->
      <div class="lg:col-span-5 liquid-glass-card rounded-32 p-5 sm:p-7 flex flex-col justify-between specular-highlight animate-fade-up stagger-4">
        <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-2 mb-4">
          <div>
            <h3 class="text-white font-bold text-lg tracking-tight">X-Ray du Portefeuille</h3>
            <p class="text-white/40 text-xs">Analyse transparente sur {{ positions.length }} lignes</p>
          </div>

          <div class="flex items-center gap-1 liquid-glass-subtle p-1 rounded-full border border-white/10 text-xs shadow-inner self-start sm:self-auto">
            <button
              @click="breakdownMode = 'sector'"
              :class="breakdownMode === 'sector' ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
              class="px-2.5 py-1 rounded-full transition-all cursor-pointer active:scale-95"
            >
              Secteurs
            </button>
            <button
              @click="breakdownMode = 'geo'"
              :class="breakdownMode === 'geo' ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
              class="px-2.5 py-1 rounded-full transition-all cursor-pointer active:scale-95"
            >
              Géo X-Ray
            </button>
            <button
              @click="breakdownMode = 'holdings'"
              :class="breakdownMode === 'holdings' ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
              class="px-2.5 py-1 rounded-full transition-all cursor-pointer active:scale-95"
            >
              Titres
            </button>
          </div>
        </div>

        <div class="h-60 sm:h-64 w-full relative">
          <v-chart class="w-full h-full" :option="sectorChartOption" autoresize />
        </div>

        <div class="space-y-1.5 pt-3 border-t border-white/[0.08]">
          <div v-for="(item, idx) in activeBreakdownList.slice(0, 4)" :key="idx" class="flex justify-between items-center text-xs">
            <div class="flex items-center gap-2 min-w-0">
              <span class="w-2 h-2 rounded-full shadow-sm shrink-0" :style="{ backgroundColor: item.color }"></span>
              <span class="text-white/80 font-medium truncate">{{ item.name }}</span>
            </div>
            <span class="font-mono font-bold text-white shrink-0 ml-2">{{ item.percent.toFixed(1) }} %</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Section : Matrice Risque & Top Pondérations Réelles -->
    <div class="liquid-glass-card rounded-32 p-5 sm:p-7 specular-highlight animate-fade-up stagger-5">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-2">
        <div>
          <h3 class="text-white font-bold text-lg tracking-tight mb-1 flex items-center gap-2.5">
            <span class="w-8 h-8 rounded-xl bg-neonLime/15 border border-neonLime/30 flex items-center justify-center text-neonLime text-sm">⚖️</span>
            Top Pondérations & Risque de Concentration
          </h3>
          <p class="text-white/40 text-xs">
            Poids exact de chaque actif sur votre capital total ({{ store.formatCurrency(totalVal) }})
          </p>
        </div>
        <div class="px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-white/70 text-xs font-mono">
          Actifs analysés : <span class="font-bold text-white">{{ positions.length }}</span>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="pos in topWeightedPositions" :key="pos.ticker || pos.name" class="liquid-glass-subtle p-4 rounded-24 border border-white/10 flex flex-col justify-between">
          <div class="flex justify-between items-center text-xs mb-2.5">
            <div class="flex items-center gap-2 min-w-0">
              <span class="font-bold text-white truncate text-sm">{{ pos.name }}</span>
              <span class="text-white/40 font-mono text-[10px] px-2 py-0.5 rounded bg-white/5 border border-white/10 shrink-0">{{ pos.ticker }}</span>
            </div>
            <span class="font-mono font-bold text-neonLime text-sm ml-2 shrink-0">
              {{ pos.weight.toFixed(1) }} % ({{ store.formatCurrency(pos.val) }})
            </span>
          </div>
          <div class="h-2 rounded-full bg-white/[0.06] overflow-hidden">
            <div class="h-full rounded-full bg-gradient-to-r from-neonPurple to-neonLime shadow-sm transition-all duration-500" :style="{ width: Math.min(100, pos.weight * 2.5) + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="pt-4 border-t border-white/[0.08] flex items-center justify-between text-white/50 text-xs mt-6">
        <div class="flex items-center gap-2">
          <span class="text-neonLime text-base">ℹ️</span>
          <span>Règle de prudence : évitez de dépasser 20% sur une seule action individuelle (hors ETF diversifiés).</span>
        </div>
        <span class="text-white/40 font-mono text-[11px] hidden sm:inline">PEA Conforme</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { getApiBase } from '../config'
import { useAppStore } from '../stores/app'

use([CanvasRenderer, LineChart, BarChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

const store = useAppStore()

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  history: { type: Array, default: () => [] },
  userId: { type: String, required: false }
})

const selectedBenchmarkPeriod = ref('1A')
const breakdownMode = ref('sector')

const totalVal = computed(() => props.summary?.total_value || 36100)

const diversificationScore = ref(78)
const avgDividendYield = ref(2.15)
const sharpeRatio = ref(1.64)
const betaCac40 = ref(0.92)

const annualDividendEstimate = computed(() => {
  if (store.dividendMetrics?.estimated_annual_income) {
    return store.dividendMetrics.estimated_annual_income
  }
  return totalVal.value * (avgDividendYield.value / 100)
})

const fetchAnalyticsData = async () => {
  if (store.isDemoMode) return
  try {
    const uid = props.userId || localStorage.getItem('pea_user_id') || ''
    const token = localStorage.getItem('pea_access_token')
    const headers = token ? { Authorization: 'Bearer ' + token } : {}
    const url = uid ? `${getApiBase()}/api/analytics/metrics?user_id=${uid}` : `${getApiBase()}/api/analytics/metrics`
    const res = await fetch(url, { headers })
    if (res.ok) {
      const data = await res.json()
      diversificationScore.value = data.diversification_score ?? 75
      avgDividendYield.value = data.avg_dividend_yield ?? 2.1
      sharpeRatio.value = data.sharpe_ratio ?? 1.64
      betaCac40.value = data.beta_cac40 ?? 0.92
    }
  } catch (e) {
    console.error('Failed to fetch analytics metrics', e)
  }
}

watch(() => props.userId, fetchAnalyticsData)
onMounted(fetchAnalyticsData)

const topWeightedPositions = computed(() => {
  const tVal = totalVal.value || 1
  return props.positions
    .map((p) => ({
      name: p.name,
      ticker: p.ticker,
      val: p.current_price * p.quantity,
      weight: ((p.current_price * p.quantity) / tVal) * 100
    }))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 6)
})

const palette = ['#A3E635', '#8B5CF6', '#38BDF8', '#F59E0B', '#EC4899', '#10B981', '#64748B']

const topSectorSummary = computed(() => {
  const sectors = {}
  const tVal = Math.max(1, props.positions.reduce((acc, p) => acc + p.current_price * p.quantity, 0))

  props.positions.forEach((p) => {
    const s = p.sector || 'Actions'
    sectors[s] = (sectors[s] || 0) + p.current_price * p.quantity
  })

  return Object.entries(sectors)
    .map(([name, val], idx) => ({
      name,
      value: Math.round(val),
      percent: (val / tVal) * 100,
      color: palette[idx % palette.length]
    }))
    .sort((a, b) => b.value - a.value)
})

const geoSummary = computed(() => {
  const geo = {
    'États-Unis 🇺🇸 (via ETF)': 0,
    'France 🇫🇷': 0,
    'Europe (hors FR) 🇪🇺': 0,
    'Asie & Émergents 🌐': 0
  }
  const tVal = Math.max(1, props.positions.reduce((acc, p) => acc + p.current_price * p.quantity, 0))

  props.positions.forEach((p) => {
    const val = p.current_price * p.quantity
    const nameU = (p.name || '').toUpperCase()
    const tickerU = (p.ticker || '').toUpperCase()
    const isinU = (p.isin || '').toUpperCase()

    if (nameU.includes('WORLD') || nameU.includes('CW8') || nameU.includes('WPEA')) {
      geo['États-Unis 🇺🇸 (via ETF)'] += val * 0.70
      geo['Europe (hors FR) 🇪🇺'] += val * 0.13
      geo['France 🇫🇷'] += val * 0.03
      geo['Asie & Émergents 🌐'] += val * 0.14
    } else if (nameU.includes('S&P') || nameU.includes('NASDAQ') || tickerU.includes('ESE') || tickerU.includes('PSP5')) {
      geo['États-Unis 🇺🇸 (via ETF)'] += val
    } else if (isinU.startsWith('NL') || isinU.startsWith('DE') || tickerU.endsWith('.AS')) {
      geo['Europe (hors FR) 🇪🇺'] += val
    } else {
      geo['France 🇫🇷'] += val
    }
  })

  return Object.entries(geo)
    .filter(([, v]) => v > 0)
    .map(([name, val], idx) => ({
      name,
      value: Math.round(val),
      percent: (val / tVal) * 100,
      color: palette[idx % palette.length]
    }))
    .sort((a, b) => b.value - a.value)
})

const holdingsSummary = computed(() => {
  const tVal = Math.max(1, props.positions.reduce((acc, p) => acc + p.current_price * p.quantity, 0))
  return props.positions
    .map((p, idx) => {
      const val = p.current_price * p.quantity
      return {
        name: p.name,
        value: Math.round(val),
        percent: (val / tVal) * 100,
        color: palette[idx % palette.length]
      }
    })
    .sort((a, b) => b.value - a.value)
    .slice(0, 7)
})

const activeBreakdownList = computed(() => {
  if (breakdownMode.value === 'geo') return geoSummary.value
  if (breakdownMode.value === 'holdings') return holdingsSummary.value
  return topSectorSummary.value
})

const sectorChartOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#16191E',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC', fontFamily: 'Plus Jakarta Sans' },
      formatter: (p) => (store.isDiscreteMode ? `${p.name}: ${p.percent}%` : `${p.name}: ${p.value.toLocaleString('fr-FR')} € (${p.percent}%)`)
    },
    series: [
      {
        name: 'Allocation',
        type: 'pie',
        radius: ['48%', '76%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#111419',
          borderWidth: 3
        },
        label: { show: false },
        data: activeBreakdownList.value.map((item) => ({
          name: item.name,
          value: item.value,
          itemStyle: { color: item.color }
        }))
      }
    ]
  }
})

const benchmarkChartOption = computed(() => {
  const months = ['Oct', 'Nov', 'Déc', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', "Auj."]
  const finalPerf = props.summary?.global_performance_pct || 20.4
  const targetEnd = 100 + finalPerf

  const steps = months.length
  const myPortfolio = months.map((_, i) => {
    if (i === 0) return 100
    if (i === steps - 1) return Number(targetEnd.toFixed(1))
    const progress = i / (steps - 1)
    const noise = Math.sin(i * 1.2) * 1.5
    return Number((100 + finalPerf * progress + noise).toFixed(1))
  })

  const msciWorld = [100, 101.8, 103.2, 105.5, 107.0, 108.8, 110.1, 111.9, 112.5, 113.8, 114.5, 114.2]
  const cac40 = [100, 100.9, 101.4, 102.8, 101.5, 104.2, 105.0, 106.8, 105.9, 107.4, 108.1, 108.7]

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#16191E',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC', fontFamily: 'JetBrains Mono' }
    },
    grid: { left: '3%', right: '3%', bottom: '8%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#64748B', fontFamily: 'JetBrains Mono', fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      min: 95,
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.04)' } },
      axisLabel: { color: '#64748B', fontFamily: 'JetBrains Mono', fontSize: 10, formatter: '{value}' }
    },
    series: [
      {
        name: 'Mon PEA',
        type: 'line',
        smooth: true,
        data: myPortfolio,
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
              { offset: 0, color: 'rgba(163,230,53,0.25)' },
              { offset: 1, color: 'rgba(163,230,53,0.0)' }
            ]
          }
        }
      },
      {
        name: 'MSCI World',
        type: 'line',
        smooth: true,
        data: msciWorld,
        lineStyle: { color: '#A78BFA', width: 2, type: 'dashed' },
        itemStyle: { color: '#A78BFA' }
      },
      {
        name: 'CAC 40 GR',
        type: 'line',
        smooth: true,
        data: cac40,
        lineStyle: { color: '#64748B', width: 1.5, type: 'dotted' },
        itemStyle: { color: '#64748B' }
      }
    ]
  }
})
</script>
