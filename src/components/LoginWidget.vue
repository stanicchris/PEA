<template>
  <div class="min-h-screen flex items-center justify-center p-4 font-sans relative overflow-hidden">
    <!-- Subtle Background Glows -->
    <div class="ambient-glow-mesh">
      <div class="ambient-glow-1"></div>
      <div class="ambient-glow-2"></div>
      <div class="ambient-glow-3"></div>
    </div>

    <div class="liquid-glass-chassis relative z-10 w-full max-w-md p-6 sm:p-10 rounded-36 border border-white/15 shadow-2xl specular-highlight animate-fade-up">
      <div class="text-center mb-6">
        <div class="relative inline-block mb-3">
          <img
            src="/logo.png"
            alt="Capfolio"
            class="mx-auto w-16 h-16 rounded-2xl object-cover shadow-[0_0_35px_rgba(163,230,53,0.35)] border border-white/15"
          />
          <span class="absolute -bottom-1 -right-1 px-1.5 py-0.5 rounded-full bg-neonLime text-black font-black text-[9px] font-mono shadow">
            PRO
          </span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-black text-white tracking-tight">
          Capfolio <span class="text-neonLime font-light">/</span> PEA
        </h1>
        <p class="text-white/50 text-xs sm:text-sm mt-1.5 font-medium">
          Cockpit patrimonial, X-Ray ETF & Copilote IA
        </p>

        <!-- Feature Badges -->
        <div class="flex flex-wrap items-center justify-center gap-1.5 mt-4">
          <span class="px-2.5 py-1 rounded-full bg-white/5 border border-white/10 text-[10px] text-white/70 font-medium">
            📈 Cours Live
          </span>
          <span class="px-2.5 py-1 rounded-full bg-neonPurple/15 border border-neonPurple/30 text-[10px] text-lavender font-medium">
            ✦ BourseAi Groq
          </span>
          <span class="px-2.5 py-1 rounded-full bg-neonLime/10 border border-neonLime/25 text-[10px] text-neonLime font-medium">
            ⚖️ Fiscalité & Rente
          </span>
        </div>
      </div>

      <form @submit.prevent="handleAuth" class="space-y-4">
        <div>
          <label class="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5 font-mono">
            Identifiant / Compte
          </label>
          <input
            v-model="username"
            type="text"
            placeholder="Ex: christo"
            autocomplete="username"
            class="w-full liquid-glass-subtle border border-white/10 rounded-2xl px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 transition-all text-sm font-medium shadow-inner"
            required
          />
        </div>

        <div>
          <label class="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5 font-mono">
            Mot de passe
          </label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
              autocomplete="current-password"
              class="w-full liquid-glass-subtle border border-white/10 rounded-2xl pl-4 pr-11 py-3 text-white placeholder-white/30 focus:outline-none focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 transition-all text-sm font-medium shadow-inner"
              required
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3.5 top-1/2 -translate-y-1/2 text-white/40 hover:text-white text-xs p-1"
              :aria-label="showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
        </div>

        <div v-if="errorMsg" class="p-3 rounded-2xl bg-roseAcc/10 border border-roseAcc/30 text-roseAcc text-xs font-medium text-center">
          {{ errorMsg }}
        </div>

        <div class="grid grid-cols-2 gap-3 pt-1">
          <button
            type="submit"
            @click="isRegistering = false"
            :disabled="isLoading"
            class="w-full py-3 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs transition-all shadow-[0_4px_20px_rgba(163,230,53,0.3)] disabled:opacity-50 active:scale-95 cursor-pointer"
          >
            {{ isLoading && !isRegistering ? 'Connexion...' : 'Se connecter' }}
          </button>

          <button
            type="submit"
            @click="isRegistering = true"
            :disabled="isLoading"
            class="w-full py-3 rounded-full liquid-glass-pill hover:bg-white/10 border border-white/15 text-white font-bold text-xs transition-all disabled:opacity-50 active:scale-95 cursor-pointer"
          >
            {{ isLoading && isRegistering ? 'Création...' : 'Créer compte' }}
          </button>
        </div>
      </form>

      <!-- Divider -->
      <div class="relative my-6 flex items-center justify-center">
        <div class="border-t border-white/10 w-full"></div>
        <span class="bg-[#0B0F17] px-3 text-[10px] font-mono uppercase tracking-widest text-white/40 shrink-0">
          Accès Instantané
        </span>
        <div class="border-t border-white/10 w-full"></div>
      </div>

      <!-- 1-Click Interactive Demo Button -->
      <button
        type="button"
        @click="$emit('demo-login')"
        class="w-full py-3.5 px-4 rounded-2xl bg-gradient-to-r from-neonPurple/20 via-lavender/15 to-neonLime/15 hover:from-neonPurple/30 hover:to-neonLime/25 border border-white/15 hover:border-neonLime/40 text-white font-bold text-xs sm:text-sm transition-all flex items-center justify-center gap-2.5 shadow-lg active:scale-95 cursor-pointer group"
      >
        <span class="text-base group-hover:scale-110 transition-transform">✨</span>
        <span>Explorer avec un Portefeuille Démo (1 clic)</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getApiBase } from '../config'

const emit = defineEmits(['login-success', 'demo-login'])

const username = ref('')
const password = ref('')
const showPassword = ref(false)
const isRegistering = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

const handleAuth = async () => {
  isLoading.value = true
  errorMsg.value = ''

  const apiBase = getApiBase()
  if (!apiBase) {
    isLoading.value = false
    errorMsg.value = 'URL API non disponible. Utilisez le Mode Démo ci-dessous.'
    return
  }

  const endpoint = isRegistering.value ? '/api/auth/register' : '/api/auth/login'

  try {
    const res = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })

    const data = await res.json()

    if (!res.ok) {
      throw new Error(data.detail || "Erreur d'authentification")
    }

    localStorage.setItem('pea_access_token', data.access_token)
    emit('login-success', { userId: data.user_id, username: data.username })
  } catch (err) {
    errorMsg.value = err.message || 'Serveur injoignable. Vous pouvez tester via le Portefeuille Démo.'
  } finally {
    isLoading.value = false
  }
}
</script>
