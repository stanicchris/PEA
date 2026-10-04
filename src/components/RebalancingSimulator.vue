<template>
  <div class="space-y-6">
    <div class="liquid-glass-card rounded-36 p-6 sm:p-8 border border-white/10 relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-lavender/20 blur-[80px] rounded-full pointer-events-none"></div>

      <div class="flex justify-between items-start mb-6 relative z-10">
        <div>
          <h3 class="text-xl font-black text-white flex items-center gap-2">
            <span class="text-2xl">⚖️</span> Rééquilibrage Intelligent
          </h3>
          <p class="text-white/50 text-xs mt-1 font-medium">Calculez quoi acheter avec votre prochain dépôt pour atteindre votre allocation cible sans vendre.</p>
        </div>
      </div>

      <div class="relative z-10">
        <!-- Input deposit -->
        <div class="bg-black/30 rounded-24 p-5 mb-6 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <label class="text-white/60 text-xs font-bold uppercase tracking-widest font-mono block mb-1">Montant à déposer</label>
            <div class="flex items-center gap-2">
              <input 
                type="number" 
                v-model="depositAmount"
                class="bg-transparent border-b border-white/20 text-xl font-black text-white font-mono w-32 focus:outline-none focus:border-lavender"
                placeholder="1000"
              />
              <span class="text-lavender font-bold">€</span>
            </div>
          </div>
          <button 
            @click="calculateRebalancing" 
            class="px-5 py-2.5 rounded-xl bg-lavender/10 hover:bg-lavender/20 border border-lavender/30 text-lavender font-bold text-xs transition-all active:scale-95"
          >
            Calculer les achats
          </button>
        </div>

        <!-- Targets & Results -->
        <div class="space-y-4">
          <div class="grid grid-cols-12 gap-2 px-4 mb-2">
            <div class="col-span-5 text-white/40 text-[10px] uppercase font-bold font-mono">Actif</div>
            <div class="col-span-3 text-white/40 text-[10px] uppercase font-bold font-mono text-center">Cible %</div>
            <div class="col-span-4 text-white/40 text-[10px] uppercase font-bold font-mono text-right">À Acheter</div>
          </div>

          <div v-for="asset in assets" :key="asset.ticker" class="grid grid-cols-12 gap-2 items-center liquid-glass-subtle bg-white/5 p-3 rounded-2xl border border-white/10">
            <div class="col-span-5">
              <p class="text-sm font-bold text-white truncate" :title="asset.name">{{ asset.ticker }}</p>
              <p class="text-white/40 text-[10px] font-mono">{{ asset.current_value.toFixed(2) }}€ ({{ ((asset.current_value / totalCurrentValue) * 100).toFixed(1) }}%)</p>
            </div>
            <div class="col-span-3 flex justify-center">
              <input 
                type="number" 
                v-model="asset.target_pct"
                class="bg-black/50 border border-white/10 rounded-lg w-14 sm:w-16 py-1 text-center text-xs font-mono text-white focus:border-lavender focus:outline-none"
              />
            </div>
            <div class="col-span-4 text-right">
              <span v-if="asset.to_buy_euros > 0" class="text-neonLime font-bold text-xs font-mono">+{{ asset.to_buy_euros.toFixed(2) }} €</span>
              <span v-else class="text-white/30 font-bold text-xs font-mono">0.00 €</span>
              <p v-if="asset.to_buy_shares > 0" class="text-white/50 text-[10px] font-mono mt-0.5">~{{ asset.to_buy_shares }} parts</p>
            </div>
          </div>

          <div v-if="totalTargetPct !== 100" class="text-roseAcc text-xs font-medium text-center mt-4">
            ⚠️ Le total des cibles doit être égal à 100% (Actuel : {{ totalTargetPct }}%)
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useAppStore } from '../stores/app';

const store = useAppStore();

const depositAmount = ref(1000);
const assets = ref([]);

const totalCurrentValue = computed(() => {
  return assets.value.reduce((sum, a) => sum + a.current_value, 0);
});

const totalTargetPct = computed(() => {
  return assets.value.reduce((sum, a) => sum + (parseFloat(a.target_pct) || 0), 0);
});

// Initialize assets from store
onMounted(() => {
  if (store.positions && store.positions.length > 0) {
    const total = store.positions.reduce((sum, p) => sum + (p.amount || 0), 0);
    assets.value = store.positions.map(p => {
      const val = p.amount || 0;
      const pct = total > 0 ? (val / total) * 100 : 0;
      return {
        ticker: p.ticker || p.isin,
        name: p.name,
        current_value: val,
        last_price: p.last_price || 1,
        target_pct: Math.round(pct), // Default target is current allocation
        to_buy_euros: 0,
        to_buy_shares: 0
      };
    }).sort((a, b) => b.current_value - a.current_value);
  }
});

const calculateRebalancing = () => {
  if (totalTargetPct.value !== 100) return;
  
  const totalFutureValue = totalCurrentValue.value + depositAmount.value;
  
  // Calculate gap for each asset
  let remainingDeposit = depositAmount.value;
  
  // First pass: Calculate ideal values
  assets.value.forEach(asset => {
    const targetValue = totalFutureValue * ((parseFloat(asset.target_pct) || 0) / 100);
    const shortfall = targetValue - asset.current_value;
    
    if (shortfall > 0) {
      asset.ideal_buy = shortfall;
    } else {
      asset.ideal_buy = 0;
    }
  });
  
  // Distribute remaining deposit proportionally to the shortfalls
  const totalShortfall = assets.value.reduce((sum, a) => sum + a.ideal_buy, 0);
  
  assets.value.forEach(asset => {
    if (totalShortfall > 0 && asset.ideal_buy > 0) {
      // Allocate proportionally if deposit isn't enough to cover all shortfalls
      const allocation = (asset.ideal_buy / totalShortfall) * depositAmount.value;
      // But don't allocate more than the ideal buy amount if deposit is larger than needed (which shouldn't happen mathematically, but just in case)
      asset.to_buy_euros = Math.min(allocation, asset.ideal_buy);
    } else {
      asset.to_buy_euros = 0;
    }
    
    asset.to_buy_shares = Math.floor(asset.to_buy_euros / asset.last_price);
  });
};
</script>
