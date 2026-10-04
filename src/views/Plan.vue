<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <FeeOptimizer />
      <RebalancingSimulator />
    </div>
    <GoalsView :userId="store.userId" />
    <ReportsView 
      :positions="store.positions" 
      :summary="store.summary" 
    />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import GoalsView from './GoalsView.vue'
import ReportsView from '../components/ReportsView.vue'
import FeeOptimizer from '../components/FeeOptimizer.vue'
import RebalancingSimulator from '../components/RebalancingSimulator.vue'

const store = useAppStore()
</script>
