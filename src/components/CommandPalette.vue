<template>
  <div v-if="isOpen" class="fixed inset-0 z-[200] flex items-start justify-center pt-16 sm:pt-28 px-3 sm:px-4">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/70 backdrop-blur-md transition-opacity" @click="$emit('close')"></div>

    <!-- Modal -->
    <div
      class="relative w-full max-w-xl bg-[#0A0D14]/95 backdrop-blur-2xl border border-white/15 rounded-3xl shadow-2xl overflow-hidden transform transition-all flex flex-col animate-fade-up"
      @keydown.esc="$emit('close')"
      @keydown.down.prevent="navigateCommand(1)"
      @keydown.up.prevent="navigateCommand(-1)"
      @keydown.enter.prevent="executeCommand"
    >
      <div class="flex items-center px-4 py-3.5 border-b border-white/10">
        <svg class="w-5 h-5 text-neonLime mr-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          ref="searchInput"
          v-model="query"
          type="text"
          placeholder="Chercher un titre (LVMH, AI.PA...), une page ou une action..."
          class="w-full bg-transparent text-white placeholder-white/40 focus:outline-none text-sm sm:text-base"
          @keydown.esc="$emit('close')"
        />
        <button @click="$emit('close')" class="ml-2 text-[10px] bg-white/10 px-2 py-1 rounded-lg border border-white/10 font-mono text-white/60 hover:text-white shrink-0">
          ESC
        </button>
      </div>

      <div class="max-h-[65vh] overflow-y-auto custom-scrollbar p-2">
        <!-- Direct AI Stock Search if query typed -->
        <div
          v-if="query.trim().length >= 2"
          @click="inspectCustomQuery"
          class="mb-2 px-3 py-2.5 rounded-2xl bg-neonPurple/15 hover:bg-neonPurple/25 border border-neonPurple/30 flex items-center justify-between cursor-pointer transition-all"
        >
          <div class="flex items-center gap-3">
            <span class="text-lg">✦</span>
            <div>
              <p class="text-xs sm:text-sm font-bold text-white">Analyser « {{ query.toUpperCase() }} » avec BourseAi</p>
              <p class="text-[10px] text-lavender">Ouvrir le diagnostic fondamental & consensus en direct</p>
            </div>
          </div>
          <span class="text-xs text-neonLime font-mono font-bold">Entrée ↵</span>
        </div>

        <!-- Positions Matching -->
        <div class="mb-2" v-if="positionCommands.length > 0">
          <div class="px-3 py-1.5 text-[10px] font-bold text-white/40 uppercase tracking-wider font-mono">Vos Titres en Portefeuille</div>
          <div
            v-for="cmd in positionCommands"
            :key="cmd.id"
            :class="['px-3 py-2.5 rounded-xl flex items-center justify-between gap-3 cursor-pointer transition-colors', selectedIndex === globalIndexOf(cmd) ? 'bg-neonLime/15 text-neonLime' : 'hover:bg-white/5 text-white/80']"
            @mouseover="selectedIndex = globalIndexOf(cmd)"
            @click="executeCommand"
          >
            <div class="flex items-center gap-3 min-w-0">
              <span class="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center font-bold text-[10px] text-white shrink-0">{{ cmd.icon }}</span>
              <div class="flex flex-col min-w-0">
                <span class="font-bold text-sm truncate">{{ cmd.title }}</span>
                <span class="text-[10px] text-white/40 font-mono truncate">{{ cmd.subtitle }}</span>
              </div>
            </div>
            <span class="text-xs font-mono font-bold shrink-0" :class="cmd.perf >= 0 ? 'text-neonLime' : 'text-roseAcc'">
              {{ cmd.perf >= 0 ? '+' : '' }}{{ cmd.perf.toFixed(1) }}%
            </span>
          </div>
        </div>

        <!-- Navigation -->
        <div class="mb-2" v-if="navigationCommands.length > 0">
          <div class="px-3 py-1.5 text-[10px] font-bold text-white/40 uppercase tracking-wider font-mono">Navigation</div>
          <div
            v-for="cmd in navigationCommands"
            :key="cmd.id"
            :class="['px-3 py-2.5 rounded-xl flex items-center gap-3 cursor-pointer transition-colors', selectedIndex === globalIndexOf(cmd) ? 'bg-neonLime/15 text-neonLime' : 'hover:bg-white/5 text-white/80']"
            @mouseover="selectedIndex = globalIndexOf(cmd)"
            @click="executeCommand"
          >
            <span class="text-lg">{{ cmd.icon }}</span>
            <div class="flex flex-col">
              <span class="font-medium text-sm">{{ cmd.title }}</span>
              <span class="text-[10px] text-white/40" v-if="cmd.subtitle">{{ cmd.subtitle }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div v-if="actionCommands.length > 0">
          <div class="px-3 py-1.5 text-[10px] font-bold text-white/40 uppercase tracking-wider font-mono">Actions Rapides</div>
          <div
            v-for="cmd in actionCommands"
            :key="cmd.id"
            :class="['px-3 py-2.5 rounded-xl flex items-center gap-3 cursor-pointer transition-colors', selectedIndex === globalIndexOf(cmd) ? 'bg-neonLime/15 text-neonLime' : 'hover:bg-white/5 text-white/80']"
            @mouseover="selectedIndex = globalIndexOf(cmd)"
            @click="executeCommand"
          >
            <span class="text-lg">{{ cmd.icon }}</span>
            <div class="flex flex-col">
              <span class="font-medium text-sm">{{ cmd.title }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../stores/app'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close'])
