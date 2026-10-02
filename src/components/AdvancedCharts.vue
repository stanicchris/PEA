<template>
  <div class="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-6">
    <!-- Treemap -->
    <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
      <h3 class="text-lg font-bold mb-4 tracking-tight">Treemap du Portefeuille</h3>
      <div class="h-80"><v-chart class="w-full h-full" :option="treemapOption" autoresize /></div>
    </div>
    
    <!-- Comparatif PRU vs Cours -->
    <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
      <h3 class="text-lg font-bold mb-4 tracking-tight">PRU vs Dernier Cours (€)</h3>
      <div class="h-80"><v-chart class="w-full h-full" :option="pruOption" autoresize /></div>
    </div>

    <!-- Matrice Poids vs Perf -->
    <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
      <h3 class="text-lg font-bold mb-4 tracking-tight">Matrice Poids vs Performance</h3>
      <div class="h-80"><v-chart class="w-full h-full" :option="scatterOption" autoresize /></div>
    </div>

    <!-- Dividendes -->
    <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
      <h3 class="text-lg font-bold mb-4 tracking-tight">Dividendes Annuels Estimés</h3>
      <div class="h-80"><v-chart class="w-full h-full" :option="dividendsOption" autoresize /></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { TreemapChart, BarChart, ScatterChart } from 'echarts/charts';
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components';
import VChart from 'vue-echarts';

use([CanvasRenderer, TreemapChart, BarChart, ScatterChart, TooltipComponent, LegendComponent, GridComponent]);

const props = defineProps({ positions: { type: Array, default: () => [] }, totalValue: { type: Number, default: 1 } });

// Treemap
const treemapOption = computed(() => {
  const data = props.positions.map(p => ({
    name: p.ticker,
    value: p.quantity * p.current_price,
    itemStyle: { color: p.variation_pct >= 0 ? '#10b981' : '#f43f5e' }
  }));
  return {
    tooltip: { formatter: '{b}: {c} €' },
    series: [{ type: 'treemap', data, roam: false, label: { show: true, formatter: '{b}\n{c} €' }, itemStyle: { borderColor: '#0E1117', borderWidth: 2 } }]
  };
});

// PRU vs Cours
const pruOption = computed(() => {
  return {
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#94a3b8' }, bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: props.positions.map(p => p.ticker), axisLabel: { color: '#94a3b8', rotate: 45 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: '#94a3b8' } },
    series: [
      { name: 'PRU', type: 'bar', data: props.positions.map(p => p.pru), itemStyle: { color: '#64748b', borderRadius: [4,4,0,0] } },
      { name: 'Cours', type: 'bar', data: props.positions.map(p => p.current_price), itemStyle: { color: '#3b82f6', borderRadius: [4,4,0,0] } }
    ]
  };
});

// Scatter (Weight vs Perf)
const scatterOption = computed(() => {
  const data = props.positions.map(p => {
    const weight = ((p.quantity * p.current_price) / props.totalValue) * 100;
    return [weight, p.variation_pct, p.ticker, p.quantity * p.current_price];
  });
  return {
    tooltip: { 
      formatter: (p) => `<div class="font-bold">${p.value[2]}</div>Poids: ${p.value[0].toFixed(1)}%<br/>Perf: ${p.value[1].toFixed(1)}%`,
      backgroundColor: 'rgba(14, 17, 23, 0.95)',
      borderColor: 'rgba(255,255,255,0.1)',
      textStyle: { color: '#F8FAFC' }
    },
    xAxis: { name: 'Poids (%)', nameTextStyle: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: '#94a3b8' } },
    yAxis: { name: 'Perf (%)', nameTextStyle: { color: '#94a3b8' }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: '#94a3b8' } },
    series: [{ 
      type: 'scatter', 
      symbolSize: (data) => Math.max(10, Math.min(40, data[3] / 100)),
      data, 
      itemStyle: { color: '#8b5cf6', shadowBlur: 10, shadowColor: 'rgba(139, 92, 246, 0.5)' } 
    }]
  };
});

// Dividends
const dividendsOption = computed(() => {
  return {
    tooltip: { trigger: 'axis', formatter: '{b}: {c} €/an' },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: props.positions.map(p => p.ticker), axisLabel: { color: '#94a3b8', rotate: 45 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
    series: [{ 
      type: 'bar', 
      data: props.positions.map(p => ((p.quantity * p.current_price * 0.03)).toFixed(2)), 
      itemStyle: { color: '#f59e0b', borderRadius: [4,4,0,0] } 
    }]
  };
});
</script>
