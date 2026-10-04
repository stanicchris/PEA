<template>
  <div class="min-h-screen bg-[#05070A] text-[#F8FAFC] font-sans p-3 sm:p-6 lg:p-8 selection:bg-neonLime selection:text-black relative overflow-x-hidden">
    <!-- Ambient Liquid Glass Caustics Mesh -->
    <div class="ambient-glow-mesh">
      <div class="ambient-glow-1"></div>
      <div class="ambient-glow-2"></div>
      <div class="ambient-glow-3"></div>
    </div>

    <!-- LOGIN SCREEN -->
    <LoginWidget v-if="!userId" @login-success="onLoginSuccess" class="relative z-10" />

    <!-- MAIN CHASSIS (Rounded 48px Master Container with Liquid Glass) -->
    <div v-else class="max-w-[1680px] mx-auto liquid-glass-chassis rounded-48 p-4 sm:p-6 lg:p-8 relative z-10 overflow-hidden flex flex-col min-h-[92vh] specular-highlight">
      
      <!-- TOP NAVIGATION BAR (Liquid Glass Pill Style) -->
      <header class="flex items-center justify-between mb-8 gap-4 flex-wrap">
        <!-- Left: Menu + Brand Logo -->
        <div class="flex items-center gap-3">
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all cursor-pointer hover:border-white/20 active:scale-95"
            title="Menu de navigation mobile"
            aria-label="Menu"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <div class="flex items-center gap-2.5 cursor-pointer group" @click="activeTab = 'dashboard'">
            <div class="w-9 h-9 rounded-xl bg-neonLime flex items-center justify-center font-black text-black text-lg shadow-[0_0_25px_rgba(163,230,53,0.4)] group-hover:scale-105 transition-transform">
              R
            </div>
            <div class="flex flex-col">
              <span class="font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5">
                Rivlo <span class="text-neonLime font-light">/</span> <span class="text-white/80 font-semibold text-base">PEA</span>
              </span>
            </div>
          </div>
        </div>

        <!-- MOBILE SLIDE-OVER DRAWER -->
        <div v-if="isMobileMenuOpen" class="fixed inset-0 z-[120] flex md:hidden">
          <!-- Backdrop -->
          <div class="fixed inset-0 bg-black/80 backdrop-blur-xl transition-opacity" @click="isMobileMenuOpen = false"></div>

          <!-- Drawer Content -->
          <div class="relative w-4/5 max-w-xs bg-[#0C1017] border-r border-white/15 h-full p-6 flex flex-col justify-between shadow-2xl z-10 text-white">
            <div>
              <!-- Drawer Header -->
              <div class="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-xl bg-neonLime flex items-center justify-center font-black text-black text-base shadow-[0_0_15px_rgba(163,230,53,0.4)]">
                    R
                  </div>
                  <span class="font-extrabold text-lg text-white">Rivlo / <span class="text-neonLime font-bold">PEA</span></span>
                </div>
                <button 
                  @click="isMobileMenuOpen = false" 
                  class="text-white/50 hover:text-white p-2 rounded-full liquid-glass-subtle active:scale-95"
                  title="Fermer le menu"
                  aria-label="Fermer"
                >
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>

              <!-- Navigation Links -->
              <div class="space-y-2">
                <button 
                  @click="activeTab = 'dashboard'; isMobileMenuOpen = false"
                  :class="activeTab === 'dashboard' ? 'bg-neonLime/15 text-neonLime border-neonLime/30 font-bold' : 'text-white/70 hover:text-white border-transparent'"
                  class="w-full text-left px-4 py-3 rounded-2xl border text-sm flex items-center gap-3 transition-all active:scale-95"
                >
                  <span class="text-base">⊞</span>
                  <span>Dashboard</span>
                </button>

                <button 
                  @click="activeTab = 'optimization'; isMobileMenuOpen = false"
                  :class="activeTab === 'optimization' ? 'bg-neonLime/15 text-neonLime border-neonLime/30 font-bold' : 'text-white/70 hover:text-white border-transparent'"
                  class="w-full text-left px-4 py-3 rounded-2xl border text-sm flex items-center gap-3 transition-all active:scale-95"
                >
                  <span class="text-base">🧠</span>
                  <span>Optimisation & IA</span>
                </button>

                <button 
                  @click="activeTab = 'goals'; isMobileMenuOpen = false"
                  :class="activeTab === 'goals' ? 'bg-neonLime/15 text-neonLime border-neonLime/30 font-bold' : 'text-white/70 hover:text-white border-transparent'"
                  class="w-full text-left px-4 py-3 rounded-2xl border text-sm flex items-center gap-3 transition-all active:scale-95"
                >
                  <span class="text-base">🎯</span>
                  <span>Objectifs & Rente</span>
                </button>

                <button 
                  @click="activeTab = 'analytics'; isMobileMenuOpen = false"
                  :class="activeTab === 'analytics' ? 'bg-neonLime/15 text-neonLime border-neonLime/30 font-bold' : 'text-white/70 hover:text-white border-transparent'"
                  class="w-full text-left px-4 py-3 rounded-2xl border text-sm flex items-center gap-3 transition-all active:scale-95"
                >
                  <span class="text-base">📊</span>
                  <span>Analytics & Graphiques</span>
                </button>

                <button 
                  @click="activeTab = 'reports'; isMobileMenuOpen = false"
                  :class="activeTab === 'reports' ? 'bg-neonLime/15 text-neonLime border-neonLime/30 font-bold' : 'text-white/70 hover:text-white border-transparent'"
                  class="w-full text-left px-4 py-3 rounded-2xl border text-sm flex items-center gap-3 transition-all active:scale-95"
                >
                  <span class="text-base">📁</span>
                  <span>Reports & Diagnostics</span>
                </button>
              </div>

              <!-- Fast Quick Actions -->
              <div class="pt-6 mt-6 border-t border-white/10 space-y-2">
                <p class="text-[10px] font-mono uppercase text-white/40 font-bold tracking-wider px-2 mb-2">Outils & Modales</p>
                <button 
                  @click="isFiscalModalOpen = true; isMobileMenuOpen = false" 
                  class="w-full text-left px-4 py-2.5 rounded-xl hover:bg-white/[0.06] text-white/80 hover:text-white flex items-center gap-3 text-xs"
                >
                  <span>⚖️</span>
                  <span>Simulateur Fiscal PEA</span>
                </button>
                <button 
                  @click="isAiAdvisorOpen = true; isMobileMenuOpen = false" 
                  class="w-full text-left px-4 py-2.5 rounded-xl hover:bg-white/[0.06] text-white/80 hover:text-white flex items-center gap-3 text-xs"
                >
                  <span>✦</span>
                  <span>AI Advisor Groq</span>
                </button>
                <button 
                  @click="isSettingsOpen = true; isMobileMenuOpen = false" 
                  class="w-full text-left px-4 py-2.5 rounded-xl hover:bg-white/[0.06] text-white/80 hover:text-white flex items-center gap-3 text-xs"
                >
                  <span>⚙️</span>
                  <span>Paramètres du Compte</span>
                </button>
              </div>
            </div>

            <!-- Drawer Footer -->
            <div class="pt-4 border-t border-white/10 flex items-center justify-between">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-bold text-xs">
                  {{ username.substring(0, 2).toUpperCase() || 'CH' }}
                </div>
                <span class="text-xs font-bold text-white truncate max-w-[120px]">{{ username }}</span>
              </div>
              <button @click="logout" class="text-xs text-roseAcc hover:underline font-bold" title="Déconnexion">
                Quitter
              </button>
            </div>
          </div>
        </div>

        <!-- Center: Floating Pill Navigation Tabs (Liquid Glass) -->
        <nav class="hidden md:flex items-center liquid-glass-pill rounded-full p-1.5 shadow-2xl">
          <button 
            @click="activeTab = 'dashboard'"
            :class="activeTab === 'dashboard' ? 'bg-white/[0.14] text-white shadow-inner font-bold border border-white/20' : 'text-white/55 hover:text-white font-medium border border-transparent'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <span class="text-sm">⊞</span>
            <span>Dashboard</span>
          </button>

          <button 
            @click="activeTab = 'optimization'"
            :class="activeTab === 'optimization' ? 'bg-white/[0.14] text-white shadow-inner font-bold border border-white/20' : 'text-white/55 hover:text-white font-medium border border-transparent'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <span class="text-sm">🧠</span>
            <span>Optimisation</span>
          </button>

          <button 
            @click="activeTab = 'goals'"
            :class="activeTab === 'goals' ? 'bg-white/[0.14] text-white shadow-inner font-bold border border-white/20' : 'text-white/55 hover:text-white font-medium border border-transparent'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <span class="text-sm">🎯</span>
            <span>Objectifs</span>
          </button>

          <button 
            @click="activeTab = 'analytics'"
            :class="activeTab === 'analytics' ? 'bg-white/[0.14] text-white shadow-inner font-bold border border-white/20' : 'text-white/55 hover:text-white font-medium border border-transparent'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <span class="text-sm">📊</span>
            <span>Analytics</span>
          </button>

          <button 
            @click="activeTab = 'reports'"
            :class="activeTab === 'reports' ? 'bg-white/[0.14] text-white shadow-inner font-bold border border-white/20' : 'text-white/55 hover:text-white font-medium border border-transparent'"
            class="px-5 py-2 rounded-full text-xs transition-all flex items-center gap-2 cursor-pointer active:scale-95"
          >
            <span class="text-sm">📁</span>
            <span>Reports</span>
          </button>

          <button 
            @click="isSettingsOpen = true"
            class="px-5 py-2 rounded-full text-xs text-white/55 hover:text-white transition-all flex items-center gap-2 font-medium cursor-pointer border border-transparent hover:border-white/10 active:scale-95"
          >
            <span class="text-sm">⚙️</span>
            <span>Settings</span>
          </button>
        </nav>

        <!-- Right: Actions & User Avatar -->
        <div class="flex items-center gap-3">
          <!-- Quick Refresh Live Button (Yahoo Finance Sync only) -->
          <button 
            @click="refreshData" 
            :disabled="isRefreshing" 
            class="flex items-center gap-1.5 px-4 py-2 rounded-full bg-neonLime/15 border border-neonLime/30 hover:bg-neonLime hover:text-black text-neonLime text-xs font-bold transition-all shadow-[0_0_20px_rgba(163,230,53,0.15)] active:scale-95 disabled:opacity-50 cursor-pointer"
            title="Actualise les cours boursiers en direct et sauvegarde le snapshot dans Supabase"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5" :class="isRefreshing ? 'animate-spin' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span class="hidden sm:inline">{{ isRefreshing ? 'Sync en cours...' : '⚡ Actualiser Cours' }}</span>
          </button>

          <!-- Search Input with Auto-trigger & Click button -->
          <div class="relative flex items-center">
            <input 
              type="text" 
              v-model="searchQuery" 
              @keyup.enter="handleHeaderSearch"
              placeholder="Analyser une action (ex: AAPL, LVMH)..."
              class="w-36 sm:w-56 lg:w-64 liquid-glass-subtle rounded-full pl-9 pr-8 py-2 text-xs text-white placeholder-white/40 focus:outline-none focus:border-neonLime/60 focus:ring-1 focus:ring-neonLime/30 transition-all shadow-inner"
            />
            <button 
              @click="handleHeaderSearch" 
              class="w-4 h-4 text-white/40 hover:text-neonLime absolute left-3 top-2.5 transition-colors cursor-pointer"
              title="Lancer l'analyse du titre"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </button>
            <button 
              v-if="searchQuery.trim()" 
              @click="handleHeaderSearch"
              class="absolute right-2 text-[10px] font-mono font-bold px-1.5 py-0.5 bg-neonLime text-black rounded-md hover:bg-neonLimeHover transition-all cursor-pointer shadow-sm"
              title="Analyser"
            >
              ↵
            </button>
          </div>

          <!-- Notification Bell with Dropdown -->
          <div class="relative">
            <button 
              @click="isNotifOpen = !isNotifOpen"
              class="w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all relative cursor-pointer hover:border-white/20 active:scale-95"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span class="w-2 h-2 rounded-full bg-neonLime absolute top-2.5 right-2.5 shadow-[0_0_8px_rgba(163,230,53,0.8)]"></span>
            </button>

            <!-- Notifications Dropdown (Liquid Glass) -->
            <div v-if="isNotifOpen" class="absolute right-0 top-full mt-2 w-80 liquid-glass rounded-24 shadow-2xl p-4 z-50 text-xs specular-highlight border border-white/15">
              <div class="flex justify-between items-center mb-3">
                <span class="font-bold text-white uppercase font-mono text-[10px] tracking-wider">Notifications Portefeuille</span>
                <span class="text-[10px] text-neonLime font-semibold">3 nouvelles</span>
              </div>
              <div class="space-y-2">
                <div class="liquid-glass-subtle p-2.5 rounded-xl border border-white/10 hover:border-white/20 transition-all">
                  <p class="font-semibold text-white flex items-center gap-1.5"><span>⚡</span> Euronext Paris Ouverte</p>
                  <p class="text-white/50 text-[11px] mt-0.5">Marché en direct, flux temps réel actif.</p>
                </div>
                <div class="liquid-glass-subtle p-2.5 rounded-xl border border-white/10 hover:border-white/20 transition-all">
                  <p class="font-semibold text-white flex items-center gap-1.5"><span>💰</span> Dividende TotalEnergies</p>
                  <p class="text-white/50 text-[11px] mt-0.5">Acompte sur dividende trimestriel programmé.</p>
                </div>
                <div class="liquid-glass-subtle p-2.5 rounded-xl border border-neonLime/20 bg-neonLime/5 transition-all">
                  <p class="font-semibold text-neonLime flex items-center gap-1.5"><span>⚖️</span> Maturité Fiscale Atteinte</p>
                  <p class="text-white/50 text-[11px] mt-0.5">PEA +5 ans : Exonération IR 0% active.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- User Avatar & Profile Dropdown -->
          <div class="relative">
            <div 
              @click="isProfileMenuOpen = !isProfileMenuOpen" 
              class="w-10 h-10 rounded-full border-2 border-neonLime/50 bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-black text-sm shadow-[0_0_15px_rgba(139,92,246,0.4)] cursor-pointer hover:scale-105 active:scale-95 transition-all select-none"
            >
              {{ username.substring(0, 2).toUpperCase() || 'CH' }}
            </div>

            <!-- Profile Dropdown (Liquid Glass) -->
            <div v-if="isProfileMenuOpen" class="absolute right-0 top-full mt-2 w-64 liquid-glass rounded-24 shadow-2xl p-4 z-50 text-xs specular-highlight border border-white/15">
              <div class="flex items-center gap-3 pb-3 border-b border-white/[0.08] mb-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
                  {{ username.substring(0, 2).toUpperCase() || 'CH' }}
                </div>
                <div>
                  <p class="font-bold text-white">{{ username }}</p>
                  <p class="text-white/40 text-[10px] font-mono truncate max-w-[140px]">{{ userId }}</p>
                </div>
              </div>
              <div class="space-y-1">
                <button @click="isFiscalModalOpen = true; isProfileMenuOpen = false" class="w-full text-left p-2 rounded-xl hover:bg-white/[0.05] text-white/80 hover:text-white flex items-center gap-2">
                  <span>⚖️</span> <span>Simulateur Fiscal PEA</span>
                </button>
                <button @click="isSettingsOpen = true; isProfileMenuOpen = false" class="w-full text-left p-2 rounded-xl hover:bg-white/[0.05] text-white/80 hover:text-white flex items-center gap-2">
                  <span>⚙️</span> <span>Paramètres & Backend</span>
                </button>
                <button @click="logout" class="w-full text-left p-2 rounded-xl hover:bg-roseAcc/20 text-roseAcc flex items-center gap-2 font-bold mt-2 border-t border-white/[0.06]">
                  <span>🚪</span> <span>Déconnexion</span>
                </button>
              </div>
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
        <button @click="isSettingsOpen = true" class="bg-neonLime text-black font-extrabold text-sm px-6 py-3 rounded-full shadow-lg hover:bg-neonLimeHover transition-all cursor-pointer">
          Importer un CSV
        </button>
      </div>

      <!-- TAB 1 : MAIN DASHBOARD CONTENT -->
      <div v-else-if="activeTab === 'dashboard'" class="space-y-6">
        
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
            @open-ai="isAiAdvisorOpen = true"
          />

          <!-- Carte 4 : Stack Fiscale & Plafond PEA 150k€ -->
          <FiscalStackCard 
            :summary="summary" 
            @open-tax-sim="isFiscalModalOpen = true"
          />
        </div>

        <!-- ÉTAGE INFÉRIEUR (Grid 2 Colonnes Asymétrique) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <!-- Carte 5 : Analytics Performance -->
          <div class="lg:col-span-7">
            <AnalyticsCharts 
              :history="history" 
              :summary="summary" 
              :positions="positions" 
              :isLoading="isLoading" 
            />
          </div>

          <!-- Carte 6 : Top Movers -->
          <div class="lg:col-span-5">
            <TopMovers 
              :positions="positions" 
              :summary="summary" 
              :isLoading="isLoading" 
              @inspect-stock="openStockInspector"
            />
          </div>
        </div>

        <!-- CALENDRIER DES DIVIDENDES -->
        <DividendCalendar :userId="userId" />

        <!-- SECTION BASSE : TABLEAU PRO DES POSITIONS -->
        <PositionsTable :positions="positions" />

      </div>

      <!-- TAB 2 : ANALYTICS DEEP DIVE -->
      <div v-else-if="activeTab === 'analytics'" class="space-y-6">
        <AnalyticsView 
          :positions="positions" 
          :summary="summary" 
          :history="history" 
        />
      </div>

      <!-- TAB 3 : REPORTS & TAX CONFORMITY -->
      <div v-else-if="activeTab === 'reports'" class="space-y-6">
        <ReportsView 
          :positions="positions" 
          :summary="summary" 
        />
      </div>

      <!-- TAB 4 : OPTIMIZATION & IA -->
      <div v-else-if="activeTab === 'optimization'" class="space-y-6">
        <OptimizationView 
          :userId="userId" 
          :isAiLoading="isAiLoading" 
          @trigger-ai="isAiAdvisorOpen = true" 
        />
      </div>

      <!-- TAB 5 : GOALS & FIRE -->
      <div v-else-if="activeTab === 'goals'" class="space-y-6">
        <GoalsView :userId="userId" />
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
        :asset="inspectedAsset" 
        @close="isSearchModalOpen = false" 
      />

      <AiAdvisorWidget 
        :isOpen="isAiAdvisorOpen" 
        :userId="userId" 
        @close="isAiAdvisorOpen = false" 
      />

      <PeaFiscalModal 
        :isOpen="isFiscalModalOpen" 
        :summary="summary" 
        @close="isFiscalModalOpen = false" 
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
import PositionsTable from './components/PositionsTable.vue';
import AssetInspectorModal from './components/AssetInspectorModal.vue';
import SettingsModal from './components/SettingsModal.vue';
import AiAdvisorWidget from './components/AiAdvisorWidget.vue';
import PeaFiscalModal from './components/PeaFiscalModal.vue';
import AnalyticsView from './components/AnalyticsView.vue';
import ReportsView from './components/ReportsView.vue';
import DividendCalendar from './components/DividendCalendar.vue';
import OptimizationView from './views/OptimizationView.vue';
import GoalsView from './views/GoalsView.vue';

