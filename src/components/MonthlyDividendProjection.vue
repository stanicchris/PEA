<template>
  <div class="glass-card rounded-36 p-6 md:p-8 border border-white/[0.08] h-full flex flex-col justify-between">
    <!-- Header with Title and Total Annual Estimate -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-2">
      <div>
        <h3 class="text-xl font-bold text-white mb-1 flex items-center gap-3">
          <span class="w-10 h-10 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.2)]">📅</span>
          Projections Annuelles
        </h3>
        <p class="text-white/40 text-xs">Estimation des versements de dividendes sur les 12 prochains mois.</p>
      </div>

      <div class="text-left sm:text-right bg-indigo-500/10 border border-indigo-500/20 px-3.5 py-1.5 rounded-2xl shrink-0">
        <p class="text-[10px] text-indigo-300/70 uppercase tracking-widest font-mono font-bold">Total Projeté</p>
        <p class="text-lg sm:text-xl font-black text-indigo-300 font-mono tabular-nums">
          {{ formatCurrency(totalProjected) }}<span class="text-xs font-normal text-white/50"> / an</span>
        </p>
      </div>
    </div>
    
    <div v-if="isLoading" class="h-56 flex justify-center items-center">
      <div class="w-8 h-8 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin"></div>
    </div>
    
    <!-- Chart Container -->
    <div v-else class="h-56 w-full flex flex-col justify-end pt-4 pb-2 relative">
      <!-- Background Guide Lines -->
      <div class="absolute inset-x-0 top-6 bottom-8 flex flex-col justify-between pointer-events-none opacity-10">
        <div class="border-b border-dashed border-white w-full"></div>
        <div class="border-b border-dashed border-white w-full"></div>
        <div class="border-b border-dashed border-white w-full"></div>
      </div>

      <!-- Month Columns -->
      <div class="flex-1 w-full flex items-end gap-1.5 sm:gap-3 relative z-10">
        <div 
          v-for="(amount, month) in chartData" 
          :key="month"
          class="flex-1 h-full flex flex-col justify-end items-center group cursor-pointer"
        >
          <!-- Bar Track -->
          <div class="relative w-full flex-1 flex items-end justify-center pb-2">
            <!-- Tooltip -->
            <div class="absolute -top-6 opacity-0 group-hover:opacity-100 transition-all duration-200 bg-[#0C1017] border border-indigo-500/40 text-[11px] font-mono font-bold text-indigo-200 rounded-lg px-2 py-1 shadow-2xl pointer-events-none z-30 whitespace-nowrap transform -translate-y-1 group-hover:translate-y-0">
              {{ formatCurrency(amount) }}
            </div>

            <!-- Active Bar (amount > 0) -->
            <div 
              v-if="amount > 0"
              class="w-full max-w-[28px] bg-gradient-to-t from-indigo-700 via-indigo-500 to-indigo-400 group-hover:from-indigo-600 group-hover:to-indigo-300 rounded-t-lg transition-all duration-500 shadow-[0_0_15px_rgba(99,102,241,0.3)] group-hover:shadow-[0_0_20px_rgba(99,102,241,0.5)]"
              :style="{ height: `${Math.max(Math.round((amount / maxAmount) * 100), 10)}%` }"
            ></div>

            <!-- Empty Bar Slot (amount == 0) -->
            <div 
              v-else
              class="w-3 h-1.5 rounded-full bg-white/[0.08] group-hover:bg-white/20 transition-colors"
            ></div>
          </div>

          <!-- Month Label -->
          <span 
            class="text-[10px] font-mono uppercase tracking-wider shrink-0 transition-colors"
            :class="amount > 0 ? 'text-indigo-300 font-bold' : 'text-white/35 group-hover:text-white/60'"
          >
            {{ monthNames[month - 1] }}
          </span>
        </div>
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
    const val = props.projections[i] ?? props.projections[String(i)] ?? 0;
    data[i] = Number(val) || 0;
  }
  return data;
});

const totalProjected = computed(() => {
  return Object.values(chartData.value).reduce((acc, v) => acc + (Number(v) || 0), 0);
});

const maxAmount = computed(() => {
  const vals = Object.values(chartData.value);
  return Math.max(...vals, 1);
});

const formatCurrency = (val) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val || 0);
};
</script>
