<template>
  <div class="liquid-glass-card rounded-2xl sm:rounded-3xl p-4 sm:p-7 relative overflow-hidden mt-6 specular-highlight">
    <!-- Header with Search & Quick Filter Badges -->
    <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-3.5 mb-5">
      <div>
        <div class="flex items-center gap-2.5 flex-wrap">
          <h3 class="text-white font-bold text-lg sm:text-xl tracking-tight">Positions du Portefeuille</h3>
          <span class="px-2.5 py-0.5 rounded-full bg-white/[0.08] text-white/80 text-xs font-mono font-bold border border-white/10 shadow-inner">
            {{ filteredAndSortedPositions.length }} / {{ positions.length }} actifs
          </span>
        </div>
        <p class="text-white/40 text-xs mt-0.5">Touchez un titre pour ouvrir l'analyse fondamentale BourseAi ou le graphique</p>
      </div>

      <!-- Filters & Search -->
      <div class="flex items-center gap-2.5 flex-wrap">
        <!-- Quick category filter pills (horizontally scrollable on mobile) -->
        <div class="flex items-center gap-1 liquid-glass-subtle p-1 rounded-full border border-white/10 text-xs shadow-inner overflow-x-auto no-scrollbar max-w-full">
          <button
            v-for="f in [
              { key: 'all', label: 'Tous' },
              { key: 'gainers', label: 'Gagnants ↗' },
              { key: 'losers', label: 'Perdants ↘' },
              { key: 'etf', label: 'ETFs' },
              { key: 'nominatif', label: '🎖️ +10%' }
            ]"
            :key="f.key"
            @click="categoryFilter = f.key"
            :class="categoryFilter === f.key ? 'bg-white/[0.18] text-white font-bold shadow-sm border border-white/20' : 'text-white/40 hover:text-white border border-transparent'"
            class="px-2.5 py-1 rounded-full transition-all cursor-pointer active:scale-95 whitespace-nowrap"
          >
            {{ f.label }}
          </button>
        </div>

        <!-- Search input -->
        <div class="relative w-full sm:w-52">
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

    <!-- MOBILE CARD VIEW (< md) — Ergonomic Thumb-Friendly Cards -->
    <div class="md:hidden space-y-3">
      <!-- Mobile Sort Bar -->
      <div class="flex items-center justify-between text-[11px] text-white/50 px-1 pb-1">
        <span>Trier par :</span>
        <div class="flex items-center gap-1.5 font-mono">
          <button @click="sortBy('val')" :class="sortKey === 'val' ? 'text-neonLime font-bold' : 'text-white/50'" class="px-2 py-0.5 rounded bg-white/5">Valeur</button>
          <button @click="sortBy('variation_pct')" :class="sortKey === 'variation_pct' ? 'text-neonLime font-bold' : 'text-white/50'" class="px-2 py-0.5 rounded bg-white/5">Perf %</button>
          <button @click="sortBy('name')" :class="sortKey === 'name' ? 'text-neonLime font-bold' : 'text-white/50'" class="px-2 py-0.5 rounded bg-white/5">Nom</button>
        </div>
      </div>

      <div
        v-for="pos in filteredAndSortedPositions"
        :key="'mob-' + (pos.ticker || pos.name)"
        @click="store.openStockInspector(pos)"
        class="liquid-glass-subtle rounded-2xl p-4 border border-white/10 active:scale-[0.99] transition-all cursor-pointer space-y-3"
      >
        <!-- Row 1: Avatar + Title + Total Value -->
        <div class="flex items-start justify-between gap-2">
          <div class="flex items-center gap-2.5 min-w-0">
            <div class="w-9 h-9 rounded-2xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center font-bold text-xs text-lavender shrink-0">
              {{ (pos.ticker || pos.name || '').substring(0, 2).toUpperCase() }}
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-1.5 flex-wrap">
                <h4 class="font-bold text-white text-sm truncate">{{ pos.name }}</h4>
                <span
                  v-if="store.isNominatifEligible(pos)"
                  class="px-1.5 py-0.2 rounded bg-amberAcc/20 border border-amberAcc/40 text-amberAcc text-[9px] font-mono font-bold"
                  title="Éligible Prime de Fidélité +10% au Nominatif Administré"
                >
                  🎖️ +10%
                </span>
              </div>
              <p class="text-[11px] text-white/45 font-mono truncate">{{ pos.ticker }} • {{ pos.sector || 'Action' }}</p>
            </div>
          </div>

          <div class="text-right shrink-0">
            <p class="font-mono font-black text-white text-sm">{{ store.formatCurrency(pos.quantity * pos.current_price) }}</p>
            <div
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-mono font-bold text-[10px] mt-0.5"
              :class="pos.variation_pct >= 0 ? 'bg-neonLime/15 text-neonLime border border-neonLime/30' : 'bg-roseAcc/15 text-roseAcc border border-roseAcc/30'"
            >
              {{ pos.variation_pct >= 0 ? '+' : '' }}{{ pos.variation_pct.toFixed(2) }}%
            </div>
          </div>
        </div>

        <!-- Row 2: Compact Details Grid (Qté, PRU, Cours, +/- €) -->
        <div class="grid grid-cols-3 gap-2 pt-2 border-t border-white/5 text-[11px] font-mono">
          <div>
            <span class="text-white/40 block text-[9px] uppercase">Qté × PRU</span>
            <span class="text-white/80 font-semibold">{{ pos.quantity }} × {{ store.formatCurrency(pos.pru) }}</span>
          </div>
          <div class="text-center">
            <span class="text-white/40 block text-[9px] uppercase">Cours Live</span>
            <span class="text-white font-bold">{{ store.formatCurrency(pos.current_price) }}</span>
          </div>
          <div class="text-right">
            <span class="text-white/40 block text-[9px] uppercase">+/- Value</span>
            <span class="font-bold" :class="pos.variation_pct >= 0 ? 'text-neonLime' : 'text-roseAcc'">
              {{ pos.variation_pct >= 0 ? '+' : '' }}{{ store.formatCurrency((pos.current_price - pos.pru) * pos.quantity) }}
            </span>
          </div>
        </div>

        <!-- Row 3: Weight Bar & Quick Mobile Actions -->
        <div class="flex items-center justify-between gap-3 pt-1">
          <div class="flex-1 flex items-center gap-2">
            <div class="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div
                class="h-full rounded-full bg-gradient-to-r from-neonPurple to-neonLime"
                :style="{ width: Math.min(100, getWeightPct(pos) * 2) + '%' }"
              ></div>
            </div>
            <span class="text-[10px] font-mono text-white/50 shrink-0">{{ getWeightPct(pos).toFixed(1) }}%</span>
          </div>

          <div class="flex items-center gap-1.5" @click.stop>
            <button
              @click="router.push(`/stock/${pos.ticker || pos.name}`)"
              class="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-[10px] text-white/80 font-semibold"
            >
              📈 Fiche
            </button>
            <button
              @click="store.openAddPositionModal(pos)"
              class="px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-[10px] text-white/70"
              title="Modifier la ligne"
            >
              ✏️
            </button>
          </div>
        </div>
      </div>

      <div v-if="!filteredAndSortedPositions.length" class="text-center py-8 text-white/40 text-xs italic border border-dashed border-white/10 rounded-2xl">
        Aucune position ne correspond à vos filtres.
      </div>
    </div>

    <!-- DESKTOP TABLE VIEW (>= md) -->
    <div class="hidden md:block overflow-x-auto">
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
            <th @click="sortBy('val')" class="pb-3 px-3 font-semibold text-right cursor-pointer hover:text-white transition-colors">
              <div class="flex items-center justify-end gap-1">
                <span>Valorisation & Poids</span>
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
                <span>Perf (%)</span>
                <span v-if="sortKey === 'variation_pct'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
              </div>
            </th>
            <th class="pb-3 px-2 text-right font-semibold">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/[0.04]">
          <tr
            v-for="pos in filteredAndSortedPositions"
            :key="pos.ticker || pos.name"
            @click="store.openStockInspector(pos)"
            class="hover:bg-white/[0.04] transition-all cursor-pointer group"
          >
            <!-- Name & Sector -->
            <td class="py-3.5 px-3">
              <div class="flex items-center gap-2.5">
                <div class="w-8 h-8 rounded-2xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center font-bold text-[10px] text-lavender group-hover:bg-neonLime group-hover:text-black group-hover:border-neonLime transition-all">
                  {{ (pos.ticker || pos.name || '').substring(0, 2).toUpperCase() }}
                </div>
                <div>
                  <div class="font-bold text-white group-hover:text-neonLime transition-colors text-sm flex items-center gap-2">
                    <span>{{ pos.name }}</span>
                    <span
                      v-if="store.isNominatifEligible(pos)"
                      class="px-1.5 py-0.5 rounded bg-amberAcc/15 border border-amberAcc/30 text-amberAcc text-[9px] font-mono font-bold"
                      title="Éligible à la prime de fidélité +10% (dividendes & actions gratuites) au Nominatif Administré"
                    >
                      🎖️ Nominatif +10%
                    </span>
                    <span class="text-[10px] text-neonLime opacity-0 group-hover:opacity-100 transition-opacity">↗</span>
                  </div>
                  <div class="text-white/40 text-[10px] font-mono">{{ pos.ticker }} &bull; {{ pos.sector || 'Général' }}</div>
                </div>
              </div>
            </td>

            <!-- Quantity -->
            <td class="py-3.5 px-3 text-right font-mono text-white/80 font-medium">{{ pos.quantity }}</td>

            <!-- PRU -->
            <td class="py-3.5 px-3 text-right font-mono text-white/70">{{ store.formatCurrency(pos.pru) }}</td>

            <!-- Current Price -->
            <td class="py-3.5 px-3 text-right font-mono font-bold text-white">{{ store.formatCurrency(pos.current_price) }}</td>

            <!-- Current Value + Weight Mini Bar -->
            <td class="py-3.5 px-3 text-right font-mono">
              <div class="font-bold text-white">{{ store.formatCurrency(pos.quantity * pos.current_price) }}</div>
              <div class="flex items-center justify-end gap-1.5 mt-1">
                <div class="w-14 h-1 rounded-full bg-white/10 overflow-hidden">
                  <div class="h-full bg-neonLime" :style="{ width: Math.min(100, getWeightPct(pos) * 2) + '%' }"></div>
                </div>
                <span class="text-[10px] text-white/45">{{ getWeightPct(pos).toFixed(1) }}%</span>
              </div>
            </td>

            <!-- Gain (€) -->
            <td class="py-3.5 px-3 text-right font-mono font-bold" :class="pos.variation_pct >= 0 ? 'text-neonLime' : 'text-roseAcc'">
              {{ pos.variation_pct >= 0 ? '+' : '' }}{{ store.formatCurrency((pos.current_price - pos.pru) * pos.quantity) }}
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

            <!-- Quick Actions -->
            <td class="py-3.5 px-2 text-right" @click.stop>
              <div class="flex items-center justify-end gap-1">
                <button
                  @click="router.push(`/stock/${pos.ticker || pos.name}`)"
                  class="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-neonLime transition-colors"
                  title="Ouvrir la fiche détaillée et le graphique"
                >
                  📈
                </button>
                <button
                  @click="store.openAddPositionModal(pos)"
                  class="p-1.5 rounded-lg hover:bg-white/10 text-white/50 hover:text-white transition-colors"
                  title="Modifier Qté / PRU"
                >
                  ✏️
                </button>
                <button
                  @click="store.removePosition(pos)"
                  class="p-1.5 rounded-lg hover:bg-roseAcc/15 text-white/35 hover:text-roseAcc transition-colors"
                  title="Supprimer la ligne"
                >
                  🗑️
                </button>
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const router = useRouter()

