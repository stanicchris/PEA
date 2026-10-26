<template>
  <div class="space-y-5 sm:space-y-6">
    <!-- ONBOARDING BANNER IF PORTFOLIO IS EMPTY -->
    <div
      v-if="!store.isLoading && store.positions.length === 0"
      class="liquid-glass-card rounded-32 p-6 sm:p-8 border border-neonLime/30 specular-highlight animate-fade-up flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6"
    >
      <div class="space-y-2 max-w-2xl">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neonLime/15 border border-neonLime/30 text-neonLime text-xs font-bold">
          <span>🚀</span>
          <span>Bienvenue sur votre Cockpit PEA</span>
        </div>
        <h2 class="text-xl sm:text-2xl font-black text-white tracking-tight">
          Prêt à visualiser et optimiser votre patrimoine ?
        </h2>
        <p class="text-white/60 text-xs sm:text-sm leading-relaxed">
          Importez un export CSV/Excel (BoursoBank, Fortuneo, Bourse Direct...), ajoutez votre première ligne manuellement, ou explorez l'application avec un portefeuille de démonstration complet.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3 w-full lg:w-auto">
        <button
          @click="store.enterDemoMode()"
          class="flex-1 sm:flex-initial px-5 py-3 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs transition-all shadow-[0_4px_20px_rgba(163,230,53,0.3)] active:scale-95 cursor-pointer"
        >
          ✨ Explorer le Portefeuille Démo
        </button>
        <button
          @click="store.openAddPositionModal()"
          class="flex-1 sm:flex-initial px-5 py-3 rounded-full liquid-glass-pill hover:bg-white/10 text-white font-bold text-xs border border-white/15 transition-all active:scale-95 cursor-pointer"
        >
          ➕ Saisir une ligne
        </button>
        <button
          @click="router.push('/settings')"
          class="w-full sm:w-auto px-4 py-3 rounded-full liquid-glass-subtle hover:bg-white/10 text-white/70 hover:text-white font-semibold text-xs border border-white/10 transition-all active:scale-95 cursor-pointer"
        >
          📁 Importer CSV
        </button>
      </div>
    </div>

    <!-- ÉTAGE SUPÉRIEUR -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6">
      <div class="animate-fade-up stagger-1 h-full">
        <HeroSection
          :summary="store.summary"
          :positions="store.positions"
          :isLoading="store.isLoading"
          :isRefreshing="store.isRefreshing"
          @refresh="store.refreshData"
          @open-settings="router.push('/settings')"
        />
      </div>
      <div class="animate-fade-up stagger-2 h-full">
        <AllocationChart
          :positions="store.positions"
          :summary="store.summary"
          :isLoading="store.isLoading"
        />
      </div>
      <div class="animate-fade-up stagger-3 h-full">
        <FinancialHealthCard
          :summary="store.summary"
          :weather="store.weather"
          :isLoading="store.isLoading"
          @open-ai="store.isAiAdvisorOpen = true"
        />
      </div>
      <div class="animate-fade-up stagger-4 h-full">
        <FiscalStackCard
          :summary="store.summary"
          @open-tax-sim="store.isFiscalModalOpen = true"
        />
      </div>
    </div>

    <!-- ÉTAGE INFÉRIEUR -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
      <div class="lg:col-span-7 animate-fade-up stagger-5">
        <AnalyticsCharts
          :history="store.history"
          :summary="store.summary"
          :positions="store.positions"
          :isLoading="store.isLoading"
        />
      </div>
      <div class="lg:col-span-5 animate-fade-up stagger-6">
        <TopMovers
          :positions="store.positions"
          :summary="store.summary"
          :isLoading="store.isLoading"
          @inspect-stock="store.openStockInspector"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'
import HeroSection from '../components/HeroSection.vue'
import AllocationChart from '../components/AllocationChart.vue'
import FinancialHealthCard from '../components/FinancialHealthCard.vue'
import FiscalStackCard from '../components/FiscalStackCard.vue'
import AnalyticsCharts from '../components/AnalyticsCharts.vue'
import TopMovers from '../components/TopMovers.vue'

const store = useAppStore()
const router = useRouter()
</script>
