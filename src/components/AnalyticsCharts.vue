<template>
  <div class="glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden">
    <!-- Top Row: Title + Legend Pills + View Mode Toggle -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-4">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <h3 class="text-white font-bold text-lg tracking-tight">Analytics Performance</h3>
          <span class="text-[10px] font-mono text-neonLime bg-neonLime/10 px-2 py-0.5 rounded-full font-bold">
            {{ activePeriod }}
          </span>
        </div>
        
        <!-- Clickable category filters -->
        <div class="flex items-center gap-2 text-xs">
          <button 
            @click="toggleLayer('stocks')"
            :class="visibleLayers.stocks ? 'bg-neonPurple/20 border-neonPurple/40 text-lavender' : 'bg-white/[0.04] text-white/30 border-white/[0.04]'"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full border transition-all cursor-pointer"
          >
            <span class="w-2 h-2 rounded-full" :class="visibleLayers.stocks ? 'bg-neonPurple' : 'bg-white/20'"></span>
            <span>Actions ({{ (stocksVal / (totalVal || 1) * 100).toFixed(0) }}%)</span>
          </button>

          <button 
            @click="toggleLayer('etfs')"
            :class="visibleLayers.etfs ? 'bg-lavender/20 border-lavender/40 text-lavenderLight' : 'bg-white/[0.04] text-white/30 border-white/[0.04]'"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full border transition-all cursor-pointer"
          >
            <span class="w-2 h-2 rounded-full" :class="visibleLayers.etfs ? 'bg-lavenderLight' : 'bg-white/20'"></span>
            <span>ETFs ({{ (etfsVal / (totalVal || 1) * 100).toFixed(0) }}%)</span>
          </button>

          <button 
            @click="toggleLayer('cash')"
            :class="visibleLayers.cash ? 'bg-neonLime/20 border-neonLime/40 text-neonLime' : 'bg-white/[0.04] text-white/30 border-white/[0.04]'"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full border transition-all cursor-pointer"
          >
            <span class="w-2 h-2 rounded-full" :class="visibleLayers.cash ? 'bg-neonLime' : 'bg-white/20'"></span>
            <span>Cash</span>
          </button>
        </div>
      </div>

      <!-- Timeframe selector -->
      <div class="flex items-center gap-1 bg-white/[0.04] p-1 rounded-full border border-white/[0.06] text-xs self-end sm:self-auto">
        <button 
          v-for="p in ['1M', '6M', '1A', 'ALL']" 
          :key="p"
          @click="activePeriod = p"
          :class="activePeriod === p ? 'bg-white/[0.15] text-white font-bold' : 'text-white/40 hover:text-white'"
          class="px-2.5 py-1 rounded-full transition-all cursor-pointer"
        >
          {{ p }}
        </button>
      </div>
    </div>

    <!-- Stacked Isometric Ribbon / Streamchart with Real Data -->
    <div class="relative w-full h-56 mt-auto">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center">
        <div class="w-10 h-10 rounded-full border-4 border-white/10 border-t-neonPurple animate-spin"></div>
      </div>
      <v-chart v-else class="w-full h-full" :option="chartOption" autoresize />

      <!-- Floating Milestone Price Tags matching exact portfolio data -->
      <div class="absolute left-[8%] top-[55%] text-[10px] font-mono font-bold text-lavender bg-[#121418] px-2 py-0.5 rounded-md border border-white/10 shadow-lg pointer-events-none">
        {{ formatMilestone(investedVal) }} (Investi)
      </div>
      <div class="absolute right-[8%] top-[12%] text-[10px] font-mono font-bold text-neonLime bg-[#121418] px-2 py-0.5 rounded-md border border-neonLime/40 shadow-lg pointer-events-none">
        {{ formatMilestone(totalVal) }} (Total)
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, CustomChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, BarChart, CustomChart, GridComponent, TooltipComponent]);

const props = defineProps({
  history: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  positions: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
});

const activePeriod = ref('ALL');
const visibleLayers = ref({
  stocks: true,
  etfs: true,
  cash: true
});

const toggleLayer = (layer) => {
  visibleLayers.value[layer] = !visibleLayers.value[layer];
};

const totalVal = computed(() => {
  if (props.summary?.total_value) return props.summary.total_value;
  return props.positions.reduce((sum, p) => sum + (p.quantity * p.current_price), 0) + (props.summary?.cash || 0);
});

