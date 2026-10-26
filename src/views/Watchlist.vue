<template>
  <div class="px-4 py-6 sm:p-8 max-w-[1400px] mx-auto min-h-screen space-y-6 animate-fade-up">
    <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <h1 class="text-2xl sm:text-4xl font-black text-white tracking-tight mb-1">⭐ Watchlist & Alertes Cours</h1>
        <p class="text-white/50 text-xs sm:text-sm">Surveillez vos pépites éligibles PEA et définissez vos seuils d'entrée idéaux.</p>
      </div>
    </div>

    <!-- Quick Add Bar -->
    <div class="liquid-glass-card rounded-32 p-5 sm:p-6 border border-white/10">
      <form @submit.prevent="addWatchlistItem" class="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
        <div class="sm:col-span-4">
          <label class="block text-[10px] font-mono uppercase tracking-widest text-white/40 mb-1.5">Nom de la société</label>
          <input
            v-model="newItem.name"
            type="text"
            placeholder="Ex: Hermès International"
            required
            class="w-full bg-black/40 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm text-white focus:outline-none focus:border-amberAcc"
          />
        </div>
        <div class="sm:col-span-3">
          <label class="block text-[10px] font-mono uppercase tracking-widest text-white/40 mb-1.5">Ticker Euronext</label>
          <input
            v-model="newItem.ticker"
            type="text"
            placeholder="Ex: RMS.PA"
            required
            class="w-full bg-black/40 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-mono text-white focus:outline-none focus:border-amberAcc uppercase"
          />
        </div>
        <div class="sm:col-span-3">
          <label class="block text-[10px] font-mono uppercase tracking-widest text-white/40 mb-1.5">Cours Cible d'achat (€)</label>
          <input
            v-model.number="newItem.target_price"
            type="number"
            step="0.01"
            placeholder="2050.00"
            class="w-full bg-black/40 border border-white/10 rounded-xl px-3.5 py-2.5 text-xs sm:text-sm font-mono text-amberAcc font-bold focus:outline-none focus:border-amberAcc"
          />
        </div>
        <div class="sm:col-span-2">
          <button
            type="submit"
            class="w-full py-2.5 px-4 rounded-xl bg-amberAcc hover:bg-amberAcc/90 text-black font-black text-xs transition-all cursor-pointer active:scale-95 shadow-[0_0_15px_rgba(245,158,11,0.3)]"
          >
            + Surveiller
          </button>
        </div>
      </form>

      <!-- Quick Suggestions -->
      <div class="flex flex-wrap items-center gap-2 mt-4 pt-3 border-t border-white/[0.06]">
        <span class="text-[10px] font-mono uppercase tracking-wider text-white/40">Suggestions PEA :</span>
        <button
          v-for="sug in suggestions"
          :key="sug.ticker"
          type="button"
          @click="quickAddSuggestion(sug)"
          class="px-2.5 py-1 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-[11px] text-white/70 hover:text-white transition-colors cursor-pointer"
        >
          + {{ sug.name }} ({{ sug.ticker }})
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="n in 3" :key="n" class="h-48 rounded-36 skeleton-shimmer border border-white/10"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="watchlist.length === 0" class="liquid-glass-card rounded-36 p-10 flex flex-col items-center justify-center text-center border border-white/10 mt-8">
      <span class="text-4xl mb-4">⭐</span>
      <h3 class="text-xl font-bold text-white mb-2">Votre watchlist est vide</h3>
      <p class="text-white/50 text-sm max-w-md mb-6">Utilisez le formulaire ci-dessus ou explorez les marchés avec BourseAi pour surveiller vos valeurs cibles.</p>
      <router-link to="/research" class="px-6 py-3 rounded-full liquid-glass-subtle hover:bg-white/10 text-white font-bold text-sm border border-white/15 transition-all">
        Explorer les marchés
      </router-link>
    </div>

    <!-- Watchlist Cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="item in watchlist" :key="item.id || item.ticker" class="liquid-glass-card p-5 sm:p-6 rounded-32 border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between group">
        <div class="flex justify-between items-start mb-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded bg-white/10 text-white text-[10px] font-mono font-bold">{{ item.ticker }}</span>
              <span v-if="item.sector" class="text-[10px] font-mono text-white/40">{{ item.sector }}</span>
            </div>
            <h3 class="text-lg font-bold text-white mt-1.5 line-clamp-1" :title="item.name">{{ item.name || item.ticker }}</h3>
          </div>
          <button
            @click="removeFromWatchlist(item.id || item.ticker)"
            aria-label="Retirer de la watchlist"
            class="text-white/30 hover:text-roseAcc transition-colors p-2 -mr-2 -mt-2 rounded-lg hover:bg-roseAcc/10 cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>
        
        <div class="bg-black/30 rounded-24 p-4 mt-1 border border-white/[0.05]">
          <div class="flex items-center justify-between">
            <span class="text-white/50 text-xs font-mono">Cours Cible d'Achat</span>
            <div class="flex items-center gap-1.5">
              <input 
                type="number" 
                step="0.01"
                v-model="item.target_price" 
                @blur="updateTargetPrice(item.id || item.ticker, item.target_price)"
                class="bg-transparent border-b border-white/20 text-right text-amberAcc font-bold font-mono w-24 focus:outline-none focus:border-amberAcc text-sm"
                placeholder="---"
              />
              <span class="text-amberAcc font-mono text-sm font-bold">€</span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-2 mt-4">
          <router-link :to="`/stock/${item.ticker}`" class="flex-1 text-center py-2.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white/80 hover:text-white text-xs font-bold transition-colors">
            📈 Graphique & Fiche
          </router-link>
          <button
            @click="convertToPosition(item)"
            class="px-3.5 py-2.5 rounded-full bg-neonLime/15 hover:bg-neonLime/25 border border-neonLime/30 text-neonLime text-xs font-bold transition-colors cursor-pointer"
            title="Ajouter à mon portefeuille PEA"
          >
            + Acheter
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getApiBase } from '../config';
import { useAppStore } from '../stores/app';

