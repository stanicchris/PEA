<template>
  <div class="space-y-6">
    <div class="liquid-glass-card rounded-36 p-5 sm:p-8 border border-white/10 relative overflow-hidden specular-highlight">
      <!-- Glow effect -->
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-lavender/20 blur-[80px] rounded-full pointer-events-none"></div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 relative z-10">
        <div>
          <h3 class="text-xl font-black text-white flex items-center gap-2">
            <span class="text-2xl">⚖️</span> Rééquilibrage Intelligent (DCA)
          </h3>
          <p class="text-white/50 text-xs mt-1 font-medium">
            Calculez quoi acheter avec votre prochain versement pour atteindre votre allocation cible sans vendre.
          </p>
        </div>

        <div class="flex items-center gap-1.5 self-start sm:self-auto">
          <button
            type="button"
            @click="equalizeTargets"
            class="px-3 py-1.5 rounded-full liquid-glass-subtle hover:bg-white/10 border border-white/10 text-[11px] text-white/80 font-semibold transition-all active:scale-95"
            title="Répartir à parts égales"
          >
            Équipondérer
          </button>
          <button
            type="button"
            @click="resetToCurrentWeights"
            class="px-3 py-1.5 rounded-full liquid-glass-subtle hover:bg-white/10 border border-white/10 text-[11px] text-white/60 hover:text-white font-semibold transition-all active:scale-95"
            title="Réinitialiser aux poids actuels"
          >
            Poids actuels
          </button>
        </div>
      </div>

      <div class="relative z-10">
        <!-- Input deposit -->
        <div class="bg-black/30 rounded-24 p-4 sm:p-5 mb-5 border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <label class="text-white/60 text-[10px] font-bold uppercase tracking-widest font-mono block mb-1">
              Prochain Versement / Liquidités à investir (€)
            </label>
            <div class="flex items-center gap-2">
              <input
                type="number"
                v-model.number="depositAmount"
                @input="calculateRebalancing"
                min="50"
                step="50"
                class="bg-transparent border-b border-white/20 text-2xl font-black text-white font-mono w-36 focus:outline-none focus:border-lavender"
                placeholder="1000"
              />
              <span class="text-lavender font-bold text-lg">€</span>
            </div>
          </div>

          <button
            @click="calculateRebalancing"
            class="px-5 py-2.5 rounded-full bg-lavender hover:bg-neonLime text-black font-black text-xs transition-all active:scale-95 cursor-pointer"
          >
            Calculer les ordres d'achat
          </button>
        </div>

        <!-- Empty State -->
        <div v-if="!assets.length" class="text-center py-8 text-white/40 text-xs border border-dashed border-white/10 rounded-2xl">
          Ajoutez des positions à votre portefeuille pour simuler votre rééquilibrage.
        </div>

        <!-- Targets & Results -->
        <div v-else class="space-y-3">
          <div class="grid grid-cols-12 gap-2 px-3 text-white/40 text-[10px] uppercase font-bold font-mono">
            <div class="col-span-5">Actif & Poids actuel</div>
            <div class="col-span-3 text-center">Cible %</div>
            <div class="col-span-4 text-right">Ordre suggéré</div>
          </div>

          <div class="max-h-[340px] overflow-y-auto custom-scrollbar space-y-2.5 pr-1">
            <div
              v-for="asset in assets"
              :key="asset.ticker"
              class="grid grid-cols-12 gap-2 items-center liquid-glass-subtle bg-white/5 p-3 rounded-2xl border border-white/10"
            >
              <div class="col-span-5 min-w-0">
                <p class="text-xs sm:text-sm font-bold text-white truncate" :title="asset.name">{{ asset.name }}</p>
                <p class="text-white/40 text-[10px] font-mono">
                  {{ store.formatCurrency(asset.current_value) }} ({{ ((asset.current_value / totalCurrentValue) * 100).toFixed(1) }}%)
                </p>
              </div>
              <div class="col-span-3 flex items-center justify-center gap-1">
                <input
                  type="number"
                  v-model.number="asset.target_pct"
                  @input="calculateRebalancing"
                  min="0"
                  max="100"
                  class="bg-black/50 border border-white/15 rounded-xl w-14 sm:w-16 py-1.5 text-center text-xs font-mono font-bold text-white focus:border-lavender focus:outline-none"
                />
                <span class="text-[10px] text-white/40 font-mono">%</span>
              </div>
              <div class="col-span-4 text-right font-mono">
                <span v-if="asset.to_buy_euros > 0" class="text-neonLime font-bold text-xs sm:text-sm">
                  +{{ asset.to_buy_euros.toFixed(0) }} €
                </span>
                <span v-else class="text-white/30 font-bold text-xs">0 €</span>
                <p v-if="asset.to_buy_shares > 0" class="text-white/60 text-[10px] mt-0.5">
                  Acheter ~{{ asset.to_buy_shares }} titre{{ asset.to_buy_shares > 1 ? 's' : '' }}
                </p>
              </div>
            </div>
          </div>

          <div
            class="flex items-center justify-between px-4 py-2.5 rounded-2xl text-xs font-mono border mt-3"
            :class="Math.abs(totalTargetPct - 100) <= 1 ? 'bg-neonLime/10 border-neonLime/25 text-neonLime' : 'bg-roseAcc/10 border-roseAcc/30 text-roseAcc'"
          >
            <span>Total des cibles d'allocation :</span>
            <span class="font-bold">{{ totalTargetPct.toFixed(0) }}% / 100%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const depositAmount = ref(1000)
