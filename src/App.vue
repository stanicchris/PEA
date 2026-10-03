<template>
  <div class="min-h-screen bg-[#080A0E] text-[#F8FAFC] font-sans p-3 sm:p-6 lg:p-8 selection:bg-neonLime selection:text-black">
    <!-- LOGIN SCREEN -->
    <LoginWidget v-if="!userId" @login-success="onLoginSuccess" />

    <!-- MAIN CHASSIS (Rounded 48px Master Container) -->
    <div v-else class="max-w-[1680px] mx-auto bg-[#0C0E12] border border-white/[0.06] rounded-48 p-4 sm:p-6 lg:p-8 shadow-2xl relative overflow-hidden flex flex-col min-h-[92vh]">
      
      <!-- TOP NAVIGATION BAR (Pill Style from interface.png) -->
      <header class="flex items-center justify-between mb-8 gap-4 flex-wrap">
        <!-- Left: Menu + Brand Logo -->
        <div class="flex items-center gap-3">
          <button class="w-10 h-10 rounded-2xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] flex items-center justify-center text-white/70 hover:text-white transition-all">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-neonLime flex items-center justify-center font-black text-black text-lg shadow-[0_0_20px_rgba(163,230,53,0.35)]">
              R
            </div>
            <span class="font-extrabold text-xl tracking-tight text-white">Rivlo / PEA</span>
          </div>
        </div>

        <!-- Center: Floating Pill Navigation Tabs -->
        <nav class="hidden md:flex items-center bg-[#16191E] border border-white/[0.08] rounded-full p-1.5 shadow-lg">
          <button 
            @click="activeTab = 'dashboard'"
            :class="activeTab === 'dashboard' ? 'bg-white/[0.12] text-white shadow-sm font-bold' : 'text-white/50 hover:text-white font-medium'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2"
          >
            <span class="text-sm">⊞</span>
            <span>Dashboard</span>
          </button>

          <button 
            @click="activeTab = 'analytics'"
            :class="activeTab === 'analytics' ? 'bg-white/[0.12] text-white shadow-sm font-bold' : 'text-white/50 hover:text-white font-medium'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2"
          >
            <span class="text-sm">📊</span>
            <span>Analytics</span>
          </button>

          <button 
            @click="activeTab = 'reports'"
            :class="activeTab === 'reports' ? 'bg-white/[0.12] text-white shadow-sm font-bold' : 'text-white/50 hover:text-white font-medium'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2"
          >
            <span class="text-sm">📁</span>
            <span>Reports</span>
          </button>

          <button 
            @click="isSettingsOpen = true"
            class="px-5 py-2 rounded-full text-xs text-white/50 hover:text-white transition-all flex items-center gap-2 font-medium"
          >
            <span class="text-sm">⚙️</span>
            <span>Settings</span>
          </button>
        </nav>

        <!-- Right: Actions & User Avatar -->
        <div class="flex items-center gap-3">
          <!-- Search Button -->
          <div class="relative hidden sm:block">
            <input 
              type="text" 
              v-model="searchQuery" 
              @keyup.enter="handleSearch"
              placeholder="Rechercher (ex: LVMH, AAPL)..."
              class="w-48 lg:w-60 bg-white/[0.04] border border-white/[0.08] rounded-full pl-9 pr-4 py-2 text-xs text-white placeholder-white/30 focus:outline-none focus:border-neonLime transition-all"
            />
            <svg class="w-3.5 h-3.5 text-white/40 absolute left-3.5 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>

          <!-- Notification Bell -->
          <button class="w-10 h-10 rounded-2xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] flex items-center justify-center text-white/70 hover:text-white transition-all relative">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span class="w-2 h-2 rounded-full bg-roseAcc absolute top-2.5 right-2.5"></span>
          </button>

          <!-- User Avatar & Logout Trigger -->
          <div class="flex items-center gap-2">
            <div 
              @click="logout" 
              class="w-10 h-10 rounded-full border-2 border-neonLime/40 bg-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-md cursor-pointer hover:opacity-80 transition-opacity"
              :title="'Connecté en tant que ' + username + ' (Cliquez pour déconnecter)'"
            >
              {{ username.substring(0, 2).toUpperCase() || 'CH' }}
            </div>
          </div>
        </div>
      </header>

      <!-- EMPTY STATE -->
      <div v-if="!positions.length && !isLoading" class="p-16 text-center glass-card rounded-36 border border-white/[0.08] my-auto">
        <div class="w-16 h-16 rounded-full bg-neonLime/10 text-neonLime flex items-center justify-center mx-auto mb-4 text-2xl">
          📈
        </div>
        <h2 class="text-2xl font-bold mb-2">Portefeuille en attente</h2>
        <p class="text-white/40 text-sm max-w-md mx-auto mb-6">Importez votre relevé de compte Boursorama au format CSV pour afficher votre terminal complet.</p>
        <button @click="isSettingsOpen = true" class="bg-neonLime text-black font-extrabold text-sm px-6 py-3 rounded-full shadow-lg hover:bg-neonLimeHover transition-all">
          Importer un CSV
        </button>
      </div>

      <!-- MAIN DASHBOARD CONTENT -->
      <div v-else class="space-y-6">
        
        <!-- ÉTAGE SUPÉRIEUR (Grid 4 Colonnes - Inspiré d'interface.png) -->
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          <!-- Carte 1 : Total Balance (Hero) -->
          <HeroSection 
            :summary="summary" 
            :positions="positions" 
            :isLoading="isLoading" 
            :isRefreshing="isRefreshing"
            @refresh="refreshData"
            @open-settings="isSettingsOpen = true"
          />

          <!-- Carte 2 : Transfer / Asset Allocation (Concentric Rings) -->
          <AllocationChart 
            :positions="positions" 
            :summary="summary" 
            :isLoading="isLoading" 
          />

          <!-- Carte 3 : Financial Health (Equalizer Soundwave & Sentiment) -->
          <FinancialHealthCard 
            :summary="summary" 
            :weather="weather" 
            :isLoading="isLoading" 
          />

          <!-- Carte 4 : Stack Fiscale & Plafond PEA 150k€ -->
          <FiscalStackCard 
            :summary="summary" 
            @open-tax-sim="isSettingsOpen = true"
          />
        </div>

        <!-- ÉTAGE INFÉRIEUR (Grid 3 Colonnes Asymétrique - Inspiré d'interface.png) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <!-- Carte 5 : Analytics Performance (Rubans Empilés 2024-2026) -->
          <div class="lg:col-span-5">
            <AnalyticsCharts 
              :history="history" 
              :summary="summary" 
              :positions="positions" 
              :isLoading="isLoading" 
            />
          </div>

          <!-- Carte 6 : Transaction Count / Radar Movers (Barres LED + Avatars) -->
          <div class="lg:col-span-4">
            <TopMovers 
              :positions="positions" 
              :summary="summary" 
              :isLoading="isLoading" 
            />
          </div>

          <!-- Carte 7 : Méga-Carte Groq AI (Vert Néon Intégral) -->
          <div class="lg:col-span-3">
            <GroqAiHighlightCard 
              :isLoading="isAiLoading" 
              @trigger-ai="isAiAdvisorOpen = true"
            />
          </div>
        </div>

        <!-- SECTION BASSE : TABLEAU PRO DES POSITIONS -->
        <PositionsTable :positions="positions" />

      </div>

      <!-- MODALES -->
      <SettingsModal 
        :isOpen="isSettingsOpen" 
        :userId="userId" 
        :currentCash="cashAmount" 
        @close="isSettingsOpen = false"
        @refresh="fetchData"
      />

      <AssetInspectorModal 
        :isOpen="isSearchModalOpen" 
        :asset="searchAsset" 
        @close="isSearchModalOpen = false" 
      />

      <AiAdvisorWidget 
        :isOpen="isAiAdvisorOpen" 
        :userId="userId" 
        @close="isAiAdvisorOpen = false" 
      />

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getApiBase } from './config';

import LoginWidget from './components/LoginWidget.vue';
import HeroSection from './components/HeroSection.vue';
import AllocationChart from './components/AllocationChart.vue';
import FinancialHealthCard from './components/FinancialHealthCard.vue';
import FiscalStackCard from './components/FiscalStackCard.vue';
import AnalyticsCharts from './components/AnalyticsCharts.vue';
import TopMovers from './components/TopMovers.vue';
import GroqAiHighlightCard from './components/GroqAiHighlightCard.vue';
import PositionsTable from './components/PositionsTable.vue';
import AssetInspectorModal from './components/AssetInspectorModal.vue';
import SettingsModal from './components/SettingsModal.vue';
import AiAdvisorWidget from './components/AiAdvisorWidget.vue';

const userId = ref(localStorage.getItem('pea_user_id') || null);
const username = ref(localStorage.getItem('pea_username') || '');
const activeTab = ref('dashboard');

const isLoading = ref(false);
const isRefreshing = ref(false);
const isAiLoading = ref(false);
const isSettingsOpen = ref(false);
const isAiAdvisorOpen = ref(false);

const summary = ref(null);
const positions = ref([]);
const history = ref([]);
const weather = ref(null);

// Search Feature
const searchQuery = ref('');
const isSearchModalOpen = ref(false);
const searchAsset = ref(null);

const cashAmount = computed(() => {
  if (!summary.value) return 0;
  const titres = positions.value.reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
  const diff = (summary.value.total_value || 0) - titres;
  return diff > 0 ? diff : 0;
});

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
  localStorage.removeItem('pea_access_token');
};

