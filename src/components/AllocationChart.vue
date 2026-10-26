<template>
  <div class="liquid-glass-card rounded-32 p-5 sm:p-7 flex flex-col justify-between h-full relative overflow-hidden group specular-highlight">
    <!-- Top Header + Mode Pills -->
    <div class="flex justify-between items-center mb-2 gap-2">
      <div class="flex items-center gap-2">
        <h3 class="text-white font-bold text-lg tracking-tight">Allocation</h3>
      </div>

      <!-- Mode Switcher Pills: Classes | Secteurs | Géo X-Ray -->
      <div class="flex items-center gap-1 liquid-glass-subtle p-1 rounded-full border border-white/10 text-[10px] font-mono">
        <button
          v-for="(m, idx) in modes"
          :key="m.key"
          @click="viewIndex = idx"
          :class="viewIndex === idx ? 'bg-neonLime/20 text-neonLime border border-neonLime/30 font-bold' : 'text-white/50 hover:text-white'"
          class="px-2 py-0.5 rounded-full transition-all cursor-pointer"
        >
          {{ m.label }}
        </button>
      </div>
    </div>

    <!-- Center Concentric Rings / Donut Graphic -->
    <div class="relative w-full h-44 my-auto flex items-center justify-center">
      <div v-if="isLoading" class="w-24 h-24 rounded-full skeleton-shimmer"></div>
      <v-chart v-else class="w-full h-full" :option="chartOption" autoresize />

      <div v-if="!isLoading" class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <div class="text-xl sm:text-2xl font-black text-white tracking-tight leading-none drop-shadow-sm">
          {{ centerMetric.value }}
        </div>
        <div class="text-[10px] text-white/40 font-semibold mt-1 uppercase tracking-wider">
          {{ centerMetric.label }}
        </div>
      </div>
    </div>

    <!-- Bottom Categories Legend with Values -->
    <div class="space-y-2 pt-3 border-t border-white/[0.08]">
      <div v-for="(cat, idx) in activeCategories.slice(0, 3)" :key="idx" class="flex items-center justify-between text-xs">
        <div class="flex items-center gap-2 min-w-0">
          <span class="w-2.5 h-2.5 rounded-full shadow-sm shrink-0" :style="{ backgroundColor: cat.color }"></span>
          <span class="text-white/80 font-medium truncate">{{ cat.name }}</span>
        </div>
        <div class="font-mono text-white font-semibold tabular-numbers shrink-0 ml-2">
          <span v-if="viewIndex === 0">{{ store.formatCurrency(cat.value) }}</span>
          <span v-else>{{ cat.pct.toFixed(1) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useAppStore } from '../stores/app'

use([CanvasRenderer, PieChart, TooltipComponent])
const store = useAppStore()

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  isLoading: { type: Boolean, default: false }
})

const modes = [
  { key: 'classes', label: 'Poches' },
  { key: 'sectors', label: 'Secteurs' },
  { key: 'geo', label: 'X-Ray Géo' }
]
const viewIndex = ref(0)

const totalVal = computed(() => props.summary?.total_value || 1)

const etfVal = computed(() => {
  return (props.positions || [])
    .filter((p) => p.sector === 'ETF & Indice' || p.name?.toUpperCase().includes('ETF') || p.name?.toUpperCase().includes('CW8'))
    .reduce((acc, p) => acc + p.quantity * p.current_price, 0)
})

const titresVal = computed(() => {
  return (props.positions || []).reduce((acc, p) => acc + p.quantity * p.current_price, 0)
})

const cashVal = computed(() => {
  return Number(props.summary?.cash || 0)
})

const actionsVal = computed(() => Math.max(0, titresVal.value - etfVal.value))

const allocationPercent = computed(() => {
  if (!totalVal.value) return 0
  return Math.min(100, Math.round((titresVal.value / totalVal.value) * 100))
})

// Mode 0: Classes
const classCategories = computed(() => {
  const tot = Math.max(1, actionsVal.value + etfVal.value + cashVal.value)
  return [
    { name: 'Actions Vives PEA', value: actionsVal.value, pct: (actionsVal.value / tot) * 100, color: '#8B5CF6' },
    { name: 'ETFs & Trackers', value: etfVal.value, pct: (etfVal.value / tot) * 100, color: '#C4B5FD' },
    { name: 'Liquidités / Cash', value: cashVal.value, pct: (cashVal.value / tot) * 100, color: '#A3E635' }
  ]
})

// Mode 1: Sectors (with ETF Look-through)
const sectorCategories = computed(() => {
  const palette = ['#A3E635', '#8B5CF6', '#38BDF8', '#F59E0B', '#EC4899', '#10B981']
  const map = {}
  const tot = Math.max(1, titresVal.value)
  ;(props.positions || []).forEach((p) => {
    const val = (p.quantity || 0) * (p.current_price || 0)
    const sec = p.sector || 'Actions'
    map[sec] = (map[sec] || 0) + val
  })
  return Object.entries(map)
    .map(([name, value], i) => ({
      name,
      value,
      pct: (value / tot) * 100,
      color: palette[i % palette.length]
    }))
    .sort((a, b) => b.value - a.value)
})

