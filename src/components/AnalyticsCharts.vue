<template>
  <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
    <h3 class="text-xl font-bold tracking-tight mb-2">Analyses</h3>
    <p class="text-white/40 text-xs mb-6">Répartition Sectorielle</p>
    <div class="h-64 w-full relative">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center">
        <div class="w-8 h-8 rounded-full border-2 border-white/10 border-t-blue-500 animate-spin"></div>
      </div>
      <v-chart v-else class="w-full h-full" :option="chartOption" autoresize />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent]);

const props = defineProps({
  positions: { type: Array, required: true },
  isLoading: { type: Boolean, default: false }
});

const chartOption = computed(() => {
  if (!props.positions || props.positions.length === 0) return {};
  
  const sectors = {};
  props.positions.forEach(p => {
    const s = p.sector || 'Inconnu';
    const val = p.quantity * p.current_price;
    if (!sectors[s]) sectors[s] = 0;
    sectors[s] += val;
  });

  const data = Object.keys(sectors).map(s => ({
    name: s,
    value: sectors[s]
  }));

  return {
    color: ['#0ea5e9', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e'],
    tooltip: { 
      trigger: 'item', 
      backgroundColor: 'rgba(14, 17, 23, 0.95)', 
      borderColor: 'rgba(255,255,255,0.1)', 
      textStyle: { color: '#F8FAFC' },
      formatter: '{b}: {c} € ({d}%)'
    },
    legend: { 
      bottom: '0%', 
      textStyle: { color: '#94a3b8', fontFamily: 'Plus Jakarta Sans' },
      icon: 'circle'
    },
    series: [
      {
        name: 'Secteur',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        data: data,
        emphasis: { itemStyle: { shadowBlur: 15, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } },
        itemStyle: { borderColor: '#151921', borderWidth: 3, borderRadius: 6 },
        label: { show: false }
      }
    ]
  };
});
</script>