const userId = ref(localStorage.getItem('pea_user_id') || null);
const username = ref(localStorage.getItem('pea_username') || '');
const activeTab = ref('dashboard');

const isLoading = ref(false);
const isRefreshing = ref(false);
const isAiLoading = ref(false);
const isSettingsOpen = ref(false);
const isAiAdvisorOpen = ref(false);
const isFiscalModalOpen = ref(false);
const isSearchModalOpen = ref(false);
const isNotifOpen = ref(false);
const isProfileMenuOpen = ref(false);
const isMobileMenuOpen = ref(false);

const searchQuery = ref('');
const inspectedAsset = ref(null);

const positions = ref([]);
const summary = ref(null);
const history = ref([]);
const weather = ref(null);

const cashAmount = computed(() => {
  return summary.value?.cash || 0;
});

const onLoginSuccess = (payload) => {
  userId.value = payload.userId;
  username.value = payload.username;
  fetchData();
};

const logout = () => {
  localStorage.removeItem('pea_user_id');
  localStorage.removeItem('pea_username');
  localStorage.removeItem('pea_access_token');
  userId.value = null;
  username.value = '';
  positions.value = [];
  summary.value = null;
  history.value = [];
  isProfileMenuOpen.value = false;
};

const openStockInspector = (stock) => {
  if (!stock) return;
  inspectedAsset.value = stock;
  isSearchModalOpen.value = true;
};