const store = useAppStore();
const watchlist = ref([]);
const isLoading = ref(true);

const newItem = ref({
  name: '',
  ticker: '',
  target_price: ''
});

const suggestions = [
  { name: 'Hermès International', ticker: 'RMS.PA', target_price: 2150, sector: 'Luxe' },
  { name: "L'Oréal", ticker: 'OR.PA', target_price: 380, sector: 'Cosmétiques' },
  { name: 'EssilorLuxottica', ticker: 'EL.PA', target_price: 210, sector: 'Santé' },
  { name: 'Dassault Systèmes', ticker: 'DSY.PA', target_price: 34, sector: 'Technologie' }
];

const defaultDemoWatchlist = [
  { id: 'w-1', name: 'Hermès International', ticker: 'RMS.PA', target_price: 2150, sector: 'Luxe' },
  { id: 'w-2', name: "L'Oréal", ticker: 'OR.PA', target_price: 380, sector: 'Cosmétiques' },
  { id: 'w-3', name: 'EssilorLuxottica', ticker: 'EL.PA', target_price: 215, sector: 'Santé' }
];

const saveLocalWatchlist = () => {
  localStorage.setItem('pea_local_watchlist', JSON.stringify(watchlist.value));
};

const fetchWatchlist = async () => {
  isLoading.value = true;
  if (store.isDemoMode) {
    const saved = localStorage.getItem('pea_local_watchlist');
    watchlist.value = saved ? JSON.parse(saved) : [...defaultDemoWatchlist];
    isLoading.value = false;
    return;
  }

  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/api/watchlist/`, { 
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') } 
    });
    if (res.ok) {
      watchlist.value = await res.json();
    } else {
      const saved = localStorage.getItem('pea_local_watchlist');
      watchlist.value = saved ? JSON.parse(saved) : [...defaultDemoWatchlist];
    }
  } catch (err) {
    const saved = localStorage.getItem('pea_local_watchlist');
    watchlist.value = saved ? JSON.parse(saved) : [...defaultDemoWatchlist];
  } finally {
    isLoading.value = false;
  }
};

const addWatchlistItem = async () => {
  if (!newItem.value.ticker || !newItem.value.name) return;
  const item = {
    id: `w-${Date.now()}`,
    name: newItem.value.name.trim(),
    ticker: newItem.value.ticker.trim().toUpperCase(),
    target_price: parseFloat(newItem.value.target_price) || 0
  };

  watchlist.value.unshift(item);
  saveLocalWatchlist();
  newItem.value = { name: '', ticker: '', target_price: '' };
  store.showToast(`${item.name} ajouté à la Watchlist`, 'success');

  if (!store.isDemoMode) {
    try {
      const apiBase = getApiBase();
      await fetch(`${apiBase}/api/watchlist/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '')
        },
        body: JSON.stringify(item)
      });
    } catch (e) {
      // Saved locally
    }
  }
};

const quickAddSuggestion = (sug) => {
  if (watchlist.value.some(w => w.ticker === sug.ticker)) {
    store.showToast(`${sug.name} est déjà dans votre Watchlist`, 'info');
    return;
  }
  newItem.value = { ...sug };
  addWatchlistItem();
};

const updateTargetPrice = async (id, newPrice) => {
  saveLocalWatchlist();
  store.showToast('Cours cible mis à jour', 'success');
  if (store.isDemoMode) return;
  try {
    const apiBase = getApiBase();
    await fetch(`${apiBase}/api/watchlist/${id}`, {
      method: 'PATCH',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') 
      },
      body: JSON.stringify({ target_price: parseFloat(newPrice) || 0 })
    });
  } catch (err) {
    console.error(err);
  }
};

const removeFromWatchlist = async (id) => {
  watchlist.value = watchlist.value.filter(item => (item.id || item.ticker) !== id);
  saveLocalWatchlist();
  store.showToast('Valeur retirée de la Watchlist', 'info');
  if (store.isDemoMode) return;
  try {
    const apiBase = getApiBase();
    await fetch(`${apiBase}/api/watchlist/${id}`, {
      method: 'DELETE',
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') }
    });
  } catch (err) {
    console.warn(err);
  }
};

const convertToPosition = (item) => {
  store.openAddPositionModal({
    name: item.name,
    ticker: item.ticker,
    isin: '',
    sector: item.sector || 'Actions',
    asset_type: 'Action',
    quantity: 1,
    pru: item.target_price || 100,
    current_price: item.target_price || 100
  });
};

onMounted(() => {
  fetchWatchlist();
});
</script>
