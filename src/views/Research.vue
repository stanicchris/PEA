<template>
  <div class="space-y-6 pb-20">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="text-neonPurple">🧠</span> Recherche & Intelligence Artificielle
      </h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- BourseAi Assistant -->
      <div class="liquid-glass-chassis rounded-48 p-8 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-neonPurple/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10 h-full flex flex-col items-start justify-center">
          <div class="w-16 h-16 rounded-3xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center text-3xl mb-6 shadow-[0_0_20px_rgba(139,92,246,0.3)]">
            ✦
          </div>
          <h2 class="text-3xl font-black text-white mb-4 tracking-tight">Directeur Financier<br/>Virtuel.</h2>
          <p class="text-white/50 text-sm mb-8 max-w-md leading-relaxed">
            Échangez avec BourseAi, propulsé par l'IA Groq (Llama-3). Il connait vos lignes en temps réel et peut auditer votre portefeuille en quelques millisecondes.
          </p>
          <button 
            @click="store.isAiAdvisorOpen = true"
            class="px-8 py-3 rounded-full bg-white text-black font-bold hover:bg-neonPurple hover:text-white hover:shadow-[0_0_20px_rgba(139,92,246,0.4)] transition-all flex items-center gap-2 active:scale-95"
          >
            Lancer une analyse 
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
          </button>
        </div>
      </div>

      <!-- Optimization / Scanner (Legacy/Other tools) -->
      <div class="space-y-6">
        <OptimizationView 
          :userId="store.userId" 
          :isAiLoading="store.isAiLoading" 
          @trigger-ai="store.isAiAdvisorOpen = true" 
          class="h-full"
        />
      </div>

    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import OptimizationView from './OptimizationView.vue'

const store = useAppStore()
</script>
