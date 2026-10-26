<template>
  <div class="glass-card rounded-32 sm:rounded-36 p-5 sm:p-7 border border-white/[0.08] specular-highlight relative overflow-hidden group">
    <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>

    <div class="flex items-center justify-between mb-6 relative z-10">
      <div>
        <h3 class="text-lg font-bold text-white flex items-center gap-2.5">
          <span class="w-9 h-9 rounded-2xl bg-neonLime/10 text-neonLime flex items-center justify-center border border-neonLime/20 shadow-[0_0_15px_rgba(163,230,53,0.15)]">📅</span>
          Prochains Détachements
        </h3>
        <p class="text-white/40 text-xs mt-1 font-medium">Calendrier ex-dividende de vos lignes</p>
      </div>

      <div class="text-right">
        <p class="text-[10px] text-white/40 uppercase tracking-widest font-mono font-bold mb-0.5">À venir</p>
        <p class="text-lg sm:text-xl font-black text-neonLime tabular-nums font-mono tracking-tight">
          {{ store.formatCurrency(totalProjected) }}
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="py-10 flex justify-center items-center">
      <div class="w-8 h-8 rounded-full border-2 border-neonLime border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="!displayDividends.length" class="py-10 text-center text-white/40 border border-dashed border-white/10 rounded-2xl">
      <span class="text-2xl mb-2 block opacity-50">💸</span>
      <p class="text-xs font-medium">Aucun détachement imminent détecté.</p>
    </div>

    <div v-else class="space-y-3 relative z-10">
      <div
        v-for="(div, idx) in displayDividends"
        :key="idx"
        class="liquid-glass-subtle p-3.5 rounded-2xl border border-white/5 hover:border-neonLime/30 transition-all group/item flex items-center justify-between gap-3"
      >
        <div class="flex items-center gap-3 min-w-0">
          <div class="w-11 h-11 rounded-xl bg-white/5 border border-white/10 flex flex-col items-center justify-center shrink-0 group-hover/item:bg-neonLime/10 group-hover/item:border-neonLime/20 transition-colors">
            <span class="text-[9px] uppercase font-bold text-white/50 group-hover/item:text-neonLime">{{ getMonth(div.ex_date) }}</span>
            <span class="text-base font-black text-white group-hover/item:text-neonLime leading-none mt-0.5">{{ getDay(div.ex_date) }}</span>
          </div>

          <div class="min-w-0">
            <h4 class="font-bold text-white text-sm truncate">{{ div.name }}</h4>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-white/10 text-white/70 border border-white/10">{{ div.ticker }}</span>
              <span v-if="div.yield_on_cost" class="text-[10px] text-neonLime font-mono font-bold">
                YoC: {{ div.yield_on_cost }}%
              </span>
            </div>
          </div>
        </div>

        <div class="text-right shrink-0">
          <p class="font-black text-white text-sm sm:text-base font-mono tabular-nums">
            +{{ store.formatCurrency(div.projected_total) }}
          </p>
          <p class="text-[10px] text-white/40 mt-0.5 font-mono">
            {{ div.amount_per_share.toFixed(2) }} € / titre
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getApiBase } from '../config'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const props = defineProps({
  userId: {
    type: String,
    required: false
  }
})

const isLoading = ref(false)
const dividends = ref([])

// Fallback calendar from store dividend positions if API returns empty or in demo mode
const displayDividends = computed(() => {
  if (dividends.value && dividends.value.length > 0) return dividends.value
  const divPos = store.dividendMetrics?.positions || []
  const upcomingMonths = ['2026-11-18', '2026-12-15', '2027-01-06', '2027-05-19', '2027-05-24']
  return divPos.slice(0, 4).map((p, i) => ({
    name: p.name,
    ticker: p.ticker,
    ex_date: upcomingMonths[i % upcomingMonths.length],
    amount_per_share: p.quantity > 0 ? p.annual_income / p.quantity : 1.5,
    projected_total: p.ticker === 'TTE.PA' ? p.annual_income / 4 : p.annual_income,
    yield_on_cost: p.yield_on_cost
  }))
})

const totalProjected = computed(() => {
  return displayDividends.value.reduce((sum, d) => sum + (d.projected_total || 0), 0)
})

const fetchDividends = async () => {
  if (store.isDemoMode) return
  const uid = props.userId || localStorage.getItem('pea_user_id') || ''
  const token = localStorage.getItem('pea_access_token')
  const headers = token ? { Authorization: 'Bearer ' + token } : {}

  isLoading.value = true
  try {
    const url = uid ? `${getApiBase()}/api/portfolio/dividends?user_id=${uid}` : `${getApiBase()}/api/portfolio/dividends`
    const res = await fetch(url, { headers })
    if (res.ok) {
      const data = await res.json()
      dividends.value = data.dividends || []
    }
  } catch (e) {
    console.error('Failed to fetch dividends', e)
  } finally {
    isLoading.value = false
  }
}

watch(() => props.userId, fetchDividends)
onMounted(fetchDividends)

const getMonth = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleString('fr-FR', { month: 'short' }).replace('.', '')
}

const getDay = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.getDate()
}
</script>
