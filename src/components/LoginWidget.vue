<template>
  <div class="min-h-screen flex items-center justify-center bg-[#0E1117] p-4 font-sans relative overflow-hidden">
    <!-- Decors de fond -->
    <div class="absolute inset-0 z-0 opacity-30">
      <div class="absolute top-[20%] left-[20%] w-96 h-96 bg-blue-600 rounded-full mix-blend-screen filter blur-[120px]"></div>
      <div class="absolute bottom-[20%] right-[20%] w-96 h-96 bg-sky-400 rounded-full mix-blend-screen filter blur-[120px]"></div>
    </div>

    <div class="glass relative z-10 w-full max-w-md p-8 rounded-3xl border border-white/10 shadow-2xl">
      <div class="text-center mb-8">
        <div class="mx-auto w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center font-bold text-white text-3xl mb-4 shadow-[0_0_20px_rgba(37,99,235,0.4)]">
          P
        </div>
        <h1 class="text-2xl font-bold text-white tracking-tight">PEA Tracker</h1>
        <p class="text-white/50 text-sm mt-2">Connectez-vous pour accéder à votre portefeuille IA</p>
      </div>

      <form @submit.prevent="handleAuth" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-white/70 uppercase tracking-widest mb-1.5">Nom de compte</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="Ex: chris"
            class="w-full bg-[#0E1117]/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
            required
          />
        </div>
        
        <div>
          <label class="block text-xs font-semibold text-white/70 uppercase tracking-widest mb-1.5">Mot de passe</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••••"
            class="w-full bg-[#0E1117]/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-white/20 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
            required
          />
        </div>

        <div v-if="errorMsg" class="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-medium text-center">
          {{ errorMsg }}
        </div>

        <div class="grid grid-cols-2 gap-3 pt-2">
          <button 
            type="submit" 
            @click="isRegistering = false"
            :disabled="isLoading"
            class="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50"
          >
            {{ isLoading && !isRegistering ? '...' : 'Se connecter' }}
          </button>
          
          <button 
            type="submit"
            @click="isRegistering = true"
            :disabled="isLoading"
            class="w-full py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold transition-all disabled:opacity-50"
          >
            {{ isLoading && isRegistering ? '...' : 'Créer compte' }}
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
    
    // Auth success
    localStorage.setItem('pea_access_token', data.access_token);
        emit('login-success', { userId: data.user_id, username: data.username });
    
  } catch (err) {
    errorMsg.value = err.message;
  } finally {
    isLoading.value = false;
  }
};
</script>