const handleHeaderSearch = () => {
  if (!searchQuery.value.trim()) return;
  const q = searchQuery.value.trim();
  const qLower = q.toLowerCase();
  
  // 1. Chercher d'abord dans les positions du portefeuille
  const match = positions.value.find(p => 
    (p.name && p.name.toLowerCase().includes(qLower)) || 
    (p.ticker && p.ticker.toLowerCase().includes(qLower)) ||
    (p.isin && p.isin.toLowerCase().includes(qLower))
  );
  
  if (match) {
    openStockInspector(match);
  } else {
    // 2. Action hors portefeuille : interrogation directe de l'API pour n'importe quelle action (ex: AAPL, NVDA, LVMH, TSLA)
    openStockInspector({
      name: q.toUpperCase(),
      ticker: q.toUpperCase(),
      sector: 'Marché Mondial / Recherche Directe'
    });
  }
};


const fetchData = async () => {
  if (!userId.value) return;
  const apiBase = getApiBase();
  if (!apiBase) return;

  isLoading.value = true;
  try {
    const token = localStorage.getItem('pea_access_token');
    const headers = token ? { Authorization: 'Bearer ' + token } : {};

    const [summaryRes, positionsRes, historyRes] = await Promise.all([
      fetch(`${apiBase}/api/portfolio/summary?user_id=${userId.value}`, { headers }).catch(() => null),
      fetch(`${apiBase}/api/portfolio/positions?user_id=${userId.value}`, { headers }).catch(() => null),
      fetch(`${apiBase}/api/portfolio/history?user_id=${userId.value}`, { headers }).catch(() => null)
    ]);

    if (summaryRes && summaryRes.ok) {
      summary.value = await summaryRes.json();
    }
    if (positionsRes && positionsRes.ok) {
      const posData = await positionsRes.json();
      positions.value = posData.positions || [];
    }
    if (historyRes && historyRes.ok) {
      const histData = await historyRes.json();
      history.value = histData.history || [];
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
    // Actualisation 100% financière (Yahoo Finance -> Supabase)
    await fetch(`${apiBase}/api/portfolio/refresh?user_id=${userId.value}`, {
      method: 'POST',
      headers: token ? { Authorization: 'Bearer ' + token } : {}
    });
    // Récupération des cours et graphiques actualisés
    await fetchData();
  } catch (error) {
    console.error("Erreur lors du rafraîchissement des cours :", error);
  } finally {
    isRefreshing.value = false;
  }
};

onMounted(() => {
  if (userId.value) fetchData();
});
</script>
