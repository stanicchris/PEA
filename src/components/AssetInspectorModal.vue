<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto glass-card border border-white/[0.08] rounded-36 shadow-2xl bg-[#111419] p-8 flex flex-col text-white">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full bg-neonLime/15 text-neonLime text-xs font-mono font-bold">BourseAi 2.0</span>
            <span class="text-white/40 text-xs font-mono">{{ asset?.ticker }}</span>
          </div>
          <h2 class="text-3xl font-black text-white tracking-tight">{{ asset?.name }}</h2>
          <p class="text-white/50 text-xs mt-0.5 font-medium">{{ asset?.sector }}</p>
        </div>
        <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors bg-white/[0.04] hover:bg-white/[0.08] p-2.5 rounded-full">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-20">
        <div class="relative w-16 h-16 mb-6">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-neonLime rounded-full border-t-transparent animate-spin"></div>
        </div>
        <p class="text-white/50 animate-pulse font-medium text-sm">Groq AI compile les fondamentaux et ratios en temps réel...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="bg-roseAcc/10 border border-roseAcc/20 text-roseAcc p-6 rounded-24 text-sm font-medium">
        {{ error }}
      </div>

      <!-- Content -->
      <div v-else-if="analysis" class="space-y-6">
        
        <!-- Score & Recommendation -->
        <div class="flex flex-col md:flex-row gap-4 items-stretch">
          <div class="flex-1 bg-[#16191E] rounded-28 p-6 border border-white/[0.08] flex items-center gap-6">
             <div class="relative w-28 h-28 shrink-0 flex items-center justify-center rounded-full" 
                  :style="`background: conic-gradient(${analysis.score_percent >= 60 ? '#A3E635' : (analysis.score_percent >= 40 ? '#F59E0B' : '#F43F5E')} ${analysis.score_percent}%, rgba(255,255,255,0.05) 0);`">
                <div class="absolute inset-2 bg-[#111419] rounded-full flex items-center justify-center flex-col shadow-inner">
                  <span class="text-3xl font-black" :class="analysis.score_percent >= 60 ? 'text-neonLime' : (analysis.score_percent >= 40 ? 'text-amberAcc' : 'text-roseAcc')">{{ analysis.score_percent }}%</span>
                </div>
             </div>
             <div>
                <p class="text-white/40 text-xs uppercase font-bold tracking-wider mb-1 font-mono">Score BourseAi</p>
                <p class="text-2xl font-black" :class="analysis.should_invest ? 'text-neonLime' : 'text-amberAcc'">
                  {{ analysis.should_invest ? 'Opportunité Favorable' : 'À Surveiller' }}
                </p>
                <p class="text-white/40 text-xs mt-2 font-mono">{{ analysis.source }}</p>
             </div>
          </div>
          
          <div class="flex-1 grid grid-cols-2 gap-3">
             <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Dernier Cours</p>
                <p class="text-xl font-bold text-white font-mono">{{ analysis.metrics?.price?.toFixed(2) }} €</p>
             </div>
             <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Objectif Analystes</p>
                <p class="text-xl font-bold text-neonLime font-mono">{{ analysis.metrics?.target_price?.toFixed(2) }} €</p>
             </div>
             <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Rendement Div.</p>
                <p class="text-xl font-bold text-lavender font-mono">{{ analysis.metrics?.div_yield?.toFixed(2) }} %</p>
             </div>
             <div class="bg-[#16191E] rounded-24 p-4 border border-white/[0.06]">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">PER</p>
                <p class="text-xl font-bold text-white font-mono">{{ analysis.metrics?.per?.toFixed(1) }}x</p>
             </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="bg-neonPurple/10 rounded-28 p-6 border border-neonPurple/20 relative overflow-hidden">
          <div class="absolute -right-10 -top-10 w-32 h-32 bg-neonPurple/10 rounded-full blur-3xl"></div>
          <h3 class="text-xs font-bold text-lavender uppercase tracking-widest mb-2 flex items-center gap-2 font-mono">
            <span>✦</span>
            Synthèse Fondamentale
          </h3>
          <p class="text-white/90 leading-relaxed font-medium text-sm">{{ analysis.summary }}</p>
        </div>

        <!-- Pros & Cons -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-28 p-5">
            <h4 class="text-neonLime font-bold mb-3 flex items-center gap-2 text-sm">
              <span>↗</span>
              Points Forts & Catalyseurs
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(pro, i) in (analysis.pros || '').split('•')" :key="'p'+i" v-show="pro.trim()" class="flex items-start gap-2">
                 <span class="text-neonLime mt-0.5">&bull;</span> {{ pro.trim() }}
              </p>
            </div>
          </div>
          
          <div class="bg-roseAcc/10 border border-roseAcc/20 rounded-28 p-5">
            <h4 class="text-roseAcc font-bold mb-3 flex items-center gap-2 text-sm">
              <span>↘</span>
              Risques & Vigilances
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(con, i) in (analysis.cons || '').split('•')" :key="'c'+i" v-show="con.trim()" class="flex items-start gap-2">
                 <span class="text-roseAcc mt-0.5">&bull;</span> {{ con.trim() }}
              </p>
            </div>
          </div>
        </div>
        
        <div class="text-center pt-2" v-if="analysis.target_url">
          <a :href="analysis.target_url" target="_blank" class="inline-flex items-center gap-2 text-neonLime hover:text-white text-xs font-bold transition-colors bg-white/[0.04] hover:bg-white/[0.08] px-4 py-2.5 rounded-full border border-white/[0.08]">
            Ouvrir la fiche sur ZoneBourse
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </a>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { getApiBase } from '../config';

const props = defineProps({
  isOpen: Boolean,
  asset: Object
});
defineEmits(['close']);

const isLoading = ref(false);
const error = ref(null);
const analysis = ref(null);

watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.asset) {
    isLoading.value = true;
    error.value = null;
    analysis.value = null;
    try {
      const apiBase = getApiBase();
      const qName = encodeURIComponent(props.asset.name);
      const res = await fetch(`${apiBase}/api/stock/analyze/${props.asset.ticker}?name=${qName}`, { headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') } });
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
