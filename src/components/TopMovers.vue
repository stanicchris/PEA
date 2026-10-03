<template>
  <div class="glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden">
    <!-- Top Row: Title + [Weekly v] Dropdown -->
    <div class="flex justify-between items-center mb-2">
      <h3 class="text-white font-bold text-lg tracking-tight">Transaction Count</h3>
      
      <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/[0.08] text-white/70 text-xs font-medium cursor-pointer hover:bg-white/[0.08] transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <span>Weekly</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-white/40 ml-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>

    <!-- Big Metric Value -->
    <div class="mb-4">
      <div class="text-3xl font-black text-white tracking-tight tabular-numbers">
        {{ formattedValue }}
      </div>
    </div>

    <!-- Segmented LED Bar Chart with Axis Scale and Avatars -->
    <div class="relative w-full flex items-end justify-between pt-2 pb-1 gap-2">
      <!-- Y-Axis Scale Marks -->
      <div class="flex flex-col justify-between h-36 text-[9px] font-mono text-white/30 pr-1 select-none">
        <span>100</span>
        <span>50</span>
        <span>25</span>
        <span>10</span>
        <span>05</span>
        <span>00</span>
      </div>

      <!-- LED Bars Grid (7 Columns) -->
      <div class="flex-1 flex items-end justify-between gap-1.5 sm:gap-2.5 h-36 border-b border-white/[0.08] pb-1">
        <div 
          v-for="(col, idx) in ledColumns" 
          :key="idx" 
          class="flex-1 flex flex-col items-center justify-end h-full group cursor-pointer"
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

    <!-- Circular Stock Avatars under each bar (matching interface.png) -->
    <div class="flex items-center justify-between gap-1.5 sm:gap-2.5 pl-6 pt-2">
      <div 
        v-for="(col, idx) in ledColumns" 
        :key="'avatar-'+idx"
        class="flex-1 flex justify-center"
      >
        <div 
          class="w-6 h-6 rounded-full border border-white/20 flex items-center justify-center font-bold text-[9px] text-white overflow-hidden shadow-sm transition-transform hover:scale-110"
          :style="{ backgroundColor: col.avatarBg }"
          :title="col.name"
        >
          <span v-if="!col.img">{{ col.symbol }}</span>
          <img v-else :src="col.img" class="w-full h-full object-cover" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) },
  isLoading: { type: Boolean, default: false }
});

const formattedValue = computed(() => {
  const val = props.summary?.total_value || 6721.48;
  return val.toLocaleString('fr-FR', { minimumFractionDigits: 2, style: 'currency', currency: 'EUR' });
});

// Segmented LED columns corresponding to top stocks
const ledColumns = computed(() => {
  const defaults = [
    { name: 'LVMH (MC)', symbol: 'MC', segments: 16, color: '#A3E635', avatarBg: '#3B82F6' },
    { name: 'TotalEnergies', symbol: 'TTE', segments: 11, color: '#A3E635', avatarBg: '#10B981' },
    { name: 'Schneider Elec', symbol: 'SU', segments: 8, color: '#98F794', avatarBg: '#F59E0B' },
    { name: 'Air Liquide', symbol: 'AI', segments: 5, color: '#64748B', avatarBg: '#6366F1' },
    { name: 'Safran', symbol: 'SAF', segments: 13, color: '#8B5CF6', avatarBg: '#EC4899' },
    { name: 'BNP Paribas', symbol: 'BNP', segments: 7, color: '#C4B5FD', avatarBg: '#8B5CF6' },
    { name: 'ETF MSCI World', symbol: 'CW8', segments: 4, color: '#334155', avatarBg: '#14B8A6' }
  ];

  if (!props.positions || props.positions.length < 3) return defaults;

  return defaults.map((d, i) => {
    const pos = props.positions[i];
    if (pos) {
      const isPositive = pos.variation_pct >= 0;
      const segCount = Math.max(3, Math.min(18, Math.round(Math.abs(pos.variation_pct) / 2)));
      return {
        name: pos.name,
        symbol: (pos.ticker || pos.name || '').substring(0, 2).toUpperCase(),
        segments: segCount,
        color: isPositive ? (segCount > 10 ? '#A3E635' : '#98F794') : '#8B5CF6',
        avatarBg: d.avatarBg
      };
    }
    return d;
  });
});
</script>
