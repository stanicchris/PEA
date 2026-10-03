<template>
  <div class="glass-card rounded-32 p-7 relative overflow-hidden mt-6">
    <!-- Header with Search & Count -->
    <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-4 mb-6">
      <div>
        <h3 class="text-white font-bold text-xl tracking-tight">Tableau Détaillé des Positions</h3>
        <p class="text-white/40 text-xs mt-0.5">Cliquez sur une ligne pour ouvrir l'analyse fondamentale BourseAi</p>
      </div>

      <div class="relative w-full sm:w-64">
        <input 
          type="text" 
          v-model="searchFilter" 
          placeholder="Filtrer (ex: LVMH, AAPL)..." 
          class="w-full bg-white/[0.04] border border-white/[0.08] rounded-full px-4 py-2 pl-9 text-xs text-white placeholder-white/30 focus:outline-none focus:border-neonLime transition-all"
        />
        <svg class="w-3.5 h-3.5 text-white/40 absolute left-3 top-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
    </div>

    <!-- Table Container -->
    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs whitespace-nowrap">
        <thead class="text-white/40 uppercase font-mono tracking-wider border-b border-white/[0.06]">
          <tr>
            <th class="pb-3 px-3 font-semibold">Titre & Secteur</th>
            <th class="pb-3 px-3 font-semibold text-right">Qté</th>
            <th class="pb-3 px-3 font-semibold text-right">PRU</th>
            <th class="pb-3 px-3 font-semibold text-right">Cours Live</th>
            <th class="pb-3 px-3 font-semibold text-right">Montant Investi</th>
            <th class="pb-3 px-3 font-semibold text-right">Valeur Actuelle</th>
            <th class="pb-3 px-3 font-semibold text-right">+/- Value (€)</th>
            <th class="pb-3 px-3 font-semibold text-right">+/- Value (%)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/[0.04]">
          <tr 
            v-for="pos in filteredPositions" 
            :key="pos.ticker || pos.name" 
            @click="openInspector(pos)" 
            class="hover:bg-white/[0.04] transition-all cursor-pointer group"
          >
            <!-- Name & Sector -->
            <td class="py-3.5 px-3">
              <div class="flex items-center gap-2.5">
                <div class="w-7 h-7 rounded-full bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center font-bold text-[10px] text-lavender group-hover:bg-neonLime group-hover:text-black group-hover:border-neonLime transition-all">
                  {{ (pos.ticker || pos.name || '').substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <div class="font-bold text-white group-hover:text-neonLime transition-colors text-sm">{{ pos.name }}</div>
                  <div class="text-white/40 text-[10px] font-mono">{{ pos.ticker }} &bull; {{ pos.sector }}</div>
                </div>
              </div>
            </td>

            <!-- Quantity -->
            <td class="py-3.5 px-3 text-right font-mono text-white/80 font-medium">{{ pos.quantity }}</td>

            <!-- PRU -->
            <td class="py-3.5 px-3 text-right font-mono text-white/70">{{ pos.pru.toFixed(2) }} €</td>

            <!-- Current Price -->
            <td class="py-3.5 px-3 text-right font-mono font-bold text-white">{{ pos.current_price.toFixed(2) }} €</td>

            <!-- Total Invested -->
            <td class="py-3.5 px-3 text-right font-mono text-white/60">{{ (pos.quantity * pos.pru).toFixed(2) }} €</td>

            <!-- Current Value -->
            <td class="py-3.5 px-3 text-right font-mono font-bold text-white">{{ (pos.quantity * pos.current_price).toFixed(2) }} €</td>

            <!-- Gain (€) -->
            <td class="py-3.5 px-3 text-right font-mono font-bold" :class="pos.variation_pct >= 0 ? 'text-neonLime' : 'text-roseAcc'">
              {{ pos.variation_pct >= 0 ? '+' : '' }}{{ ((pos.current_price - pos.pru) * pos.quantity).toFixed(2) }} €
            </td>

            <!-- Gain (%) Badge -->
            <td class="py-3.5 px-3 text-right">
              <div 
                class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full font-mono font-bold text-xs" 
                :class="pos.variation_pct >= 0 ? 'bg-neonLime/15 text-neonLime border border-neonLime/30' : 'bg-roseAcc/15 text-roseAcc border border-roseAcc/30'"
              >
                {{ pos.variation_pct >= 0 ? '+' : '' }}{{ pos.variation_pct.toFixed(2) }}%
              </div>
            </td>
          </tr>

          <tr v-if="!filteredPositions.length">
            <td colspan="8" class="text-center py-8 text-white/40 text-xs italic">
              Aucune position ne correspond à votre filtre.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <AssetInspectorModal 
    :isOpen="isInspectorOpen" 
    :asset="selectedAsset" 
    @close="isInspectorOpen = false" 
  />
</template>

<script setup>
import { ref, computed } from 'vue';
import AssetInspectorModal from './AssetInspectorModal.vue';

const props = defineProps({
  positions: { type: Array, default: () => [] }
});

const searchFilter = ref('');
const isInspectorOpen = ref(false);
const selectedAsset = ref(null);

const filteredPositions = computed(() => {
  if (!searchFilter.value.trim()) return props.positions;
  const q = searchFilter.value.toLowerCase().trim();
  return props.positions.filter(p => 
    (p.name && p.name.toLowerCase().includes(q)) || 
    (p.ticker && p.ticker.toLowerCase().includes(q)) ||
    (p.sector && p.sector.toLowerCase().includes(q))
  );
});

const openInspector = (asset) => {
  selectedAsset.value = asset;
  isInspectorOpen.value = true;
};
</script>
