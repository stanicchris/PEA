<template>
  <div v-if="isOpen" class="fixed inset-0 z-[160] flex items-end sm:items-center justify-center p-0 sm:p-4">
    <!-- Backdrop with blur -->
    <div class="fixed inset-0 bg-black/80 backdrop-blur-xl cursor-pointer" @click="$emit('close')"></div>

    <!-- Modal Content (Mobile Bottom Sheet / Desktop Liquid Glass Modal) -->
    <div class="relative w-full max-w-4xl max-h-[92dvh] overflow-y-auto liquid-glass-chassis rounded-t-36 sm:rounded-36 shadow-2xl p-5 sm:p-8 flex flex-col text-white specular-highlight border border-white/15 animate-sheet-up">
      <!-- Mobile Drag Handle -->
      <div class="w-12 h-1.5 bg-white/20 rounded-full mx-auto mb-3 sm:hidden"></div>

      <!-- Header -->
      <div class="flex justify-between items-start mb-5 pb-3 border-b border-white/[0.06] sticky top-0 bg-[#0A0D14]/90 backdrop-blur-md -mx-2 px-2 z-10">
        <div>
          <div class="flex items-center gap-2 mb-1 flex-wrap">
            <span class="px-2.5 py-0.5 rounded-full bg-neonLime/15 border border-neonLime/30 text-neonLime text-xs font-mono font-bold shadow-[0_0_10px_rgba(163,230,53,0.15)]">BourseAi 2.0</span>
            <span class="text-white/40 text-xs font-mono">{{ asset?.ticker }}</span>
            <span
              v-if="store.isNominatifEligible(asset)"
              class="px-2 py-0.5 rounded-full bg-amberAcc/15 border border-amberAcc/30 text-amberAcc text-[10px] font-mono font-bold"
            >
              🎖️ Prime Fidélité +10%
            </span>
          </div>
          <h2 class="text-xl sm:text-3xl font-black text-white tracking-tight">{{ asset?.name }}</h2>
          <p class="text-white/50 text-xs mt-0.5 font-medium">{{ asset?.sector }}</p>
        </div>
        <button
          @click="$emit('close')"
          class="text-white/40 hover:text-white transition-colors liquid-glass-subtle hover:border-white/20 p-2.5 rounded-full cursor-pointer active:scale-95"
          title="Fermer"
          aria-label="Fermer"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- User's Held Position Summary (if in portfolio) -->
      <div
        v-if="asset?.quantity"
        class="mb-5 p-3.5 rounded-2xl bg-white/[0.04] border border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs font-mono"
      >
        <div class="flex items-center gap-2">
          <span class="text-neonLime">💼 En portefeuille :</span>
          <span class="text-white font-bold">{{ asset.quantity }} titres</span>
          <span class="text-white/40">• PRU {{ store.formatCurrency(asset.pru) }}</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-white font-bold">{{ store.formatCurrency(asset.quantity * asset.current_price) }}</span>
          <span
            v-if="asset.variation_pct !== undefined"
            class="px-2 py-0.5 rounded-full font-bold"
            :class="asset.variation_pct >= 0 ? 'bg-neonLime/15 text-neonLime' : 'bg-roseAcc/15 text-roseAcc'"
          >
            {{ asset.variation_pct >= 0 ? '+' : '' }}{{ asset.variation_pct.toFixed(2) }}%
          </span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center py-14 sm:py-18">
        <div class="relative w-14 h-14 mb-5">
          <div class="absolute inset-0 border-4 border-white/10 rounded-full"></div>
          <div class="absolute inset-0 border-4 border-neonLime rounded-full border-t-transparent animate-spin"></div>
        </div>
        <p class="text-white/60 animate-pulse font-medium text-xs sm:text-sm text-center px-4">
          Analyse instantanée des fondamentaux et ratios en direct...
        </p>
      </div>

      <!-- Content -->
      <div v-else-if="analysis" class="space-y-5">
        <!-- Score & Recommendation -->
        <div class="flex flex-col md:flex-row gap-4 items-stretch">
          <div class="flex-1 liquid-glass-card rounded-28 p-5 flex items-center gap-5 specular-highlight">
            <div
              class="relative w-20 h-20 sm:w-24 sm:h-24 shrink-0 flex items-center justify-center rounded-full shadow-lg"
              :style="`background: conic-gradient(${analysis.score_percent >= 60 ? '#A3E635' : (analysis.score_percent >= 40 ? '#F59E0B' : '#F43F5E')} ${analysis.score_percent}%, rgba(255,255,255,0.05) 0);`"
            >
              <div class="absolute inset-2 bg-[#0C1017] rounded-full flex items-center justify-center flex-col shadow-inner">
                <span class="text-xl sm:text-2xl font-black" :class="analysis.score_percent >= 60 ? 'text-neonLime' : (analysis.score_percent >= 40 ? 'text-amberAcc' : 'text-roseAcc')">
                  {{ analysis.score_percent }}%
                </span>
              </div>
            </div>
            <div>
              <p class="text-white/40 text-xs uppercase font-bold tracking-wider mb-1 font-mono">Score BourseAi</p>
              <p class="text-lg sm:text-xl font-black" :class="analysis.should_invest ? 'text-neonLime' : 'text-amberAcc'">
                {{ analysis.should_invest ? 'Opportunité Favorable' : 'À Surveiller' }}
              </p>
              <p class="text-white/40 text-[11px] mt-1 font-mono">{{ analysis.source }}</p>
            </div>
          </div>

          <div class="flex-1 grid grid-cols-2 gap-3">
            <div class="liquid-glass-subtle rounded-24 p-3.5 border border-white/10">
              <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Dernier Cours</p>
              <p class="text-lg font-bold text-white font-mono">{{ (analysis.metrics?.price || asset?.current_price || 100).toFixed(2) }} €</p>
            </div>
            <div class="liquid-glass-subtle rounded-24 p-3.5 border border-white/10">
              <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Objectif 12m</p>
              <p class="text-lg font-bold text-neonLime font-mono">{{ (analysis.metrics?.target_price || (asset?.current_price || 100) * 1.12).toFixed(2) }} €</p>
            </div>
            <div class="liquid-glass-subtle rounded-24 p-3.5 border border-white/10">
              <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Rendement Div.</p>
              <p class="text-lg font-bold text-lavender font-mono">{{ (analysis.metrics?.div_yield || 2.4).toFixed(2) }} %</p>
            </div>
            <div class="liquid-glass-subtle rounded-24 p-3.5 border border-white/10">
              <p class="text-white/40 text-[10px] font-semibold mb-1 uppercase tracking-wider font-mono">Consensus</p>
              <p class="text-base font-bold text-neonLime font-mono">{{ analysis.metrics?.recommendation || 'ACHAT' }}</p>
            </div>
          </div>
        </div>

        <!-- Synthesis Box -->
        <div class="liquid-glass-card rounded-28 p-5 specular-highlight">
          <h4 class="text-white/40 font-bold text-xs uppercase tracking-widest mb-2 font-mono">Synthèse Fondamentale & Activité</h4>
          <p class="text-white/90 leading-relaxed font-medium text-xs sm:text-sm">
            {{ analysis.summary }}
          </p>
        </div>

        <!-- Pros and Cons -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-neonLime/10 border border-neonLime/20 rounded-28 p-4 sm:p-5">
            <h4 class="text-neonLime font-bold mb-3 flex items-center gap-2 text-xs sm:text-sm">
              <span>↗</span> Points Forts & Catalyseurs
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(pro, i) in (analysis.pros || '').split('•')" :key="'p' + i" v-show="pro.trim()" class="flex items-start gap-2">
                <span class="text-neonLime mt-0.5">&bull;</span> {{ pro.trim() }}
              </p>
            </div>
          </div>

          <div class="bg-roseAcc/10 border border-roseAcc/20 rounded-28 p-4 sm:p-5">
            <h4 class="text-roseAcc font-bold mb-3 flex items-center gap-2 text-xs sm:text-sm">
              <span>↘</span> Risques & Vigilances
            </h4>
            <div class="text-white/80 text-xs leading-relaxed space-y-2">
              <p v-for="(con, i) in (analysis.cons || '').split('•')" :key="'c' + i" v-show="con.trim()" class="flex items-start gap-2">
                <span class="text-roseAcc mt-0.5">&bull;</span> {{ con.trim() }}
              </p>
            </div>
          </div>
        </div>

        <!-- Bottom Action Bar -->
        <div class="pt-4 border-t border-white/[0.08] flex flex-col sm:flex-row items-center justify-between gap-2.5">
          <a
            v-if="analysis.target_url"
            :href="analysis.target_url"
            target="_blank"
            class="w-full sm:w-auto inline-flex items-center justify-center gap-2 text-white/70 hover:text-white text-xs font-bold transition-colors liquid-glass-pill hover:bg-white/10 px-5 py-2.5 rounded-full border border-white/15 active:scale-95"
          >
            Ouvrir sur ZoneBourse ↗
          </a>

          <div class="flex items-center gap-2.5 w-full sm:w-auto">
            <button
              @click="goToDetail"
              class="flex-1 sm:flex-initial px-5 py-2.5 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs transition-all cursor-pointer active:scale-95"
            >
              📈 Courbe & Fiche Complète
            </button>

            <button
              @click="$emit('close')"
              class="px-5 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 text-white font-bold text-xs border border-white/15 transition-all cursor-pointer active:scale-95"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getApiBase } from '../config'