const router = useRouter()
const store = useAppStore()

const searchInput = ref(null)
const query = ref('')
const selectedIndex = ref(0)

const baseCommands = computed(() => {
  const posCmds = (store.positions || []).map((p) => ({
    id: `pos-${p.ticker || p.name}`,
    type: 'pos',
    title: p.name,
    subtitle: `${p.ticker} • ${p.quantity} titres`,
    perf: p.variation_pct || 0,
    icon: (p.ticker || p.name || 'P').substring(0, 2).toUpperCase(),
    action: () => store.openStockInspector(p)
  }))

  const navAndActions = [
    { id: 'nav-home', type: 'nav', title: 'Synthèse', subtitle: 'Tableau de bord global', icon: '⊞', action: () => router.push('/') },
    { id: 'nav-portfolio', type: 'nav', title: 'Portefeuille', subtitle: 'Vos positions & allocation', icon: '💼', action: () => router.push('/portfolio') },
    { id: 'nav-perf', type: 'nav', title: 'Performance & X-Ray', subtitle: 'Sharpe, Beta, Benchmark, Géo', icon: '📈', action: () => router.push('/performance') },
    { id: 'nav-div', type: 'nav', title: 'Dividendes & Rente', subtitle: 'Calendrier, YoC et simulateur FIRE', icon: '💰', action: () => router.push('/dividends') },
    { id: 'nav-plan', type: 'nav', title: 'Plan, Frais & Fiscalité', subtitle: 'Rééquilibrage, TER et Statut PEA', icon: '🎯', action: () => router.push('/plan') },
    { id: 'nav-research', type: 'nav', title: 'Recherche & Copilote IA', subtitle: 'Directeur Financier BourseAi', icon: '🧠', action: () => router.push('/research') },
    { id: 'nav-watchlist', type: 'nav', title: 'Watchlist & Alertes', subtitle: 'Cibles d’achat', icon: '⭐', action: () => router.push('/watchlist') },
    { id: 'act-add-pos', type: 'act', title: 'Ajouter une ligne au portefeuille', icon: '➕', action: () => store.openAddPositionModal() },
    { id: 'act-ai', type: 'act', title: 'Ouvrir le Copilote IA BourseAi', icon: '✦', action: () => { store.isAiAdvisorOpen = true } },
    { id: 'act-discrete', type: 'act', title: 'Activer/Désactiver le Mode Discret', icon: '👁️', action: () => store.toggleDiscreteMode() },
    { id: 'act-refresh', type: 'act', title: 'Actualiser les cours en direct', icon: '⚡', action: () => store.refreshData() },
    { id: 'act-settings', type: 'act', title: 'Paramètres & Import CSV', icon: '⚙️', action: () => router.push('/settings') }
  ]

  return [...posCmds, ...navAndActions]
})

const filteredCommands = computed(() => {
  if (!query.value.trim()) {
    // Show top 4 positions + nav + actions when empty
    return baseCommands.value.filter((c, idx) => c.type !== 'pos' || idx < 4)
  }
  const q = query.value.toLowerCase()
  return baseCommands.value.filter(
    (c) =>
      c.title.toLowerCase().includes(q) ||
      (c.subtitle && c.subtitle.toLowerCase().includes(q))
  )
})

const positionCommands = computed(() => filteredCommands.value.filter((c) => c.type === 'pos'))
const navigationCommands = computed(() => filteredCommands.value.filter((c) => c.type === 'nav'))
const actionCommands = computed(() => filteredCommands.value.filter((c) => c.type === 'act'))

const globalIndexOf = (cmd) => {
  return filteredCommands.value.findIndex((c) => c.id === cmd.id)
}

const navigateCommand = (dir) => {
  const max = filteredCommands.value.length - 1
  if (max < 0) return
  selectedIndex.value += dir
  if (selectedIndex.value < 0) selectedIndex.value = max
  if (selectedIndex.value > max) selectedIndex.value = 0
}

const inspectCustomQuery = () => {
  const q = query.value.trim().toUpperCase()
  if (!q) return
  store.openStockInspector({
    name: q,
    ticker: q,
    sector: 'Recherche Directe'
  })
  emit('close')
}

const executeCommand = () => {
  const cmd = filteredCommands.value[selectedIndex.value]
  if (cmd && cmd.action) {
    cmd.action()
    emit('close')
  } else if (query.value.trim()) {
    inspectCustomQuery()
  }
}

watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      query.value = ''
      selectedIndex.value = 0
      nextTick(() => {
        if (searchInput.value) searchInput.value.focus()
      })
    }
  }
)
</script>
