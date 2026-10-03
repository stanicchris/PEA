<template>
  <div class="glass-card rounded-36 p-6 md:p-8 border border-white/[0.08] h-full flex flex-col">
    <div class="flex justify-between items-start mb-6">
      <div>
        <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-3">
          <span class="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-400 flex items-center justify-center border border-amber-500/20">🛡️</span>
          Safety Score
        </h3>
        <p class="text-white/40 text-xs">Analyse du Payout Ratio pour évaluer la sûreté des dividendes.</p>
      </div>
    </div>
    
    <div v-if="isLoading" class="flex-1 flex justify-center items-center">
      <div class="w-8 h-8 rounded-full border-2 border-amber-400 border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="!scores.length" class="flex-1 flex items-center justify-center text-white/40 text-sm border border-dashed border-white/10 rounded-2xl">
      Aucune donnée de distribution disponible.
    </div>

    <div v-else class="space-y-4 overflow-y-auto pr-2 max-h-64 custom-scrollbar">
      <div 
        v-for="asset in scores" 
        :key="asset.isin"
        class="flex items-center justify-between p-3 rounded-xl border border-white/5 bg-white/5"
      >
        <div class="flex-1 min-w-0 pr-4">
          <h4 class="text-sm font-bold text-white truncate">{{ asset.name }}</h4>
          <p class="text-[10px] text-white/50 font-mono mt-0.5">Payout: {{ formatRatio(asset.payout_ratio) }}</p>
        </div>
        
        <div class="shrink-0 flex items-center gap-2">
          <div class="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
            <div 
              class="h-full rounded-full"
              :class="getScoreColor(asset.score)"
              :style="{ width: `${asset.score}%` }"
            ></div>
          </div>
          <span class="text-xs font-bold w-8 text-right" :class="getTextColor(asset.score)">{{ asset.score }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  scores: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

const formatRatio = (val) => {
  if (val === null || val === undefined) return 'N/A';
  return `${(val * 100).toFixed(1)}%`;
};

const getScoreColor = (score) => {
  if (score >= 80) return 'bg-neonLime';
  if (score >= 50) return 'bg-amber-400';
  return 'bg-roseAcc';
};

const getTextColor = (score) => {
  if (score >= 80) return 'text-neonLime';
  if (score >= 50) return 'text-amber-400';
  return 'text-roseAcc';
};
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}
</style>
