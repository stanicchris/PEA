<template>
  <div class="space-y-6">
    <!-- ÉTAGE SUPÉRIEUR -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      <HeroSection 
        :summary="store.summary" 
        :positions="store.positions" 
        :isLoading="store.isLoading" 
        :isRefreshing="store.isRefreshing"
        @refresh="store.refreshData"
        @open-settings="router.push('/settings')"
      />
      <AllocationChart 
        :positions="store.positions" 
        :summary="store.summary" 
        :isLoading="store.isLoading" 
      />
      <FinancialHealthCard 
        :summary="store.summary" 
        :weather="store.weather" 
        :isLoading="store.isLoading" 
        @open-ai="store.isAiAdvisorOpen = true"
      />
      <FiscalStackCard 
        :summary="store.summary" 
        @open-tax-sim="store.isFiscalModalOpen = true"
      />
    </div>

    <!-- ÉTAGE INFÉRIEUR -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="lg:col-span-7">
        <AnalyticsCharts 
          :history="store.history" 
          :summary="store.summary" 
          :positions="store.positions" 
          :isLoading="store.isLoading" 
        />
      </div>
      <div class="lg:col-span-5">
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
