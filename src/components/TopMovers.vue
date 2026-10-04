<template>
  <div class="liquid-glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden group specular-highlight">
    <!-- Top Row: Title + Dropdown Mode Switcher -->
    <div class="flex justify-between items-center mb-2">
      <h3 class="text-white font-bold text-lg tracking-tight">Top Mouvements</h3>
      
      <div class="relative">
        <button 
          @click="isDropdownOpen = !isDropdownOpen" 
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-full liquid-glass-subtle border border-white/10 text-white/90 text-xs font-medium cursor-pointer hover:border-white/20 transition-all active:scale-95"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-neonLime" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
          <span>{{ currentFilterLabel }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white/40 ml-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Dropdown Menu (Liquid Glass) -->
        <div v-if="isDropdownOpen" class="absolute right-0 top-full mt-2 w-44 liquid-glass rounded-2xl shadow-2xl py-1.5 z-50 text-xs border border-white/15 specular-highlight">
          <button 
            @click="selectFilter('gainers')" 
            class="w-full text-left px-3.5 py-2 hover:bg-white/[0.08] text-neonLime flex items-center justify-between transition-colors cursor-pointer"
          >
            <span>↗ Top Gainers</span>
            <span v-if="filterMode === 'gainers'">✓</span>
          </button>
          <button 
            @click="selectFilter('losers')" 
            class="w-full text-left px-3.5 py-2 hover:bg-white/[0.08] text-roseAcc flex items-center justify-between transition-colors cursor-pointer"
          >
            <span>↘ Top Losers</span>
            <span v-if="filterMode === 'losers'">✓</span>
          </button>
          <button 
            @click="selectFilter('weight')" 
            class="w-full text-left px-3.5 py-2 hover:bg-white/[0.08] text-lavender flex items-center justify-between transition-colors cursor-pointer"
          >
            <span>⚖️ Plus Gros Poids</span>
            <span v-if="filterMode === 'weight'">✓</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Big Metric Value -->
    <div class="mb-4">
      <div class="text-3xl font-black text-white tracking-tight tabular-numbers">
        {{ formattedValue }}
      </div>
      <p class="text-white/40 text-[11px] mt-0.5">Cliquez sur une colonne pour inspecter les fondamentaux</p>
    </div>

    <div v-if="!ledColumns.length" class="h-44 flex items-center justify-center text-white/40 text-xs border border-dashed border-white/10 rounded-2xl">
      Aucune position disponible.
    </div>

    <!-- Segmented LED Bar Chart with Axis Scale and Avatars -->
    <div v-else class="space-y-0">
      <div class="relative w-full flex items-end justify-between pt-2 pb-1 gap-2">
        <!-- Y-Axis Scale Marks -->
        <div class="flex flex-col justify-between h-36 text-[9px] font-mono text-white/30 pr-1 select-none">
          <span>+40%</span>
          <span>+20%</span>
          <span>+10%</span>
          <span>+05%</span>
          <span>00%</span>
          <span>-10%</span>
        </div>

        <!-- LED Bars Grid -->
        <div class="flex-1 flex items-end justify-between gap-1.5 sm:gap-2.5 h-36 border-b border-white/[0.08] pb-1">
          <div 
            v-for="(col, idx) in ledColumns" 
            :key="idx" 
            @click="$emit('inspect-stock', col.rawPosition)"
            class="flex-1 flex flex-col items-center justify-end h-full group cursor-pointer"
            :title="`${col.name}: ${col.perf >= 0 ? '+' : ''}${col.perf.toFixed(2)}%`"
          >
            <!-- Stack of LED segments -->
            <div class="w-full max-w-[20px] flex flex-col-reverse gap-[2.5px] items-center mb-1">
              <div 
                v-for="seg in col.segments" 
                :key="seg"
                class="w-full h-1.5 rounded-[2px] transition-all group-hover:brightness-125"
                :style="{ backgroundColor: col.color }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Circular Stock Avatars under each bar -->
      <div class="flex items-center justify-between gap-1.5 sm:gap-2.5 pl-6 pt-2">
        <div 
          v-for="(col, idx) in ledColumns" 
          :key="'avatar-'+idx"
          class="flex-1 flex justify-center"
        >
          <div 
            @click="$emit('inspect-stock', col.rawPosition)"
            class="w-6 h-6 rounded-full border border-white/20 flex items-center justify-center font-bold text-[9px] text-white overflow-hidden shadow-sm transition-transform hover:scale-125 cursor-pointer"
            :style="{ backgroundColor: col.avatarBg }"
            :title="col.name"
          >
            <span>{{ col.symbol }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  isLoading: { type: Boolean, default: false }
});

const emit = defineEmits(['inspect-stock']);

const isDropdownOpen = ref(false);
const filterMode = ref('gainers');

const filterLabels = {
  gainers: 'Top Gainers',
  losers: 'Top Losers',
  weight: 'Plus Gros Poids'
};

const currentFilterLabel = computed(() => filterLabels[filterMode.value]);

const selectFilter = (mode) => {
  filterMode.value = mode;
  isDropdownOpen.value = false;
};

const formattedValue = computed(() => {
  const val = props.summary?.total_value ?? 0;
  return val.toLocaleString('fr-FR', { minimumFractionDigits: 2, style: 'currency', currency: 'EUR' });
});

const ledColumns = computed(() => {
  if (!props.positions || !props.positions.length) {
    return [];
  }

  const sorted = [...props.positions].sort((a, b) => {
    if (filterMode.value === 'gainers') return b.variation_pct - a.variation_pct;
    if (filterMode.value === 'losers') return a.variation_pct - b.variation_pct;
    return (b.current_price * b.quantity) - (a.current_price * a.quantity);
  }).slice(0, 7);

  const avatarColors = ['#3B82F6', '#10B981', '#F59E0B', '#6366F1', '#EC4899', '#8B5CF6', '#14B8A6'];

  return sorted.map((pos, i) => {
    const isPositive = pos.variation_pct >= 0;
    const segCount = Math.max(2, Math.min(18, Math.round(Math.abs(pos.variation_pct) / 2)));
    return {
      name: pos.name,
      symbol: (pos.ticker || pos.name || '').substring(0, 2).toUpperCase(),
      segments: segCount,
      color: isPositive ? (segCount > 10 ? '#A3E635' : '#98F794') : '#F43F5E',
      avatarBg: avatarColors[i % avatarColors.length],
      perf: pos.variation_pct,
      rawPosition: pos
    };
  });
});
</script>
