<template>
  <div class="glass-card rounded-36 p-6 md:p-8 border border-white/[0.08] specular-highlight relative overflow-hidden group">
    <div class="absolute inset-0 bg-gradient-to-br from-roseAcc/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
    
    <div class="flex items-center justify-between mb-8 relative z-10">
      <div>
        <h3 class="text-xl font-bold text-white flex items-center gap-3">
          <span class="w-10 h-10 rounded-2xl bg-roseAcc/10 text-roseAcc flex items-center justify-center border border-roseAcc/20 shadow-[0_0_15px_rgba(244,63,94,0.15)]">🔍</span>
          Scanner de Frais (TER)
        </h3>
        <p class="text-white/40 text-xs mt-1 font-medium">Détecte les ETFs chargés en frais de gestion et propose des alternatives PEA moins chères.</p>
      </div>
      
      <div class="text-right">
        <p class="text-xs text-white/40 uppercase tracking-widest font-mono font-bold mb-1">Économies Potentielles</p>
        <p class="text-2xl font-black text-roseAcc tabular-nums tracking-tight">
          {{ store.isDiscreteMode ? '••• €' : formatCurrency(totalSavings) }} / an
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="py-12 flex justify-center items-center">
      <div class="w-8 h-8 rounded-full border-2 border-roseAcc border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="!scannedAssets.length" class="py-12 text-center text-white/40 border border-dashed border-white/10 rounded-2xl">
      <span class="text-2xl mb-2 block opacity-50">✨</span>
      <p class="text-sm font-medium">Votre portefeuille est parfaitement optimisé.</p>
    </div>

    <div v-else class="space-y-4 relative z-10">
      <div 
        v-for="(asset, idx) in scannedAssets" 
        :key="idx"
        class="liquid-glass-subtle p-4 rounded-2xl border border-white/5 transition-all flex flex-col gap-3"
        :class="asset.is_high_fee ? 'hover:border-roseAcc/30' : 'hover:border-white/20'"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <h4 class="font-bold text-white text-sm sm:text-base line-clamp-1">{{ asset.name }}</h4>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/70 border border-white/10">{{ asset.isin }}</span>
              <span 
                class="text-[10px] font-bold px-2 py-0.5 rounded"
                :class="asset.is_high_fee ? 'bg-roseAcc/20 text-roseAcc' : 'bg-neonLime/20 text-neonLime'"
              >
                TER: {{ asset.ter }}%
              </span>
            </div>
          </div>

          <div class="text-right shrink-0">
            <p class="font-bold text-white text-sm tabular-nums">
              Frais actuels : {{ store.isDiscreteMode ? '••• €' : formatCurrency(asset.annual_fee_euros) }}/an
            </p>
          </div>
        </div>

        <div v-if="asset.is_high_fee && asset.alternative" class="mt-2 p-3 bg-white/5 rounded-xl border border-roseAcc/20 flex flex-col sm:flex-row justify-between items-center gap-3">
          <div class="flex-1">
            <p class="text-xs text-white/70">
              <span class="font-bold text-neonLime">Alternative suggérée :</span> {{ asset.alternative.name }}
            </p>
            <p class="text-[10px] text-white/50 font-mono mt-0.5">ISIN: {{ asset.alternative.isin }} | Nouveau TER: {{ asset.alternative.ter }}%</p>
          </div>
          <div class="text-right bg-neonLime/10 px-3 py-1.5 rounded-lg border border-neonLime/20 shrink-0">
            <p class="text-xs font-bold text-neonLime text-center">Gain estimé</p>
            <p class="text-sm font-black text-neonLime">+{{ store.isDiscreteMode ? '••• €' : formatCurrency(asset.alternative.savings_euros) }}/an</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { getApiBase } from '../config';
import { useAppStore } from '../stores/app';

const props = defineProps({
  userId: {
    type: String,
    required: false
  }
});

const store = useAppStore();
const isLoading = ref(false);
const scannedAssets = ref([]);
const totalSavings = ref(0);

const currencyFmt = new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' });
const formatCurrency = (val) => currencyFmt.format(val || 0);

const computeLocalFallback = () => {
  const list = [];
  let savings = 0;
  (store.positions || []).forEach(p => {
    const nameUp = (p.name || '').toUpperCase();
    const isEtf = p.asset_type === 'ETF' || nameUp.includes('ETF') || nameUp.includes('MSCI') || nameUp.includes('S&P');
    if (!isEtf) return;
    const val = (Number(p.quantity) || 0) * (Number(p.current_price) || 0);
    if (nameUp.includes('CW8') || (nameUp.includes('AMUNDI') && nameUp.includes('WORLD'))) {
      const ter = 0.38;
      const altTer = 0.25;
      const sav = val * ((ter - altTer) / 100);
      savings += sav;
      list.push({
        name: p.name,
        isin: p.isin || p.ticker,
        ter,
        annual_fee_euros: val * (ter / 100),
        is_high_fee: true,
        alternative: {
          name: 'iShares MSCI World Swap PEA UCITS ETF (WPEA)',
          isin: 'IE0002XZSHO1',
          ter: altTer,
          savings_euros: sav
        }
      });
    } else {
      const ter = 0.15;
      list.push({
        name: p.name,
        isin: p.isin || p.ticker,
        ter,
        annual_fee_euros: val * (ter / 100),
        is_high_fee: false,
        alternative: null
      });
    }
  });
  scannedAssets.value = list;
  totalSavings.value = savings;
};

const fetchFees = async () => {
  if (store.isDemoMode) {
    computeLocalFallback();
    return;
  }

  const uid = props.userId || localStorage.getItem('pea_user_id') || '';
  const token = localStorage.getItem('pea_access_token');
  const headers = token ? { Authorization: 'Bearer ' + token } : {};
  
  isLoading.value = true;
  try {
    const url = uid ? `${getApiBase()}/api/optimization/fee-scan?user_id=${uid}` : `${getApiBase()}/api/optimization/fee-scan`;
    const res = await fetch(url, { headers });
    if (res.ok) {
      const data = await res.json();
      if (data.scanned_assets && data.scanned_assets.length) {
        scannedAssets.value = data.scanned_assets;
        totalSavings.value = data.total_potential_savings || 0;
      } else {
        computeLocalFallback();
      }
    } else {
      computeLocalFallback();
    }
  } catch (e) {
    computeLocalFallback();
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.userId, fetchFees);
onMounted(fetchFees);
</script>
