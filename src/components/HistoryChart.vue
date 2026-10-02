<template>
  <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
    <h3 class="text-xl font-bold mb-4 tracking-tight flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>
      Évolution du Portefeuille
    </h3>
    <div class="h-96 w-full relative">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center">
        <div class="w-8 h-8 rounded-full border-2 border-white/10 border-t-blue-500 animate-spin"></div>
      </div>
      <v-chart v-else-if="history && history.length > 0" class="w-full h-full" :option="chartOption" autoresize />
      <div v-else class="absolute inset-0 flex items-center justify-center text-white/40 text-sm">
        Pas assez d'historique (minimum 1 sauvegarde requise)
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { LineChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent, GridComponent, DataZoomComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, LineChart, TooltipComponent, LegendComponent, GridComponent, DataZoomComponent]);

const props = defineProps({ history: { type: Array, default: () => [] }, isLoading: { type: Boolean, default: false } });

const chartOption = computed(() => {
  const dates = props.history.map(h => h.date);
  const totalValue = props.history.map(h => h.total_valeur);
  const invested = props.history.map(h => h.cout_investi);

  return {
    tooltip: { 
      trigger: 'axis', 
      backgroundColor: 'rgba(14, 17, 23, 0.95)', 
      borderColor: 'rgba(255,255,255,0.1)', 
      textStyle: { color: '#F8FAFC' } 
    },
    legend: { 
      data: ['Valorisation Totale', 'Capital Investi'], 
      textStyle: { color: '#94a3b8' }, 
      bottom: 0 
    },
    grid: { left: '3%', right: '4%', bottom: '15%', top: '5%', containLabel: true },
    dataZoom: [
      { type: 'inside' }, 
      { type: 'slider', bottom: 25, height: 10, borderColor: 'transparent', textStyle: { color: 'transparent' } }
    ],
    xAxis: { 
      type: 'category', 
      boundaryGap: false, 
      data: dates, 
      axisLabel: { color: '#94a3b8' } 
    },
    yAxis: { 
      type: 'value', 
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, 
      axisLabel: { color: '#94a3b8' } 
    },
    series: [
      {
        name: 'Valorisation Totale',
        type: 'line',
        smooth: true,
        data: totalValue,
        symbol: 'none',
        lineStyle: { width: 3, color: '#3b82f6' },
        areaStyle: {
          color: {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(59, 130, 246, 0.4)' }, { offset: 1, color: 'rgba(59, 130, 246, 0)' }]
          }
        }
      },
      {
        name: 'Capital Investi',
        type: 'line',
        smooth: true,
        data: invested,
        symbol: 'none',
        lineStyle: { width: 2, type: 'dashed', color: '#94a3b8' }
      }
    ]
  };
});
</script>
