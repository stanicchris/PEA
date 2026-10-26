<template>
  <div class="min-h-screen bg-[#05070A] text-[#F8FAFC] font-sans p-0 sm:p-5 lg:p-8 selection:bg-neonLime selection:text-black relative overflow-x-hidden">
    <!-- Ambient Liquid Glass Caustics Mesh -->
    <div class="ambient-glow-mesh">
      <div class="ambient-glow-1"></div>
      <div class="ambient-glow-2"></div>
      <div class="ambient-glow-3"></div>
    </div>

    <!-- GLOBAL TOAST NOTIFICATION -->
    <transition name="toast-pop">
      <div
        v-if="store.toast"
        class="fixed top-4 right-4 left-4 sm:left-auto z-[250] max-w-sm liquid-glass-chassis px-4 py-3 rounded-2xl border shadow-2xl flex items-center gap-3"
        :class="store.toast.type === 'error' ? 'border-roseAcc/40 text-roseAcc' : 'border-neonLime/40 text-white'"
      >
        <span class="text-lg shrink-0">{{ store.toast.type === 'error' ? '⚠️' : (store.toast.type === 'info' ? 'ℹ️' : '✨') }}</span>
        <p class="text-xs sm:text-sm font-semibold leading-snug flex-1">{{ store.toast.message }}</p>
        <button @click="store.toast = null" class="text-white/40 hover:text-white text-xs p-1">✕</button>
      </div>
    </transition>

    <!-- LOGIN SCREEN -->
    <LoginWidget
      v-if="!store.userId"
      @login-success="store.setLoginData"
      @demo-login="store.enterDemoMode"
      class="relative z-10"
    />

    <!-- MAIN CHASSIS -->
    <div
      v-else
      class="max-w-[1680px] mx-auto liquid-glass-chassis rounded-none sm:rounded-3xl md:rounded-[48px] border-0 sm:border p-3.5 sm:p-6 lg:p-8 pb-28 md:pb-8 relative z-10 overflow-hidden flex flex-col min-h-screen sm:min-h-[92vh] specular-highlight"
    >
      <!-- TOP NAVIGATION BAR -->
      <header class="flex items-center justify-between mb-4 sm:mb-6 gap-2 sm:gap-4 flex-wrap">
        <!-- Left: Mobile Menu + Brand Logo -->
        <div class="flex items-center gap-2.5 sm:gap-3">
          <button
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="md:hidden w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all cursor-pointer hover:border-white/20 active:scale-95"
            title="Menu mobile"
            aria-label="Ouvrir le menu mobile"
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
              <span class="font-extrabold text-lg sm:text-xl tracking-tight text-white flex items-center gap-1.5">
                Capfolio <span class="text-neonLime font-light">/</span> <span class="text-white/80 font-semibold text-sm sm:text-base">PEA</span>
              </span>
            </div>
          </router-link>
        </div>

        <!-- MOBILE SLIDE-OVER DRAWER -->
        <div v-if="isMobileMenuOpen" class="fixed inset-0 z-[150] flex md:hidden">
          <div class="fixed inset-0 bg-black/80 backdrop-blur-xl transition-opacity" @click="isMobileMenuOpen = false"></div>
          <div class="relative w-4/5 max-w-xs bg-[#0C1017] border-r border-white/15 h-full p-6 flex flex-col justify-between shadow-2xl z-10 text-white animate-fade-up">
            <div>
              <div class="flex items-center justify-between pb-4 border-b border-white/10 mb-5">
                <div class="flex items-center gap-2.5">
                  <img src="/logo.png" alt="Capfolio" class="w-8 h-8 rounded-xl object-cover shadow-[0_0_15px_rgba(163,230,53,0.3)] border border-white/10" />
                  <span class="font-extrabold text-lg text-white">Capfolio / <span class="text-neonLime font-bold">PEA</span></span>
                </div>
                <button @click="isMobileMenuOpen = false" class="text-white/50 hover:text-white p-2 rounded-full liquid-glass-subtle active:scale-95" aria-label="Fermer le menu">
                  <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
              </div>

              <div class="space-y-1.5">
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
                  <span class="text-base">💰</span> Dividendes & Rente
                </router-link>
                <router-link to="/research" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">🧠</span> Recherche & IA
                </router-link>
                <router-link to="/watchlist" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">⭐</span> Watchlist & Alertes
                </router-link>
                <router-link to="/plan" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">🎯</span> Plan & Fiscalité
                </router-link>
                <router-link to="/settings" @click="isMobileMenuOpen = false" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 font-bold" class="w-full text-left px-4 py-3 rounded-2xl border border-transparent text-white/70 hover:text-white text-sm flex items-center gap-3 transition-all active:scale-95">
                  <span class="text-base">⚙️</span> Paramètres
                </router-link>
              </div>
            </div>

            <div class="pt-5 border-t border-white/10 mt-auto">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-neonLime/40 to-lavender/40 flex items-center justify-center text-white font-bold border border-white/20">
                  {{ (store.username || 'U').charAt(0).toUpperCase() }}
                </div>
                <div class="overflow-hidden">
                  <p class="text-sm font-semibold truncate">{{ store.username }}</p>
                  <p class="text-xs text-neonLime/80 truncate">{{ store.isDemoMode ? 'Mode Démo Actif' : 'Investisseur PEA' }}</p>
                </div>
              </div>
              <button @click="store.logout(); isMobileMenuOpen = false" class="w-full py-2.5 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 text-sm font-medium transition-colors">
                {{ store.isDemoMode ? 'Quitter le Mode Démo' : 'Déconnexion' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Center: Desktop Navigation Pills -->
        <nav class="hidden md:flex items-center gap-1 p-1.5 bg-black/40 backdrop-blur-md rounded-2xl border border-white/5 shadow-inner">
          <router-link to="/" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            ⊞ Synthèse
          </router-link>
          <router-link to="/portfolio" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            💼 Portefeuille
          </router-link>
          <router-link to="/performance" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            📈 Performance
          </router-link>
          <router-link to="/dividends" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            💰 Dividendes
          </router-link>
          <router-link to="/research" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            🧠 Recherche
          </router-link>
          <router-link to="/watchlist" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            ⭐ Watchlist
          </router-link>
          <router-link to="/plan" exact-active-class="bg-neonLime/15 text-neonLime border-neonLime/30 shadow-[0_0_15px_rgba(163,230,53,0.15)]" class="px-3.5 py-2 rounded-xl text-xs lg:text-sm font-semibold text-white/70 hover:text-white transition-all border border-transparent hover:bg-white/5">
            🎯 Plan & Fisc
          </router-link>
        </nav>

        <!-- Right: Actions & Profile -->
        <div class="flex items-center gap-2 sm:gap-3 ml-auto md:ml-0">
          <!-- Mobile Search Button (opens CommandPalette) -->
          <button
            @click="store.isCommandPaletteOpen = true"
            class="sm:hidden w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all active:scale-95"
            aria-label="Rechercher une action ou une page"
            title="Rechercher"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>

          <!-- Mobile Discrete Mode Toggle -->
          <button
            @click="store.toggleDiscreteMode()"
            class="sm:hidden w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center transition-all active:scale-95"
            :class="store.isDiscreteMode ? 'text-neonLime border-neonLime/40' : 'text-white/70'"
            :aria-label="store.isDiscreteMode ? 'Désactiver le mode discret' : 'Activer le mode discret'"
            title="Mode Discret"
          >
            <svg v-if="!store.isDiscreteMode" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>

          <!-- Global Search (Desktop/Tablet) -->
          <div class="relative hidden sm:block group">
            <input
              v-model="searchQuery"
              @keyup.enter="handleHeaderSearch"
              type="text"
              placeholder="Chercher (ex: AI, LVMH, CW8...)"
              class="w-44 xl:w-64 bg-black/40 border border-white/10 rounded-2xl py-2 pl-10 pr-12 text-sm text-white placeholder-white/40 focus:outline-none focus:border-neonLime/50 focus:w-60 xl:focus:w-72 transition-all duration-300"
            />
            <svg class="w-4 h-4 text-white/50 absolute left-3.5 top-1/2 -translate-y-1/2 group-focus-within:text-neonLime transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <button
              type="button"
              @click="store.isCommandPaletteOpen = true"
              class="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1 opacity-60 hover:opacity-100 transition-opacity"
              title="Ouvrir la palette de commandes (Ctrl+K)"
            >
              <span class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded border border-white/10 font-mono">⌘K</span>
            </button>
          </div>

          <!-- Notification Bell -->
          <div class="relative">
            <button
              @click="isNotifOpen = !isNotifOpen"
              class="w-10 h-10 rounded-2xl liquid-glass-pill flex items-center justify-center text-white/70 hover:text-white transition-all hover:border-white/20 relative active:scale-95"
              aria-label="Notifications"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <!-- Animated Notification Badge -->
              <template v-if="store.unreadNotifCount > 0">
                <span class="absolute top-2 right-2 w-2.5 h-2.5 bg-neonLime rounded-full border-2 border-[#0A0D14] shadow-[0_0_8px_rgba(163,230,53,0.8)]"></span>
                <span class="absolute top-2 right-2 w-2.5 h-2.5 bg-neonLime rounded-full animate-ping opacity-75"></span>
              </template>
            </button>

            <!-- Notif Dropdown -->
            <div v-if="isNotifOpen" class="absolute right-0 mt-3 w-80 sm:w-96 bg-[#12161E]/95 backdrop-blur-2xl border border-white/15 rounded-2xl shadow-2xl z-50 overflow-hidden transform origin-top-right animate-fade-up">
              <div class="p-4 border-b border-white/10 flex justify-between items-center bg-black/20">
                <h3 class="font-bold text-white text-sm">Insights & Alertes PEA</h3>
                <span class="text-xs text-neonLime bg-neonLime/10 px-2.5 py-0.5 rounded-full font-bold">
                  {{ store.unreadNotifCount }} active{{ store.unreadNotifCount > 1 ? 's' : '' }}
                </span>
              </div>
              <div class="max-h-[320px] overflow-y-auto custom-scrollbar divide-y divide-white/5">
                <div
                  v-for="n in store.notifications"
                  :key="n.id"
                  @click="router.push(n.route); isNotifOpen = false"
                  class="p-4 hover:bg-white/5 transition-colors cursor-pointer group"
                >
                  <div class="flex items-start gap-3">
                    <div class="w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 mt-0.5 group-hover:scale-110 transition-transform" :class="n.color">
                      {{ n.icon }}
                    </div>
                    <div class="min-w-0 flex-1">
                      <p class="text-xs sm:text-sm text-white font-bold mb-1 group-hover:text-neonLime transition-colors">{{ n.title }}</p>
                      <p class="text-xs text-white/60 leading-relaxed">{{ n.desc }}</p>
                      <p class="text-[10px] text-white/35 mt-1.5 uppercase tracking-wider font-mono font-semibold">{{ n.time }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <div @click="store.markAllNotificationsRead(); isNotifOpen = false" class="p-3 text-center bg-black/40 hover:bg-black/60 transition-colors cursor-pointer">
                <span class="text-xs text-white/60 hover:text-white font-medium">Marquer tout comme lu ✓</span>
              </div>
            </div>
          </div>

          <!-- Profile / Settings Dropdown (Desktop/Tablet) -->
          <div class="relative hidden sm:block">
            <button
              @click="isProfileMenuOpen = !isProfileMenuOpen"
              class="flex items-center gap-2 pl-2 pr-3.5 py-1.5 rounded-2xl liquid-glass-pill hover:border-white/20 transition-all active:scale-95 group"
            >
              <div class="w-7 h-7 rounded-full bg-gradient-to-br from-neonLime/40 to-lavender/40 flex items-center justify-center text-white font-bold text-xs border border-white/20 shadow-[0_0_10px_rgba(163,230,53,0.2)] group-hover:shadow-[0_0_15px_rgba(163,230,53,0.4)] transition-shadow">
                {{ (store.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <span class="text-sm font-semibold text-white/80 group-hover:text-white transition-colors max-w-[110px] truncate">
                {{ store.username }}
              </span>
              <svg class="w-4 h-4 text-white/40 group-hover:text-white/80 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <!-- Profile Menu -->
            <div v-if="isProfileMenuOpen" class="absolute right-0 mt-3 w-60 bg-[#12161E]/95 backdrop-blur-2xl border border-white/15 rounded-2xl shadow-2xl z-50 overflow-hidden transform origin-top-right animate-fade-up">
              <div class="p-4 border-b border-white/10 bg-black/20">
                <p class="text-sm text-white font-bold truncate">{{ store.username }}</p>
                <p class="text-[11px] text-neonLime/80 font-mono mt-0.5">{{ store.isDemoMode ? '✨ Portefeuille Démo' : 'Compte PEA Vérifié' }}</p>
              </div>
              <div class="p-2 space-y-1">
                <button @click="store.openAddPositionModal(); isProfileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-xl text-sm text-white/80 hover:text-neonLime hover:bg-white/10 flex items-center gap-3 transition-colors">
                  <span class="text-base">➕</span> Ajouter une ligne
                </button>
                <router-link to="/settings" @click="isProfileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/10 flex items-center gap-3 transition-colors">
                  <span class="text-base">⚙️</span> Paramètres & Données
                </router-link>
                <button @click="store.toggleDiscreteMode(); isProfileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/10 flex items-center gap-3 transition-colors">
                  <span class="text-base">{{ store.isDiscreteMode ? '👁️' : '🌙' }}</span>
                  {{ store.isDiscreteMode ? 'Désactiver Mode Discret' : 'Activer Mode Discret' }}
                </button>
              </div>
              <div class="p-2 border-t border-white/10">
                <button @click="store.logout(); isProfileMenuOpen = false" class="w-full text-left px-3 py-2 rounded-xl text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 flex items-center gap-3 transition-colors font-medium">
                  <span class="text-base">🚪</span> {{ store.isDemoMode ? 'Quitter la Démo' : 'Déconnexion' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- WELCOMING SUB-HEADER & LIVE MARKET STATUS BAR -->
      <div class="flex flex-wrap items-center justify-between gap-2.5 mb-5 pb-3.5 border-b border-white/[0.06] text-xs">
        <div class="flex items-center gap-2.5 flex-wrap">
          <span class="text-white/80 font-medium text-xs sm:text-sm">
            {{ greetingText }}, <strong class="text-white font-extrabold">{{ store.username }}</strong> 👋
          </span>
          <span
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-mono font-semibold border"
            :class="marketOpen ? 'bg-neonLime/10 text-neonLime border-neonLime/25' : 'bg-white/5 text-white/60 border-white/10'"
          >
            <span class="w-1.5 h-1.5 rounded-full" :class="marketOpen ? 'bg-neonLime animate-ping' : 'bg-white/40'"></span>
            {{ marketOpen ? 'Euronext Ouvert' : 'Euronext Fermé' }}
          </span>
          <span
            v-if="store.isDemoMode"
            class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-neonPurple/15 text-lavender border border-neonPurple/30 text-[11px] font-bold"
          >
            ✨ Mode Démo Interactif
          </span>
        </div>

        <div class="flex items-center gap-2 ml-auto">
          <button
            @click="store.openAddPositionModal()"
            class="px-3.5 py-1.5 rounded-full bg-neonLime/15 hover:bg-neonLime hover:text-black text-neonLime border border-neonLime/30 font-bold text-xs transition-all flex items-center gap-1.5 active:scale-95 cursor-pointer"
          >
            <span>＋</span>
            <span>Ajouter une ligne</span>
          </button>
          <button
            v-if="!store.isDemoMode && store.positions.length === 0"
            @click="store.enterDemoMode()"
            class="px-3 py-1.5 rounded-full liquid-glass-subtle hover:bg-white/10 text-lavender border border-neonPurple/30 font-bold text-xs transition-all active:scale-95 cursor-pointer"
          >
            ✨ Charger Démo
          </button>
        </div>
      </div>

      <!-- MAIN CONTENT AREA -->
      <main class="flex-1 w-full overflow-hidden flex flex-col relative z-10">
        <router-view v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- FLOATING AI COPILOT BUTTON -->
      <button
        @click="store.isAiAdvisorOpen = true"
        class="fixed bottom-24 md:bottom-7 right-4 md:right-8 z-[85] liquid-glass-pill px-4 py-2.5 rounded-full border border-neonPurple/40 shadow-[0_10px_30px_rgba(139,92,246,0.35)] hover:shadow-[0_12px_35px_rgba(163,230,53,0.35)] hover:border-neonLime/50 flex items-center gap-2 text-white font-bold text-xs transition-all active:scale-95 group cursor-pointer"
        title="Ouvrir le Directeur Financier Virtuel BourseAi"
      >
        <span class="w-6 h-6 rounded-full bg-neonPurple/25 border border-neonPurple/40 flex items-center justify-center text-lavender group-hover:bg-neonLime group-hover:text-black group-hover:border-neonLime transition-colors">✦</span>
        <span class="hidden sm:inline">Copilote IA</span>
      </button>

      <!-- MOBILE FLOATING BOTTOM TAB BAR (App Native Feel) -->
      <nav
        class="md:hidden fixed bottom-2.5 inset-x-3 z-[95] liquid-glass-chassis rounded-3xl px-2 py-1.5 border border-white/15 shadow-[0_20px_50px_rgba(0,0,0,0.9)] flex items-center justify-around pb-safe"
        aria-label="Navigation principale mobile"
      >
        <router-link
          to="/"
          exact-active-class="text-neonLime bg-neonLime/15 border-neonLime/25"
          class="flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl text-white/55 border border-transparent transition-all active:scale-90"
        >
          <span class="text-base leading-none">⊞</span>
          <span class="text-[10px] font-bold mt-1">Synthèse</span>
        </router-link>

        <router-link
          to="/portfolio"
          exact-active-class="text-neonLime bg-neonLime/15 border-neonLime/25"
          class="flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl text-white/55 border border-transparent transition-all active:scale-90"
        >
          <span class="text-base leading-none">💼</span>
          <span class="text-[10px] font-bold mt-1">Lignes</span>
        </router-link>

        <router-link
          to="/performance"
          exact-active-class="text-neonLime bg-neonLime/15 border-neonLime/25"
          class="flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl text-white/55 border border-transparent transition-all active:scale-90"
        >
          <span class="text-base leading-none">📈</span>
          <span class="text-[10px] font-bold mt-1">Perf</span>
        </router-link>

        <router-link
          to="/dividends"
          exact-active-class="text-neonLime bg-neonLime/15 border-neonLime/25"
          class="flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl text-white/55 border border-transparent transition-all active:scale-90"
        >
          <span class="text-base leading-none">💰</span>
          <span class="text-[10px] font-bold mt-1">Rente</span>
        </router-link>

        <button
          @click="isMobileMenuOpen = true"
          class="flex flex-col items-center justify-center py-1.5 px-3 rounded-2xl text-white/55 hover:text-white border border-transparent transition-all active:scale-90"
        >
          <span class="text-base leading-none">🎯</span>
          <span class="text-[10px] font-bold mt-1">Plus</span>
        </button>
      </nav>

      <!-- ADD / EDIT POSITION MODAL (Mobile Bottom Sheet / Desktop Modal) -->
      <div v-if="store.isAddPositionOpen" class="fixed inset-0 z-[180] flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div class="fixed inset-0 bg-black/80 backdrop-blur-xl" @click="store.isAddPositionOpen = false"></div>
        <div class="relative w-full max-w-lg liquid-glass-chassis rounded-t-36 sm:rounded-36 p-6 sm:p-8 border border-white/15 shadow-2xl z-10 text-white animate-sheet-up">
          <!-- Mobile Drag Handle -->
          <div class="w-12 h-1.5 bg-white/20 rounded-full mx-auto mb-4 sm:hidden"></div>

          <div class="flex items-center justify-between mb-5">
            <div>
              <h3 class="text-xl font-black text-white tracking-tight">
                {{ store.editingPosition ? 'Modifier la position' : 'Ajouter une ligne au PEA' }}
              </h3>
              <p class="text-xs text-white/50 mt-0.5">Saisie directe sans fichier CSV</p>
            </div>
            <button @click="store.isAddPositionOpen = false" class="p-2 rounded-full liquid-glass-subtle text-white/50 hover:text-white">✕</button>
          </div>

          <!-- Quick Presets -->
          <div v-if="!store.editingPosition" class="mb-4">
            <p class="text-[10px] font-mono uppercase tracking-wider text-white/40 mb-2">Valeurs phares PEA (1 clic) :</p>
            <div class="flex gap-1.5 overflow-x-auto no-scrollbar pb-1">
              <button
                v-for="preset in quickPresets"
                :key="preset.ticker"
                type="button"
                @click="applyPreset(preset)"
                class="px-2.5 py-1 rounded-full bg-white/5 hover:bg-neonLime/15 hover:text-neonLime border border-white/10 text-xs font-mono whitespace-nowrap transition-colors"
              >
                {{ preset.label }}
              </button>
            </div>
          </div>

          <form @submit.prevent="submitPositionForm" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-[10px] font-mono uppercase text-white/50 mb-1">Nom du titre *</label>
                <input
                  v-model="posForm.name"
                  type="text"
                  required
                  placeholder="Ex: Air Liquide, MSCI World..."
                  class="w-full liquid-glass-subtle border border-white/10 focus:border-neonLime rounded-2xl px-4 py-2.5 text-sm text-white outline-none"
                />
              </div>
              <div>
                <label class="block text-[10px] font-mono uppercase text-white/50 mb-1">Ticker ou ISIN *</label>
                <input
                  v-model="posForm.ticker"
                  type="text"
                  required
                  placeholder="Ex: AI.PA, CW8.PA, MC.PA"
                  class="w-full liquid-glass-subtle border border-white/10 focus:border-neonLime rounded-2xl px-4 py-2.5 text-sm font-mono text-white outline-none uppercase"
                />
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-[10px] font-mono uppercase text-white/50 mb-1">Quantité *</label>
                <input
                  v-model.number="posForm.quantity"
                  type="number"
                  step="any"
                  min="0.01"
                  required
                  class="w-full liquid-glass-subtle border border-white/10 focus:border-neonLime rounded-2xl px-3.5 py-2.5 text-sm font-mono text-white outline-none"
                />
              </div>
              <div>
                <label class="block text-[10px] font-mono uppercase text-white/50 mb-1">PRU (€) *</label>
                <input
                  v-model.number="posForm.pru"
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  class="w-full liquid-glass-subtle border border-white/10 focus:border-neonLime rounded-2xl px-3.5 py-2.5 text-sm font-mono text-white outline-none"
                />
              </div>
              <div>
                <label class="block text-[10px] font-mono uppercase text-white/50 mb-1">Cours actuel (€)</label>
                <input
                  v-model.number="posForm.current_price"
                  type="number"
                  step="0.01"
                  min="0.01"
                  placeholder="Auto"
                  class="w-full liquid-glass-subtle border border-white/10 focus:border-neonLime rounded-2xl px-3.5 py-2.5 text-sm font-mono text-white outline-none"
                />
              </div>
            </div>

            <div>
              <label class="block text-[10px] font-mono uppercase text-white/50 mb-1">Secteur / Catégorie</label>
              <select
                v-model="posForm.sector"
                class="w-full bg-[#12161E] border border-white/10 focus:border-neonLime rounded-2xl px-4 py-2.5 text-sm text-white outline-none"
              >
                <option value="ETF & Indice">ETF & Indice (CW8, WPEA, S&P 500...)</option>
                <option value="Luxe">Luxe & Cosmétiques</option>
                <option value="Industrie & Gaz">Industrie & Gaz</option>
                <option value="Énergie">Énergie</option>
                <option value="Technologie">Technologie & Semi-conducteurs</option>
                <option value="Santé">Santé & Pharma</option>
                <option value="Finance & Banque">Finance & Banque</option>
                <option value="Action">Autre Action Européenne</option>
              </select>
            </div>

            <div class="pt-2 flex gap-3">
              <button
                type="button"
                @click="store.isAddPositionOpen = false"
                class="flex-1 py-3 rounded-full liquid-glass-subtle border border-white/10 text-white/70 hover:text-white text-xs font-bold"
              >
                Annuler
              </button>
              <button
                type="submit"
                class="flex-1 py-3 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs shadow-[0_4px_20px_rgba(163,230,53,0.3)] transition-all active:scale-95"
              >
                Enregistrer la ligne
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- MODALS -->
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from './stores/app'

import LoginWidget from './components/LoginWidget.vue'
import AssetInspectorModal from './components/AssetInspectorModal.vue'
import AiAdvisorWidget from './components/AiAdvisorWidget.vue'
import PeaFiscalModal from './components/PeaFiscalModal.vue'
import CommandPalette from './components/CommandPalette.vue'

const store = useAppStore()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isNotifOpen = ref(false)
const isProfileMenuOpen = ref(false)
const searchQuery = ref('')

// Greeting & Market Open status
const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Bonjour'
  if (h < 18) return 'Bon après-midi'
  return 'Bonsoir'
})

const marketOpen = computed(() => {
  const now = new Date()
  const day = now.getDay()
  if (day === 0 || day === 6) return false
  const mins = now.getHours() * 60 + now.getMinutes()
  return mins >= 9 * 60 && mins <= 17 * 60 + 35
})

// Add/Edit Position Form
const posForm = ref({
  name: '',
  ticker: '',
  isin: '',
  quantity: 10,
  pru: 100,
  current_price: 105,
  sector: 'Action'
})

const quickPresets = [
  { label: '🌍 CW8 (MSCI World)', name: 'Amundi MSCI World UCITS ETF (CW8)', ticker: 'CW8.PA', isin: 'LU1681043599', pru: 520, current_price: 538.6, sector: 'ETF & Indice' },
  { label: '🌍 WPEA (iShares World)', name: 'iShares MSCI World Swap PEA (WPEA)', ticker: 'WPEA.PA', isin: 'IE0002XZSHO1', pru: 5.2, current_price: 5.58, sector: 'ETF & Indice' },
  { label: '🫧 Air Liquide', name: 'Air Liquide', ticker: 'AI.PA', isin: 'FR0000120073', pru: 165, current_price: 176.4, sector: 'Industrie & Gaz' },
  { label: '👜 LVMH', name: 'LVMH Moët Hennessy', ticker: 'MC.PA', isin: 'FR0000121014', pru: 685, current_price: 718.5, sector: 'Luxe' },
  { label: '⚡ TotalEnergies', name: 'TotalEnergies', ticker: 'TTE.PA', isin: 'FR0000120271', pru: 58, current_price: 63.8, sector: 'Énergie' },
  { label: '🇺🇸 ESE (S&P 500)', name: 'BNP Paribas Easy S&P 500 (ESE)', ticker: 'ESE.PA', isin: 'FR0011550185', pru: 24.5, current_price: 26.85, sector: 'ETF & Indice' }
]

const applyPreset = (p) => {
  posForm.value = {
    name: p.name,
    ticker: p.ticker,
    isin: p.isin,
    quantity: 10,
    pru: p.pru,
    current_price: p.current_price,
    sector: p.sector
  }
}

watch(
  () => store.editingPosition,
  (val) => {
    if (val) {
      posForm.value = {
        name: val.name || '',
        ticker: val.ticker || val.isin || '',
        isin: val.isin || val.ticker || '',
        quantity: val.quantity || 1,
        pru: val.pru || 100,
        current_price: val.current_price || val.pru || 100,
        sector: val.sector || 'Action'
      }
    } else {
      posForm.value = {
        name: '',
        ticker: '',
        isin: '',
        quantity: 10,
        pru: 100,
        current_price: 105,
        sector: 'Action'
      }
    }
  }
)

const submitPositionForm = () => {
  store.upsertPosition(posForm.value)
}

const handleHeaderSearch = () => {
  if (!searchQuery.value.trim()) return
  const q = searchQuery.value.trim()
  const qLower = q.toLowerCase()

  const match = store.positions.find(
    (p) =>
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
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
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
/* Transition fluide pour le router-view */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.24s cubic-bezier(0.16, 1, 0.3, 1), transform 0.24s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Toast pop transition */
.toast-pop-enter-active,
.toast-pop-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-pop-enter-from,
.toast-pop-leave-to {
  opacity: 0;
  transform: translateY(-16px) scale(0.95);
}
</style>
