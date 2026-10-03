<template>
  <div class="liquid-glass-card rounded-32 p-7 relative overflow-hidden mt-6 specular-highlight">
    <!-- Header with Search & Quick Filter Badges -->
    <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-4 mb-6">
      <div>
        <div class="flex items-center gap-3">
          <h3 class="text-white font-bold text-xl tracking-tight">Tableau Détaillé des Positions</h3>
          <span class="px-2.5 py-0.5 rounded-full bg-white/[0.08] text-white/80 text-xs font-mono font-bold border border-white/10 shadow-inner">
            {{ filteredAndSortedPositions.length }} / {{ positions.length }} actifs
          </span>
        </div>
        <p class="text-white/40 text-xs mt-0.5">Cliquez sur un titre pour ouvrir la fiche d'analyse fondamentale BourseAi</p>
      </div>

      <!-- Filters & Search -->
      <div class="flex items-center gap-3 flex-wrap">
        <!-- Quick category filter pills -->
        <div class="flex items-center gap-1.5 liquid-glass-subtle p-1 rounded-full border border-white/10 text-xs shadow-inner">
          <button 
            v-for="f in [
              { key: 'all', label: 'Tous' },
              { key: 'gainers', label: 'Plus-values ↗' },
              { key: 'losers', label: 'Moins-values ↘' },
              { key: 'etf', label: 'ETFs' }
            ]" 
            :key="f.key"
            @click="categoryFilter = f.key"
            :class="categoryFilter === f.key ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
            class="px-3 py-1 rounded-full transition-all cursor-pointer active:scale-95"
          >
            {{ f.label }}
          </button>
        </div>

        <!-- Search input -->
        <div class="relative w-full sm:w-56">
          <input 
            type="text" 
            v-model="searchFilter" 
            placeholder="Filtrer (ex: LVMH, AI)..." 
            class="w-full liquid-glass-subtle rounded-full px-4 py-2 pl-9 text-xs text-white placeholder-white/40 focus:outline-none focus:border-neonLime/60 focus:ring-1 focus:ring-neonLime/30 transition-all shadow-inner"
          />
          <svg class="w-3.5 h-3.5 text-white/40 absolute left-3 top-2.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- Table Container -->
    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs whitespace-nowrap">
        <thead class="text-white/40 uppercase font-mono tracking-wider border-b border-white/[0.06] select-none">
          <tr>
            <th @click="sortBy('name')" class="pb-3 px-3 font-semibold cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center gap-1">
                <span>Titre & Secteur</span>
                <span v-if="sortKey === 'name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('quantity')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>Qté</span>
                <span v-if="sortKey === 'quantity'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('pru')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>PRU</span>
                <span v-if="sortKey === 'pru'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('current_price')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>Cours Live</span>
                <span v-if="sortKey === 'current_price'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('invested')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>Montant Investi</span>
                <span v-if="sortKey === 'invested'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('val')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>Valeur Actuelle</span>
                <span v-if="sortKey === 'val'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('amount_var')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>+/- Value (€)</span>
                <span v-if="sortKey === 'amount_var'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th @click="sortBy('variation_pct')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>+/- Value (%)</span>
                <span v-if="sortKey === 'variation_pct'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/[0.04]">
          <tr 
            v-for="pos in filteredAndSortedPositions" 
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
                  <div class="font-bold text-white group-hover:text-neonLime transition-colors text-sm flex items-center gap-2">
                    <span>{{ pos.name }}</span>
                    <span class="text-[10px] text-neonLime opacity-0 group-hover:opacity-100 transition-opacity">↗</span>
                  </div>
                  <div class="text-white/40 text-[10px] font-mono">{{ pos.ticker }} &bull; {{ pos.sector || 'Général' }}</div>
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

          <tr v-if="!filteredAndSortedPositions.length">
            <td colspan="8" class="text-center py-8 text-white/40 text-xs italic">
              Aucune position ne correspond à vos filtres.
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
  positions: { type: Array, default: () => [] },
  globalSearch: { type: String, default: '' }
});

const searchFilter = ref('');
const categoryFilter = ref('all');
const sortKey = ref('val');
const sortOrder = ref('desc');

const isInspectorOpen = ref(false);
const selectedAsset = ref(null);

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortOrder.value = 'desc';
  }
};

const filteredAndSortedPositions = computed(() => {
  let list = [...props.positions];

  // Global search or local search
  const q = (searchFilter.value || props.globalSearch || '').toLowerCase().trim();
  if (q) {
    list = list.filter(p => 
      (p.name && p.name.toLowerCase().includes(q)) || 
      (p.ticker && p.ticker.toLowerCase().includes(q)) ||
      (p.sector && p.sector.toLowerCase().includes(q))
    );
  }

  // Category Filter
  if (categoryFilter.value === 'gainers') {
    list = list.filter(p => p.variation_pct >= 0);
  } else if (categoryFilter.value === 'losers') {
    list = list.filter(p => p.variation_pct < 0);
  } else if (categoryFilter.value === 'etf') {
    list = list.filter(p => p.sector === 'ETF & Indice' || (p.name && p.name.toUpperCase().includes('ETF')));
  }

  // Sorting
  list.sort((a, b) => {
    let valA = 0;
    let valB = 0;

    switch (sortKey.value) {
      case 'name':
        return sortOrder.value === 'asc' ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name);
      case 'quantity':
        valA = a.quantity;
        valB = b.quantity;
        break;
      case 'pru':
        valA = a.pru;
        valB = b.pru;
        break;
      case 'current_price':
        valA = a.current_price;
        valB = b.current_price;
        break;
      case 'invested':
        valA = a.quantity * a.pru;
        valB = b.quantity * b.pru;
        break;
      case 'val':
        valA = a.quantity * a.current_price;
        valB = b.quantity * b.current_price;
        break;
      case 'amount_var':
        valA = (a.current_price - a.pru) * a.quantity;
        valB = (b.current_price - b.pru) * b.quantity;
        break;
      case 'variation_pct':
        valA = a.variation_pct;
        valB = b.variation_pct;
        break;
    }

    return sortOrder.value === 'asc' ? valA - valB : valB - valA;
  });

  return list;
});

const openInspector = (asset) => {
  selectedAsset.value = asset;
  isInspectorOpen.value = true;
};
</script>
