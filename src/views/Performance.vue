<template>
  <div class="space-y-6">
    <AnalyticsView 
      :positions="store.positions" 
      :summary="store.summary" 
      :history="store.history" 
      :userId="store.userId"
    />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import AnalyticsView from '../components/AnalyticsView.vue'

const store = useAppStore()
</script>
