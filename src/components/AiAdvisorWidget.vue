<template>
  <div class="glass rounded-3xl p-6 relative flex flex-col border border-white/5 bg-gradient-to-br from-[#151921] to-[#1a2130]">
    
    <!-- Header: Title & Weather Emoji -->
    <div class="flex justify-between items-center mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(59,130,246,0.15)]">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
        </div>
        <h3 class="text-xl font-bold tracking-tight">AI Advisor</h3>
      </div>
      
      <!-- Weather Badge -->
      <div v-if="!isLoading && weather" class="flex items-center gap-2 px-3 py-1.5 bg-white/5 rounded-full border border-white/10 shadow-inner">
        <span class="text-xl">{{ weather.emoji }}</span>
        <span class="text-sm font-semibold tracking-wide text-white/90">{{ weather.text }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center space-y-4 py-8">
      <div class="relative">
        <div class="w-12 h-12 rounded-full border-4 border-white/10 border-t-blue-500 animate-spin"></div>
        <div class="absolute inset-0 flex items-center justify-center text-blue-500">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
        </div>
      </div>
      <p class="text-white/50 text-sm font-medium text-center animate-pulse">Groq LLM analyse les marchés en temps réel...</p>
    </div>

    <!-- Pre-load State (Button) -->
    <div v-else-if="!diagnostic && !isLoading" class="flex-1 flex flex-col items-center justify-center space-y-5 py-8">
      <p class="text-white/50 text-sm font-medium text-center max-w-md">
        L'IA peut analyser vos positions, lire l'actualité financière récente, et générer un diagnostic complet de votre portefeuille.
      </p>
      <button @click="fetchAiData" class="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
        Lancer l'Analyse IA
      </button>
    </div>

    <!-- Content -->
    <div v-else-if="diagnostic" class="flex flex-col md:flex-row gap-6">
      
      <!-- Diagnostic Text (Left) -->
      <div class="flex-1">
        <p class="text-white/80 text-[15px] leading-relaxed mb-6 font-medium">
          {{ diagnostic.diagnostic_global }}
        </p>

        <!-- Recommendations -->
        <div v-if="diagnostic.recommandations_pea?.length">
          <h4 class="text-white/40 font-bold text-xs uppercase tracking-widest mb-3">Plan d'Action Recommandé</h4>
          <div class="space-y-2">
            <div v-for="(rec, idx) in diagnostic.recommandations_pea" :key="idx" class="flex gap-3 items-start bg-white/5 rounded-xl p-3 border border-white/5 transition-all hover:bg-white/10">
               <div class="text-blue-400 mt-0.5 text-lg">💡</div>
               <p class="text-white/70 text-sm leading-relaxed font-medium">{{ rec }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Strengths & Weaknesses (Right) -->
      <div class="flex-1 flex flex-col gap-4">
        
        <!-- Points Forts -->
        <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4 flex-1">
          <h4 class="text-emerald-400 font-bold text-xs uppercase tracking-widest mb-3 flex items-center gap-2">
            <div class="bg-emerald-500/20 p-1 rounded">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
            </div>
            Points Forts
          </h4>
          <ul class="space-y-2">
            <li v-for="(item, idx) in diagnostic.points_forts" :key="idx" class="text-emerald-100/80 text-sm leading-snug flex items-start gap-2">
              <span class="text-emerald-500 mt-0.5">•</span> {{ item }}
            </li>
          </ul>
        </div>

        <!-- Risques -->
        <div class="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4 flex-1">
          <h4 class="text-rose-400 font-bold text-xs uppercase tracking-widest mb-3 flex items-center gap-2">
            <div class="bg-rose-500/20 p-1 rounded">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>
            </div>
            Points de Vigilance
          </h4>
          <ul class="space-y-2">
            <li v-for="(item, idx) in diagnostic.alertes_et_risques" :key="idx" class="text-rose-100/80 text-sm leading-snug flex items-start gap-2">
              <span class="text-rose-500 mt-0.5">•</span> {{ item }}
            </li>
          </ul>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
import { ref } from 'vue';

const diagnostic = ref(null);
const weather = ref(null);
const isLoading = ref(false);
const error = ref(null);

const props = defineProps({
  userId: { type: String, required: true }
});

const fetchAiData = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const [diagRes, weatherRes] = await Promise.all([
      fetch(`${API_BASE}/api/portfolio/ai-diagnostic?user_id=${props.userId}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } }),
      fetch(`${API_BASE}/api/portfolio/weather?user_id=${props.userId}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } })
    ]);

    if (!diagRes.ok || !weatherRes.ok) {
      throw new Error("Erreur de connexion à l'API IA.");
    }

    diagnostic.value = await diagRes.json();
    weather.value = await weatherRes.json();
  } catch (err) {
    console.error("AI Advisor error:", err);
    error.value = "Impossible de joindre l'IA Groq.";
    
    // Fallback display if AI fails
    diagnostic.value = {
        diagnostic_global: "Mode de secours activé. L'IA a rencontré une erreur ou un rate limit.",
        points_forts: ["Vos données ont été calculées via l'algorithme financier de base."],
        alertes_et_risques: ["Connexion à Groq échouée."],
        recommandations_pea: ["Vérifiez votre clé GROQ_API_KEY", "Réessayez dans quelques instants"]
    };
    weather.value = { emoji: '🌩️', text: 'Déconnecté' };
  } finally {
    isLoading.value = false;
  }
};
</script>
