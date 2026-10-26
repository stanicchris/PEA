<template>
  <div class="space-y-5 sm:space-y-6 pb-10">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="text-neonLime">💰</span> Dividendes & Rente Passive
      </h1>

      <div
        v-if="nominatifBonus > 0"
        class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amberAcc/15 border border-amberAcc/30 text-amberAcc text-xs font-bold"
        title="Prime de fidélité +10% sur Air Liquide, L'Oréal, Engie, Seb après 2 ans au nominatif administré"
      >
        <span>🎖️ Bonus Nominatif +10% potentiel :</span>
        <span class="font-mono">+{{ store.formatCurrency(nominatifBonus) }}/an</span>
      </div>
    </div>

    <!-- KPIs Dividendes -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3.5 sm:gap-4" v-if="metrics">
      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-1">
        <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-xs sm:text-sm text-white/50 font-medium mb-1 flex items-center gap-1.5 flex-wrap">
            <span>Revenu Annuel</span>
            <span class="text-[10px] px-2 py-0.5 rounded-full bg-white/10">Estimé</span>
          </p>
          <p class="text-xl sm:text-3xl font-black text-white font-mono tracking-tight">
            {{ store.formatCurrency(metrics.estimated_annual_income) }}
          </p>
          <p class="text-[11px] text-neonLime mt-1.5 font-medium">
            ~{{ store.formatCurrency(metrics.estimated_annual_income / 12) }} / mois
          </p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-2">
        <div class="relative z-10">
          <p class="text-xs sm:text-sm text-white/50 font-medium mb-1">Rendement Moyen</p>
          <p class="text-xl sm:text-3xl font-black text-white font-mono tracking-tight">
            {{ (metrics.average_yield || 0).toFixed(2) }}%
          </p>
          <p class="text-[11px] text-white/40 mt-1.5">Sur la valorisation actuelle</p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-3">
        <div class="relative z-10">
          <p class="text-xs sm:text-sm text-white/50 font-medium mb-1" title="Yield on Cost : Rendement calculé sur votre prix d'achat initial (PRU)">
            Yield on Cost (YoC) ℹ️
          </p>
          <p class="text-xl sm:text-3xl font-black text-neonLime font-mono tracking-tight drop-shadow-[0_0_15px_rgba(163,230,53,0.3)]">
            {{ (metrics.yield_on_cost || 0).toFixed(2) }}%
          </p>
          <p class="text-[11px] text-white/40 mt-1.5">Sur votre PRU initial</p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-4">
        <div class="relative z-10">
          <p class="text-xs sm:text-sm text-white/50 font-medium mb-1">Score de Sûreté</p>
          <div class="flex items-baseline gap-1 mt-1">
            <p class="text-xl sm:text-3xl font-black text-white font-mono tracking-tight">{{ metrics.safety_score }}</p>
            <span class="text-white/40 text-xs sm:text-sm font-mono">/100</span>
          </div>
          <div class="w-full h-1.5 bg-black/40 rounded-full mt-2.5 overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :style="{
                width: `${metrics.safety_score}%`,
                backgroundColor: metrics.safety_score > 70 ? '#A3E635' : metrics.safety_score > 40 ? '#FBBF24' : '#EF4444'
              }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="h-28 rounded-3xl skeleton-shimmer"></div>

    <!-- Layout Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5 sm:gap-6">
      <!-- Colonne Principale: Histogramme Mensuel + Lignes à Rendement -->
      <div class="lg:col-span-2 space-y-5 sm:space-y-6">
        <!-- Histogramme Mensuel des Dividendes -->
        <MonthlyDividendProjection
          :projections="monthlyProjectionsData"
          :isLoading="store.isLoading"
          class="animate-fade-up stagger-2"
        />

        <!-- Positions génératrices de rendement -->
        <div class="liquid-glass-chassis rounded-32 sm:rounded-48 p-5 sm:p-6 border border-white/5 relative overflow-hidden animate-fade-up stagger-3">
          <div class="flex justify-between items-center mb-5">
            <h2 class="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <span class="text-xl">🧾</span> Lignes Génératrices de Dividendes
            </h2>
            <span class="text-xs font-mono text-white/40">{{ sortedDivPositions.length }} lignes</span>
          </div>

          <!-- MOBILE CARDS (< sm) -->
          <div class="sm:hidden space-y-3" v-if="sortedDivPositions.length">
            <div
              v-for="pos in sortedDivPositions"
              :key="'mob-div-' + pos.ticker"
              class="liquid-glass-subtle p-3.5 rounded-2xl border border-white/10 space-y-2"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="flex items-center gap-2.5 min-w-0">
                  <div class="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center font-bold text-xs border border-white/10 shrink-0">
                    {{ (pos.ticker || pos.name || '?').substring(0, 2) }}
                  </div>
                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5">
                      <p class="font-bold text-white text-sm truncate">{{ pos.name || pos.ticker }}</p>
                      <span v-if="store.isNominatifEligible(pos)" class="px-1.5 py-0.2 rounded bg-amberAcc/20 text-amberAcc text-[9px] font-mono font-bold">🎖️ +10%</span>
                    </div>
                    <p class="text-[11px] text-white/45 font-mono">{{ pos.quantity }} titres</p>
                  </div>
                </div>
                <div class="text-right shrink-0">
                  <p class="font-mono font-black text-white text-sm">{{ store.formatCurrency(pos.annual_income) }}/an</p>
                  <p class="text-[11px] font-mono text-neonLime font-bold">YoC : {{ pos.yield_on_cost.toFixed(2) }}%</p>
                </div>
              </div>
            </div>
          </div>

          <!-- DESKTOP/TABLET TABLE (>= sm) -->
          <div class="hidden sm:block overflow-x-auto custom-scrollbar">
            <table class="w-full text-left text-sm border-collapse" v-if="sortedDivPositions.length">
              <thead>
                <tr class="text-white/40 font-medium border-b border-white/10 uppercase text-[10px] tracking-wider font-mono">
                  <th class="pb-3 font-semibold">Actif</th>
                  <th class="pb-3 text-right font-semibold">Revenu Annuel</th>
                  <th class="pb-3 text-right font-semibold">Rendement</th>
                  <th class="pb-3 text-right font-semibold text-neonLime">YoC</th>
                  <th class="pb-3 text-right font-semibold">Sûreté</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="pos in sortedDivPositions"
                  :key="pos.ticker"
                  class="border-b border-white/5 hover:bg-white/5 transition-colors group"
                >
                  <td class="py-3.5">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center font-bold text-xs border border-white/10 group-hover:border-neonLime/30 transition-colors">
                        {{ pos.ticker?.substring(0, 2) || '?' }}
                      </div>
                      <div>
                        <div class="flex items-center gap-2">
                          <p class="font-bold text-white">{{ pos.name || pos.ticker }}</p>
                          <span
                            v-if="store.isNominatifEligible(pos)"
                            class="px-1.5 py-0.5 rounded bg-amberAcc/15 border border-amberAcc/30 text-amberAcc text-[9px] font-mono font-bold"
                            title="Éligible au bonus +10% de dividende au Nominatif Administré"
                          >
                            🎖️ Nominatif +10%
                          </span>
                        </div>
                        <p class="text-xs text-white/50 font-mono">{{ pos.ticker }} • {{ pos.quantity }} parts</p>
                      </div>
                    </div>
                  </td>
                  <td class="py-3.5 text-right font-mono font-bold text-white">
                    {{ store.formatCurrency(pos.annual_income) }}
                  </td>
                  <td class="py-3.5 text-right font-mono text-white/70">
                    {{ pos.yield.toFixed(2) }}%
                  </td>
                  <td class="py-3.5 text-right font-mono font-bold text-neonLime">
                    {{ pos.yield_on_cost.toFixed(2) }}%
                  </td>
                  <td class="py-3.5 text-right">
                    <span
                      :class="[
                        'px-2.5 py-1 rounded-full text-[10px] font-mono font-bold',
                        pos.safety_score > 70
                          ? 'bg-neonLime/10 text-neonLime border border-neonLime/20'
                          : pos.safety_score > 40
                          ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                          : 'bg-red-500/10 text-red-400 border border-red-500/20'
                      ]"
                    >
                      {{ pos.safety_score }}/100
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else class="text-center py-8 text-white/50 text-sm">
              Aucune position générant des dividendes identifiée.
            </div>
          </div>
        </div>
      </div>

      <!-- Colonne Latérale: Simulateur Rente (FIRE) & Calendrier -->
      <div class="space-y-5 sm:space-y-6">
        <FireSimulator
          v-if="metrics"
          :currentCapital="store.summary?.total_value || 0"
          class="animate-fade-up stagger-3"
        />

        <DividendCalendar :userId="store.userId" class="animate-fade-up stagger-4" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'
