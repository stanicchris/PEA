<template>
  <div class="space-y-6">
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

const store = useAppStore()
</script>
