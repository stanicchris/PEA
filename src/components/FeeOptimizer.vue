<template>
  <div class="space-y-6">
    <div class="liquid-glass-card rounded-36 p-6 sm:p-8 border border-white/10 relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-roseAcc/20 blur-[80px] rounded-full pointer-events-none"></div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 relative z-10">
        <div>
          <h3 class="text-xl font-black text-white flex items-center gap-2">
            <span class="text-2xl">🔍</span> Optimiseur de Frais (TER)
          </h3>
          <p class="text-white/50 text-xs mt-1 font-medium">Scannez vos ETF pour détecter les frais de gestion élevés et calculer l'impact composé sur 20 ans.</p>
        </div>
        <button 
          @click="scanFees" 
          :disabled="isLoading"
          class="px-4 py-2 rounded-xl liquid-glass-subtle bg-white/5 hover:bg-white/10 border border-white/10 text-white text-xs font-bold transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2 self-start sm:self-auto cursor-pointer"
        >
          <span v-if="isLoading" class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
          {{ isLoading ? 'Scan en cours...' : 'Actualiser le scan' }}
        </button>
      </div>

      <div v-if="results" class="relative z-10 space-y-6">
        <!-- Impact sur 20 ans -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-black/30 border border-white/5 rounded-24 p-5 flex flex-col justify-center">
            <p class="text-white/40 text-[10px] uppercase tracking-widest font-bold mb-1 font-mono">Frais Annuels Actuels (TER)</p>
            <p class="text-2xl font-black text-roseAcc font-mono">{{ store.isDiscreteMode ? '••• €' : `${results.total_annual_fees.toFixed(2)} € / an` }}</p>
            <p class="text-white/40 text-xs mt-1">Prélevés automatiquement par les émetteurs sur la valeur liquidative.</p>
          </div>
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-24 p-5 flex flex-col justify-center shadow-[0_0_20px_rgba(163,230,53,0.05)]">
            <p class="text-white/40 text-[10px] uppercase tracking-widest font-bold mb-1 font-mono">Économie Potentielle (sur 20 ans)*</p>
            <p class="text-2xl font-black text-neonLime font-mono">{{ store.isDiscreteMode ? '+ ••• €' : `+ ${impact20Years.toFixed(0)} €` }}</p>
            <p class="text-white/50 text-[10px] mt-1">*Projection avec intérêts composés (7% / an) si arbitré vers l'alternative.</p>
          </div>
        </div>

        <!-- Détails des actifs scannés -->
        <div v-if="results.scanned_assets.length > 0" class="space-y-3">
          <h4 class="text-white/60 text-xs font-bold uppercase tracking-wider mb-2 font-mono">Détail par ETF détecté</h4>
          <div v-for="asset in results.scanned_assets" :key="asset.isin || asset.name" 
               class="p-4 rounded-24 border transition-all"
               :class="asset.is_high_fee ? 'bg-roseAcc/5 border-roseAcc/30' : 'bg-white/5 border-white/10'">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold" 
                        :class="asset.is_high_fee ? 'bg-roseAcc/20 text-roseAcc' : 'bg-neonLime/15 text-neonLime'">
                    TER: {{ asset.ter }}%
                  </span>
                  <p class="text-sm font-bold text-white">{{ asset.name }}</p>
                </div>
                <p class="text-white/40 text-xs mt-1 font-mono">
                  {{ store.isDiscreteMode ? '•••• €' : `${asset.value.toFixed(2)} €` }} investis • Frais: {{ store.isDiscreteMode ? '••• €' : `${asset.annual_fee_euros.toFixed(2)} €/an` }}
                </p>
              </div>
              
              <div v-if="asset.alternative" class="sm:text-right bg-black/40 p-3 rounded-xl border border-neonLime/20">
                <p class="text-neonLime text-xs font-bold mb-1">💡 Alternative suggérée :</p>
                <p class="text-white text-xs font-medium">{{ asset.alternative.name }}</p>
                <p class="text-white/60 text-[10px] font-mono mt-0.5">
                  Nouveau TER: {{ asset.alternative.ter }}% (-{{ asset.alternative.savings_euros.toFixed(2) }}€/an)
                </p>
              </div>
              <div v-else class="sm:text-right">
                <span class="text-neonLime text-xs font-bold px-3 py-1 rounded-full bg-neonLime/10 border border-neonLime/20">Frais Optimisés ✓</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-6 text-white/50 text-sm">
          Aucun ETF n'a été détecté dans votre portefeuille actuel.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { getApiBase } from '../config';
