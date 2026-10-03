<template>
  <div class="glass-card rounded-36 p-6 md:p-8 border border-white/[0.08] relative overflow-hidden group">
    <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

    <div class="flex flex-col md:flex-row gap-8 relative z-10">
      
      <!-- CONTROLS -->
      <div class="md:w-1/3 flex flex-col justify-center space-y-6">
        <div>
          <h3 class="text-2xl font-bold text-white flex items-center gap-3">
            <span class="w-10 h-10 rounded-2xl bg-neonLime/10 text-neonLime flex items-center justify-center border border-neonLime/20 shadow-[0_0_15px_rgba(163,230,53,0.15)]">🔥</span>
            Simulateur FIRE
          </h3>
          <p class="text-white/40 text-xs mt-2">Atteignez l'indépendance financière.</p>
        </div>

        <div class="space-y-5">
          <div class="space-y-2">
            <label class="text-xs font-bold text-white/70 uppercase tracking-wider">Épargne Mensuelle (€)</label>
            <input type="range" v-model.number="monthlySavings" min="50" max="5000" step="50" class="w-full accent-neonLime" />
            <div class="text-right text-sm font-black text-neonLime">{{ monthlySavings }} €</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-bold text-white/70 uppercase tracking-wider">Rendement Annuel (%)</label>
            <input type="range" v-model.number="annualYield" min="2" max="15" step="0.5" class="w-full accent-neonLime" />
            <div class="text-right text-sm font-black text-neonLime">{{ annualYield }} %</div>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-bold text-white/70 uppercase tracking-wider">Objectif de Rente (€/mois)</label>
            <input type="range" v-model.number="targetIncome" min="500" max="10000" step="100" class="w-full accent-roseAcc" />
            <div class="text-right text-sm font-black text-roseAcc">{{ targetIncome }} €</div>
          </div>
        </div>
      </div>

      <!-- VISUALIZATION -->
      <div class="md:w-2/3 border-t md:border-t-0 md:border-l border-white/10 pt-6 md:pt-0 md:pl-8 flex flex-col justify-center relative">
        <div class="text-center space-y-2">
          <p class="text-sm font-medium text-white/50">Temps estimé avant indépendance financière</p>
          <div class="text-6xl md:text-8xl font-black tabular-nums tracking-tighter" :class="yearsToFire < 50 ? 'text-white' : 'text-roseAcc'">
            {{ yearsToFire < 50 ? yearsToFire : '∞' }}<span class="text-2xl text-white/30 ml-2">ans</span>
          </div>
          <p v-if="yearsToFire < 50" class="text-neonLime font-bold mt-2">Soit vers l'année {{ currentYear + yearsToFire }}</p>
          <p class="text-xs text-white/40 mt-4 max-w-sm mx-auto">
            Basé sur la règle des 4% (Capital cible: {{ formatCurrency(targetCapital) }}). Capital actuel : {{ formatCurrency(currentCapital) }}.
          </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  currentCapital: {
    type: Number,
    default: 0
  }
});

const currentYear = new Date().getFullYear();

// Inputs
const monthlySavings = ref(500);
const annualYield = ref(7.0);
const targetIncome = ref(2000);

// Calculations
const targetCapital = computed(() => (targetIncome.value * 12) / 0.04);

const yearsToFire = computed(() => {
  let capital = props.currentCapital;
  const target = targetCapital.value;
  const monthlyRate = annualYield.value / 100 / 12;
  const savings = monthlySavings.value;
  
  if (savings <= 0 && capital < target && monthlyRate <= 0) return 999;

  let months = 0;
  while (capital < target && months < 1200) { // Max 100 years
    capital = capital * (1 + monthlyRate) + savings;
    months++;
  }
  
  if (months >= 1200) return 999;
  return Math.ceil(months / 12);
});

const formatCurrency = (val) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(val || 0);
};
</script>
