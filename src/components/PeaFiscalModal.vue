<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-4">
    <!-- Backdrop with blur -->
    <div class="absolute inset-0 bg-black/85 backdrop-blur-xl cursor-pointer" @click="$emit('close')"></div>
    
    <!-- Modal Content (Liquid Glass) -->
    <div class="relative w-full max-w-4xl max-h-[92dvh] overflow-y-auto liquid-glass-chassis rounded-36 shadow-2xl p-5 sm:p-8 flex flex-col text-white specular-highlight border border-white/15">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6 pb-2 border-b border-white/[0.06] sticky top-0 bg-[#0A0D14]/80 backdrop-blur-md -mx-2 px-2 z-10">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonLime/15 border border-neonLime/30 flex items-center justify-center text-neonLime font-bold text-lg shadow-[0_0_12px_rgba(163,230,53,0.2)]">
            ⚖️
          </div>
          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="text-xl sm:text-2xl font-black text-white tracking-tight">Audit & Simulateur Fiscal PEA</h2>
              <span class="px-2.5 py-0.5 rounded-full bg-neonLime/15 border border-neonLime/30 text-neonLime text-[11px] font-mono font-bold shadow-[0_0_8px_rgba(163,230,53,0.15)]">
                Exonération IR Active
              </span>
            </div>
            <p class="text-white/40 text-xs mt-0.5">Prélèvements sociaux (17,2%), plafond 150k€ et simulation de retrait net.</p>
          </div>
        </div>

        <button 
          @click="$emit('close')" 
          class="text-white/40 hover:text-white transition-colors liquid-glass-subtle hover:border-white/20 p-2.5 rounded-full cursor-pointer active:scale-95"
          title="Fermer"
          aria-label="Fermer"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Overview Cards Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-6">
        <div class="liquid-glass-card rounded-24 p-4 specular-highlight">
          <p class="text-white/40 text-[10px] uppercase font-bold tracking-wider font-mono mb-1">Ancienneté du Plan</p>
          <div class="flex items-baseline gap-2">
            <span class="text-xl sm:text-2xl font-black text-white font-mono">> 5 Ans</span>
            <span class="text-[11px] text-neonLime font-bold">Maturité</span>
          </div>
          <p class="text-white/50 text-[11px] mt-1">Retraits libres sans clôture</p>
        </div>

        <div class="liquid-glass-card rounded-24 p-4 specular-highlight">
          <p class="text-white/40 text-[10px] uppercase font-bold tracking-wider font-mono mb-1">Impôt sur le Revenu (IR)</p>
          <div class="flex items-baseline gap-2">
            <span class="text-xl sm:text-2xl font-black text-neonLime font-mono">0,00 %</span>
            <span class="text-[11px] line-through text-white/30">12,8%</span>
          </div>
          <p class="text-white/50 text-[11px] mt-1">Exonération totale des gains</p>
        </div>

        <div class="liquid-glass-card rounded-24 p-4 specular-highlight">
          <p class="text-white/40 text-[10px] uppercase font-bold tracking-wider font-mono mb-1">Prélèvements Sociaux</p>
          <div class="flex items-baseline gap-2">
            <span class="text-xl sm:text-2xl font-black text-lavender font-mono">17,20 %</span>
            <span class="text-[11px] text-white/50">CSG/CRDS</span>
          </div>
          <p class="text-white/50 text-[11px] mt-1">Uniquement lors des retraits</p>
        </div>
      </div>

      <!-- Plafond de Versement 150 000 € -->
      <div class="liquid-glass-card rounded-28 p-4 sm:p-5 mb-6 specular-highlight">
        <div class="flex justify-between items-center mb-3">
          <div class="flex items-center gap-2">
            <span class="text-xs sm:text-sm font-bold text-white">Plafond Légal de Versement</span>
            <span class="text-[10px] sm:text-xs text-white/40 font-mono">(Art. L221-30 CMF)</span>
          </div>
          <span class="text-xs font-mono font-bold text-neonLime">{{ percentInvested.toFixed(1) }} % utilisé</span>
        </div>

        <div class="h-3 rounded-full bg-white/[0.06] p-0.5 overflow-hidden mb-2 border border-white/5 shadow-inner">
          <div 
            class="h-full rounded-full bg-gradient-to-r from-neonPurple to-neonLime transition-all duration-700 shadow-[0_0_12px_rgba(163,230,53,0.4)]" 
            :style="{ width: percentInvested + '%' }"
          ></div>
        </div>

        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center text-xs font-mono gap-1">
          <span class="text-white font-semibold">Versé : {{ investedAmount.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
          <span class="text-neonLime font-semibold">Capacité restante : {{ remainingCapacity.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
          <span class="text-white/40">Plafond : 150 000,00 €</span>
        </div>
      </div>

      <!-- Simulateur de Retrait Interactif -->
      <div class="liquid-glass-card rounded-28 p-4 sm:p-6 mb-6 specular-highlight">
        <h3 class="text-xs sm:text-sm font-bold text-white uppercase tracking-wider font-mono mb-4 flex items-center gap-2">
          <span>🧮</span>
          Simulateur de Rachat Partiel Net d'Impôt
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div>
            <label class="text-xs text-white/70 block mb-2 font-medium">Montant brut à retirer (€) :</label>
            <div class="relative">
              <input 
                type="number" 
                v-model.number="withdrawalAmount" 
                min="100" 
                :max="totalPortfolioValue"
                step="500"
                class="w-full liquid-glass-subtle border border-white/15 focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 rounded-2xl px-4 py-3 text-lg font-mono font-bold text-white outline-none transition-all shadow-inner"
              />
              <span class="absolute right-4 top-3.5 text-white/40 font-mono text-sm">EUR</span>
            </div>
            
            <input 
              type="range" 
              v-model.number="withdrawalAmount" 
              min="500" 
              :max="Math.max(1000, totalPortfolioValue)" 
              step="500"
              class="w-full mt-4 accent-neonLime cursor-pointer"
            />
            
            <div class="flex justify-between text-[10px] text-white/40 font-mono mt-1">
              <span>Min : 500 €</span>
              <span>Max disponible : {{ totalPortfolioValue.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
            </div>
          </div>

          <!-- Résultat du Rachat Net -->
          <div class="liquid-glass-subtle rounded-28 p-5 border border-white/10 space-y-3">
            <div class="flex justify-between items-center text-xs">
              <span class="text-white/60">Part de Capital récupérée :</span>
              <span class="font-mono text-white font-bold">{{ (withdrawalAmount - simGainPart).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
            </div>
            <div class="flex justify-between items-center text-xs">
              <span class="text-white/60">Part de Plus-Value brute :</span>
              <span class="font-mono text-lavender font-bold">{{ simGainPart.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
            </div>
            <div class="flex justify-between items-center text-xs pb-2 border-b border-white/[0.08]">
              <span class="text-white/60">Prélèvements Sociaux (17,2%) :</span>
              <span class="font-mono text-roseAcc font-bold">- {{ simSocialTax.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
            </div>
            <div class="flex justify-between items-center text-xs text-neonLime">
              <span class="font-bold">Économie d'IR grâce au PEA (12,8%) :</span>
              <span class="font-mono font-bold">+ {{ simTaxSaved.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
            </div>
            
            <div class="pt-2 border-t border-white/10 flex justify-between items-center">
              <div>
                <p class="text-[10px] font-mono uppercase text-white/50 font-bold">Net Viré sur votre Compte</p>
                <p class="text-2xl font-black text-neonLime font-mono">{{ simNetReceived.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</p>
              </div>
              <div class="text-right">
                <span class="text-[10px] font-mono bg-neonLime/15 text-neonLime px-2 py-1 rounded-full font-bold">
                  {{ ((simNetReceived / withdrawalAmount) * 100).toFixed(1) }}% du Brut
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Action Bar -->
      <div class="pt-4 border-t border-white/[0.08] flex items-center justify-end">
        <button 
          @click="$emit('close')"
          class="w-full sm:w-auto px-6 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 text-white font-bold text-xs border border-white/15 hover:border-white/30 transition-all cursor-pointer active:scale-95"
        >
          Fermer le Simulateur Fiscal
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  summary: Object
});

const emit = defineEmits(['close']);

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close');
  }
};

onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));

const totalPortfolioValue = computed(() => props.summary?.total_value || 0);
const investedAmount = computed(() => props.summary?.total_invested || 0);
const gainTotal = computed(() => Math.max(0, totalPortfolioValue.value - investedAmount.value));

const percentInvested = computed(() => {
  return Math.min(100, (investedAmount.value / 150000) * 100);
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
