<template>
  <div class="glass rounded-3xl p-6 relative flex flex-col h-[400px] border border-white/5">
    <h3 class="text-lg font-bold tracking-tight mb-2">Asset Allocation</h3>
    
    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
       <div class="w-32 h-32 rounded-full border-4 border-white/10 border-t-blue-500 animate-spin"></div>
    </div>
    
    <div v-else class="flex-1 relative w-full h-full">
      <v-chart class="w-full h-full" :option="chartOption" autoresize />
      <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        <div class="text-white/40 text-xs font-semibold uppercase tracking-widest mb-1">Total</div>
        <div class="text-2xl font-bold tracking-tight text-white drop-shadow-[0_0_12px_rgba(255,255,255,0.4)]">
          {{ summary?.total_value?.toLocaleString('fr-FR', {maximumFractionDigits: 0}) }} €
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, provide } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TooltipComponent } from 'echarts/components';
import VChart, { THEME_KEY } from 'vue-echarts';

use([CanvasRenderer, PieChart, TooltipComponent]);
provide(THEME_KEY, 'dark');

const props = defineProps({
  positions: Array,
  summary: Object,
  isLoading: Boolean
});

const chartOption = computed(() => {
  // Map API positions to the ECharts format dynamically
  const data = (props.positions || []).map(p => ({
    name: p.name,
    value: p.quantity * p.current_price
  }));
  
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      transitionDuration: 0.2,
      backgroundColor: 'rgba(21, 25, 33, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      textStyle: { color: '#F8FAFC' },
      padding: [12, 16],
      borderRadius: 12,
      formatter: (params) => {
        return `
          <div class="font-bold mb-1.5" style="color: #F8FAFC">${params.name}</div>
          <div class="flex items-center gap-2" style="display: flex; align-items: center; gap: 8px;">
            <span style="background-color: ${params.color}; width: 8px; height: 8px; border-radius: 50%; display: inline-block;"></span>
            <span class="font-medium" style="color: #F8FAFC">${params.value.toLocaleString('fr-FR', {minimumFractionDigits: 2})} €</span>
            <span style="color: rgba(255,255,255,0.5); font-size: 12px">(${params.percent}%)</span>
          </div>
        `;
      }
    },
    series: [
      {
        type: 'pie',
        radius: ['65%', '85%'],
        center: ['50%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#0E1117',
          borderWidth: 4
        },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: false }, itemStyle: { shadowBlur: 20, shadowColor: 'rgba(0, 0, 0, 0.5)' } },
        labelLine: { show: false },
        data: data
      }
    ]
  };
});
</script>
