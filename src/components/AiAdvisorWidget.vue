<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto glass-card border border-white/[0.08] rounded-36 shadow-2xl bg-[#111419] p-8 flex flex-col text-white">
      
      <!-- Header -->
      <div class="flex justify-between items-start mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center text-lavender font-bold">
            ✦
          </div>
          <div>
            <h2 class="text-2xl font-black text-white tracking-tight">AI Strategic Advisor (Groq)</h2>
            <p class="text-white/40 text-xs">Diagnostic holistique du portefeuille et recommandations PEA</p>
          </div>
        </div>

        <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors bg-white/[0.04] hover:bg-white/[0.08] p-2.5 rounded-full">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-20 space-y-4">
        <div class="relative w-16 h-16">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-neonPurple rounded-full border-t-transparent animate-spin"></div>
        </div>
        <p class="text-white/50 animate-pulse font-medium text-sm">Groq LLM analyse votre diversification et les risques sectoriels...</p>
      </div>

      <!-- Content -->
      <div v-else-if="diagnostic" class="space-y-6">
        <!-- Global Diagnostic Summary -->
        <div class="bg-gradient-to-br from-neonPurple/10 to-transparent rounded-28 p-6 border border-neonPurple/20">
          <h3 class="text-xs font-bold text-lavender uppercase tracking-widest mb-3 font-mono">Synthèse Stratégique Globale</h3>
          <p class="text-white/90 leading-relaxed font-medium text-sm sm:text-[15px]">
            {{ diagnostic.diagnostic_global }}
          </p>
        </div>

        <!-- Recommendations Grid -->
        <div v-if="diagnostic.recommandations_pea?.length" class="bg-[#16191E] rounded-28 p-6 border border-white/[0.06]">
          <h4 class="text-white/40 font-bold text-xs uppercase tracking-widest mb-4 font-mono">Plan d'Action Recommandé</h4>
          <div class="space-y-3">
            <div v-for="(rec, idx) in diagnostic.recommandations_pea" :key="idx" class="flex gap-3 items-start bg-white/[0.03] rounded-2xl p-4 border border-white/[0.04] hover:bg-white/[0.06] transition-all">
              <div class="text-neonLime mt-0.5 text-base">💡</div>
              <p class="text-white/80 text-xs sm:text-sm leading-relaxed font-medium">{{ rec }}</p>
            </div>
          </div>
        </div>

        <!-- Pros & Weaknesses -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-28 p-5">
            <h4 class="text-neonLime font-bold mb-3 flex items-center gap-2 text-xs uppercase tracking-wider font-mono">
              <span>↗</span>
              Forces du Portefeuille
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(pro, idx) in (diagnostic.points_forts || [])" :key="idx" class="flex items-start gap-2">
                <span class="text-neonLime mt-0.5">&bull;</span> {{ pro }}
              </p>
            </div>
          </div>

          <div class="bg-roseAcc/10 border border-roseAcc/20 rounded-28 p-5">
            <h4 class="text-roseAcc font-bold mb-3 flex items-center gap-2 text-xs uppercase tracking-wider font-mono">
              <span>↘</span>
              Risques & Vigilances
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(weak, idx) in (diagnostic.points_faibles || [])" :key="idx" class="flex items-start gap-2">
                <span class="text-roseAcc mt-0.5">&bull;</span> {{ weak }}
              </p>
            </div>
          </div>
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
  userId: String
});

defineEmits(['close']);

const isLoading = ref(false);
const diagnostic = ref(null);

watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.userId) {
    isLoading.value = true;
    try {
      const apiBase = getApiBase();
      const res = await fetch(`${apiBase}/api/portfolio/ai-diagnostic`, {
        headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') }
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
