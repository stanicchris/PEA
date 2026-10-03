<template>
  <div class="glass-card rounded-36 p-6 md:p-8 border border-white/[0.08] h-full flex flex-col">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-3">
      <span class="w-10 h-10 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">📅</span>
      Projections Annuelles
    </h3>
    <p class="text-white/40 text-xs mb-6">Estimation des dividendes sur les 12 prochains mois.</p>
    
    <div v-if="isLoading" class="flex-1 flex justify-center items-center">
      <div class="w-8 h-8 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin"></div>
    </div>
    
    <div v-else class="flex-1 flex items-end gap-1 sm:gap-2 h-48 mt-auto relative">
      <div 
        v-for="(amount, month) in chartData" 
        :key="month"
        class="flex-1 flex flex-col justify-end items-center group"
      >
        <div class="relative w-full flex justify-center">
          <!-- Tooltip -->
          <div class="absolute -top-10 opacity-0 group-hover:opacity-100 transition-opacity bg-black border border-white/10 text-xs rounded-lg px-2 py-1 pointer-events-none z-10 whitespace-nowrap">
            {{ formatCurrency(amount) }}
          </div>
          <!-- Bar -->
          <div 
            class="w-full max-w-[24px] bg-gradient-to-t from-indigo-600/50 to-indigo-400 rounded-t-md transition-all duration-500 group-hover:brightness-125"
            :style="{ height: `${Math.max((amount / maxAmount) * 100, 4)}%` }"
          ></div>
        </div>
        <span class="text-[10px] text-white/50 mt-2 font-mono uppercase">{{ monthNames[month - 1] }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  projections: {
    type: Object,
    default: () => ({})
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const monthNames = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];

const chartData = computed(() => {
  const data = {};
  for (let i = 1; i <= 12; i++) {
    data[i] = props.projections[i] || 0;
  }
  return data;
});

const maxAmount = computed(() => {
  const vals = Object.values(chartData.value);
  return Math.max(...vals, 1); // fallback to 1 to avoid /0
});

const formatCurrency = (val) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val || 0);
};
</script>
