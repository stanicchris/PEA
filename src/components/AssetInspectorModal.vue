<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-4">
    <!-- Backdrop with blur -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-xl cursor-pointer" @click="$emit('close')"></div>
    
    <!-- Modal Content (Liquid Glass) -->
    <div class="relative w-full max-w-4xl max-h-[92dvh] overflow-y-auto liquid-glass-chassis rounded-36 shadow-2xl p-5 sm:p-8 flex flex-col text-white specular-highlight border border-white/15">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6 pb-2 border-b border-white/[0.06] sticky top-0 bg-[#0A0D14]/80 backdrop-blur-md -mx-2 px-2 z-10">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="px-2.5 py-0.5 rounded-full bg-neonLime/15 border border-neonLime/30 text-neonLime text-xs font-mono font-bold shadow-[0_0_10px_rgba(163,230,53,0.15)]">BourseAi 2.0</span>
            <span class="text-white/40 text-xs font-mono">{{ asset?.ticker }}</span>
          </div>
          <h2 class="text-xl sm:text-3xl font-black text-white tracking-tight">{{ asset?.name }}</h2>
          <p class="text-white/50 text-xs mt-0.5 font-medium">{{ asset?.sector }}</p>
        </div>
        <button 
          @click="$emit('close')" 
          class="text-white/40 hover:text-white transition-colors liquid-glass-subtle hover:border-white/20 p-2.5 rounded-full cursor-pointer active:scale-95"
          title="Fermer"
          aria-label="Fermer"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-16 sm:py-20">
        <div class="relative w-16 h-16 mb-6">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-neonLime rounded-full border-t-transparent animate-spin"></div>
        </div>
        <p class="text-white/60 animate-pulse font-medium text-xs sm:text-sm text-center px-4">Analyse instantanée des fondamentaux et ratios en direct...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="bg-roseAcc/10 border border-roseAcc/20 text-roseAcc p-6 rounded-24 text-sm font-medium">
        {{ error }}
      </div>

      <!-- Content -->
      <div v-else-if="analysis" class="space-y-6">
        
        <!-- Score & Recommendation -->
        <div class="flex flex-col md:flex-row gap-4 items-stretch">
          <div class="flex-1 liquid-glass-card rounded-28 p-5 sm:p-6 flex items-center gap-5 sm:gap-6 specular-highlight">
             <div class="relative w-24 h-24 sm:w-28 sm:h-28 shrink-0 flex items-center justify-center rounded-full shadow-lg" 
                  :style="`background: conic-gradient(${analysis.score_percent >= 60 ? '#A3E635' : (analysis.score_percent >= 40 ? '#F59E0B' : '#F43F5E')} ${analysis.score_percent}%, rgba(255,255,255,0.05) 0);`">
                <div class="absolute inset-2 bg-[#0C1017] rounded-full flex items-center justify-center flex-col shadow-inner">
                  <span class="text-2xl sm:text-3xl font-black" :class="analysis.score_percent >= 60 ? 'text-neonLime' : (analysis.score_percent >= 40 ? 'text-amberAcc' : 'text-roseAcc')">{{ analysis.score_percent }}%</span>
                </div>
             </div>
             <div>
                <p class="text-white/40 text-xs uppercase font-bold tracking-wider mb-1 font-mono">Score BourseAi</p>
                <p class="text-xl sm:text-2xl font-black" :class="analysis.should_invest ? 'text-neonLime' : 'text-amberAcc'">
                  {{ analysis.should_invest ? 'Opportunité Favorable' : 'À Surveiller' }}
                </p>
                <p class="text-white/40 text-[11px] mt-1 font-mono">{{ analysis.source }}</p>
             </div>
          </div>
          
          <div class="flex-1 grid grid-cols-2 gap-3">
             <div class="liquid-glass-subtle rounded-24 p-3.5 sm:p-4 border border-white/10">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Dernier Cours</p>
                <p class="text-lg sm:text-xl font-bold text-white font-mono">{{ analysis.metrics?.price?.toFixed(2) }} €</p>
             </div>
             <div class="liquid-glass-subtle rounded-24 p-3.5 sm:p-4 border border-white/10">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Objectif Analystes</p>
                <p class="text-lg sm:text-xl font-bold text-neonLime font-mono">{{ analysis.metrics?.target_price?.toFixed(2) }} €</p>
             </div>
             <div class="liquid-glass-subtle rounded-24 p-3.5 sm:p-4 border border-white/10">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Rendement Div.</p>
                <p class="text-lg sm:text-xl font-bold text-lavender font-mono">{{ analysis.metrics?.div_yield?.toFixed(2) }} %</p>
             </div>
             <div class="liquid-glass-subtle rounded-24 p-3.5 sm:p-4 border border-white/10">
                <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Recommandation</p>
                <p class="text-base font-bold text-neonLime font-mono">{{ analysis.metrics?.recommendation || 'ACHAT' }}</p>
             </div>
          </div>
        </div>

        <!-- Synthesis Box -->
        <div class="liquid-glass-card rounded-28 p-5 sm:p-6 specular-highlight">
          <h4 class="text-white/40 font-bold text-xs uppercase tracking-widest mb-2 font-mono">Synthèse Fondamentale & Activité</h4>
          <p class="text-white/90 leading-relaxed font-medium text-xs sm:text-sm">
            {{ analysis.summary }}
          </p>
        </div>

        <!-- Pros and Cons -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-28 p-4 sm:p-5 shadow-[0_0_20px_rgba(163,230,53,0.08)]">
            <h4 class="text-neonLime font-bold mb-3 flex items-center gap-2 text-xs sm:text-sm">
              <span>↗</span>
              Points Forts & Catalyseurs
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(pro, i) in (analysis.pros || '').split('•')" :key="'p'+i" v-show="pro.trim()" class="flex items-start gap-2">
                 <span class="text-neonLime mt-0.5">&bull;</span> {{ pro.trim() }}
              </p>
            </div>
          </div>
          
          <div class="bg-roseAcc/10 border border-roseAcc/20 rounded-28 p-4 sm:p-5 shadow-[0_0_20px_rgba(244,63,94,0.08)]">
            <h4 class="text-roseAcc font-bold mb-3 flex items-center gap-2 text-xs sm:text-sm">
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
        
        <!-- Bottom Action Bar -->
        <div class="pt-4 border-t border-white/[0.08] flex flex-col sm:flex-row items-center justify-between gap-3">
          <a 
            v-if="analysis.target_url" 
            :href="analysis.target_url" 
            target="_blank" 
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 text-neonLime hover:text-white text-xs font-bold transition-colors liquid-glass-pill hover:bg-white/10 px-5 py-2.5 rounded-full border border-white/15 active:scale-95"
          >
            Ouvrir sur ZoneBourse
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
          </a>
          
          <button 
            @click="goToDetail"
            class="w-full sm:w-auto px-6 py-2.5 rounded-full liquid-glass-subtle bg-neonLime/10 text-neonLime font-bold text-xs border border-neonLime/30 hover:bg-neonLime/20 transition-all cursor-pointer active:scale-95"
          >
            Voir la fiche détaillée
          </button>
          
          <button 
            @click="$emit('close')" 
            class="w-full sm:w-auto px-6 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 text-white font-bold text-xs border border-white/15 hover:border-white/30 transition-all cursor-pointer active:scale-95"
          >
            Fermer l'analyse
          </button>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { getApiBase } from '../config';

const props = defineProps({
  isOpen: Boolean,
  asset: Object
});
const emit = defineEmits(['close']);

const isLoading = ref(false);
const error = ref(null);
const analysis = ref(null);
const router = useRouter();

const goToDetail = () => {
  emit('close');
  router.push(`/stock/${props.asset.ticker || props.asset.name}`);
};

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close');
  }
};

onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));

watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.asset) {
    isLoading.value = true;
    error.value = null;
    analysis.value = null;
    try {
      const apiBase = getApiBase();
      const qName = encodeURIComponent(props.asset.name);
      const res = await fetch(`${apiBase}/api/stock/analyze/${props.asset.ticker || props.asset.name}?name=${qName}`, { 
        headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') } 
      });
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
