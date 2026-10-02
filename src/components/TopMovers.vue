<template>
  <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
    <h3 class="text-xl font-bold tracking-tight mb-6 flex items-center gap-2">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clip-rule="evenodd" /></svg>
      Top Mouvements
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- Gainers -->
      <div>
        <h4 class="text-emerald-400 font-bold text-xs uppercase tracking-widest mb-3 flex items-center gap-1">Top Plus-Values</h4>
        <div v-if="isLoading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-16 rounded-2xl bg-white/5 animate-pulse"></div>
        </div>
        <div v-else class="space-y-3">
          <div v-for="pos in gainers" :key="pos.ticker" class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 flex items-center justify-between transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/10">
            <div>
              <div class="font-bold text-[#f8fafc] text-sm">{{ pos.name }}</div>
              <div class="text-xs text-white/50 mt-0.5">Val: {{ (pos.quantity * pos.current_price).toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'}) }}</div>
            </div>
            <div class="px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold shadow-sm shadow-emerald-500/20">
              +{{ pos.variation_pct }}%
            </div>
          </div>
          <div v-if="!gainers.length" class="text-xs text-white/40 italic p-2">Aucune plus-value.</div>
        </div>
      </div>
      
      <!-- Losers -->
      <div>
        <h4 class="text-rose-400 font-bold text-xs uppercase tracking-widest mb-3 flex items-center gap-1">Top Moins-Values</h4>
        <div v-if="isLoading" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-16 rounded-2xl bg-white/5 animate-pulse"></div>
        </div>
        <div v-else class="space-y-3">
          <div v-for="pos in losers" :key="pos.ticker" class="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4 flex items-center justify-between transition-all hover:-translate-y-1 hover:shadow-lg hover:shadow-rose-500/10">
            <div>
              <div class="font-bold text-[#f8fafc] text-sm">{{ pos.name }}</div>
              <div class="text-xs text-white/50 mt-0.5">Val: {{ (pos.quantity * pos.current_price).toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'}) }}</div>
            </div>
            <div class="px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/30 text-rose-400 text-xs font-bold shadow-sm shadow-rose-500/20">
              {{ pos.variation_pct }}%
            </div>
          </div>
          <div v-if="!losers.length" class="text-xs text-white/40 italic p-2">Aucune moins-value.</div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  positions: { type: Array, required: true },
  isLoading: { type: Boolean, default: false }
});

const gainers = computed(() => {
  if (!props.positions) return [];
  return [...props.positions].filter(p => p.variation_pct >= 0).sort((a, b) => b.variation_pct - a.variation_pct).slice(0, 3);
});

const losers = computed(() => {
  if (!props.positions) return [];
  return [...props.positions].filter(p => p.variation_pct < 0).sort((a, b) => a.variation_pct - b.variation_pct).slice(0, 3);
});
</script>
