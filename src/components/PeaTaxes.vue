<template>
  <div class="glass rounded-3xl p-6 border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
    <h3 class="text-xl font-bold mb-4 flex items-center gap-2 tracking-tight">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
      Fiscalité PEA & Retrait
    </h3>
    
    <div class="grid grid-cols-2 gap-4 mb-6">
      <div class="bg-white/5 rounded-2xl p-4 border border-white/10">
        <p class="text-white/50 text-xs mb-1 font-semibold uppercase tracking-wider">Plus-Value Imposable</p>
        <p class="text-2xl font-bold" :class="plusValue >= 0 ? 'text-emerald-400' : 'text-rose-400'">
          {{ plusValue >= 0 ? '+' : '' }}{{ plusValue.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'}) }}
        </p>
      </div>
      <div class="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4">
        <p class="text-rose-400/80 text-xs mb-1 font-semibold uppercase tracking-wider">Taxes (PS 17.2%)</p>
        <p class="text-2xl font-bold text-rose-400">-{{ taxes.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'}) }}</p>
      </div>
    </div>
    
    <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-6 text-center relative overflow-hidden">
      <div class="absolute -right-4 -top-4 w-16 h-16 bg-emerald-500/20 rounded-full blur-xl"></div>
      <p class="text-emerald-400/80 text-sm mb-2 font-medium">Net dans votre poche en cas de retrait total (après 5 ans) :</p>
      <p class="text-4xl font-black text-emerald-400 tracking-tight">{{ netValue.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'}) }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
const props = defineProps({ summary: { type: Object, default: () => ({}) } });

const plusValue = computed(() => props.summary?.global_performance_value || 0);
const totalValue = computed(() => props.summary?.total_value || 0);
const taxes = computed(() => Math.max(0, plusValue.value) * 0.172);
const netValue = computed(() => totalValue.value - taxes.value);
</script>