import DividendCalendar from '../components/DividendCalendar.vue'
import FireSimulator from '../components/FireSimulator.vue'
import MonthlyDividendProjection from '../components/MonthlyDividendProjection.vue'

const store = useAppStore()
const metrics = computed(() => store.dividendMetrics)

const sortedDivPositions = computed(() => {
  if (!metrics.value?.positions) return []
  return [...metrics.value.positions].sort((a, b) => b.annual_income - a.annual_income)
})

const nominatifBonus = computed(() => {
  return sortedDivPositions.value
    .filter((p) => store.isNominatifEligible(p))
    .reduce((acc, p) => acc + p.annual_income * 0.1, 0)
})

// Build 12-month realistic distribution of annual dividends (French dividend season peaks in May/June + quarterly TotalEnergies)
const monthlyProjectionsData = computed(() => {
  const annual = metrics.value?.estimated_annual_income || 0
  if (annual <= 0) return {}
  // Typical French PEA seasonal weights (Jan, Mar, Apr, May peak, Jun peak, Jul, Sep, Oct, Dec)
  const weights = {
    1: 0.05,
    2: 0.02,
    3: 0.08,
    4: 0.09,
    5: 0.34,
    6: 0.18,
    7: 0.06,
    8: 0.01,
    9: 0.06,
    10: 0.05,
    11: 0.01,
    12: 0.05
  }
  const out = {}
  for (let m = 1; m <= 12; m++) {
    out[m] = Math.round(annual * weights[m] * 100) / 100
  }
  return out
})
</script>
