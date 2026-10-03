<template>
  <div class="min-h-screen flex items-center justify-center bg-[#080A0E] p-4 font-sans relative overflow-hidden">
    <!-- Subtle Background Glows -->
    <div class="absolute inset-0 z-0 pointer-events-none opacity-20">
      <div class="absolute top-[20%] left-[20%] w-96 h-96 bg-neonPurple rounded-full mix-blend-screen filter blur-[140px]"></div>
      <div class="absolute bottom-[20%] right-[20%] w-96 h-96 bg-neonLime rounded-full mix-blend-screen filter blur-[140px]"></div>
    </div>

    <div class="glass-card relative z-10 w-full max-w-md p-8 sm:p-10 rounded-36 border border-white/[0.08] shadow-2xl bg-[#111419]">
      <div class="text-center mb-8">
        <div class="mx-auto w-14 h-14 bg-neonLime rounded-2xl flex items-center justify-center font-black text-black text-2xl mb-4 shadow-[0_0_30px_rgba(163,230,53,0.3)]">
          P
        </div>
        <h1 class="text-2xl font-black text-white tracking-tight">PEA Tracker SaaS</h1>
        <p class="text-white/40 text-xs mt-1.5 font-medium">Terminal financier privé & Copilote IA</p>
      </div>

      <form @submit.prevent="handleAuth" class="space-y-4">
        <div>
          <label class="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5 font-mono">Identifiant / Compte</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="Ex: chris"
            class="w-full bg-[#0C0E12] border border-white/[0.08] rounded-full px-5 py-3 text-white placeholder-white/20 focus:outline-none focus:border-neonLime transition-all text-sm font-medium"
            required
          />
        </div>
        
        <div>
          <label class="block text-[11px] font-semibold text-white/50 uppercase tracking-wider mb-1.5 font-mono">Mot de passe</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••••"
            class="w-full bg-[#0C0E12] border border-white/[0.08] rounded-full px-5 py-3 text-white placeholder-white/20 focus:outline-none focus:border-neonLime transition-all text-sm font-medium"
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
            class="w-full py-3 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-extrabold text-xs transition-all shadow-[0_4px_20px_rgba(163,230,53,0.25)] disabled:opacity-50 active:scale-95"
          >
            {{ isLoading && !isRegistering ? '...' : 'Se connecter' }}
          </button>
          
          <button 
            type="submit"
            @click="isRegistering = true"
            :disabled="isLoading"
            class="w-full py-3 rounded-full bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-white font-bold text-xs transition-all disabled:opacity-50 active:scale-95"
          >
            {{ isLoading && isRegistering ? '...' : 'Créer un compte' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
import { ref } from 'vue';

const emit = defineEmits(['login-success']);

const username = ref('');
const password = ref('');
const isRegistering = ref(false);
const isLoading = ref(false);
const errorMsg = ref('');

const handleAuth = async () => {
  isLoading.value = true;
  errorMsg.value = '';
  
  const endpoint = isRegistering.value ? '/api/auth/register' : '/api/auth/login';
  
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
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
    errorMsg.value = err.message;
  } finally {
    isLoading.value = false;
  }
};
</script>
