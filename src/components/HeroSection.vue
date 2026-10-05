<template>
  <div class="liquid-glass-card rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden group specular-highlight">
    <!-- Top Row: Icon + Expand Arrow -->
    <div class="flex justify-between items-center mb-4">
      <div class="w-10 h-10 rounded-2xl liquid-glass-subtle flex items-center justify-center text-white/90 shadow-inner border border-white/10 group-hover:border-neonLime/30 transition-all">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      </div>
      
      <div class="flex gap-2">
        <button @click="store.toggleDiscreteMode()" class="w-8 h-8 rounded-full liquid-glass-subtle hover:bg-white/10 text-white/50 hover:text-white flex items-center justify-center transition-all cursor-pointer" :title="store.isDiscreteMode ? 'Désactiver le mode discret' : 'Activer le mode discret'">
          <!-- Eye closed / open depending on state -->
          <svg v-if="!store.isDiscreteMode" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-neonLime" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
          </svg>
        </button>
        <button @click="$emit('open-settings')" class="w-8 h-8 rounded-full liquid-glass-subtle hover:bg-white/10 text-white/50 hover:text-white flex items-center justify-center transition-all cursor-pointer">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 17L17 7M17 7H7M17 7V17" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Balance & Value -->
    <div class="mb-5">
      <div class="text-white/50 text-xs font-semibold uppercase tracking-wider mb-1.5 flex items-center gap-2">
        <span>Total Balance</span>
        <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-neonLime/15 text-neonLime text-[10px] font-bold border border-neonLime/25 shadow-[0_0_10px_rgba(163,230,53,0.2)]">
          <span class="w-1.5 h-1.5 rounded-full bg-neonLime animate-ping"></span>
          LIVE
        </span>
        <span v-if="summary?.performance?.xirr !== undefined" class="inline-flex items-center ml-2 px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-white/90 text-[10px] font-mono shadow-inner">
          TRI: <span :class="(summary.performance.xirr >= 0 ? 'text-neonLime' : 'text-red-400') + ' ml-1 font-bold'">{{ (summary.performance.xirr * 100).toFixed(2) }}%</span>
        </span>
      </div>

      <div v-if="isLoading" class="h-12 bg-white/5 rounded-2xl animate-pulse w-3/4 mb-2"></div>
      <div v-else class="flex items-baseline gap-1 text-3xl sm:text-4xl lg:text-[40px] font-black tracking-tight text-white tabular-numbers drop-shadow-sm">
        <span>{{ formattedTotal.main }}</span>
        <span class="text-white/40 text-2xl font-bold">,{{ formattedTotal.decimals }} €</span>
      </div>
    </div>

    <!-- 3 Segmented Pill Bars (Breakdown) -->
    <div class="space-y-2 mb-6">
      <div class="grid grid-cols-3 gap-2">
        <div class="h-2 rounded-full bg-neonLime/90 shadow-[0_0_8px_rgba(163,230,53,0.4)]"></div>
        <div class="h-2 rounded-full bg-neonPurple/90 shadow-[0_0_8px_rgba(139,92,246,0.4)]"></div>
        <div class="h-2 rounded-full bg-white/40 shadow-[0_0_8px_rgba(255,255,255,0.2)]"></div>
      </div>
      
      <div class="grid grid-cols-3 text-[11px] font-mono text-white/70 pt-1">
        <div class="flex flex-col">
          <span class="text-white font-bold">{{ formatCurrency(actionsValue) }}</span>
          <span class="text-white/40 text-[10px]">Actions</span>
        </div>
        <div class="flex flex-col">
          <span class="text-white font-bold">{{ formatCurrency(etfValue) }}</span>
          <span class="text-white/40 text-[10px]">ETFs</span>
        </div>
        <div class="flex flex-col">
          <span class="text-white font-bold">{{ formatCurrency(cashValue) }}</span>
          <span class="text-white/40 text-[10px]">Cash</span>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="grid grid-cols-2 gap-3 mt-auto">
      <button 
        @click="$emit('refresh')" 
        :disabled="isRefreshing" 
        class="bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] font-black text-xs sm:text-sm py-3 px-3 rounded-full transition-all shadow-[0_4px_20px_rgba(163,230,53,0.3)] hover:shadow-[0_6px_25px_rgba(163,230,53,0.5)] flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 cursor-pointer"
        title="Interroge Yahoo Finance pour actualiser les cours et enregistrer l'historique dans Supabase"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" :class="isRefreshing ? 'animate-spin' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>{{ isRefreshing ? 'Sync en cours...' : '⚡ Actualiser Cours' }}</span>
      </button>

      <div class="relative">
        <input 
          type="file" 
          ref="csvInputRef"
          accept=".csv,text/csv,text/plain,application/vnd.ms-excel" 
          @change="handleCsvFileChange" 
          :disabled="isUploadingCsv"
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10 disabled:pointer-events-none touch-manipulation" 
        />
        <button 
          type="button"
          :disabled="isUploadingCsv" 
          class="w-full liquid-glass-pill hover:bg-white/10 text-white font-bold text-xs sm:text-sm py-3 px-3 rounded-full transition-all flex items-center justify-center gap-2 active:scale-95 hover:border-white/20 disabled:opacity-50 pointer-events-none"
          title="Importer un fichier CSV de portefeuille BoursoBank"
        >
          <svg v-if="!isUploadingCsv" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white/70 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          <svg v-else class="animate-spin h-4 w-4 text-neonLime shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <span class="truncate">{{ isUploadingCsv ? 'Importation...' : (uploadStatusMessage || '📁 Importer CSV') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAppStore } from '../stores/app';

