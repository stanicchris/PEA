<template>
  <div class="min-h-screen flex items-center justify-center p-4 font-sans relative overflow-hidden">
    <!-- Subtle Background Glows -->
    <div class="ambient-glow-mesh">
      <div class="ambient-glow-1"></div>
      <div class="ambient-glow-2"></div>
      <div class="ambient-glow-3"></div>
    </div>

    <div class="liquid-glass-chassis relative z-10 w-full max-w-md p-8 sm:p-10 rounded-36 border border-white/15 shadow-2xl specular-highlight">
      <div class="text-center mb-8">
        <img 
          src="/logo.png" 
          alt="Capfolio" 
          class="mx-auto w-16 h-16 rounded-2xl object-cover mb-4 shadow-[0_0_35px_rgba(163,230,53,0.35)] border border-white/15"
        />
        <h1 class="text-2xl font-black text-white tracking-tight">Capfolio <span class="text-neonLime font-light">/</span> PEA</h1>
        <p class="text-white/40 text-xs mt-1.5 font-medium">Terminal financier privé & Copilote IA</p>
      </div>

      <form @submit.prevent="handleAuth" class="space-y-4">
        <div>
          <label class="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5 font-mono">Identifiant / Compte</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="Ex: christo"
            class="w-full liquid-glass-subtle border border-white/10 rounded-full px-5 py-3 text-white placeholder-white/30 focus:outline-none focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 transition-all text-sm font-medium shadow-inner"
            required
          />
        </div>
        
        <div>
          <label class="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5 font-mono">Mot de passe</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••••"
            class="w-full liquid-glass-subtle border border-white/10 rounded-full px-5 py-3 text-white placeholder-white/30 focus:outline-none focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 transition-all text-sm font-medium shadow-inner"
            required
          />
        </div>

        <div v-if="errorMsg" class="p-3 rounded-2xl bg-roseAcc/10 border border-roseAcc/30 text-roseAcc text-xs font-medium text-center">
          {{ errorMsg }}
        </div>

        <div class="grid grid-cols-2 gap-3 pt-2">
          <button 
            type="submit" 
            @click="isRegistering = false"
            :disabled="isLoading"
            class="w-full py-3 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs transition-all shadow-[0_4px_20px_rgba(163,230,53,0.3)] disabled:opacity-50 active:scale-95 cursor-pointer"
          >
            {{ isLoading && !isRegistering ? '...' : 'Se connecter' }}
          </button>
          
          <button 
            type="submit"
            @click="isRegistering = true"
            :disabled="isLoading"
            class="w-full py-3 rounded-full liquid-glass-pill hover:bg-white/10 border border-white/15 text-white font-bold text-xs transition-all disabled:opacity-50 active:scale-95 cursor-pointer"
          >
            {{ isLoading && isRegistering ? '...' : 'Créer compte' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { getApiBase } from '../config';

const emit = defineEmits(['login-success']);

const username = ref('');
const password = ref('');
const isRegistering = ref(false);
const isLoading = ref(false);
const errorMsg = ref('');

const handleAuth = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  
  const apiBase = getApiBase();
  if (!apiBase) {
    isLoading.value = false;
    errorMsg.value = "URL API non disponible.";
    return;
  }

  const endpoint = isRegistering.value ? '/api/auth/register' : '/api/auth/login';
  
  try {
    const res = await fetch(`${apiBase}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    });
    
    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data.detail || "Erreur d'authentification");
    }
    
    localStorage.setItem('pea_access_token', data.access_token);
    emit('login-success', { userId: data.user_id, username: data.username });
    
  } catch (err) {
    errorMsg.value = err.message || "Impossible de joindre le serveur. Vérifiez votre connexion.";
  } finally {
    isLoading.value = false;
  }
};
</script>
