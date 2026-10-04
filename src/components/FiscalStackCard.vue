<template>
  <div class="flex flex-col gap-4 h-full">
    <!-- Sub-card 4A: Account Verification / Fiscalité PEA -->
    <div class="liquid-glass-card rounded-32 p-6 flex-1 flex flex-col justify-between relative overflow-hidden group specular-highlight">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="w-7 h-7 rounded-xl liquid-glass-subtle border border-neonLime/30 flex items-center justify-center text-white/90 shadow-[0_0_12px_rgba(163,230,53,0.2)]">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-neonLime" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clip-rule="evenodd" />
            </svg>
          </div>
          <h4 class="text-white font-bold text-sm tracking-tight">Régime Fiscal PEA</h4>
        </div>
        
        <p v-if="taxStatus?.is_mature" class="text-white/50 text-xs leading-relaxed mb-4">
          Plan mature (+5 ans) : Exonération totale d'impôt sur le revenu (prélèvements sociaux de {{ taxStatus.social_taxes_pct }}% uniquement). Ouvert le {{ taxStatus.opened_at }}.
        </p>
        <p v-else class="text-white/50 text-xs leading-relaxed mb-4">
          Plan en maturation (encore {{ Math.ceil((taxStatus?.days_to_maturity || 0)/30) }} mois). Exonération d'impôt sur le revenu (IR) après le {{ taxStatus?.maturity_date }}.
        </p>
      </div>

      <button 
        @click="$emit('open-tax-sim')" 
        class="bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] font-black text-xs py-2.5 px-4 rounded-full transition-all shadow-[0_2px_12px_rgba(163,230,53,0.3)] w-fit active:scale-95 cursor-pointer"
      >
        Simulateur Fiscal
      </button>
    </div>

    <!-- Sub-card 4B: Monthly Budget Limit / Plafond PEA 150 000 € -->
    <div class="liquid-glass-card rounded-32 p-6 flex-1 flex flex-col justify-between relative overflow-hidden group specular-highlight">
      <div class="flex justify-between items-center mb-3">
        <h4 class="text-white font-bold text-sm tracking-tight">Plafond Légal de Versement</h4>
        <button @click="$emit('open-tax-sim')" class="text-white/40 hover:text-white transition-colors p-1 cursor-pointer">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      <!-- Segmented Bar -->
      <div class="space-y-2 mb-2">
        <div class="h-3 rounded-full bg-white/[0.06] p-0.5 flex gap-1 overflow-hidden shadow-inner border border-white/5">
          <div 
            class="h-full rounded-full bg-gradient-to-r from-neonPurple to-lavender transition-all duration-700 shadow-[0_0_12px_rgba(139,92,246,0.5)]" 
            :style="{ width: percentInvested + '%' }"
          ></div>
        </div>
        
        <div class="flex justify-between items-baseline text-xs font-mono">
          <span class="text-white font-bold tabular-numbers">
            {{ investedAmount.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} € <span class="text-white/40 font-sans text-[10px]">versés nets</span>
          </span>
          <span class="text-white/50 tabular-numbers">
            {{ (taxStatus?.legal_limit || 150000).toLocaleString('fr-FR') }} € max
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  summary: { type: Object, default: () => ({}) }
});

defineEmits(['open-tax-sim']);

const taxStatus = computed(() => props.summary?.tax_status);

const investedAmount = computed(() => {
  return taxStatus.value?.net_invested ?? props.summary?.total_invested ?? 0;
});

const percentInvested = computed(() => {
  const max = taxStatus.value?.legal_limit || 150000;
  const val = investedAmount.value;
  return Math.min(100, Math.max(5, (val / max) * 100));
});
</script>
