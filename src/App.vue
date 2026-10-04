<template>
  <div class="min-h-screen bg-[#05070A] text-[#F8FAFC] font-sans p-3 sm:p-6 lg:p-8 selection:bg-neonLime selection:text-black relative overflow-x-hidden">
    <!-- Ambient Liquid Glass Caustics Mesh -->
    <div class="ambient-glow-mesh">
      <div class="ambient-glow-1"></div>
      <div class="ambient-glow-2"></div>
      <div class="ambient-glow-3"></div>
    </div>

    <!-- LOGIN SCREEN -->
    <LoginWidget v-if="!store.userId" @login-success="store.setLoginData" class="relative z-10" />

    <!-- MAIN CHASSIS -->
    <div v-else class="max-w-[1680px] mx-auto liquid-glass-chassis rounded-48 p-4 sm:p-6 lg:p-8 relative z-10 overflow-hidden flex flex-col min-h-[92vh] specular-highlight">
      
      <!-- TOP NAVIGATION BAR -->
      <header class="flex items-center justify-between mb-8 gap-4 flex-wrap">
        <!-- Left: Menu + Brand Logo -->
        <div class="flex items-center gap-3">
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all cursor-pointer hover:border-white/20 active:scale-95"
            title="Menu mobile"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <router-link to="/" class="flex items-center gap-2.5 cursor-pointer group">
            <img 
              src="/logo.png" 
              alt="Capfolio" 
              class="w-9 h-9 rounded-xl object-cover shadow-[0_0_20px_rgba(163,230,53,0.3)] border border-white/10 group-hover:scale-105 transition-transform"
            />
            <div class="flex flex-col">
              <span class="font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5">
                Capfolio <span class="text-neonLime font-light">/</span> <span class="text-white/80 font-semibold text-base">PEA</span>
              </span>
            </div>
          </router-link>
        </div>

        <!-- MOBILE SLIDE-OVER DRAWER -->
        <div v-if="isMobileMenuOpen" class="fixed inset-0 z-[120] flex md:hidden">
          <div class="fixed inset-0 bg-black/80 backdrop-blur-xl transition-opacity" @click="isMobileMenuOpen = false"></div>
          <div class="relative w-4/5 max-w-xs bg-[#0C1017] border-r border-white/15 h-full p-6 flex flex-col justify-between shadow-2xl z-10 text-white">
            <div>
              <div class="flex items-center justify-between pb-4 border-b border-white/10 mb-6">
                <div class="flex items-center gap-2.5">
                  <img src="/logo.png" alt="Capfolio" class="w-8 h-8 rounded-xl object-cover shadow-[0_0_15px_rgba(163,230,53,0.3)] border border-white/10"/>
                  <span class="font-extrabold text-lg text-white">Capfolio / <span class="text-neonLime font-bold">PEA</span></span>
                </div>
                <button @click="isMobileMenuOpen = false" class="text-white/50 hover:text-white p-2 rounded-full liquid-glass-subtle active:scale-95">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>

              <div class="space-y-2">
                <router-link to="/" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">⊞</span> Synthèse
                </router-link>
                <router-link to="/portfolio" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">💼</span> Portefeuille
                </router-link>
                <router-link to="/performance" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">📈</span> Performance
                </router-link>
                <router-link to="/dividends" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">💰</span> Dividendes
                </router-link>
                <router-link to="/research" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">🧠</span> Recherche & IA
                </router-link>
                <router-link to="/plan" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">🎯</span> Plan & Fiscalité
                </router-link>
                <button @click="store.isSettingsOpen = true; isMobileMenuOpen = false" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">⚙️</span> Paramètres
                </button>
              </div>
            </div>
            
            <div class="pt-6 border-t border-white/10 mt-auto">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-neonLime/40 to-lavender/40 flex items-center justify-center text-white font-bold border border-white/20">
                  {{ store.username.charAt(0).toUpperCase() }}
                </div>
                <div class="overflow-hidden">
                  <p class="text-sm font-semibold truncate">{{ store.username }}</p>
                  <p class="text-xs text-white/50 truncate">Premium Investor</p>
                </div>
              </div>
              <button @click="store.logout(); isMobileMenuOpen = false" class="w-full py-2.5 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 text-sm font-medium transition-colors">
                Déconnexion
              </button>
            </div>
          </div>
        </div>

        <!-- Center: Desktop Navigation Pills -->
        <nav class="hidden md:flex items-center gap-1.5 p-1.5 bg-black/40 backdrop-blur-md rounded-2xl border border-white/5 shadow-inner">
          <router-link to="/" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-4 py-2 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            ⊞ Synthèse
          </router-link>
          <router-link to="/portfolio" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-4 py-2 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            💼 Portefeuille
          </router-link>
          <router-link to="/performance" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-4 py-2 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            📈 Performance
          </router-link>
          <router-link to="/dividends" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-4 py-2 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            💰 Dividendes
          </router-link>
          <router-link to="/research" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-4 py-2 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            🧠 Recherche
          </router-link>
          <router-link to="/plan" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-4 py-2 rounded-xl text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            🎯 Plan & Fisc
          </router-link>
        </nav>

        <!-- Right: Actions & Profile -->
        <div class="flex items-center gap-3 ml-auto md:ml-0">
          <!-- Global Search -->
          <div class="relative hidden sm:block group">
            <input 
              v-model="searchQuery"
              @keyup.enter="handleHeaderSearch"
              type="text" 
              placeholder="Chercher (ex: AAPL, LVMH...)" 
              class="w-48 xl:w-64 bg-black/40 border border-white/10 rounded-2xl py-2 pl-10 pr-4 text-sm text-white placeholder-white/40 focus:outline-none focus:border-neonLime/50 focus:w-64 xl:focus:w-72 transition-all duration-300"
            />
            <svg class="w-4 h-4 text-white/50 absolute left-3.5 top-1/2 -translate-y-1/2 group-focus-within:text-neonLime transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <div class="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1 pointer-events-none opacity-50 group-focus-within:opacity-0 transition-opacity">
              <span class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded border border-white/10 font-mono">⌘</span>
              <span class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded border border-white/10 font-mono">K</span>
            </div>
          </div>

          <!-- Notification Bell -->
          <div class="relative">
            <button 
              @click="isNotifOpen = !isNotifOpen"
              class="w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all hover:border-white/20 relative"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <!-- Animated Notification Badge -->
              <span class="absolute top-2 right-2 w-2.5 h-2.5 bg-neonLime rounded-full border-2 border-[#0A0D14] shadow-[0_0_8px_rgba(163,230,53,0.8)]"></span>
              <span class="absolute top-2 right-2 w-2.5 h-2.5 bg-neonLime rounded-full animate-ping opacity-75"></span>
            </button>
            
            <!-- Notif Dropdown -->
            <div v-if="isNotifOpen" class="absolute right-0 mt-3 w-80 bg-[#12161E]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden transform origin-top-right transition-all">
              <div class="p-4 border-b border-white/10 flex justify-between items-center bg-black/20">
                <h3 class="font-bold text-white text-sm">Notifications</h3>
                <span class="text-xs text-neonLime bg-neonLime/10 px-2 py-0.5 rounded-full font-medium">3 Nouvelles</span>
              </div>
              <div class="max-h-[300px] overflow-y-auto custom-scrollbar">
                <div class="p-4 border-b border-white/5 hover:bg-white/5 transition-colors cursor-pointer group">
                  <div class="flex items-start gap-3">
                    <div class="w-8 h-8 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0 mt-0.5 group-hover:scale-110 transition-transform">
                      💰
                    </div>
                    <div>
                      <p class="text-sm text-white font-medium mb-1 group-hover:text-neonLime transition-colors">Dividende TotalEnergies</p>
                      <p class="text-xs text-white/50 leading-relaxed">Détachement de 0,79€ par action dans 3 jours.</p>
                      <p class="text-[10px] text-white/30 mt-2 uppercase tracking-wider font-semibold">Il y a 2 heures</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="p-3 text-center bg-black/40 hover:bg-black/60 transition-colors cursor-pointer">
                <span class="text-xs text-white/50 font-medium">Marquer tout comme lu</span>
              </div>
            </div>
          </div>

          <!-- Profile / Settings Dropdown -->
          <div class="relative hidden sm:block">
            <button 
              @click="isProfileMenuOpen = !isProfileMenuOpen"
              class="flex items-center gap-2 pl-2 pr-4 py-1.5 rounded-2xl liquid-glass-pill hover:border-white/20 transition-all active:scale-95 group"
            >
              <div class="w-7 h-7 rounded-full bg-gradient-to-br from-neonLime/40 to-lavender/40 flex items-center justify-center text-white font-bold text-xs border border-white/20 shadow-[0_0_10px_rgba(163,230,53,0.2)] group-hover:shadow-[0_0_15px_rgba(163,230,53,0.4)] transition-shadow">
                {{ store.username.charAt(0).toUpperCase() }}
              </div>
              <span class="text-sm font-semibold text-white/80 group-hover:text-white transition-colors max-w-[100px] truncate">
                {{ store.username }}
              </span>
              <svg class="w-4 h-4 text-white/40 group-hover:text-white/80 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Profile Menu -->
            <div v-if="isProfileMenuOpen" class="absolute right-0 mt-3 w-56 bg-[#12161E]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl z-50 overflow-hidden transform origin-top-right transition-all">
              <div class="p-4 border-b border-white/10 bg-black/20">
                <p class="text-sm text-white font-bold truncate">{{ store.username }}</p>
                <p class="text-xs text-white/50 mt-1 font-mono text-[10px] break-all">{{ store.userId }}</p>
              </div>
              <div class="p-2 space-y-1">
                <button @click="store.isSettingsOpen = true; isProfileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/10 flex items-center gap-3 transition-colors">
                  <span class="text-base">⚙️</span> Paramètres & Données
                </button>
                <button class="w-full text-left px-3 py-2 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/10 flex items-center gap-3 transition-colors">
                  <span class="text-base">🌙</span> Mode Discret (Bientôt)
                </button>
              </div>
              <div class="p-2 border-t border-white/10">
                <button @click="store.logout" class="w-full text-left px-3 py-2 rounded-xl text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 flex items-center gap-3 transition-colors font-medium">
                  <span class="text-base">🚪</span> Déconnexion
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- MAIN CONTENT AREA -->
      <main class="flex-1 w-full overflow-hidden flex flex-col relative z-10">
        <!-- Rendu dynamique des vues selon la route -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- MODALS -->
      <SettingsModal 
        :isOpen="store.isSettingsOpen" 
        :userId="store.userId" 
        :currentCash="store.cashAmount" 
        @close="store.isSettingsOpen = false"
        @refresh="store.fetchData"
      />

      <AssetInspectorModal 
        :isOpen="store.isSearchModalOpen" 
        :asset="store.inspectedAsset" 
        @close="store.isSearchModalOpen = false" 
      />

      <AiAdvisorWidget 
        :isOpen="store.isAiAdvisorOpen" 
        :userId="store.userId" 
        @close="store.isAiAdvisorOpen = false" 
      />

      <PeaFiscalModal 
        :isOpen="store.isFiscalModalOpen" 
        :summary="store.summary" 
        @close="store.isFiscalModalOpen = false" 
      />

      <CommandPalette 
        :isOpen="store.isCommandPaletteOpen" 
        @close="store.isCommandPaletteOpen = false" 
      />

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAppStore } from './stores/app'