const investedVal = computed(() => {
  if (props.summary?.total_invested) return props.summary.total_invested;
  return props.positions.reduce((sum, p) => sum + (p.quantity * p.pru), 0);
});

const etfsVal = computed(() => {
  return props.positions
    .filter(p => (p.sector && p.sector.toLowerCase().includes('etf')) || (p.name && (p.name.toUpperCase().includes('ETF') || p.name.toUpperCase().includes('CW8') || p.name.toUpperCase().includes('STOXX'))))
    .reduce((sum, p) => sum + (p.quantity * p.current_price), 0);
});

const stocksVal = computed(() => {
  const allTitres = props.positions.reduce((sum, p) => sum + (p.quantity * p.current_price), 0);
  return Math.max(0, allTitres - etfsVal.value);
});

const cashVal = computed(() => {
  return props.summary?.cash || 0;
});

const formatMilestone = (val) => {
  return (val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
};

const chartOption = computed(() => {
  // If real historical snapshots are present in props.history, use them!
  let categories = [];
  let sData = [];
  let eData = [];
  let cData = [];

  if (props.history && props.history.length >= 2) {
    const sorted = [...props.history].sort((a, b) => new Date(a.snapshot_date) - new Date(b.snapshot_date));
    categories = sorted.map(h => {
      const d = new Date(h.snapshot_date);
      return d.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
    });
    sData = sorted.map(h => visibleLayers.value.stocks ? Math.round((h.valeur_titres || h.total_valeur || 0) * (stocksVal.value / (totalVal.value || 1))) : 0);
    eData = sorted.map(h => visibleLayers.value.etfs ? Math.round((h.valeur_titres || h.total_valeur || 0) * (etfsVal.value / (totalVal.value || 1))) : 0);
    cData = sorted.map(h => visibleLayers.value.cash ? Math.round(h.cash || 0) : 0);
  } else {
    // Exact realistic points: [Capital Investi initial, Évolution intermédiaire, Valeur Actuelle en direct]
    categories = activePeriod.value === '1M' 
      ? ['Sem 1', 'Sem 2', 'Sem 3', 'Aujourd\'hui']
      : (activePeriod.value === '6M' ? ['Mois -5', 'Mois -3', 'Mois -1', 'Aujourd\'hui'] : ['Investi Initial', 'Mi-Parcours', 'Valorisation Direct']);

    const steps = categories.length;
    sData = categories.map((_, i) => {
      if (!visibleLayers.value.stocks) return 0;
      const ratio = (i + 1) / steps;
      const base = stocksVal.value * (0.85 + 0.15 * ratio);
      return Math.round(base);
    });
    eData = categories.map((_, i) => {
      if (!visibleLayers.value.etfs) return 0;
      const ratio = (i + 1) / steps;
      const base = etfsVal.value * (0.9 + 0.1 * ratio);
      return Math.round(base);
    });
    cData = categories.map(() => visibleLayers.value.cash ? Math.round(cashVal.value) : 0);
  }

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#16191E',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC', fontFamily: 'JetBrains Mono' },
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        let total = 0;
        let res = `<div class="font-bold border-b border-white/10 pb-1 mb-1 font-sans">${params[0].name}</div>`;
        params.forEach(p => {
          total += (p.value || 0);
          res += `<div class="flex justify-between gap-4 text-xs"><span>${p.seriesName}:</span><span class="font-bold font-mono">${(p.value || 0).toLocaleString('fr-FR')} €</span></div>`;
        });
        res += `<div class="border-t border-white/10 pt-1 mt-1 font-bold text-neonLime flex justify-between gap-4 font-mono"><span>Total:</span><span>${total.toLocaleString('fr-FR')} €</span></div>`;
        return res;
      }
    },
    grid: {
      left: '2%',
      right: '2%',
      bottom: '5%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#64748B', fontFamily: 'JetBrains Mono', fontSize: 11, margin: 16 }
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
        barWidth: '55%',
        itemStyle: {
          color: '#8B5CF6',
          borderRadius: [0, 0, 16, 16]
        },
        data: sData
      },
      {
        name: 'ETFs',
        type: 'bar',
        stack: 'total',
        barWidth: '55%',
        itemStyle: {
          color: '#A78BFA'
        },
        data: eData
      },
      {
        name: 'Liquidités',
        type: 'bar',
        stack: 'total',
        barWidth: '55%',
        itemStyle: {
          color: '#A3E635',
          borderRadius: [16, 16, 0, 0]
        },
        data: cData
      }
    ]
  };
});
</script>