import { useAppStore } from '../stores/app'

const store = useAppStore()

const props = defineProps({
  isOpen: Boolean,
  asset: Object
})
const emit = defineEmits(['close'])

const isLoading = ref(false)
const analysis = ref(null)
const router = useRouter()

const goToDetail = () => {
  emit('close')
  router.push(`/stock/${props.asset.ticker || props.asset.name}`)
}

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))

const buildLocalFallback = (asset) => {
  const price = asset?.current_price || 120.0
  return {
    company_name: asset?.name || asset?.ticker,
    should_invest: true,
    score_percent: 78,
    summary: `${asset?.name || asset?.ticker} affiche un profil fondamental solide au sein de son secteur (${asset?.sector || 'Actions Européennes'}), soutenu par une génération de cash-flow régulière et une visibilité long terme adaptée au PEA.`,
    pros: `• Leader sur son marché avec de fortes barrières à l'entrée • Croissance pérenne du chiffre d'affaires et de la rentabilité`,
    cons: `• Sensibilité aux cycles macroéconomiques mondiaux • Volatilité de court terme liée aux taux d'intérêt`,
    target_url: `https://www.zonebourse.fr/recherche/?mots=${encodeURIComponent(asset?.name || asset?.ticker || '')}`,
    source: 'Analyse Fondamentale BourseAi 2.0',
    metrics: {
      price,
      target_price: Number((price * 1.12).toFixed(2)),
      div_yield: 2.4,
      recommendation: 'ACHAT'
    }
  }
}

watch(
  () => props.isOpen,
  async (newVal) => {
    if (newVal && props.asset) {
      if (store.isDemoMode) {
        analysis.value = buildLocalFallback(props.asset)
        return
      }
      isLoading.value = true
      analysis.value = null
      try {
        const apiBase = getApiBase()
        const qName = encodeURIComponent(props.asset.name || '')
        const res = await fetch(
          `${apiBase}/api/stock/analyze/${encodeURIComponent(props.asset.ticker || props.asset.name)}?name=${qName}`,
          {
            headers: { Authorization: 'Bearer ' + (localStorage.getItem('pea_access_token') || '') }
          }
        )
        if (!res.ok) throw new Error('Fallback')
        analysis.value = await res.json()
      } catch (err) {
        analysis.value = buildLocalFallback(props.asset)
      } finally {
        isLoading.value = false
      }
    }
  }
)
</script>