import LoginWidget from './components/LoginWidget.vue'
import SettingsModal from './components/SettingsModal.vue'
import AssetInspectorModal from './components/AssetInspectorModal.vue'
import AiAdvisorWidget from './components/AiAdvisorWidget.vue'
import PeaFiscalModal from './components/PeaFiscalModal.vue'
import CommandPalette from './components/CommandPalette.vue'

const store = useAppStore()

const isMobileMenuOpen = ref(false)
const isNotifOpen = ref(false)
const isProfileMenuOpen = ref(false)
const searchQuery = ref('')

const handleHeaderSearch = () => {
  if (!searchQuery.value.trim()) return
  const q = searchQuery.value.trim()
  const qLower = q.toLowerCase()
  
  const match = store.positions.find(p => 
    (p.name && p.name.toLowerCase().includes(qLower)) || 
    (p.ticker && p.ticker.toLowerCase().includes(qLower)) ||
    (p.isin && p.isin.toLowerCase().includes(qLower))
  )
  
  if (match) {
    store.openStockInspector(match)
  } else {
    store.openStockInspector({
      name: q.toUpperCase(),
      ticker: q.toUpperCase(),
      sector: 'Marché Mondial / Recherche Directe'
    })
  }
}


const handleGlobalKeydown = (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    store.isCommandPaletteOpen = !store.isCommandPaletteOpen
  }
}

onMounted(() => {
  if (store.userId) {
    store.fetchData()
  }
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>

<style>
/* Transition pour le router-view */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