const fetchData = async () => {
  if (!userId.value) return;
  const apiBase = getApiBase();
  if (!apiBase) return;
  isLoading.value = true;
  try {
    const token = localStorage.getItem('pea_access_token');
    const authHeaders = token ? { Authorization: 'Bearer ' + token } : {};

    const [summaryRes, positionsRes, historyRes, weatherRes] = await Promise.all([
      fetch(`${apiBase}/api/portfolio/summary?user_id=${userId.value}`, { headers: authHeaders }),
      fetch(`${apiBase}/api/portfolio/positions?user_id=${userId.value}`, { headers: authHeaders }),
      fetch(`${apiBase}/api/portfolio/history?user_id=${userId.value}`, { headers: authHeaders }).catch(() => null),
      fetch(`${apiBase}/api/portfolio/weather?user_id=${userId.value}`, { headers: authHeaders }).catch(() => null)
    ]);

    if (summaryRes.ok) summary.value = await summaryRes.json();
    if (positionsRes.ok) {
      const posData = await positionsRes.json();
      positions.value = posData.positions || [];
    }
    if (historyRes && historyRes.ok) {
      const histData = await historyRes.json();
      history.value = histData.history || [];
    }
    if (weatherRes && weatherRes.ok) {
      weather.value = await weatherRes.json();
    }
  } catch (error) {
    console.error("Erreur lors de la récupération des données :", error);
  } finally {
    isLoading.value = false;
  }
};

const refreshData = async () => {
  if (!userId.value) return;
  const apiBase = getApiBase();
  if (!apiBase) return;
  isRefreshing.value = true;
  try {
    const token = localStorage.getItem('pea_access_token');
    await fetch(`${apiBase}/api/portfolio/refresh?user_id=${userId.value}`, {
      method: 'POST',
      headers: token ? { Authorization: 'Bearer ' + token } : {}
    });
    await fetchData();
  } catch (error) {
    console.error("Erreur lors du rafraîchissement des cours en direct :", error);
  } finally {
    isRefreshing.value = false;
  }
};

onMounted(() => {
  if (userId.value) fetchData();
});
</script>
