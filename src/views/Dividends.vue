<template>
  <div class="space-y-6 pb-20">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="text-neonLime">💰</span> Dividendes & Rente
      </h1>
    </div>

    <!-- KPIs Dividendes -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4" v-if="metrics">
      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1 flex items-center gap-2">
            <span>Revenu Annuel</span>
            <span class="text-xs px-2 py-0.5 rounded-full bg-white/10">Estimé</span>
          </p>
          <p class="text-3xl font-black text-white font-mono tracking-tight">
            {{ store.formatCurrency(metrics.estimated_annual_income) }}
          </p>
          <p class="text-xs text-neonLime mt-2 font-medium">Soit ~{{ store.formatCurrency(metrics.estimated_annual_income / 12) }} / mois</p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1">Rendement Moyen</p>
          <p class="text-3xl font-black text-white font-mono tracking-tight">
            {{ (metrics.average_yield || 0).toFixed(2) }}%
          </p>
          <p class="text-xs text-white/40 mt-2">Sur la valeur actuelle</p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-neonLime/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1 tooltip" title="Yield on Cost : Rendement calculé sur votre prix d'achat initial">
            Yield on Cost (YoC) ℹ️
          </p>
          <p class="text-3xl font-black text-neonLime font-mono tracking-tight drop-shadow-[0_0_15px_rgba(163,230,53,0.3)]">
            {{ (metrics.yield_on_cost || 0).toFixed(2) }}%
          </p>
          <p class="text-xs text-white/40 mt-2">Sur la valeur investie</p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1">Score de Sûreté</p>
          <div class="flex items-baseline gap-1 mt-1">
            <p class="text-3xl font-black text-white font-mono tracking-tight">{{ metrics.safety_score }}</p>
            <span class="text-white/40 text-sm font-mono">/100</span>
          </div>
          <!-- Bar progress -->
          <div class="w-full h-1.5 bg-black/40 rounded-full mt-3 overflow-hidden">
            <div class="h-full rounded-full transition-all" :style="{ width: `${metrics.safety_score}%`, backgroundColor: metrics.safety_score > 70 ? '#A3E635' : (metrics.safety_score > 40 ? '#FBBF24' : '#EF4444') }"></div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="h-32 flex items-center justify-center liquid-glass-chassis rounded-3xl border border-white/5">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-neonLime"></div>
    </div>

    <!-- Layout Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Colonne Principale: Positions à dividendes & Calendrier -->
      <div class="lg:col-span-2 space-y-6">
        
        <!-- Positions génératrices de rendement -->
        <div class="liquid-glass-chassis rounded-48 p-6 border border-white/5 relative overflow-hidden">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-bold text-white flex items-center gap-2">
              <span class="text-xl">🧾</span> Lignes à Rendement
            </h2>
          </div>
          
          <div class="overflow-x-auto custom-scrollbar">
            <table class="w-full text-left text-sm border-collapse" v-if="metrics && metrics.positions.length">
              <thead>
                <tr class="text-white/40 font-medium border-b border-white/10 uppercase text-[10px] tracking-wider">
                  <th class="pb-3 font-semibold">Actif</th>
                  <th class="pb-3 text-right font-semibold">Revenu Annuel</th>
                  <th class="pb-3 text-right font-semibold">Rendement</th>
                  <th class="pb-3 text-right font-semibold text-neonLime">YoC</th>
                  <th class="pb-3 text-right font-semibold">Sûreté</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="pos in metrics.positions.sort((a,b) => b.annual_income - a.annual_income)" :key="pos.ticker" class="border-b border-white/5 hover:bg-white/5 transition-colors group">
                  <td class="py-4">
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center font-bold text-xs border border-white/10 group-hover:border-neonLime/30 transition-colors">
                        {{ pos.ticker?.substring(0,2) || '?' }}
                      </div>
                      <div>
                        <p class="font-bold text-white">{{ pos.name || pos.ticker }}</p>
                        <p class="text-xs text-white/50">{{ pos.ticker }} • {{ pos.quantity }} parts</p>
                      </div>
                    </div>
                  </td>
                  <td class="py-4 text-right font-mono font-medium text-white">
                    {{ store.formatCurrency(pos.annual_income) }}
                  </td>
                  <td class="py-4 text-right font-mono text-white/70">
                    {{ pos.yield.toFixed(2) }}%
                  </td>
                  <td class="py-4 text-right font-mono font-bold text-neonLime">
                    {{ pos.yield_on_cost.toFixed(2) }}%
                  </td>
                  <td class="py-4 text-right">
                    <span :class="['px-2 py-1 rounded-full text-[10px] font-bold', pos.safety_score > 70 ? 'bg-neonLime/10 text-neonLime border border-neonLime/20' : (pos.safety_score > 40 ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20')]">
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

      <!-- Colonne Latérale: Objectif FIRE & Graphiques -->
      <div class="space-y-6">
        
        <!-- Simulateur Rente (FIRE) -->
        <FireSimulator v-if="metrics" :currentCapital="store.summary?.total_value || 0" />

        <div class="liquid-glass-chassis rounded-48 p-6 border border-white/5">
          <h2 class="text-lg font-bold text-white mb-4">Calendrier Prochainement</h2>
          <DividendCalendar :userId="store.userId" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '../stores/app'
import DividendCalendar from '../components/DividendCalendar.vue'
import FireSimulator from '../components/FireSimulator.vue'

const store = useAppStore()
const metrics = computed(() => store.dividendMetrics)
</script>