const props = defineProps({
  positions: { type: Array, default: () => [] },
  globalSearch: { type: String, default: '' }
})

const searchFilter = ref('')
const categoryFilter = ref('all')
const sortKey = ref('val')
const sortOrder = ref('desc')

const totalPortfolioVal = computed(() => {
  const sumTitres = (props.positions || []).reduce((acc, p) => acc + p.quantity * p.current_price, 0)
  return Math.max(1, store.summary?.total_value || sumTitres)
})

const getWeightPct = (pos) => {
  return ((pos.quantity * pos.current_price) / totalPortfolioVal.value) * 100
}

const sortBy = (key) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'desc'
  }
}

const filteredAndSortedPositions = computed(() => {
  let list = [...props.positions]

  const q = (searchFilter.value || props.globalSearch || '').toLowerCase().trim()
  if (q) {
    list = list.filter(
      (p) =>
        (p.name && p.name.toLowerCase().includes(q)) ||
        (p.ticker && p.ticker.toLowerCase().includes(q)) ||
        (p.sector && p.sector.toLowerCase().includes(q))
    )
  }

  if (categoryFilter.value === 'gainers') {
    list = list.filter((p) => p.variation_pct >= 0)
  } else if (categoryFilter.value === 'losers') {
    list = list.filter((p) => p.variation_pct < 0)
  } else if (categoryFilter.value === 'etf') {
    list = list.filter((p) => p.sector === 'ETF & Indice' || (p.name && p.name.toUpperCase().includes('ETF')))
  } else if (categoryFilter.value === 'nominatif') {
    list = list.filter((p) => store.isNominatifEligible(p))
  }

  list.sort((a, b) => {
    let valA = 0
    let valB = 0

    switch (sortKey.value) {
      case 'name':
        return sortOrder.value === 'asc' ? a.name.localeCompare(b.name) : b.name.localeCompare(a.name)
      case 'quantity':
        valA = a.quantity
        valB = b.quantity
        break
      case 'pru':
        valA = a.pru
        valB = b.pru
        break
      case 'current_price':
        valA = a.current_price
        valB = b.current_price
        break
      case 'invested':
        valA = a.quantity * a.pru
        valB = b.quantity * b.pru
        break
      case 'val':
        valA = a.quantity * a.current_price
        valB = b.quantity * b.current_price
        break
      case 'amount_var':
        valA = (a.current_price - a.pru) * a.quantity
        valB = (b.current_price - b.pru) * b.quantity
        break
      case 'variation_pct':
        valA = a.variation_pct
        valB = b.variation_pct
        break
    }

    return sortOrder.value === 'asc' ? valA - valB : valB - valA
  })

  return list
})
</script>
