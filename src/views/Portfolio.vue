<template>
  <div class="space-y-6 pb-20">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="text-neonLime">💼</span> Portefeuille & Allocation
      </h1>
    </div>

    <!-- KPIs Haut de Page -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4" v-if="store.summary">
      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1">Valeur Totale (PEA)</p>
          <p class="text-3xl font-black text-white font-mono tracking-tight">
            {{ store.formatCurrency(store.summary.total_value) }}
          </p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1">Plus-Value Latente</p>
          <p class="text-3xl font-black font-mono tracking-tight" :class="store.summary.total_amount_var >= 0 ? 'text-neonLime drop-shadow-[0_0_15px_rgba(163,230,53,0.3)]' : 'text-roseAcc drop-shadow-[0_0_15px_rgba(244,63,94,0.3)]'">
            {{ store.summary.total_amount_var >= 0 ? '+' : '' }}{{ store.formatCurrency(store.summary.total_amount_var) }}
          </p>
          <p class="text-xs mt-2 font-medium" :class="store.summary.total_pct_var >= 0 ? 'text-neonLime' : 'text-roseAcc'">
            {{ store.summary.total_pct_var >= 0 ? '+' : '' }}{{ (store.summary.total_pct_var || 0).toFixed(2) }}%
          </p>
        </div>
      </div>

      <div class="liquid-glass-chassis rounded-3xl p-5 border border-white/5 relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-neonPurple/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="relative z-10">
          <p class="text-sm text-white/50 font-medium mb-1">Liquidités / Espèces</p>
          <p class="text-3xl font-black text-white font-mono tracking-tight">
            {{ store.formatCurrency(store.cashAmount) }}
          </p>
          <p class="text-xs text-white/40 mt-2">Prêt à investir</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      
      <!-- Graphique d'Allocation -->
      <div class="lg:col-span-1">
        <AllocationChart 
          :positions="store.positions" 
          :summary="store.summary" 
          :isLoading="store.isLoading" 
        />
      </div>

      <!-- Tableau des Positions -->
      <div class="lg:col-span-3">
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
