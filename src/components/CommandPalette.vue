<template>
  <div v-if="isOpen" class="fixed inset-0 z-[200] flex items-start justify-center pt-32 px-4">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-md transition-opacity" @click="$emit('close')"></div>
    
    <!-- Modal -->
    <div 
      class="relative w-full max-w-xl bg-[#0A0D14]/90 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-2xl overflow-hidden transform transition-all flex flex-col"
      @keydown.esc="$emit('close')"
      @keydown.down.prevent="navigateCommand(1)"
      @keydown.up.prevent="navigateCommand(-1)"
      @keydown.enter.prevent="executeCommand"
    >
      <div class="flex items-center px-4 py-3 border-b border-white/10">
        <svg class="w-5 h-5 text-white/50 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input 
          ref="searchInput"
          v-model="query"
          type="text" 
          placeholder="Rechercher une page ou une action..." 
          class="w-full bg-transparent text-white placeholder-white/40 focus:outline-none text-lg"
          @keydown.esc="$emit('close')"
        />
        <div class="flex items-center gap-1 ml-3 shrink-0">
          <span class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded border border-white/10 font-mono text-white/50">ESC</span>
        </div>
      </div>
      
      <div class="max-h-[60vh] overflow-y-auto custom-scrollbar p-2">
        <div v-if="filteredCommands.length === 0" class="p-8 text-center text-white/50 text-sm">
          Aucun résultat pour "{{ query }}"
        </div>
        
        <template v-else>
          <!-- Navigation -->
          <div class="mb-2" v-if="navigationCommands.length > 0">
            <div class="px-3 py-1.5 text-[10px] font-bold text-white/40 uppercase tracking-wider">Navigation</div>
            <div 
              v-for="(cmd, index) in navigationCommands" 
              :key="cmd.id"
              :class="['px-3 py-2.5 rounded-xl flex items-center gap-3 cursor-pointer transition-colors', selectedIndex === globalIndexOf(cmd) ? 'bg-neonLime/15 text-neonLime' : 'hover:bg-white/5 text-white/80']"
              @mouseover="selectedIndex = globalIndexOf(cmd)"
              @click="executeCommand"
            >
              <span class="text-xl">{{ cmd.icon }}</span>
              <div class="flex flex-col">
                <span class="font-medium text-sm">{{ cmd.title }}</span>
                <span class="text-[10px] text-white/40" v-if="cmd.subtitle">{{ cmd.subtitle }}</span>
              </div>
            </div>
          </div>
          
          <!-- Actions -->
          <div v-if="actionCommands.length > 0">
            <div class="px-3 py-1.5 text-[10px] font-bold text-white/40 uppercase tracking-wider">Actions Rapides</div>
            <div 
              v-for="(cmd, index) in actionCommands" 
              :key="cmd.id"
              :class="['px-3 py-2.5 rounded-xl flex items-center gap-3 cursor-pointer transition-colors', selectedIndex === globalIndexOf(cmd) ? 'bg-neonLime/15 text-neonLime' : 'hover:bg-white/5 text-white/80']"
              @mouseover="selectedIndex = globalIndexOf(cmd)"
              @click="executeCommand"
            >
              <span class="text-xl">{{ cmd.icon }}</span>
              <div class="flex flex-col">
                <span class="font-medium text-sm">{{ cmd.title }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '../stores/app';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);
const router = useRouter();
const store = useAppStore();

const searchInput = ref(null);
const query = ref('');
const selectedIndex = ref(0);

const commands = [
  { id: 'nav-home', type: 'nav', title: 'Synthèse', subtitle: 'Tableau de bord', icon: '⊞', action: () => router.push('/') },
  { id: 'nav-portfolio', type: 'nav', title: 'Portefeuille', subtitle: 'Vos positions', icon: '💼', action: () => router.push('/portfolio') },
  { id: 'nav-perf', type: 'nav', title: 'Performance', subtitle: 'TWR, XIRR, Benchmark', icon: '📈', action: () => router.push('/performance') },
  { id: 'nav-div', type: 'nav', title: 'Dividendes', subtitle: 'Calendrier et rente', icon: '💰', action: () => router.push('/dividends') },
  { id: 'nav-plan', type: 'nav', title: 'Plan & Fiscalité', subtitle: 'Statut PEA', icon: '🎯', action: () => router.push('/plan') },
  { id: 'nav-research', type: 'nav', title: 'Recherche & IA', subtitle: 'Groq Advisor', icon: '🧠', action: () => router.push('/research') },
  { id: 'act-discrete', type: 'act', title: 'Activer/Désactiver Mode Discret', icon: '🌙', action: () => store.toggleDiscreteMode() },
  { id: 'act-import-csv', type: 'act', title: 'Importer un fichier CSV (BoursoBank)', icon: '📁', action: () => router.push('/settings') },
  { id: 'act-settings', type: 'act', title: 'Ouvrir les Paramètres', icon: '⚙️', action: () => router.push('/settings') },
  { id: 'act-logout', type: 'act', title: 'Déconnexion', icon: '🚪', action: () => store.logout() }
];

const filteredCommands = computed(() => {
  if (!query.value.trim()) return commands;
  const q = query.value.toLowerCase();
  return commands.filter(c => c.title.toLowerCase().includes(q) || (c.subtitle && c.subtitle.toLowerCase().includes(q)));
});

const navigationCommands = computed(() => filteredCommands.value.filter(c => c.type === 'nav'));
const actionCommands = computed(() => filteredCommands.value.filter(c => c.type === 'act'));

const globalIndexOf = (cmd) => {
  return filteredCommands.value.findIndex(c => c.id === cmd.id);
};

const navigateCommand = (dir) => {
  const max = filteredCommands.value.length - 1;
  if (max < 0) return;
  selectedIndex.value += dir;
  if (selectedIndex.value < 0) selectedIndex.value = max;
  if (selectedIndex.value > max) selectedIndex.value = 0;
};

const executeCommand = () => {
  const cmd = filteredCommands.value[selectedIndex.value];
  if (cmd && cmd.action) {
    cmd.action();
    emit('close');
  }
};

watch(() => props.isOpen, (val) => {
  if (val) {
    query.value = '';
    selectedIndex.value = 0;
    nextTick(() => {
      if (searchInput.value) searchInput.value.focus();
    });
  }
});
</script>
