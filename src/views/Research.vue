<template>
  <div class="space-y-6">
    <OptimizationView 
      :userId="store.userId" 
      :isAiLoading="store.isAiLoading" 
      @trigger-ai="store.isAiAdvisorOpen = true" 
    />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import OptimizationView from './OptimizationView.vue'

const store = useAppStore()
</script>
