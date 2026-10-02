<template>
  <div class="glass rounded-3xl p-6 border border-white/5 overflow-hidden bg-gradient-to-br from-[#151921] to-[#1a2130] mt-6">
    <h3 class="text-xl font-bold mb-6 tracking-tight">Tableau Détaillé des Positions</h3>
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm whitespace-nowrap">
        <thead class="text-white/50 text-xs uppercase tracking-wider bg-white/5 border-b border-white/10">
          <tr>
            <th class="px-4 py-3 font-semibold rounded-tl-xl">Titre</th>
            <th class="px-4 py-3 font-semibold text-right">Qté</th>
            <th class="px-4 py-3 font-semibold text-right">PRU</th>
            <th class="px-4 py-3 font-semibold text-right">Cours Actuel</th>
            <th class="px-4 py-3 font-semibold text-right">Montant Investi</th>
            <th class="px-4 py-3 font-semibold text-right">Valeur Actuelle</th>
            <th class="px-4 py-3 font-semibold text-right">+/- Value (€)</th>
            <th class="px-4 py-3 font-semibold text-right rounded-tr-xl">+/- Value (%)</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr v-for="pos in positions" :key="pos.ticker" @click="openInspector(pos)" class="hover:bg-white/10 transition-colors cursor-pointer group">
            <td class="px-4 py-4">
              <div class="font-bold text-white group-hover:text-blue-400 transition-colors">{{ pos.name }}</div>
              <div class="text-xs text-white/40 mt-0.5">{{ pos.ticker }} &bull; {{ pos.sector }}</div>
            </td>
            <td class="px-4 py-4 text-right font-medium text-white/80">{{ pos.quantity }}</td>
            <td class="px-4 py-4 text-right font-medium text-white/80">{{ pos.pru.toFixed(2) }} €</td>
            <td class="px-4 py-4 text-right font-medium text-white/80">{{ pos.current_price.toFixed(2) }} €</td>
            <td class="px-4 py-4 text-right font-medium text-white/80">{{ (pos.quantity * pos.pru).toFixed(2) }} €</td>
            <td class="px-4 py-4 text-right font-bold text-white">{{ (pos.quantity * pos.current_price).toFixed(2) }} €</td>
            <td class="px-4 py-4 text-right font-bold" :class="pos.variation_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'">
               {{ pos.variation_pct >= 0 ? '+' : '' }}{{ ((pos.current_price - pos.pru) * pos.quantity).toFixed(2) }} €
            </td>
            <td class="px-4 py-4 text-right font-bold" :class="pos.variation_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'">
              <div class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg" :class="pos.variation_pct >= 0 ? 'bg-emerald-500/10' : 'bg-rose-500/10'">
                {{ pos.variation_pct >= 0 ? '+' : '' }}{{ pos.variation_pct.toFixed(2) }}%
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <AssetInspectorModal :isOpen="isInspectorOpen" :asset="selectedAsset" @close="isInspectorOpen = false" />
</template>

<script setup>
import { ref } from 'vue';
import AssetInspectorModal from './AssetInspectorModal.vue';

defineProps({ positions: { type: Array, default: () => [] } });

const isInspectorOpen = ref(false);
const selectedAsset = ref(null);

const openInspector = (asset) => {
  selectedAsset.value = asset;
  isInspectorOpen.value = true;
};
</script>
