<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/85 backdrop-blur-md" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-4xl max-h-[92vh] overflow-y-auto glass-card border border-white/[0.08] rounded-36 shadow-2xl bg-[#111419] p-6 sm:p-8 flex flex-col text-white">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonLime/15 border border-neonLime/30 flex items-center justify-center text-neonLime font-bold text-lg">
            ⚖️
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-2xl font-black text-white tracking-tight">Audit & Simulateur Fiscal PEA</h2>
              <span class="px-2.5 py-0.5 rounded-full bg-neonLime/15 border border-neonLime/30 text-neonLime text-[11px] font-mono font-bold">
                Exonération IR Active
              </span>
            </div>
            <p class="text-white/40 text-xs mt-0.5">Calcul des prélèvements sociaux (17,2%), plafond de versement et simulation de retrait net.</p>
          </div>
        </div>

        <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors bg-white/[0.04] hover:bg-white/[0.08] p-2.5 rounded-full">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Overview Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
          <p class="text-white/40 text-[10px] uppercase font-bold tracking-wider font-mono mb-1">Ancienneté du Plan</p>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-white font-mono">> 5 Ans</span>
            <span class="text-[11px] text-neonLime font-bold">Maturité Fiscale</span>
          </div>
          <p class="text-white/40 text-[11px] mt-1">Retraits possibles sans clôture du PEA</p>
        </div>

        <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
          <p class="text-white/40 text-[10px] uppercase font-bold tracking-wider font-mono mb-1">Impôt sur le Revenu (IR)</p>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-neonLime font-mono">0,00 %</span>
            <span class="text-[11px] line-through text-white/30">12,8%</span>
          </div>
          <p class="text-white/40 text-[11px] mt-1">Exonération totale sur les plus-values</p>
        </div>

        <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
          <p class="text-white/40 text-[10px] uppercase font-bold tracking-wider font-mono mb-1">Prélèvements Sociaux</p>
          <div class="flex items-baseline gap-2">
            <span class="text-2xl font-black text-lavender font-mono">17,20 %</span>
            <span class="text-[11px] text-white/40">CSG/CRDS</span>
          </div>
          <p class="text-white/40 text-[11px] mt-1">Dûs uniquement lors des retraits effectifs</p>
        </div>
      </div>

      <!-- Plafond de Versement 150 000 € -->
      <div class="bg-[#16191E] rounded-28 p-5 border border-white/[0.06] mb-6">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-white">Plafond Légal de Versement</span>
            <span class="text-xs text-white/40 font-mono">(Art. L221-30 CMF)</span>
          </div>
          <span class="text-xs font-mono font-bold text-neonLime">{{ percentInvested.toFixed(1) }} % utilisé</span>
        </div>

        <div class="h-3 rounded-full bg-white/[0.06] p-0.5 overflow-hidden mb-2">
          <div 
            class="h-full rounded-full bg-gradient-to-r from-neonPurple to-neonLime transition-all duration-700" 
            :style="{ width: percentInvested + '%' }"
          ></div>
        </div>

        <div class="flex justify-between items-center text-xs font-mono">
          <span class="text-white font-semibold">Versé : {{ investedAmount.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
          <span class="text-neonLime font-semibold">Capacité restante : {{ remainingCapacity.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
          <span class="text-white/40">Max : 150 000,00 €</span>
        </div>
      </div>

      <!-- Simulateur de Retrait Interactif -->
      <div class="bg-gradient-to-br from-white/[0.04] to-transparent rounded-28 p-6 border border-white/[0.08] mb-6">
        <h3 class="text-sm font-bold text-white uppercase tracking-wider font-mono mb-4 flex items-center gap-2">
          <span>🧮</span>
          Simulateur de Rachat Partiel Net d'Impôt
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div>
            <label class="text-xs text-white/60 block mb-2 font-medium">Montant brut à retirer (€) :</label>
            <div class="relative">
              <input 
                type="number" 
                v-model.number="withdrawalAmount" 
                min="100" 
                :max="totalPortfolioValue"
                step="100"
                class="w-full bg-[#111419] border border-white/[0.12] focus:border-neonLime rounded-2xl px-4 py-3 text-lg font-mono font-bold text-white outline-none transition-all"
              />
              <span class="absolute right-4 top-3.5 text-white/40 font-mono">EUR</span>
            </div>
            <input 
              type="range" 
              v-model.number="withdrawalAmount" 
              min="100" 
              :max="totalPortfolioValue" 
              step="100"
              class="w-full mt-3 accent-neonLime cursor-pointer"
            />
          </div>

          <!-- Simulation Result Box -->
          <div class="bg-[#111419] rounded-24 p-4 border border-white/[0.06] space-y-2.5 text-xs font-mono">
            <div class="flex justify-between items-center text-white/70">
              <span>Montant Brut Retiré :</span>
              <span class="font-bold text-white">{{ withdrawalAmount.toFixed(2) }} €</span>
            </div>
            <div class="flex justify-between items-center text-white/70">
              <span>Quote-part de Plus-Value :</span>
              <span class="text-lavender">{{ simGainPart.toFixed(2) }} € ({{ simGainPct.toFixed(1) }}%)</span>
            </div>
            <div class="flex justify-between items-center text-roseAcc">
              <span>Prélèvements Sociaux (17,2%) :</span>
              <span class="font-bold">- {{ simSocialTax.toFixed(2) }} €</span>
            </div>
            <div class="flex justify-between items-center text-neonLime">
              <span>Impôt sur le Revenu PEA (0%) :</span>
              <span class="font-bold">0,00 € (Économie : {{ simTaxSaved.toFixed(2) }} €)</span>
            </div>
            <div class="pt-2 border-t border-white/[0.08] flex justify-between items-center text-sm font-bold">
              <span class="text-white">Net Viré sur Compte :</span>
              <span class="text-neonLime text-base">{{ simNetReceived.toFixed(2) }} €</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Comparatif PEA vs Compte-Titres Ordinaire (CTO) -->
      <div class="bg-[#16191E] rounded-28 p-5 border border-white/[0.06]">
        <h4 class="text-xs font-bold text-lavender uppercase tracking-widest mb-3 font-mono">Avantage Fiscal Cumulé vs Compte-Titres (CTO Flat Tax 30%)</h4>
        <div class="flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/[0.02] p-4 rounded-20 border border-white/[0.04]">
          <div>
            <p class="text-white/80 text-xs font-medium">Sur vos plus-values latentes actuelles de <span class="text-neonLime font-bold font-mono">{{ gainTotal.toFixed(2) }} €</span> :</p>
            <p class="text-white/40 text-[11px] mt-0.5">Le PEA vous fait économiser 12,8% d'impôt forfaitaire sur chaque euro de bénéfice.</p>
          </div>
          <div class="text-right">
            <span class="text-xs text-white/40 block font-mono">Économie d'impôt latente</span>
            <span class="text-xl font-black text-neonLime font-mono">+ {{ (gainTotal * 0.128).toFixed(2) }} €</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  summary: { type: Object, default: () => ({}) }
});

defineEmits(['close']);

const totalPortfolioValue = computed(() => props.summary?.total_value || 36100);
const investedAmount = computed(() => props.summary?.total_invested || 30000);
const gainTotal = computed(() => Math.max(0, (props.summary?.global_performance_value || 6100)));

const percentInvested = computed(() => {
  return Math.min(100, Math.max(0, (investedAmount.value / 150000) * 100));
});

const remainingCapacity = computed(() => {
  return Math.max(0, 150000 - investedAmount.value);
});

// Simulation state
const withdrawalAmount = ref(5000);

const simGainPct = computed(() => {
  if (totalPortfolioValue.value <= 0) return 0;
  return (gainTotal.value / totalPortfolioValue.value) * 100;
});

const simGainPart = computed(() => {
  return withdrawalAmount.value * (simGainPct.value / 100);
});

const simSocialTax = computed(() => {
  return simGainPart.value * 0.172;
});

const simTaxSaved = computed(() => {
  return simGainPart.value * 0.128;
});

const simNetReceived = computed(() => {
  return withdrawalAmount.value - simSocialTax.value;
});
</script>
