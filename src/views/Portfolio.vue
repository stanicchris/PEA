<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
      <span class="text-neonLime">💼</span> Portefeuille & Positions
    </h1>
    <PositionsTable :positions="store.positions" />
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/app'
import PositionsTable from '../components/PositionsTable.vue'

const store = useAppStore()
</script>
