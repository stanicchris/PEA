<template>
  <div class="glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden">
    <!-- Top Row: Title + Legend Pills + Icon -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-4">
      <div>
        <h3 class="text-white font-bold text-lg tracking-tight mb-2">Analytics Performance</h3>
        <div class="flex items-center gap-2 text-xs">
          <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-neonPurple/20 border border-neonPurple/30 text-lavender font-medium">
            <span class="w-2 h-2 rounded-full bg-neonPurple"></span>
            <span>Stocks</span>
          </div>
          <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] text-white/50 hover:text-white transition-colors cursor-pointer">
            <span class="w-2 h-2 rounded-full bg-lavenderLight"></span>
            <span>ETFs</span>
          </div>
          <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] text-white/50 hover:text-white transition-colors cursor-pointer">
            <span class="w-2 h-2 rounded-full bg-white/30"></span>
            <span>Liquidités</span>
          </div>
        </div>
      </div>

      <button class="w-8 h-8 rounded-full bg-white/[0.03] hover:bg-white/[0.08] text-white/40 hover:text-white flex items-center justify-center transition-all self-end sm:self-auto">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
        </svg>
      </button>
    </div>

    <!-- Stacked Isometric Ribbon / Streamchart -->
    <div class="relative w-full h-56 mt-auto">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center">
        <div class="w-10 h-10 rounded-full border-4 border-white/10 border-t-neonPurple animate-spin"></div>
      </div>
      <v-chart v-else class="w-full h-full" :option="chartOption" autoresize />

      <!-- Floating Milestone Price Tags -->
      <div class="absolute left-[8%] top-[55%] text-[10px] font-mono font-bold text-lavender bg-[#121418] px-2 py-0.5 rounded-md border border-white/10 shadow-lg">
        {{ formatMilestone(firstMilestone) }}
      </div>
      <div class="absolute left-[45%] top-[30%] text-[10px] font-mono font-bold text-lavender bg-[#121418] px-2 py-0.5 rounded-md border border-white/10 shadow-lg">
        {{ formatMilestone(midMilestone) }}
      </div>
      <div class="absolute right-[8%] top-[12%] text-[10px] font-mono font-bold text-white bg-[#121418] px-2 py-0.5 rounded-md border border-neonPurple/40 shadow-lg">
        {{ formatMilestone(lastMilestone) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
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

const firstMilestone = computed(() => {
  return props.history?.[0]?.total_valeur || 2487.85;
});

const midMilestone = computed(() => {
  if (props.history && props.history.length >= 2) {
    return props.history[Math.floor(props.history.length / 2)].total_valeur;
  }
  return 3745.29;
});

const lastMilestone = computed(() => {
  return props.summary?.total_value || 8987.12;
});

const formatMilestone = (val) => {
  return (val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) + ' €';
};

// Isometric stacked block ribbon chart matching interface.png
const chartOption = computed(() => {
  const years = ['2024', '2025', '2026'];
  
  // 3 Layers in shades of lavender / purple
  const layer1 = [2000, 3500, 7500]; // Bottom block
  const layer2 = [1200, 2200, 4800]; // Mid block
  const layer3 = [600, 1100, 2500];  // Top block

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#16191E',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC', fontFamily: 'Plus Jakarta Sans' },
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
      data: years,
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
        name: 'Stocks',
        type: 'bar',
        stack: 'total',
        barWidth: '65%',
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
        barWidth: '65%',
        itemStyle: {
          color: '#A78BFA'
        },
        data: layer2
      },
      {
        name: 'Liquidités',
        type: 'bar',
        stack: 'total',
        barWidth: '65%',
        itemStyle: {
          color: '#C4B5FD',
          borderRadius: [16, 16, 0, 0]
        },
        data: layer3
      }
    ]
  };
});
</script>
