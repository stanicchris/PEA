<template>
  <div class="flex flex-col gap-4 h-full">
    <!-- Sub-card 4A: Régime Fiscal PEA -->
    <div class="liquid-glass-card rounded-32 p-5 sm:p-6 flex-1 flex flex-col justify-between relative overflow-hidden group specular-highlight">
      <div>
        <div class="flex items-center justify-between gap-2 mb-2">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-xl liquid-glass-subtle border border-neonLime/30 flex items-center justify-center text-white/90 shadow-[0_0_12px_rgba(163,230,53,0.2)]">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-neonLime" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clip-rule="evenodd" />
              </svg>
            </div>
            <h4 class="text-white font-bold text-sm tracking-tight">Horloge Fiscale PEA</h4>
          </div>
          <span
            class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold border"
            :class="taxStatus?.is_mature ? 'bg-neonLime/15 text-neonLime border-neonLime/30' : 'bg-amberAcc/15 text-amberAcc border-amberAcc/30'"
          >
            {{ taxStatus?.is_mature ? 'IR 0% (> 5 ans)' : 'En maturation' }}
          </span>
        </div>

        <p v-if="taxStatus?.is_mature" class="text-white/55 text-xs leading-relaxed mb-3">
          Exonération totale d'impôt sur le revenu (prélèvements sociaux de 17,2% uniquement). Ouvert le {{ taxStatus.opened_at }}.
        </p>
        <p v-else class="text-white/55 text-xs leading-relaxed mb-3">
          Maturation dans {{ Math.ceil((taxStatus?.days_to_maturity || 0) / 30) }} mois (le {{ taxStatus?.maturity_date }}). Modifiable dans les paramètres.
        </p>
      </div>

      <button
        @click="$emit('open-tax-sim')"
        class="bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] font-black text-xs py-2 px-4 rounded-full transition-all shadow-[0_2px_12px_rgba(163,230,53,0.3)] w-fit active:scale-95 cursor-pointer"
      >
        Simulateur de Retrait Net
      </button>
    </div>

    <!-- Sub-card 4B: Plafond PEA 150 000 € -->
    <div class="liquid-glass-card rounded-32 p-5 sm:p-6 flex-1 flex flex-col justify-between relative overflow-hidden group specular-highlight">
      <div class="flex justify-between items-center mb-2">
        <h4 class="text-white font-bold text-sm tracking-tight">Plafond Légal (150k€)</h4>
        <span class="text-[11px] font-mono font-bold text-lavender">{{ percentInvested.toFixed(1) }}%</span>
      </div>

      <!-- Segmented Bar -->
      <div class="space-y-2">
        <div class="h-3 rounded-full bg-white/[0.06] p-0.5 flex gap-1 overflow-hidden shadow-inner border border-white/5">
          <div
            class="h-full rounded-full bg-gradient-to-r from-neonPurple to-neonLime transition-all duration-700 shadow-[0_0_12px_rgba(139,92,246,0.5)]"
            :style="{ width: Math.max(4, percentInvested) + '%' }"
          ></div>
        </div>

        <div class="flex justify-between items-baseline text-xs font-mono">
          <span class="text-white font-bold tabular-numbers">
            {{ store.formatCurrency(investedAmount) }} <span class="text-white/40 font-sans text-[10px]">versés</span>
          </span>
          <span class="text-white/50 tabular-numbers text-[11px]">
            Reste {{ store.formatCurrency(Math.max(0, 150000 - investedAmount)) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const props = defineProps({
  summary: { type: Object, default: () => ({}) }
})

defineEmits(['open-tax-sim'])

const taxStatus = computed(() => props.summary?.tax_status)

const investedAmount = computed(() => {
  return taxStatus.value?.net_invested ?? props.summary?.total_invested ?? 0
})

const percentInvested = computed(() => {
  const max = taxStatus.value?.legal_limit || 150000
  const val = investedAmount.value
  return Math.min(100, Math.max(0, (val / max) * 100))
})
</script>
