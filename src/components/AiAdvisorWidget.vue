<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-4">
    <!-- Backdrop with blur -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-xl cursor-pointer" @click="$emit('close')"></div>
    
    <!-- Modal Content (Liquid Glass) -->
    <div class="relative w-full max-w-4xl max-h-[92dvh] overflow-y-auto liquid-glass-chassis rounded-36 shadow-2xl p-5 sm:p-8 flex flex-col text-white specular-highlight border border-white/15">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6 pb-2 border-b border-white/[0.06] sticky top-0 bg-[#0A0D14]/80 backdrop-blur-md -mx-2 px-2 z-10">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center text-lavender font-bold shadow-[0_0_15px_rgba(139,92,246,0.3)]">
            ✦
          </div>
          <div>
            <h2 class="text-xl sm:text-2xl font-black text-white tracking-tight">AI Strategic Advisor (Groq)</h2>
            <p class="text-white/40 text-xs">Diagnostic holistique et recommandations PEA</p>
          </div>
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
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-16 sm:py-20 space-y-4">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-neonPurple rounded-full border-t-transparent animate-spin"></div>
        </div>
        <p class="text-white/50 animate-pulse font-medium text-xs sm:text-sm text-center px-4">Groq LLM analyse votre diversification et les risques sectoriels...</p>
      </div>

      <!-- Content -->
      <div v-else-if="diagnostic" class="space-y-6">
        <!-- Global Diagnostic Summary -->
        <div class="liquid-glass-card rounded-28 p-5 sm:p-6 border border-neonPurple/30 shadow-[0_0_25px_rgba(139,92,246,0.12)] specular-highlight">
          <h3 class="text-xs font-bold text-lavender uppercase tracking-widest mb-3 font-mono">Synthèse Stratégique Globale</h3>
          <p class="text-white/90 leading-relaxed font-medium text-xs sm:text-[15px]">
            {{ diagnostic.diagnostic_global }}
          </p>
        </div>

        <!-- Recommendations Grid -->
        <div v-if="diagnostic.recommandations_pea?.length" class="liquid-glass-card rounded-28 p-5 sm:p-6 specular-highlight">
          <h4 class="text-white/40 font-bold text-xs uppercase tracking-widest mb-4 font-mono">Plan d'Action Recommandé</h4>
          <div class="space-y-3">
            <div v-for="(rec, idx) in diagnostic.recommandations_pea" :key="idx" class="flex gap-3 items-start liquid-glass-subtle rounded-2xl p-4 border border-white/10 hover:border-white/20 transition-all">
              <div class="text-neonLime mt-0.5 text-base">💡</div>
              <p class="text-white/80 text-xs sm:text-sm leading-relaxed font-medium">{{ rec }}</p>
            </div>
          </div>
        </div>

        <!-- Pros & Weaknesses -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-28 p-4 sm:p-5 shadow-[0_0_20px_rgba(163,230,53,0.08)]">
            <h4 class="text-neonLime font-bold mb-3 flex items-center gap-2 text-xs uppercase tracking-wider font-mono">
              <span>↗</span>
              Forces du Portefeuille
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(pro, idx) in (diagnostic.points_forts || [])" :key="'p'+idx" class="flex items-start gap-2">
                <span class="text-neonLime mt-0.5">&bull;</span> {{ pro }}
              </p>
            </div>
          </div>

          <div class="bg-roseAcc/10 border border-roseAcc/20 rounded-28 p-4 sm:p-5 shadow-[0_0_20px_rgba(244,63,94,0.08)]">
            <h4 class="text-roseAcc font-bold mb-3 flex items-center gap-2 text-xs uppercase tracking-wider font-mono">
              <span>↘</span>
              Risques & Vigilances
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(weak, idx) in (diagnostic.points_faibles || [])" :key="'w'+idx" class="flex items-start gap-2">
                <span class="text-roseAcc mt-0.5">&bull;</span> {{ weak }}
              </p>
            </div>
          </div>
        </div>

        <!-- Bottom Action Bar -->
        <div class="pt-4 border-t border-white/[0.08] flex items-center justify-end">
          <button 
            @click="$emit('close')"
            class="w-full sm:w-auto px-6 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 text-white font-bold text-xs border border-white/15 hover:border-white/30 transition-all cursor-pointer active:scale-95"
          >
            Fermer le Diagnostic AI
          </button>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { getApiBase } from '../config';

const props = defineProps({
  isOpen: Boolean,
  userId: String
});

const emit = defineEmits(['close']);

const isLoading = ref(false);
const diagnostic = ref(null);

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close');
  }
};

onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));

watch(() => props.isOpen, async (newVal) => {
  if (newVal && !diagnostic.value) {
    isLoading.value = true;
    try {
      const apiBase = getApiBase();
      const token = localStorage.getItem('pea_access_token');
      const res = await fetch(`${apiBase}/api/portfolio/ai-diagnostic`, {
        headers: token ? { 'Authorization': 'Bearer ' + token } : {}
      });
      if (res.ok) {
        diagnostic.value = await res.json();
      }
    } catch (e) {
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  }
});
</script>
