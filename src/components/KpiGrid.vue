<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6 h-full">
    <div v-for="(kpi, index) in kpis" :key="index" class="glass rounded-3xl p-6 relative overflow-hidden flex flex-col justify-between border border-white/5">
      
      <svg class="w-0 h-0 absolute pointer-events-none">
        <defs>
          <linearGradient id="grad-emerald" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#10B981" stop-opacity="0.25" /><stop offset="100%" stop-color="#10B981" stop-opacity="0" /></linearGradient>
          <linearGradient id="grad-rose" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#F43F5E" stop-opacity="0.25" /><stop offset="100%" stop-color="#F43F5E" stop-opacity="0" /></linearGradient>
        </defs>
      </svg>
      <div v-if="kpi.hasSparkline && !isLoading" class="absolute bottom-0 left-0 right-0 h-2/3 opacity-40 pointer-events-none">
        <svg preserveAspectRatio="none" viewBox="0 0 100 50" class="w-full h-full">
          <path :d="kpi.isPositive ? 'M0,50 L15,35 L35,42 L55,20 L75,30 L100,5' : 'M0,5 L20,15 L40,10 L60,35 L80,25 L100,45'" fill="none" :stroke="kpi.isPositive ? '#10B981' : '#F43F5E'" stroke-width="2.5" vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round"/>
          <path :d="kpi.isPositive ? 'M0,50 L15,35 L35,42 L55,20 L75,30 L100,5 L100,50 Z' : 'M0,5 L20,15 L40,10 L60,35 L80,25 L100,45 L100,50 L0,50 Z'" :fill="kpi.isPositive ? 'url(#grad-emerald)' : 'url(#grad-rose)'" />
        </svg>
      </div>

      <div class="text-white/60 font-medium text-sm relative z-10 tracking-wide">{{ kpi.title }}</div>
      
      <div class="mt-4 relative z-10 flex-1 flex flex-col justify-end">
        <div v-if="isLoading" class="space-y-3">
          <div class="h-8 bg-white/5 rounded-lg animate-pulse w-3/4"></div>
          <div class="h-4 bg-white/5 rounded-lg animate-pulse w-1/2"></div>
        </div>
        <div v-else>
          <div class="text-2xl lg:text-3xl font-bold tabular-nums tracking-tight">{{ kpi.value }}</div>
          <div v-if="kpi.subtitle" :class="['text-sm font-medium mt-1.5', kpi.isPositive ? 'text-emerald-400' : kpi.isPositive === false ? 'text-rose-400' : 'text-white/40']">
            {{ kpi.subtitle }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  summary: Object,
  isLoading: Boolean
});

const kpis = computed(() => {
  if (!props.summary) return [];
  return [
    {
      title: 'Total Invested',
      value: `${props.summary.total_invested.toLocaleString('fr-FR', {minimumFractionDigits: 2})} €`,
      hasSparkline: false
    },
    {
      title: 'Global Return',
      value: `${props.summary.global_performance_value > 0 ? '+' : ''}${props.summary.global_performance_value.toLocaleString('fr-FR', {minimumFractionDigits: 2})} €`,
      subtitle: `${props.summary.global_performance_pct > 0 ? '+' : ''}${props.summary.global_performance_pct}% All-time`,
      hasSparkline: true,
      isPositive: props.summary.global_performance_value >= 0
    }
  ];
});
</script>