import { useAppStore } from '../stores/app';

const store = useAppStore();
const isLoading = ref(false);
const results = ref(null);

const buildLocalFeeScan = () => {
  const positions = store.positions || [];
  const scanned = [];
  let totalAnnualFees = 0;
  let totalPotentialSavings = 0;

  positions.forEach(p => {
    const nameUp = (p.name || '').toUpperCase();
    const isEtf = p.asset_type === 'ETF' || nameUp.includes('ETF') || nameUp.includes('MSCI') || nameUp.includes('S&P');
    if (!isEtf) return;

    const val = (Number(p.quantity) || 0) * (Number(p.current_price) || 0);
    let ter = 0.25;
    let isHighFee = false;
    let alternative = null;

    if (nameUp.includes('CW8') || (nameUp.includes('AMUNDI') && nameUp.includes('WORLD'))) {
      ter = 0.38;
      isHighFee = true;
      const altTer = 0.25;
      const savings = val * ((ter - altTer) / 100);
      alternative = {
        name: 'iShares MSCI World Swap PEA UCITS ETF (WPEA)',
        isin: 'IE0002XZSHO1',
        ter: altTer,
        savings_euros: savings
      };
      totalPotentialSavings += savings;
    } else if (nameUp.includes('S&P 500') || nameUp.includes('ESE')) {
      ter = 0.15;
      isHighFee = false;
    } else if (nameUp.includes('NASDAQ') || nameUp.includes('PUST')) {
      ter = 0.30;
      isHighFee = true;
      const altTer = 0.20;
      const savings = val * ((ter - altTer) / 100);
      alternative = {
        name: 'Amundi S&P 500 II UCITS ETF PEA (0.15%)',
        isin: 'FR0011550185',
        ter: altTer,
        savings_euros: savings
      };
      totalPotentialSavings += savings;
    }

    const annualFee = val * (ter / 100);
    totalAnnualFees += annualFee;

    scanned.push({
      isin: p.isin || p.ticker,
      name: p.name,
      value: val,
      ter,
      annual_fee_euros: annualFee,
      is_high_fee: isHighFee,
      alternative
    });
  });

  return {
    total_annual_fees: totalAnnualFees,
    total_potential_savings: totalPotentialSavings,
    scanned_assets: scanned
  };
};

const impact20Years = computed(() => {
  if (!results.value) return 0;
  const annualSavings = results.value.total_potential_savings;
  if (annualSavings <= 0) return 0;
  const r = 0.07;
  const n = 20;
  return annualSavings * (((Math.pow(1 + r, n)) - 1) / r);
});

const scanFees = async () => {
  if (store.isDemoMode) {
    results.value = buildLocalFeeScan();
    return;
  }

  isLoading.value = true;
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/api/optimization/fee-scan`, { 
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') } 
    });
    if (res.ok) {
      const data = await res.json();
      results.value = (data.scanned_assets && data.scanned_assets.length) ? data : buildLocalFeeScan();
    } else {
      results.value = buildLocalFeeScan();
    }
  } catch (err) {
    results.value = buildLocalFeeScan();
  } finally {
    isLoading.value = false;
  }
};

watch(() => store.positions, () => {
  results.value = buildLocalFeeScan();
}, { deep: true });

onMounted(() => {
  scanFees();
});
</script>
