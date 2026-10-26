<template>
  <div class="space-y-5 sm:space-y-6 pb-8">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <h1 class="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="text-neonLime">💼</span> Portefeuille & Allocation
      </h1>

      <div class="flex items-center gap-2">
        <button
          @click="store.openAddPositionModal()"
          class="px-4 py-2 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs transition-all shadow-[0_4px_15px_rgba(163,230,53,0.25)] active:scale-95 cursor-pointer flex items-center gap-1.5"
        >
          <span>＋</span>
          <span>Nouvelle Ligne</span>
        </button>
      </div>
    </div>

    <!-- KPIs Haut de Page -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3.5 sm:gap-4" v-if="store.summary">
      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-1">
        <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-xs text-white/50 font-medium mb-1">Valeur Totale (PEA)</p>
          <p class="text-2xl sm:text-3xl font-black text-white font-mono tracking-tight">
            {{ store.formatCurrency(store.summary.total_value) }}
          </p>
          <p class="text-[11px] text-white/40 mt-1.5 font-mono">
            Investi : {{ store.formatCurrency(store.summary.total_invested) }}
          </p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-2">
        <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-xs text-white/50 font-medium mb-1">Plus-Value Latente</p>
          <p
            class="text-2xl sm:text-3xl font-black font-mono tracking-tight"
            :class="store.summary.global_performance_value >= 0 ? 'text-neonLime drop-shadow-[0_0_15px_rgba(163,230,53,0.3)]' : 'text-roseAcc drop-shadow-[0_0_15px_rgba(244,63,94,0.3)]'"
          >
            {{ store.summary.global_performance_value >= 0 ? '+' : '' }}{{ store.formatCurrency(store.summary.global_performance_value) }}
          </p>
          <p
            class="text-[11px] mt-1.5 font-mono font-bold"
            :class="store.summary.global_performance_pct >= 0 ? 'text-neonLime' : 'text-roseAcc'"
          >
            {{ store.summary.global_performance_pct >= 0 ? '+' : '' }}{{ (store.summary.global_performance_pct || 0).toFixed(2) }}% depuis l'origine
          </p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-4 sm:p-5 border border-white/5 relative overflow-hidden group animate-fade-up stagger-3">
        <div class="absolute inset-0 bg-gradient-to-br from-neonPurple/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-1">
            <p class="text-xs text-white/50 font-medium">Liquidités / Espèces</p>
            <router-link to="/settings" class="text-[10px] text-lavender hover:text-neonLime font-mono">Modifier ✎</router-link>
          </div>
          <p class="text-2xl sm:text-3xl font-black text-white font-mono tracking-tight">
            {{ store.formatCurrency(store.cashAmount) }}
          </p>
          <p class="text-[11px] text-white/40 mt-1.5">Disponible pour renforcer</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-5 sm:gap-6">
      <!-- Graphique d'Allocation -->
      <div class="lg:col-span-1 animate-fade-up stagger-3">
        <AllocationChart
          :positions="store.positions"
          :summary="store.summary"
          :isLoading="store.isLoading"
        />
      </div>

      <!-- Tableau / Cartes des Positions -->
      <div class="lg:col-span-3 animate-fade-up stagger-4">
        <PositionsTable :positions="store.positions" class="!mt-0 h-full" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import PositionsTable from '../components/PositionsTable.vue'
import AllocationChart from '../components/AllocationChart.vue'

const store = useAppStore()
</script>
