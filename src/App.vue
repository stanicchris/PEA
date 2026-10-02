<template>
  <div>
    <!-- LOGIN SCREEN -->
    <LoginWidget v-if="!userId" @login-success="onLoginSuccess" />

    <!-- MAIN DASHBOARD -->
    <div v-else class="min-h-screen bg-[#0E1117] text-[#F8FAFC] font-sans flex flex-col md:flex-row">
      <!-- Header Mobile -->
      <header class="md:hidden glass p-4 flex justify-between items-center sticky top-0 z-50">
        <div class="font-bold text-xl tracking-tight">PEA Tracker</div>
        <button @click="logout" class="text-white/50 hover:text-rose-400 text-sm font-semibold">Déconnexion</button>
      </header>

      <!-- Sidebar Desktop -->
      <aside class="fixed inset-y-0 left-0 z-40 w-20 glass flex-col items-center py-6 hidden md:flex border-r border-white/5 justify-between">
        <div class="flex flex-col items-center gap-6">
          <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center font-bold text-lg shadow-[0_0_15px_rgba(37,99,235,0.4)]">P</div>
          <button @click="isSettingsOpen = true" class="w-10 h-10 rounded-xl bg-white/5 hover:bg-blue-500/20 hover:text-blue-400 flex items-center justify-center transition-all text-white/50" title="Paramètres">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
          </button>
        </div>
        <button @click="logout" class="w-10 h-10 rounded-xl bg-white/5 hover:bg-rose-500/20 hover:text-rose-400 flex items-center justify-center transition-all text-white/50" title="Déconnexion">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" /></svg>
        </button>
      </aside>

      <main class="flex-1 p-4 md:p-8 md:ml-20 overflow-y-auto w-full max-w-[1600px] mx-auto">
        <header class="mb-8 hidden md:flex justify-between items-end">
          <div>
            <h1 class="text-3xl font-bold tracking-tight">Bonjour, {{ username }} 👋</h1>
            <p class="text-white/50 mt-1">Live data from Supabase & Groq AI</p>
          </div>
                      <div class="flex gap-4 items-center">
              <!-- Search Bar -->
              <div class="relative hidden lg:block">
                <input type="text" v-model="searchQuery" @keyup.enter="handleSearch" placeholder="Rechercher (ex: AAPL, LVMH)" class="bg-[#151921] border border-white/10 rounded-xl px-4 py-2.5 pl-10 text-sm text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 w-64 transition-all shadow-inner placeholder-white/30" />
                <svg class="w-4 h-4 text-white/50 absolute left-3.5 top-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              </div>
            <button @click="isSettingsOpen = true" class="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-5 py-2.5 rounded-xl font-semibold transition-all shadow-lg flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
              Import CSV
            </button>
            <button @click="refreshData" :disabled="isRefreshing" class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl font-semibold transition-all shadow-lg shadow-blue-600/20 flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" :class="isRefreshing ? 'animate-spin' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              {{ isRefreshing ? 'Fetching...' : 'Refresh Live Market' }}
            </button>
          </div>
        </header>

        <div v-if="!positions.length && !isLoading" class="p-12 text-center glass rounded-3xl border border-white/5">
          <h2 class="text-2xl font-bold mb-4">Portefeuille vide</h2>
          <p class="text-white/50">Aucune donnée trouvée. Cliquez sur "Import CSV" pour démarrer.</p>
        </div>

        <!-- Bento Grid Layout -->
        <div v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            <div class="md:col-span-1 lg:col-span-2"><HeroSection :summary="summary" :isLoading="isLoading" /></div>
            <div class="md:col-span-1 lg:col-span-1"><KpiGrid :summary="summary" :isLoading="isLoading" /></div>
            
            <div class="md:col-span-2 lg:col-span-3"><HistoryChart :history="history" :isLoading="isLoading" /></div>
            
            <div class="md:col-span-1 lg:col-span-2"><TopMovers :positions="positions" :isLoading="isLoading" /></div>
            <div class="md:col-span-1 lg:col-span-1"><AnalyticsCharts :positions="positions" :isLoading="isLoading" /></div>
            
            <div class="md:col-span-2 lg:col-span-3"><AiAdvisorWidget :userId="userId" /></div>
            
            <div class="md:col-span-2 lg:col-span-2"><PeaTaxes :summary="summary" /></div>
            <div class="md:col-span-1 lg:col-span-1"><AllocationChart :positions="positions" :summary="summary" :isLoading="isLoading" /></div>
          </div>
          
          <AdvancedCharts :positions="positions" :totalValue="summary?.total_value" />
          <PositionsTable :positions="positions" />
        </div>
      </main>

      <SettingsModal 
        :isOpen="isSettingsOpen" 
        :userId="userId" 
        :currentCash="summary?.total_value - summary?.total_invested - summary?.global_performance_value || 0" 
        @close="isSettingsOpen = false"
        @refresh="fetchData"
      />

      <!-- Search Modal -->
      <AssetInspectorModal 
        :isOpen="isSearchModalOpen" 
        :asset="searchAsset" 
        @close="isSearchModalOpen = false" 
      />
    </div>
  </div>
