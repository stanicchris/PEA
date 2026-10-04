<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
      <span class="text-neonLime">💰</span> Calendrier des Dividendes
    </h1>
    <DividendCalendar :userId="store.userId" />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import DividendCalendar from '../components/DividendCalendar.vue'

const store = useAppStore()
</script>
