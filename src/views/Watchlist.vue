<template>
  <div class="px-4 py-6 sm:p-8 max-w-[1400px] mx-auto min-h-screen">
    <div class="mb-8">
      <h1 class="text-3xl sm:text-4xl font-black text-white tracking-tight mb-2">Watchlist & Alertes</h1>
      <p class="text-white/50 text-sm">Surveillez vos actions favorites et configurez vos cours cibles d'achat.</p>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <div class="relative w-12 h-12 mb-4">
        <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-amberAcc rounded-full border-t-transparent animate-spin"></div>
      </div>
      <p class="text-white/60 animate-pulse text-sm font-medium">Chargement de votre watchlist...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-roseAcc/10 border border-roseAcc/20 text-roseAcc p-6 rounded-24 text-sm font-medium">
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="watchlist.length === 0" class="liquid-glass-card rounded-36 p-10 flex flex-col items-center justify-center text-center border border-white/10 mt-8">
      <span class="text-4xl mb-4">⭐</span>
      <h3 class="text-xl font-bold text-white mb-2">Votre watchlist est vide</h3>
      <p class="text-white/50 text-sm max-w-md mb-6">Recherchez une action dans l'outil BourseAi ou utilisez le scanner pour découvrir de nouvelles opportunités, puis ajoutez-les ici.</p>
      <router-link to="/research" class="px-6 py-3 rounded-full liquid-glass-subtle hover:bg-white/10 text-white font-bold text-sm border border-white/15 transition-all">
        Explorer les marchés
      </router-link>
    </div>

    <!-- Watchlist Table/Cards -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="item in watchlist" :key="item.id" class="liquid-glass-subtle p-5 rounded-36 border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between">
        <div class="flex justify-between items-start mb-4">
          <div>
            <span class="px-2 py-0.5 rounded bg-white/10 text-white text-[10px] font-mono font-bold">{{ item.ticker }}</span>
            <h3 class="text-lg font-bold text-white mt-1 line-clamp-1" :title="item.name">{{ item.name || item.ticker }}</h3>
          </div>
          <button @click="removeFromWatchlist(item.id)" class="text-white/30 hover:text-roseAcc transition-colors p-2 -mr-2 -mt-2">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
          </button>
        </div>
        
        <div class="bg-black/30 rounded-24 p-4 mt-2">
          <div class="flex items-center justify-between">
            <span class="text-white/50 text-xs font-mono">Cours Cible</span>
            <div class="flex items-center gap-2">
              <input 
                type="number" 
                v-model="item.target_price" 
                @blur="updateTargetPrice(item.id, item.target_price)"
                class="bg-transparent border-b border-white/20 text-right text-amberAcc font-bold font-mono w-20 focus:outline-none focus:border-amberAcc"
                placeholder="---"
              />
              <span class="text-amberAcc font-mono text-sm">€</span>
            </div>
          </div>
        </div>
        
        <router-link :to="`/stock/${item.ticker}`" class="mt-4 w-full text-center py-2 rounded-full border border-white/10 text-white/70 hover:text-white hover:bg-white/5 text-xs font-bold transition-colors">
          Voir la fiche
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getApiBase } from '../config';

const watchlist = ref([]);
const isLoading = ref(true);
const error = ref(null);

const fetchWatchlist = async () => {
  isLoading.value = true;
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/api/watchlist/`, { 
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') } 
    });
    if (!res.ok) throw new Error("Erreur de récupération de la watchlist");
    watchlist.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

const updateTargetPrice = async (id, newPrice) => {
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
  if (!confirm("Retirer cette action de la watchlist ?")) return;
  try {
    const apiBase = getApiBase();
    await fetch(`${apiBase}/api/watchlist/${id}`, {
      method: 'DELETE',
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') }
    });
    watchlist.value = watchlist.value.filter(item => item.id !== id);
  } catch (err) {
    alert(err.message);
  }
};

onMounted(() => {
  fetchWatchlist();
});
</script>