const store = useAppStore();

const csvInputRef = ref(null);
const isUploadingCsv = ref(false);
const uploadStatusMessage = ref('');

const triggerCsvImport = () => {
  if (csvInputRef.value) {
    csvInputRef.value.click();
  }
};

const handleCsvFileChange = async (event) => {
  const file = event.target?.files?.[0];
  if (!file) return;

  isUploadingCsv.value = true;
  uploadStatusMessage.value = 'Import en cours...';

  try {
    const result = await store.uploadCsv(file);
    if (result.success) {
      uploadStatusMessage.value = '✅ Importé !';
      setTimeout(() => {
        uploadStatusMessage.value = '';
      }, 3000);
    } else {
      uploadStatusMessage.value = '❌ Erreur';
      alert(result.message || "Erreur lors de l'importation du CSV");
      setTimeout(() => {
        uploadStatusMessage.value = '';
      }, 3000);
    }
  } catch (err) {
    uploadStatusMessage.value = '❌ Erreur réseau';
    setTimeout(() => {
      uploadStatusMessage.value = '';
    }, 3000);
  } finally {
    isUploadingCsv.value = false;
    if (event.target) event.target.value = '';
  }
};

const props = defineProps({
  summary: { type: Object, default: () => ({}) },
  positions: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false },
  isRefreshing: { type: Boolean, default: false }
});

defineEmits(['refresh', 'open-settings']);

const formattedTotal = computed(() => {
  if (store.isDiscreteMode) return { main: '***', decimals: '**' };
  const val = props.summary?.total_value || 0;
  const parts = val.toFixed(2).split('.');
  const intPart = parseInt(parts[0], 10).toLocaleString('fr-FR');
  return { main: intPart, decimals: parts[1] || '00' };
});

const cashValue = computed(() => {
  return Number(props.summary?.cash || 0);
});

const etfValue = computed(() => {
  return (props.positions || [])
    .filter(p => p.sector === 'ETF & Indice' || p.name?.toUpperCase().includes('ETF') || p.name?.toUpperCase().includes('CW8') || p.asset_type === 'ETF')
    .reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
});

const actionsValue = computed(() => {
  const titres = (props.positions || []).reduce((acc, p) => acc + (p.quantity * p.current_price), 0);
  return Math.max(0, titres - etfValue.value);
});

const formatCurrency = (val) => {
  if (store.isDiscreteMode) return '*** €';
  return (val || 0).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';
};
</script>
