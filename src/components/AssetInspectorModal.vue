<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto glass border border-white/10 rounded-3xl shadow-2xl bg-[#0E1117] p-8 flex flex-col">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-3xl font-black text-white tracking-tight">{{ asset?.name }}</h2>
          <p class="text-white/50 text-sm mt-1 font-medium">{{ asset?.ticker }} &bull; {{ asset?.sector }}</p>
        </div>
        <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors bg-white/5 hover:bg-white/10 p-2 rounded-full">
          <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-20">
        <div class="relative w-16 h-16 mb-6">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-blue-500 rounded-full border-t-transparent animate-spin"></div>
        </div>
        <p class="text-white/50 animate-pulse font-medium text-lg">BourseAi compile les données de marché et génère l'analyse...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-6 rounded-2xl">
        {{ error }}
      </div>

      <!-- Content -->
      <div v-else-if="analysis" class="space-y-6">
        
        <!-- Score & Recommendation -->
        <div class="flex flex-col md:flex-row gap-4 items-stretch">
          <div class="flex-1 bg-gradient-to-br from-[#151921] to-[#1a2130] rounded-2xl p-6 border border-white/10 flex items-center gap-6">
             <div class="relative w-28 h-28 shrink-0 flex items-center justify-center rounded-full" 
                  :style="`background: conic-gradient(${analysis.score_percent >= 60 ? '#10b981' : (analysis.score_percent >= 40 ? '#f59e0b' : '#f43f5e')} ${analysis.score_percent}%, transparent 0);`">
                <div class="absolute inset-2 bg-[#151921] rounded-full flex items-center justify-center flex-col shadow-inner">
                  <span class="text-3xl font-black" :class="analysis.score_percent >= 60 ? 'text-emerald-400' : (analysis.score_percent >= 40 ? 'text-amber-400' : 'text-rose-400')">{{ analysis.score_percent }}%</span>
                </div>
             </div>
             <div>
                <p class="text-white/50 text-xs uppercase font-bold tracking-wider mb-1">Score BourseAi</p>
                <p class="text-2xl font-black" :class="analysis.should_invest ? 'text-emerald-400' : 'text-amber-400'">
                  {{ analysis.should_invest ? 'Opportunité Favorable' : 'À Surveiller' }}
                </p>
                <p class="text-white/40 text-xs mt-2">{{ analysis.source }}</p>
             </div>
          </div>
          
          <div class="flex-1 grid grid-cols-2 gap-4">
             <div class="bg-white/5 rounded-2xl p-4 border border-white/10">
                <p class="text-white/50 text-xs font-semibold mb-1 uppercase tracking-wider">Dernier Cours</p>
                <p class="text-2xl font-bold text-white">{{ analysis.metrics?.price?.toFixed(2) }} €</p>
             </div>
             <div class="bg-white/5 rounded-2xl p-4 border border-white/10">
                <p class="text-white/50 text-xs font-semibold mb-1 uppercase tracking-wider">Objectif Analystes</p>
                <p class="text-2xl font-bold text-blue-400">{{ analysis.metrics?.target_price?.toFixed(2) }} €</p>
             </div>
             <div class="bg-white/5 rounded-2xl p-4 border border-white/10">
                <p class="text-white/50 text-xs font-semibold mb-1 uppercase tracking-wider">Rendement Div.</p>
                <p class="text-2xl font-bold text-yellow-400">{{ analysis.metrics?.div_yield?.toFixed(2) }} %</p>
             </div>
             <div class="bg-white/5 rounded-2xl p-4 border border-white/10">
                <p class="text-white/50 text-xs font-semibold mb-1 uppercase tracking-wider">PER</p>
                <p class="text-2xl font-bold text-white">{{ analysis.metrics?.per?.toFixed(1) }}x</p>
             </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="bg-gradient-to-br from-blue-900/20 to-purple-900/20 rounded-2xl p-6 border border-blue-500/20 relative overflow-hidden">
          <div class="absolute -right-10 -top-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl"></div>
          <h3 class="text-sm font-bold text-blue-400 uppercase tracking-widest mb-3 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            Synthèse Fondamentale
          </h3>
          <p class="text-white/90 leading-relaxed font-medium text-[16px]">{{ analysis.summary }}</p>
        </div>

        <!-- Pros & Cons -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5">
            <h4 class="text-emerald-400 font-bold mb-4 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
              Arguments Haussiers
            </h4>
            <div class="text-emerald-100/90 text-[15px] whitespace-pre-line leading-relaxed space-y-2">
              <p v-for="(pro, i) in analysis.pros.split('•')" :key="'p'+i" v-show="pro.trim()" class="flex items-start gap-2">
                 <span class="text-emerald-500 mt-1">&bull;</span> {{ pro.trim() }}
              </p>
            </div>
          </div>
          
          <div class="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-5">
            <h4 class="text-rose-400 font-bold mb-4 flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              Points de Vigilance
            </h4>
            <div class="text-rose-100/90 text-[15px] whitespace-pre-line leading-relaxed space-y-2">
              <p v-for="(con, i) in analysis.cons.split('•')" :key="'c'+i" v-show="con.trim()" class="flex items-start gap-2">
                 <span class="text-rose-500 mt-1">&bull;</span> {{ con.trim() }}
              </p>
            </div>
          </div>
        </div>
        
        <div class="text-center pt-4" v-if="analysis.target_url">
          <a :href="analysis.target_url" target="_blank" class="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm font-bold transition-colors bg-blue-500/10 hover:bg-blue-500/20 px-4 py-2 rounded-lg">
            Ouvrir la fiche détaillée sur ZoneBourse
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </a>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
import { ref, watch } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  asset: Object
});
const emit = defineEmits(['close']);

const isLoading = ref(false);
const error = ref(null);
const analysis = ref(null);

watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.asset) {
    isLoading.value = true;
    error.value = null;
    analysis.value = null;
    try {
      const qName = encodeURIComponent(props.asset.name);
      const res = await fetch(`${API_BASE}/api/stock/analyze/${props.asset.ticker}?name=${qName}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } });
      if (!res.ok) throw new Error("Erreur de récupération de l'analyse");
      analysis.value = await res.json();
    } catch (err) {
      error.value = err.message;
    } finally {
      isLoading.value = false;
    }
  }
});
</script>