const assets = ref([])

const totalCurrentValue = computed(() => {
  return Math.max(1, assets.value.reduce((sum, a) => sum + a.current_value, 0))
})

const totalTargetPct = computed(() => {
  return assets.value.reduce((sum, a) => sum + (parseFloat(a.target_pct) || 0), 0)
})

const buildAssetsFromPositions = () => {
  const list = store.positions || []
  if (!list.length) {
    assets.value = []
    return
  }
  const total = Math.max(
    1,
    list.reduce((sum, p) => sum + (p.amount || p.quantity * p.current_price || 0), 0)
  )
  assets.value = list
    .map((p) => {
      const val = p.amount || p.quantity * p.current_price || 0
      const pct = (val / total) * 100
      return {
        ticker: p.ticker || p.isin || p.name,
        name: p.name,
        current_value: val,
        last_price: p.current_price || p.last_price || 1,
        target_pct: Math.round(pct),
        ideal_buy: 0,
        to_buy_euros: 0,
        to_buy_shares: 0
      }
    })
    .sort((a, b) => b.current_value - a.current_value)

  // Ensure sum is exactly 100%
  const diff = 100 - assets.value.reduce((s, a) => s + a.target_pct, 0)
  if (assets.value[0]) {
    assets.value[0].target_pct += diff
  }
  calculateRebalancing()
}

const equalizeTargets = () => {
  if (!assets.value.length) return
  const eq = Math.floor(100 / assets.value.length)
  assets.value.forEach((a, idx) => {
    a.target_pct = idx === 0 ? 100 - eq * (assets.value.length - 1) : eq
  })
  calculateRebalancing()
}

const resetToCurrentWeights = () => {
  buildAssetsFromPositions()
}

const calculateRebalancing = () => {
  if (!assets.value.length) return
  const normFactor = totalTargetPct.value > 0 ? 100 / totalTargetPct.value : 1
  const totalFutureValue = totalCurrentValue.value + (Number(depositAmount.value) || 0)

  assets.value.forEach((asset) => {
    const normalizedTarget = (parseFloat(asset.target_pct) || 0) * normFactor
    const targetValue = totalFutureValue * (normalizedTarget / 100)
    const shortfall = targetValue - asset.current_value
    asset.ideal_buy = shortfall > 0 ? shortfall : 0
  })

  const totalShortfall = assets.value.reduce((sum, a) => sum + a.ideal_buy, 0)

  assets.value.forEach((asset) => {
    if (totalShortfall > 0 && asset.ideal_buy > 0) {
      const allocation = (asset.ideal_buy / totalShortfall) * (Number(depositAmount.value) || 0)
      asset.to_buy_euros = Math.min(allocation, asset.ideal_buy)
    } else {
      asset.to_buy_euros = 0
    }
    asset.to_buy_shares = Math.max(0, Math.round(asset.to_buy_euros / (asset.last_price || 1)))
  })
}

watch(() => store.positions, buildAssetsFromPositions, { immediate: true, deep: true })
</script>
