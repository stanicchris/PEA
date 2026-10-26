<template>
  <div class="liquid-glass-card rounded-32 p-5 sm:p-7 flex flex-col justify-between h-full relative overflow-hidden group specular-highlight">
    <!-- Top Row: Title + AI Trigger -->
    <div class="flex justify-between items-center mb-3">
      <h3 class="text-white font-bold text-lg tracking-tight">Santé & Plus-Value</h3>
      <button
        @click="$emit('open-ai')"
        class="text-white/40 hover:text-neonLime transition-colors p-1.5 rounded-full liquid-glass-subtle cursor-pointer"
        title="Ouvrir le diagnostic IA"
        aria-label="Ouvrir le diagnostic IA"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
        </svg>
      </button>
    </div>

    <!-- Status Badge & Metric -->
    <div class="space-y-1.5 mb-2">
      <button
        type="button"
        @click="$emit('open-ai')"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-neonPurple/15 border border-neonPurple/30 text-lavender text-xs font-semibold cursor-pointer hover:bg-neonPurple/25 transition-all shadow-[0_0_15px_rgba(139,92,246,0.15)] active:scale-95"
        title="Cliquez pour lancer le diagnostic IA complet"
      >
        <span>{{ weather?.text || (perfPct >= 0 ? 'Momentum Positif' : 'Consolidation') }}</span>
        <span class="text-xs">{{ weather?.emoji || (perfPct >= 0 ? '☀️' : '⛅') }}</span>
        <span class="text-[10px] text-white/50 ml-1 font-normal">✦ Groq AI</span>
      </button>

      <div class="flex items-baseline gap-2 pt-1 flex-wrap">
        <span class="text-2xl sm:text-3xl font-black tracking-tight tabular-numbers drop-shadow-sm" :class="gainValue >= 0 ? 'text-white' : 'text-roseAcc'">
          {{ formatPrice(gainValue) }}
        </span>
        <span class="text-xs font-bold font-mono" :class="perfPct >= 0 ? 'text-neonLime' : 'text-roseAcc'">
          {{ perfPct >= 0 ? '+' : '' }}{{ Number(perfPct || 0).toFixed(2) }}% vs PRU
        </span>
      </div>
    </div>

    <!-- Animated Soundwave Equalizer Graphic -->
    <div class="h-20 sm:h-24 flex items-end justify-between gap-1.5 px-1 my-2">
      <div
        v-for="(bar, index) in soundwaveBars"
        :key="index"
        class="w-2 rounded-full transition-all duration-500 hover:opacity-100 opacity-90 shadow-sm animate-equalizer"
        :style="{
          height: bar.height + '%',
          backgroundColor: bar.color,
          boxShadow: '0 0 10px ' + bar.color + '40',
          animationDelay: (index * 110) + 'ms'
        }"
      ></div>
    </div>

    <!-- Bottom Notice Info -->
    <div class="pt-3 border-t border-white/[0.08] flex items-center justify-between gap-2 text-white/40 text-[11px]">
      <div class="flex items-center gap-1.5 min-w-0">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0 text-neonPurple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="truncate">Sentiment IA & plus-value latente</span>
      </div>
      <button @click="$emit('open-ai')" class="text-lavender hover:text-neonLime font-bold shrink-0 cursor-pointer">
        Auditer →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  weather: { type: Object, default: () => null },
  isLoading: { type: Boolean, default: false }
})

defineEmits(['open-ai'])

const gainValue = computed(() => {
  return props.summary?.global_performance_value ?? 0
})

const perfPct = computed(() => {
  return props.summary?.global_performance_pct ?? 0
})

const formatPrice = (val) => {
  if (store.isDiscreteMode) return '••• €'
  return (val >= 0 ? '+' : '') + (val || 0).toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })
}

const soundwaveBars = [
  { height: 35, color: '#8B5CF6' },
  { height: 55, color: '#A78BFA' },
  { height: 75, color: '#98F794' },
  { height: 42, color: '#8B5CF6' },
  { height: 90, color: '#A3E635' },
  { height: 60, color: '#A78BFA' },
  { height: 85, color: '#98F794' },
  { height: 48, color: '#8B5CF6' },
  { height: 100, color: '#A3E635' },
  { height: 70, color: '#A78BFA' },
  { height: 80, color: '#98F794' },
  { height: 50, color: '#8B5CF6' },
  { height: 95, color: '#A3E635' },
  { height: 65, color: '#A78BFA' },
  { height: 85, color: '#98F794' },
  { height: 45, color: '#8B5CF6' },
  { height: 75, color: '#A3E635' },
  { height: 88, color: '#A78BFA' }
]
</script>
