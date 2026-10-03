<template>
  <div class="glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden group">
    <!-- Top Row: Icon + Expand Arrow -->
    <div class="flex justify-between items-center mb-4">
      <div class="w-10 h-10 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-white/80 shadow-inner">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      </div>
      
      <button @click="$emit('open-settings')" class="w-8 h-8 rounded-full bg-white/[0.03] hover:bg-white/[0.08] text-white/40 hover:text-white flex items-center justify-center transition-all">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17L17 7M17 7H7M17 7V17" />
        </svg>
      </button>
    </div>

    <!-- Balance & Value -->
    <div class="mb-5">
      <div class="text-white/40 text-xs font-semibold uppercase tracking-wider mb-1.5 flex items-center gap-2">
        <span>Total Balance</span>
        <span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-neonLime/10 text-neonLime text-[10px] font-bold">
          <span class="w-1.5 h-1.5 rounded-full bg-neonLime animate-ping"></span>
          LIVE
        </span>
      </div>

      <div v-if="isLoading" class="h-12 bg-white/5 rounded-2xl animate-pulse w-3/4 mb-2"></div>
      <div v-else class="flex items-baseline gap-1 text-3xl sm:text-4xl lg:text-[40px] font-black tracking-tight text-white tabular-numbers">
        <span>{{ formattedTotal.main }}</span>
        <span class="text-white/40 text-2xl font-bold">,{{ formattedTotal.decimals }} €</span>
      </div>
    </div>

    <!-- 3 Segmented Pill Bars (Breakdown) -->
    <div class="space-y-2 mb-6">
      <div class="grid grid-cols-3 gap-2">
        <div class="h-2 rounded-full bg-neonLime/90"></div>
        <div class="h-2 rounded-full bg-neonPurple/90"></div>
        <div class="h-2 rounded-full bg-white/30"></div>
      </div>
      
      <div class="grid grid-cols-3 text-[11px] font-mono text-white/60 pt-1">
        <div class="flex flex-col">
          <span class="text-white font-semibold">{{ formatCurrency(actionsValue) }}</span>
          <span class="text-white/30 text-[10px]">Actions</span>
        </div>
        <div class="flex flex-col">
          <span class="text-white font-semibold">{{ formatCurrency(etfValue) }}</span>
          <span class="text-white/30 text-[10px]">ETFs</span>
        </div>
        <div class="flex flex-col">
          <span class="text-white font-semibold">{{ formatCurrency(cashValue) }}</span>
          <span class="text-white/30 text-[10px]">Cash</span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="grid grid-cols-2 gap-3 mt-auto">
      <button 
        @click="$emit('refresh')" 
        :disabled="isRefreshing" 
        class="bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] font-extrabold text-xs sm:text-sm py-3 px-3 rounded-full transition-all shadow-[0_4px_20px_rgba(163,230,53,0.25)] hover:shadow-[0_6px_25px_rgba(163,230,53,0.4)] flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50"
        title="Interroge Yahoo Finance pour actualiser les cours et enregistrer l'historique dans Supabase"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :class="isRefreshing ? 'animate-spin' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>{{ isRefreshing ? 'Sync en cours...' : '⚡ Actualiser Cours' }}</span>
      </button>

      <button 
        @click="$emit('open-settings')" 
        class="bg-white/[0.04] hover:bg-white/[0.08] text-white font-bold text-xs sm:text-sm py-3 px-3 rounded-full border border-white/[0.08] transition-all flex items-center justify-center gap-2 active:scale-95"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white/60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        <span>📁 Importer CSV</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  positions: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  isRefreshing: { type: Boolean, default: false }
});

defineEmits(['refresh', 'open-settings']);

const formattedTotal = computed(() => {
  const val = props.summary?.total_value || 0;
  const parts = val.toFixed(2).split('.');
  const intPart = parseInt(parts[0], 10).toLocaleString('fr-FR');
  return { main: intPart, decimals: parts[1] || '00' };
});

const cashValue = computed(() => {
  const total = props.summary?.total_value || 0;
  const invested = props.summary?.total_invested || 0;
  const perf = props.summary?.global_performance_value || 0;
  const titres = (props.positions || []).reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
  const diff = total - titres;
  return diff > 0 ? diff : 0;
});

const etfValue = computed(() => {
  return (props.positions || [])
    .filter(p => p.sector === 'ETF & Indice' || p.name?.toUpperCase().includes('ETF') || p.name?.toUpperCase().includes('CW8'))
    .reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
});

const actionsValue = computed(() => {
  const titres = (props.positions || []).reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
  return Math.max(0, titres - etfValue.value);
});

const formatCurrency = (val) => {
  return (val || 0).toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' €';
};
</script>
