<template>
  <div class="flex flex-col gap-4 h-full">
    <!-- Sub-card 4A: Account Verification / Fiscalité PEA -->
    <div class="glass-card rounded-32 p-6 flex-1 flex flex-col justify-between relative overflow-hidden">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="w-7 h-7 rounded-xl bg-white/[0.05] border border-white/[0.08] flex items-center justify-center text-white/80">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-neonLime" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clip-rule="evenodd" />
            </svg>
          </div>
          <h4 class="text-white font-bold text-sm tracking-tight">Account Verification</h4>
        </div>
        
        <p class="text-white/40 text-xs leading-relaxed mb-4">
          Plan mature (+5 ans) : Exonération totale d'impôt sur le revenu (prélèvements sociaux de 17,2 % uniquement).
        </p>
      </div>

      <button 
        @click="$emit('open-tax-sim')" 
        class="bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] font-extrabold text-xs py-2.5 px-4 rounded-full transition-all shadow-sm w-fit active:scale-95"
      >
        Verify Account
      </button>
    </div>

    <!-- Sub-card 4B: Monthly Budget Limit / Plafond PEA 150 000 € -->
    <div class="glass-card rounded-32 p-6 flex-1 flex flex-col justify-between relative overflow-hidden">
      <div class="flex justify-between items-center mb-3">
        <h4 class="text-white font-bold text-sm tracking-tight">Monthly Budget Limit</h4>
        <button class="text-white/40 hover:text-white transition-colors p-1">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
          </svg>
        </button>
      </div>

      <!-- Segmented Bar -->
      <div class="space-y-2 mb-2">
        <div class="h-3 rounded-full bg-white/[0.05] p-0.5 flex gap-1 overflow-hidden">
          <div 
            class="h-full rounded-full bg-gradient-to-r from-neonPurple to-lavender transition-all duration-700" 
            :style="{ width: percentInvested + '%' }"
          ></div>
        </div>
        
        <div class="flex justify-between items-baseline text-xs font-mono">
          <span class="text-white font-semibold tabular-numbers">
            {{ investedAmount.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} € <span class="text-white/40 font-sans text-[10px]">Spend out of</span>
          </span>
          <span class="text-white/40 tabular-numbers">
            150 000.00 €
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  summary: { type: Object, default: () => ({}) }
});

defineEmits(['open-tax-sim']);

const investedAmount = computed(() => {
  return props.summary?.total_invested || 7458.78;
});

const percentInvested = computed(() => {
  const max = 150000;
  const val = investedAmount.value;
  return Math.min(100, Math.max(5, (val / max) * 100));
});
</script>
