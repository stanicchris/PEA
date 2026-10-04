<template>
  <div class="space-y-6">
    <div class="liquid-glass-card rounded-36 p-6 sm:p-8 border border-white/10 relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-roseAcc/20 blur-[80px] rounded-full pointer-events-none"></div>

      <div class="flex justify-between items-start mb-8 relative z-10">
        <div>
          <h3 class="text-xl font-black text-white flex items-center gap-2">
            <span class="text-2xl">🔍</span> Optimiseur de Frais (TER)
          </h3>
          <p class="text-white/50 text-xs mt-1 font-medium">Scannez vos ETF pour détecter les frais abusifs et calculer l'impact sur 20 ans.</p>
        </div>
        <button 
          @click="scanFees" 
          :disabled="isLoading"
          class="px-4 py-2 rounded-xl liquid-glass-subtle bg-white/5 hover:bg-white/10 border border-white/10 text-white text-xs font-bold transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
        >
          <span v-if="isLoading" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ isLoading ? 'Scan en cours...' : 'Lancer le scan' }}
        </button>
      </div>

      <div v-if="results" class="relative z-10 space-y-6">
        <!-- Impact sur 20 ans -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-black/30 border border-white/5 rounded-24 p-5 flex flex-col justify-center">
            <p class="text-white/40 text-[10px] uppercase tracking-widest font-bold mb-1 font-mono">Frais Annuels Actuels</p>
            <p class="text-2xl font-black text-roseAcc font-mono">{{ results.total_annual_fees.toFixed(2) }} €</p>
            <p class="text-white/40 text-xs mt-1">Prélevés automatiquement par les émetteurs.</p>
          </div>
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-24 p-5 flex flex-col justify-center shadow-[0_0_20px_rgba(163,230,53,0.05)]">
            <p class="text-white/40 text-[10px] uppercase tracking-widest font-bold mb-1 font-mono">Économie Potentielle (sur 20 ans)*</p>
            <p class="text-2xl font-black text-neonLime font-mono">+ {{ impact20Years.toFixed(0) }} €</p>
            <p class="text-white/50 text-[10px] mt-1">*Projection avec intérêts composés (7% / an) si réinvestis.</p>
          </div>
        </div>

        <!-- Détails des actifs scannés -->
        <div v-if="results.scanned_assets.length > 0" class="space-y-3">
          <h4 class="text-white/60 text-xs font-bold uppercase tracking-wider mb-2 font-mono">Détail par actif</h4>
          <div v-for="asset in results.scanned_assets" :key="asset.isin" 
               class="p-4 rounded-24 border transition-all"
               :class="asset.is_high_fee ? 'bg-roseAcc/5 border-roseAcc/30' : 'bg-white/5 border-white/10'">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold" 
                        :class="asset.is_high_fee ? 'bg-roseAcc/20 text-roseAcc' : 'bg-white/10 text-white/70'">
                    TER: {{ asset.ter }}%
                  </span>
                  <p class="text-sm font-bold text-white">{{ asset.name }}</p>
                </div>
                <p class="text-white/40 text-xs mt-1 font-mono">{{ asset.value.toFixed(2) }} € investis • Frais: {{ asset.annual_fee_euros.toFixed(2) }} €/an</p>
              </div>
              
              <div v-if="asset.alternative" class="sm:text-right bg-black/40 p-3 rounded-xl border border-neonLime/20">
                <p class="text-neonLime text-xs font-bold mb-1">💡 Alternative suggérée :</p>
                <p class="text-white text-xs font-medium">{{ asset.alternative.name }}</p>
                <p class="text-white/60 text-[10px] font-mono mt-0.5">Nouveau TER: {{ asset.alternative.ter }}% (-{{ asset.alternative.savings_euros.toFixed(2) }}€/an)</p>
              </div>
              <div v-else-if="!asset.is_high_fee" class="sm:text-right">
                <span class="text-neonLime text-xs font-bold px-3 py-1 rounded-full bg-neonLime/10 border border-neonLime/20">Optimisé ✓</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-6 text-white/50 text-sm">
          Aucun ETF avec des données de frais connues n'a été détecté dans votre portefeuille.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { getApiBase } from '../config';

const isLoading = ref(false);
const results = ref(null);

// Approximation of compounding savings over 20 years at 7% return
const impact20Years = computed(() => {
  if (!results.value) return 0;
  const annualSavings = results.value.total_potential_savings;
  if (annualSavings <= 0) return 0;
  
  // Future Value of a Series formula: PMT * (((1 + r)^n - 1) / r)
  const r = 0.07;
  const n = 20;
  return annualSavings * (((Math.pow(1 + r, n)) - 1) / r);
});

const scanFees = async () => {
  isLoading.value = true;
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/api/optimization/fee-scan`, { 
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') } 
    });
    if (res.ok) {
      results.value = await res.json();
    }
  } catch (err) {
    console.error(err);
  } finally {
    isLoading.value = false;
  }
};
</script>