</template>

<script setup>
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
import { ref, onMounted } from 'vue';
import LoginWidget from './components/LoginWidget.vue';
import AssetInspectorModal from './components/AssetInspectorModal.vue';
import SettingsModal from './components/SettingsModal.vue';
import HeroSection from './components/HeroSection.vue';
import KpiGrid from './components/KpiGrid.vue';
import HistoryChart from './components/HistoryChart.vue';
import TopMovers from './components/TopMovers.vue';
import AnalyticsCharts from './components/AnalyticsCharts.vue';
import PeaTaxes from './components/PeaTaxes.vue';
import AllocationChart from './components/AllocationChart.vue';
import AiAdvisorWidget from './components/AiAdvisorWidget.vue';
import AdvancedCharts from './components/AdvancedCharts.vue';
import PositionsTable from './components/PositionsTable.vue';

const userId = ref(localStorage.getItem('pea_user_id') || null);
const username = ref(localStorage.getItem('pea_username') || '');

const isLoading = ref(false);
const isRefreshing = ref(false);
const isSettingsOpen = ref(false);
const summary = ref(null);
const positions = ref([]);
const history = ref([]);

// Search Feature
const searchQuery = ref('');
const isSearchModalOpen = ref(false);
const searchAsset = ref(null);

const handleSearch = () => {
  const q = searchQuery.value.trim();
  if (!q) return;
  searchAsset.value = { name: q, ticker: q, sector: "Recherche Libre" };
  isSearchModalOpen.value = true;
  searchQuery.value = '';
};

const onLoginSuccess = (userData) => {
  userId.value = userData.userId;
  username.value = userData.username;
  localStorage.setItem('pea_user_id', userData.userId);
  localStorage.setItem('pea_username', userData.username);
  fetchData();
};

const logout = () => {
  userId.value = null;
  username.value = '';
  localStorage.removeItem('pea_user_id');
  localStorage.removeItem('pea_username');
};

const fetchData = async () => {
  if (!userId.value) return;
  isLoading.value = true;
  try {
    const [summaryRes, positionsRes, historyRes] = await Promise.all([
      fetch(`${API_BASE}/api/portfolio/summary?user_id=${userId.value}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } }),
      fetch(`${API_BASE}/api/portfolio/positions?user_id=${userId.value}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } }),
      fetch(`${API_BASE}/api/portfolio/history?user_id=${userId.value}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } })
    ]);
    summary.value = await summaryRes.json();
    const posData = await positionsRes.json();
    positions.value = posData.positions;
    
    if (historyRes.ok) {
      const histData = await historyRes.json();
      history.value = histData.history || [];
    }
  } catch (error) {
    console.error("Error fetching API data:", error);
  } finally {
    isLoading.value = false;
  }
};

const refreshData = async () => {
  if (!userId.value) return;
  isRefreshing.value = true;
  try {
    await fetch(`${API_BASE}/api/portfolio/refresh?user_id=${userId.value}`, { method: 'POST', headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } });
    // Fetch data immediately after sync finishes
    await fetchData();
  } catch (error) {
    console.error("Error triggering refresh:", error);
  } finally {
    isRefreshing.value = false;
  }
};

onMounted(() => {
  if (userId.value) fetchData();
});
</script>

<style>
body { background-color: #0E1117; color: #F8FAFC; margin: 0; }
.glass {
  background-color: rgba(21, 25, 33, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
</style>
