<template>
  <div class="glass rounded-3xl p-6 md:p-8 h-full border border-white/5">
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-xl font-bold tracking-tight">Your Positions</h3>
    </div>

    <!-- Header -->
    <div class="hidden sm:grid grid-cols-12 gap-4 text-xs font-semibold text-white/40 uppercase tracking-widest mb-4 px-3">
      <div class="col-span-5 md:col-span-5">Asset</div>
      <div class="col-span-4 md:col-span-4 grid grid-cols-2 text-right">
        <div>Quantity</div>
        <div>Avg Cost (PRU)</div>
      </div>
      <div class="col-span-3 md:col-span-3 text-right">Value & Return</div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-16 bg-white/5 rounded-2xl animate-pulse"></div>
    </div>

    <!-- Rows -->
    <div v-else class="space-y-1 md:space-y-2">
      <div v-for="pos in positions" :key="pos.ticker" class="grid grid-cols-1 sm:grid-cols-12 gap-4 sm:gap-4 items-center p-3 rounded-2xl hover:bg-white/[0.04] transition-all duration-300 hover:shadow-[0_4px_20px_rgba(255,255,255,0.02)] cursor-pointer group">
        
        <div class="col-span-1 sm:col-span-5 flex items-center gap-4">
          <div class="w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg text-white shadow-inner bg-gradient-to-br from-blue-900 to-gray-900">
            {{ pos.ticker.charAt(0) }}
          </div>
          <div>
            <div class="font-bold text-white group-hover:text-blue-400 transition-colors">{{ pos.name }}</div>
            <div class="text-xs text-white/50 font-medium mt-0.5 tracking-wide">{{ pos.ticker }}</div>
          </div>
        </div>

        <div class="hidden sm:grid col-span-4 md:col-span-4 grid-cols-2 text-right text-sm">
          <div class="font-semibold text-white/80 tabular-nums">{{ pos.quantity }}</div>
          <div class="font-semibold text-white/80 tabular-nums">{{ pos.pru.toLocaleString('fr-FR', {minimumFractionDigits: 2}) }} €</div>
        </div>

        <div class="col-span-1 sm:col-span-3 flex sm:flex-col items-center sm:items-end justify-between sm:justify-center mt-2 sm:mt-0 pt-2 sm:pt-0 border-t border-white/5 sm:border-0">
          <div class="font-bold tabular-nums text-lg sm:text-base">{{ (pos.quantity * pos.current_price).toLocaleString('fr-FR', {minimumFractionDigits: 2}) }} €</div>
          <div class="sm:mt-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold tracking-wide" :class="pos.variation_pct >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'">
            {{ pos.variation_pct >= 0 ? '+' : '' }}{{ pos.variation_pct }}%
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  positions: Array,
  isLoading: Boolean
});
</script>
