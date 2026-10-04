<template>
  <div class="px-4 py-6 sm:p-8 max-w-[1400px] mx-auto min-h-screen">
    <div class="flex items-center gap-4 mb-8">
      <button 
        @click="router.back()" 
        class="liquid-glass-subtle p-3 rounded-full hover:bg-white/10 transition-colors border border-white/10"
      >
        <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
      </button>
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="px-2 py-0.5 rounded bg-neonLime/15 border border-neonLime/30 text-neonLime text-xs font-mono font-bold">{{ ticker }}</span>
          <span v-if="stockData?.sector" class="text-white/40 text-xs font-mono">{{ stockData.sector }}</span>
        </div>
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <h1 class="text-2xl sm:text-4xl font-black text-white tracking-tight">{{ stockData?.name || ticker }}</h1>
          <button 
            @click="addToWatchlist" 
            class="px-4 py-2 rounded-full liquid-glass-subtle bg-white/5 border border-white/10 hover:bg-white/10 text-white text-xs font-bold transition-all active:scale-95 flex items-center gap-2"
          >
            <span class="text-amberAcc">★</span> Ajouter à la Watchlist
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
      <div class="relative w-16 h-16 mb-6">
        <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
        <div class="absolute inset-0 border-4 border-neonLime rounded-full border-t-transparent animate-spin"></div>
      </div>
      <p class="text-white/60 animate-pulse font-medium">Chargement des données...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-roseAcc/10 border border-roseAcc/20 text-roseAcc p-6 rounded-24 text-sm font-medium">
      {{ error }}
    </div>

    <!-- Content -->
    <div v-else class="space-y-6">
      
      <!-- Top Stats & Graph Placeholder -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- Graph Placeholder -->
        <div class="lg:col-span-2 liquid-glass-card rounded-36 p-6 min-h-[300px] flex flex-col items-center justify-center border border-white/10">
          <span class="text-white/40 text-sm font-mono mb-2">Graphique interactif</span>
          <p class="text-white/20 text-xs text-center">(Intégration ECharts prévue pour la v1.1)</p>
          <div v-if="stockData?.metrics?.price" class="mt-8 text-center">
            <p class="text-white/50 text-xs uppercase tracking-widest mb-2 font-mono">Dernier Cours</p>
            <p class="text-4xl font-black text-white font-mono">{{ stockData.metrics.price.toFixed(2) }} €</p>
          </div>
        </div>

        <!-- BourseAi Score & Quick Stats -->
        <div class="space-y-6">
          <div class="liquid-glass-card rounded-36 p-6 border border-white/10">
            <h3 class="text-white/50 text-xs font-bold uppercase tracking-widest mb-6 font-mono">Analyse BourseAi</h3>
            <div class="flex items-center gap-6">
              <div class="relative w-24 h-24 shrink-0 flex items-center justify-center rounded-full shadow-lg" 
                  :style="`background: conic-gradient(${stockData?.score_percent >= 60 ? '#A3E635' : (stockData?.score_percent >= 40 ? '#F59E0B' : '#F43F5E')} ${stockData?.score_percent}%, rgba(255,255,255,0.05) 0);`">
                <div class="absolute inset-2 bg-[#0C1017] rounded-full flex items-center justify-center flex-col shadow-inner">
                  <span class="text-3xl font-black" :class="stockData?.score_percent >= 60 ? 'text-neonLime' : (stockData?.score_percent >= 40 ? 'text-amberAcc' : 'text-roseAcc')">{{ stockData?.score_percent }}%</span>
                </div>
              </div>
              <div>
                <p class="text-lg font-black" :class="stockData?.should_invest ? 'text-neonLime' : 'text-amberAcc'">
                  {{ stockData?.should_invest ? 'ACHAT' : 'CONSERVER' }}
                </p>
                <p class="text-white/40 text-xs mt-1">{{ stockData?.source }}</p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="liquid-glass-subtle rounded-24 p-4 border border-white/10">
              <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Objectif</p>
              <p class="text-lg font-bold text-neonLime font-mono">{{ stockData?.metrics?.target_price?.toFixed(2) || '--' }} €</p>
            </div>
            <div class="liquid-glass-subtle rounded-24 p-4 border border-white/10">
              <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Rendement</p>
              <p class="text-lg font-bold text-lavender font-mono">{{ stockData?.metrics?.div_yield?.toFixed(2) || '0.00' }} %</p>
            </div>
          </div>
        </div>

      </div>

      <!-- Synthesis -->
      <div class="liquid-glass-card rounded-36 p-6 border border-white/10">
        <h3 class="text-white/50 text-xs font-bold uppercase tracking-widest mb-4 font-mono">Synthèse Fondamentale</h3>
        <p class="text-white/90 leading-relaxed text-sm">
          {{ stockData?.summary }}
        </p>
      </div>

      <!-- Pros / Cons -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-neonLime/10 border border-neonLime/20 rounded-36 p-6">
          <h4 class="text-neonLime font-bold mb-4 flex items-center gap-2">
            <span>↗</span> Points Forts
          </h4>
          <div class="text-white/80 text-sm leading-relaxed space-y-2">
            <p v-for="(pro, i) in (stockData?.pros || '').split('•')" :key="'p'+i" v-show="pro.trim()" class="flex items-start gap-2">
               <span class="text-neonLime mt-0.5">&bull;</span> {{ pro.trim() }}
            </p>
          </div>
        </div>
        
        <div class="bg-roseAcc/10 border border-roseAcc/20 rounded-36 p-6">
          <h4 class="text-roseAcc font-bold mb-4 flex items-center gap-2">
            <span>↘</span> Risques
          </h4>
          <div class="text-white/80 text-sm leading-relaxed space-y-2">
            <p v-for="(con, i) in (stockData?.cons || '').split('•')" :key="'c'+i" v-show="con.trim()" class="flex items-start gap-2">
               <span class="text-roseAcc mt-0.5">&bull;</span> {{ con.trim() }}
            </p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getApiBase } from '../config';

const route = useRoute();
const router = useRouter();

const ticker = computed(() => route.params.ticker);
const stockData = ref(null);
const isLoading = ref(true);
const error = ref(null);

const addToWatchlist = async () => {
  try {
    const apiBase = getApiBase();
    const res = await fetch(`${apiBase}/api/watchlist/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') 
      },
      body: JSON.stringify({
        ticker: ticker.value,
        name: stockData.value?.name,
        target_price: stockData.value?.metrics?.target_price || null
      })
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Erreur d'ajout à la watchlist");
    }
    alert("Action ajoutée à la watchlist !");
  } catch (err) {
    alert(err.message);
  }
};

onMounted(async () => {
  try {
    const apiBase = getApiBase();
    // We fetch the same AI analysis as AssetInspectorModal to populate the page for now
    // In v1.1, we'd add more endpoints for graph data, etc.
    const res = await fetch(`${apiBase}/api/stock/analyze/${ticker.value}`, { 
      headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') } 
    });
    if (!res.ok) throw new Error("Impossible de charger les détails de l'action.");
    stockData.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
});
</script>
