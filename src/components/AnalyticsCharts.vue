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
            <span>Actions</span>
          </button>

          <button 
            @click="toggleLayer('etfs')"
            :class="visibleLayers.etfs ? 'bg-lavender/20 border-lavender/40 text-lavenderLight' : 'bg-white/[0.04] text-white/30 border-white/[0.04]'"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full border transition-all cursor-pointer"
          >
            <span class="w-2 h-2 rounded-full" :class="visibleLayers.etfs ? 'bg-lavenderLight' : 'bg-white/20'"></span>
            <span>ETFs</span>
          </button>

          <button 
            @click="toggleLayer('cash')"
            :class="visibleLayers.cash ? 'bg-neonLime/20 border-neonLime/40 text-neonLime' : 'bg-white/[0.04] text-white/30 border-white/[0.04]'"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-full border transition-all cursor-pointer"
          >
            <span class="w-2 h-2 rounded-full" :class="visibleLayers.cash ? 'bg-neonLime' : 'bg-white/20'"></span>
            <span>Liquidités</span>
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

    <!-- Stacked Isometric Ribbon / Streamchart -->
    <div class="relative w-full h-56 mt-auto">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center">
        <div class="w-10 h-10 rounded-full border-4 border-white/10 border-t-neonPurple animate-spin"></div>
      </div>
      <v-chart v-else class="w-full h-full" :option="chartOption" autoresize />

      <!-- Floating Milestone Price Tags -->
      <div class="absolute left-[8%] top-[55%] text-[10px] font-mono font-bold text-lavender bg-[#121418] px-2 py-0.5 rounded-md border border-white/10 shadow-lg pointer-events-none">
        {{ formatMilestone(firstMilestone) }}
      </div>
      <div class="absolute left-[45%] top-[30%] text-[10px] font-mono font-bold text-lavender bg-[#121418] px-2 py-0.5 rounded-md border border-white/10 shadow-lg pointer-events-none">
        {{ formatMilestone(midMilestone) }}
      </div>
      <div class="absolute right-[8%] top-[12%] text-[10px] font-mono font-bold text-white bg-[#121418] px-2 py-0.5 rounded-md border border-neonPurple/40 shadow-lg pointer-events-none">
        {{ formatMilestone(lastMilestone) }}
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

const totalVal = computed(() => props.summary?.total_value || 36100);

const firstMilestone = computed(() => {
  return props.history?.[0]?.total_valeur || Math.round(totalVal.value * 0.45);
});

const midMilestone = computed(() => {
  if (props.history && props.history.length >= 2) {
    return props.history[Math.floor(props.history.length / 2)].total_valeur;
  }
  return Math.round(totalVal.value * 0.72);
});

const lastMilestone = computed(() => {
  return totalVal.value;
});

const formatMilestone = (val) => {
  return (val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
};

const chartOption = computed(() => {
  const periods = activePeriod.value === '1M' 
    ? ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
    : (activePeriod.value === '6M' ? ['M-5', 'M-3', 'M-1', 'Aujourd\'hui'] : ['2024', '2025', '2026']);
  
  const baseT = totalVal.value;
  const layer1 = periods.map((_, i) => visibleLayers.value.stocks ? Math.round(baseT * (0.45 + i * 0.12)) : 0);
  const layer2 = periods.map((_, i) => visibleLayers.value.etfs ? Math.round(baseT * (0.15 + i * 0.05)) : 0);
  const layer3 = periods.map((_, i) => visibleLayers.value.cash ? Math.round(baseT * 0.04) : 0);

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#16191E',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC', fontFamily: 'JetBrains Mono' },
      axisPointer: { type: 'shadow' }
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
      data: periods,
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
        barWidth: '60%',
        itemStyle: {
          color: '#8B5CF6',
          borderRadius: [0, 0, 16, 16]
        },
        data: layer1
      },
      {
        name: 'ETFs',
        type: 'bar',
        stack: 'total',
        barWidth: '60%',
        itemStyle: {
          color: '#A78BFA'
        },
        data: layer2
      },
      {
        name: 'Liquidités',
        type: 'bar',
        stack: 'total',
        barWidth: '60%',
        itemStyle: {
          color: '#A3E635',
          borderRadius: [16, 16, 0, 0]
        },
        data: layer3
      }
    ]
  };
});
</script>