// Mode 2: Geographic X-Ray (Decomposes MSCI World & S&P 500 ETFs automatically!)
const geoCategories = computed(() => {
  const geoMap = {
    'États-Unis 🇺🇸': 0,
    'France 🇫🇷': 0,
    'Europe (hors FR) 🇪🇺': 0,
    'Asie & Monde 🌐': 0
  }
  const tot = Math.max(1, titresVal.value)

  ;(props.positions || []).forEach((p) => {
    const val = (p.quantity || 0) * (p.current_price || 0)
    const nameU = (p.name || '').toUpperCase()
    const tickerU = (p.ticker || '').toUpperCase()
    const isinU = (p.isin || '').toUpperCase()

    if (nameU.includes('WORLD') || nameU.includes('CW8') || nameU.includes('WPEA')) {
      // MSCI World Look-through
      geoMap['États-Unis 🇺🇸'] += val * 0.70
      geoMap['Europe (hors FR) 🇪🇺'] += val * 0.13
      geoMap['France 🇫🇷'] += val * 0.03
      geoMap['Asie & Monde 🌐'] += val * 0.14
    } else if (nameU.includes('S&P') || nameU.includes('NASDAQ') || tickerU.includes('ESE') || tickerU.includes('PSP5') || isinU.startsWith('US')) {
      geoMap['États-Unis 🇺🇸'] += val
    } else if (nameU.includes('EMERGING') || nameU.includes('ASIA')) {
      geoMap['Asie & Monde 🌐'] += val
    } else if (isinU.startsWith('NL') || isinU.startsWith('DE') || tickerU.endsWith('.AS') || nameU.includes('STOXX') || nameU.includes('EUROPE')) {
      geoMap['Europe (hors FR) 🇪🇺'] += val
    } else {
      geoMap['France 🇫🇷'] += val
    }
  })

  const colors = {
    'États-Unis 🇺🇸': '#38BDF8',
    'France 🇫🇷': '#A3E635',
    'Europe (hors FR) 🇪🇺': '#8B5CF6',
    'Asie & Monde 🌐': '#F59E0B'
  }

  return Object.entries(geoMap)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({
      name,
      value,
      pct: (value / tot) * 100,
      color: colors[name] || '#A3E635'
    }))
    .sort((a, b) => b.value - a.value)
})

const activeCategories = computed(() => {
  if (viewIndex.value === 1) return sectorCategories.value
  if (viewIndex.value === 2) return geoCategories.value
  return classCategories.value
})

const centerMetric = computed(() => {
  if (viewIndex.value === 1) {
    return { value: sectorCategories.value.length || 0, label: 'Secteurs' }
  }
  if (viewIndex.value === 2) {
    const topGeo = geoCategories.value[0]
    return {
      value: topGeo ? `${Math.round(topGeo.pct)}%` : '100%',
      label: topGeo ? topGeo.name.split(' ')[0] : 'Monde'
    }
  }
  return { value: `${allocationPercent.value}%`, label: 'Investi' }
})

const chartOption = computed(() => {
  if (viewIndex.value === 0) {
    const actVal = actionsVal.value
    const etfV = etfVal.value
    const cashV = cashVal.value
    const total = Math.max(1, actVal + etfV + cashV)

    return {
      backgroundColor: 'transparent',
      tooltip: { show: false },
      series: [
        {
          type: 'pie',
          radius: ['72%', '84%'],
          center: ['50%', '50%'],
          startAngle: 90,
          avoidLabelOverlap: false,
          label: { show: false },
          data: [
            { value: actVal, itemStyle: { color: '#8B5CF6', borderRadius: 8 } },
            { value: Math.max(0.1, total - actVal), itemStyle: { color: 'rgba(255,255,255,0.03)' } }
          ]
        },
        {
          type: 'pie',
          radius: ['54%', '66%'],
          center: ['50%', '50%'],
          startAngle: 90,
          avoidLabelOverlap: false,
          label: { show: false },
          data: [
            { value: etfV, itemStyle: { color: '#C4B5FD', borderRadius: 6 } },
            { value: Math.max(0.1, total - etfV), itemStyle: { color: 'rgba(255,255,255,0.03)' } }
          ]
        },
        {
          type: 'pie',
          radius: ['36%', '48%'],
          center: ['50%', '50%'],
          startAngle: 90,
          avoidLabelOverlap: false,
          label: { show: false },
          data: [
            { value: cashV, itemStyle: { color: '#A3E635', borderRadius: 4 } },
            { value: Math.max(0.1, total - cashV), itemStyle: { color: 'rgba(255,255,255,0.03)' } }
          ]
        }
      ]
    }
  }

  // Donut for Mode 1 (Sectors) & Mode 2 (Geo X-Ray)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#12161E',
      borderColor: 'rgba(255,255,255,0.12)',
      textStyle: { color: '#F8FAFC', fontSize: 11, fontFamily: 'JetBrains Mono' },
      formatter: (p) => `${p.name}: <b>${p.percent}%</b>`
    },
    series: [
      {
        type: 'pie',
        radius: ['58%', '82%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#0E131B',
          borderWidth: 2
        },
        label: { show: false },
        data: activeCategories.value.map((c) => ({
          name: c.name,
          value: Math.round(c.value),
          itemStyle: { color: c.color }
        }))
      }
    ]
  }
})
</script>
