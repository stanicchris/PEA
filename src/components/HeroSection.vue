<template>
  <div class="glass rounded-3xl p-8 relative overflow-hidden flex flex-col justify-center min-h-[220px] h-full border border-white/5">
    <div class="absolute top-0 right-0 w-72 h-72 bg-emerald-500/10 blur-3xl rounded-full -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>

    <div class="relative z-10 flex justify-between items-start mb-6">
      <div class="text-white/60 font-medium text-lg tracking-wide">Total Portfolio Value</div>
      
      <div class="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-full border border-white/10 shadow-sm backdrop-blur-md">
        <span class="relative flex h-2.5 w-2.5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
        </span>
        <span class="text-xs font-semibold text-white/80 uppercase tracking-widest">Live</span>
      </div>
    </div>

    <div class="relative z-10 flex flex-col sm:flex-row sm:items-baseline gap-4 mt-auto">
      <div v-if="isLoading" class="animate-pulse h-16 bg-white/10 rounded-lg w-2/3"></div>
      <div v-else class="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight tabular-nums">
        {{ summary?.total_value?.toLocaleString('fr-FR', {minimumFractionDigits: 2}) }} <span class="text-3xl md:text-5xl text-white/40 font-medium ml-1">€</span>
      </div>
      
      <div v-if="!isLoading && summary" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full font-semibold text-sm md:text-base border"
           :class="summary.global_performance_pct >= 0 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'">
        <svg v-if="summary.global_performance_pct >= 0" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m0-16l-6 6m6-6l6 6" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 md:h-5 md:w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 20V4m0 16l-6-6m6 6l6-6" />
        </svg>
        <span>{{ summary.global_performance_pct >= 0 ? '+' : '' }}{{ summary.global_performance_pct }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  summary: Object,
  isLoading: Boolean
});
</script>
