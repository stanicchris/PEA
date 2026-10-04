<template>
  <div class="liquid-glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden group specular-highlight">
    <!-- Top Header -->
    <div class="flex justify-between items-center mb-2">
      <div class="flex items-center gap-2">
        <h3 class="text-white font-bold text-lg tracking-tight">Allocation</h3>
        <span class="text-[10px] font-mono font-bold text-neonLime/90 bg-neonLime/10 border border-neonLime/20 px-2 py-0.5 rounded-full">3 Niveaux</span>
      </div>
      
      <button 
        @click="cycleView" 
        class="w-8 h-8 rounded-full liquid-glass-subtle hover:bg-white/10 text-white/50 hover:text-white flex items-center justify-center transition-all cursor-pointer hover:border-white/20 active:scale-95"
        title="Changer de vue d'allocation"
      >
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
        <div class="text-2xl font-black text-white tracking-tight leading-none drop-shadow-sm">{{ allocationPercent }}%</div>
        <div class="text-[11px] text-white/40 font-semibold mt-1 uppercase tracking-wider">Investi</div>
      </div>
    </div>

    <!-- Bottom Categories Legend with Values -->
    <div class="space-y-2.5 pt-3 border-t border-white/[0.08]">
      <div v-for="(cat, idx) in categories" :key="idx" class="flex items-center justify-between text-xs">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full shadow-sm" :style="{ backgroundColor: cat.color }"></span>
          <span class="text-white/80 font-medium">{{ cat.name }}</span>
        </div>
        <div class="font-mono text-white font-semibold tabular-numbers">
          {{ store.formatCurrency(cat.value) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TooltipComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { useAppStore } from '../stores/app';

use([CanvasRenderer, PieChart, TooltipComponent]);
const store = useAppStore();

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  isLoading: { type: Boolean, default: false }
});

const viewIndex = ref(0);
const cycleView = () => {
  viewIndex.value = (viewIndex.value + 1) % 2;
};

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
  return Number(props.summary?.cash || 0);
});

const actionsVal = computed(() => Math.max(0, titresVal.value - etfVal.value));

const allocationPercent = computed(() => {
  if (!totalVal.value) return 0;
  return Math.min(100, Math.round((titresVal.value / totalVal.value) * 100));
});

const categories = computed(() => [
  { name: 'Actions Vives PEA', value: actionsVal.value, color: '#8B5CF6' },
  { name: 'ETFs & Trackers', value: etfVal.value, color: '#C4B5FD' },
  { name: 'Liquidités / Espèces', value: cashVal.value, color: '#A3E635' }
]);

const ringOption = computed(() => {
  const actVal = actionsVal.value;
  const etfV = etfVal.value;
  const cashV = cashVal.value;
  const total = Math.max(1, actVal + etfV + cashV);

  return {
    backgroundColor: 'transparent',
    tooltip: { show: false },
    series: [
      // Outer ring (Purple: Actions)
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
      // Middle ring (Lavender: ETFs)
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
      // Inner ring (Neon Lime: Cash)
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
  };
});
</script>
