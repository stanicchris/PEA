<template>
  <div class="glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden">
    <!-- Top Header -->
    <div class="flex justify-between items-center mb-2">
      <h3 class="text-white font-bold text-lg tracking-tight">Transfer</h3>
      <button class="w-8 h-8 rounded-full bg-white/[0.03] hover:bg-white/[0.08] text-white/40 hover:text-white flex items-center justify-center transition-all">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
      </button>
    </div>

    <!-- Center Concentric Rings Graphic -->
    <div class="relative w-full h-44 my-auto flex items-center justify-center">
      <div v-if="isLoading" class="w-24 h-24 rounded-full border-4 border-white/10 border-t-neonLime animate-spin"></div>
      <v-chart v-else class="w-full h-full" :option="ringOption" autoresize />
      
      <div v-if="!isLoading" class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <div class="text-2xl font-black text-white tracking-tight leading-none">{{ allocationPercent }}%</div>
        <div class="text-[11px] text-white/40 font-medium mt-1 uppercase tracking-wider">Total</div>
      </div>
    </div>

    <!-- Bottom Categories Legend with Values -->
    <div class="space-y-2.5 pt-2 border-t border-white/[0.06]">
      <div v-for="(cat, idx) in categories" :key="idx" class="flex items-center justify-between text-xs">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: cat.color }"></span>
          <span class="text-white/70 font-medium">{{ cat.name }}</span>
        </div>
        <div class="font-mono text-white/90 font-semibold tabular-numbers">
          {{ cat.value.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TooltipComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, PieChart, TooltipComponent]);

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  isLoading: { type: Boolean, default: false }
});

const totalVal = computed(() => props.summary?.total_value || 1);

const etfVal = computed(() => {
  return (props.positions || [])
    .filter(p => p.sector === 'ETF & Indice' || p.name?.toUpperCase().includes('ETF') || p.name?.toUpperCase().includes('CW8'))
    .reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
});

const titresVal = computed(() => {
  return (props.positions || []).reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
});

const cashVal = computed(() => {
  const diff = totalVal.value - titresVal.value;
  return diff > 0 ? diff : 0;
});

const actionsVal = computed(() => Math.max(0, titresVal.value - etfVal.value));

const allocationPercent = computed(() => {
  if (!totalVal.value) return 43;
  const pct = Math.round((etfVal.value + cashVal.value) / totalVal.value * 100);
  return pct > 0 ? pct : 43;
});

const categories = computed(() => [
  { name: 'Product / Titres Vifs', value: actionsVal.value || 4571.15, color: '#8B5CF6' },
  { name: 'Restaurants & ETF World', value: etfVal.value || 3450.75, color: '#C4B5FD' },
  { name: 'Internet / Liquidités', value: cashVal.value || 1240.75, color: '#A3E635' }
]);

const ringOption = computed(() => {
  const actVal = actionsVal.value || 60;
  const etfV = etfVal.value || 40;
  const cashV = cashVal.value || 20;
  const total = actVal + etfV + cashV;

  return {
    backgroundColor: 'transparent',
    tooltip: { show: false },
    series: [
      // Outer ring (Purple)
      {
        type: 'pie',
        radius: ['72%', '84%'],
        center: ['50%', '50%'],
        startAngle: 90,
        avoidLabelOverlap: false,
        label: { show: false },
        data: [
          { value: actVal, itemStyle: { color: '#8B5CF6', borderRadius: 8 } },
          { value: total - actVal, itemStyle: { color: 'rgba(255,255,255,0.03)' } }
        ]
      },
      // Middle ring (Lavender)
      {
        type: 'pie',
        radius: ['54%', '66%'],
        center: ['50%', '50%'],
        startAngle: 90,
        avoidLabelOverlap: false,
        label: { show: false },
        data: [
          { value: etfV, itemStyle: { color: '#C4B5FD', borderRadius: 6 } },
          { value: total - etfV, itemStyle: { color: 'rgba(255,255,255,0.03)' } }
        ]
      },
      // Inner ring (Neon Lime)
      {
        type: 'pie',
        radius: ['36%', '48%'],
        center: ['50%', '50%'],
        startAngle: 90,
        avoidLabelOverlap: false,
        label: { show: false },
        data: [
          { value: cashV, itemStyle: { color: '#A3E635', borderRadius: 4 } },
          { value: total - cashV, itemStyle: { color: 'rgba(255,255,255,0.03)' } }
        ]
      }
    ]
  };
});
</script>
