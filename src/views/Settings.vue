<template>
  <div class="space-y-6 pb-20 max-w-3xl mx-auto animate-fade-up">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span class="text-white/80">⚙️</span> Paramètres & Configuration PEA
        </h1>
        <p class="text-white/40 text-xs mt-1">Personnalisez votre horloge fiscale, vos liquidités et vos imports courtiers.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          @click="store.openAddPositionModal()"
          class="px-4 py-2 rounded-full bg-neonLime/15 hover:bg-neonLime/25 border border-neonLime/30 text-neonLime text-xs font-bold transition-all cursor-pointer active:scale-95"
        >
          + Ajouter un titre
        </button>
        <button
          v-if="!store.isDemoMode"
          @click="store.enterDemoMode()"
          class="px-4 py-2 rounded-full bg-neonPurple/15 hover:bg-neonPurple/25 border border-neonPurple/30 text-lavender text-xs font-bold transition-all cursor-pointer active:scale-95"
        >
          ✨ Charger Démo
        </button>
      </div>
    </div>

    <!-- Section 1 : Horloge Fiscale & Date d'Ouverture PEA -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-white/10">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h2 class="text-lg font-bold text-white flex items-center gap-2">
            <span>🏛️</span> Horloge Fiscale PEA (Cap des 5 ans)
          </h2>
          <p class="text-white/40 text-xs mt-1">La date de votre 1er versement détermine l'exonération d'Impôt sur le Revenu (0% IR).</p>
        </div>
        <span 
          class="px-3 py-1 rounded-full text-xs font-mono font-bold border self-start sm:self-auto"
          :class="store.summary?.tax_status?.is_mature ? 'bg-neonLime/15 text-neonLime border-neonLime/30' : 'bg-amberAcc/15 text-amberAcc border-amberAcc/30'"
        >
          {{ store.summary?.tax_status?.is_mature ? '✓ Exonéré IR (> 5 ans)' : `⏳ J-${store.summary?.tax_status?.days_to_maturity || 0} avant 5 ans` }}
        </span>
      </div>

      <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
        Date d'ouverture officielle du PEA
      </label>

      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <input 
          type="date" 
          v-model="openedAtDate"
          class="flex-1 max-w-sm liquid-glass-subtle border border-white/10 focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 rounded-2xl px-4 py-3 text-sm font-mono font-bold text-white outline-none transition-all"
        />
        <button 
          @click="saveOpenedAt"
          class="bg-white hover:bg-neonLime text-[#0C0E12] px-6 py-3 rounded-full font-black text-xs transition-all shadow-[0_2px_15px_rgba(255,255,255,0.1)] hover:shadow-[0_2px_15px_rgba(163,230,53,0.3)] active:scale-95 shrink-0 cursor-pointer"
        >
          Mettre à jour la date
        </button>
      </div>
    </div>

    <!-- Section 2 : Liquidités (Cash) -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-white/10">
      <h2 class="text-lg font-bold text-white mb-2">💶 Gestion du Compte Espèces (PEA)</h2>
      <p class="text-white/40 text-xs mb-6">Solde disponible pour vos prochains ordres ou versements DCA.</p>
      
      <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
        Liquidités Disponibles
      </label>
      
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
        <div class="relative flex-1 max-w-sm">
          <span class="absolute left-4 top-3 text-white/40 font-mono">€</span>
          <input 
            type="number" 
            step="0.01" 
            v-model="cash" 
            placeholder="0.00" 
            class="w-full liquid-glass-subtle border border-white/10 focus:border-neonLime/70 focus:ring-1 focus:ring-neonLime/30 rounded-2xl pl-8 pr-4 py-3 text-sm font-mono font-bold text-white outline-none transition-all shadow-inner"
          />
        </div>
        
        <button 
          @click="saveCash" 
          :disabled="isSavingCash"
          class="bg-white hover:bg-neonLime text-[#0C0E12] px-6 py-3 rounded-full font-black text-xs transition-all shadow-[0_2px_15px_rgba(255,255,255,0.1)] hover:shadow-[0_2px_15px_rgba(163,230,53,0.3)] active:scale-95 disabled:opacity-50 shrink-0 cursor-pointer"
        >
          {{ isSavingCash ? 'Sauvegarde...' : 'Sauvegarder' }}
        </button>
      </div>
      
      <p v-if="cashMsg" class="text-xs mt-3 font-medium" :class="cashMsg.includes('succès') ? 'text-neonLime' : 'text-roseAcc'">
        {{ cashMsg }}
      </p>
    </div>

    <!-- Section 3 : Import CSV Multi-Courtiers -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-white/10">
      <div class="flex flex-wrap items-center justify-between gap-2 mb-4">
        <h2 class="text-lg font-bold text-white">📂 Importation Portefeuille (CSV / Excel)</h2>
        <div class="flex flex-wrap gap-1.5">
          <span class="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-white/60">BoursoBank</span>
          <span class="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-white/60">Fortuneo</span>
          <span class="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-white/60">Bourse Direct</span>
          <span class="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-mono text-white/60">Trade Republic</span>
        </div>
      </div>
      
      <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
        Glissez un export CSV ou Excel (.xlsx) de votre courtier
      </label>

      <div class="border-2 border-dashed border-white/15 hover:border-neonLime/40 transition-colors rounded-24 p-8 text-center cursor-pointer relative liquid-glass-subtle">
        <input 
          type="file" 
          accept=".csv,.xlsx,.xls" 
          @change="handleFileUpload" 
          class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        />
        <div class="flex flex-col items-center">
          <svg class="w-8 h-8 text-white/40 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
          </svg>
          <p v-if="!selectedFile" class="text-sm text-white/70 font-medium">Cliquez ou glissez votre fichier CSV ou Excel ici</p>
          <p v-else class="text-sm text-neonLime font-bold">{{ selectedFile.name }}</p>
          <p class="text-[11px] text-white/40 mt-1 font-mono">Colonnes reconnues automatiquement : Libellé/Nom, ISIN, Quantité, PRU, Cours</p>
        </div>
      </div>

      <button 
        v-if="selectedFile" 
        @click="uploadFile" 
        :disabled="store.isUploadingCsv"
        class="w-full mt-4 bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] py-3 rounded-full font-black text-sm transition-all active:scale-95 disabled:opacity-50 cursor-pointer shadow-[0_0_20px_rgba(163,230,53,0.3)]"
      >
        {{ store.isUploadingCsv ? 'Importation en cours...' : 'Synchroniser le fichier' }}
      </button>

      <p v-if="uploadMsg" class="text-xs mt-3 font-medium" :class="uploadError ? 'text-roseAcc' : 'text-neonLime'">
        {{ uploadMsg }}
      </p>
    </div>

    <!-- Section 4 : Danger Zone -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-roseAcc/30">
      <h2 class="text-lg font-bold text-roseAcc mb-2">Session & Sécurité</h2>
      <p class="text-white/50 text-sm mb-6">
        {{ store.isDemoMode ? 'Vous naviguez actuellement avec le portefeuille de démonstration.' : 'Déconnectez-vous de votre session actuelle.' }}
      </p>
      
      <button 
        @click="logout" 
        class="px-6 py-3 rounded-full bg-roseAcc/10 hover:bg-roseAcc/20 border border-roseAcc/30 text-roseAcc font-bold text-xs transition-all active:scale-95 cursor-pointer"
      >
        {{ store.isDemoMode ? 'Quitter le Mode Démo' : 'Se déconnecter' }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getApiBase } from '../config';
import { useAppStore } from '../stores/app';

const store = useAppStore();
const router = useRouter();

const cash = ref(0);
const cashMsg = ref('');
const isSavingCash = ref(false);
const openedAtDate = ref(store.peaOpenedAt || '2022-03-15');

const selectedFile = ref(null);
const uploadMsg = ref('');
const uploadError = ref(false);

onMounted(() => {
  cash.value = store.summary?.cash || 0;
  openedAtDate.value = store.summary?.tax_status?.opened_at || store.peaOpenedAt || '2022-03-15';
});

const saveOpenedAt = () => {
  if (!openedAtDate.value) return;
  store.setPeaOpenedAt(openedAtDate.value);
};

const saveCash = async () => {
  if (!store.userId) return;
  const parsedCash = parseFloat(cash.value) || 0;

  if (store.isDemoMode) {
    store.summary.cash = parsedCash;
    store.recomputeSummaryFromPositions();
    cashMsg.value = 'Liquidités enregistrées avec succès !';
    store.showToast('Solde espèces mis à jour', 'success');
    setTimeout(() => { cashMsg.value = ''; }, 3000);
    return;
  }

  const apiBase = getApiBase();
  isSavingCash.value = true;
  cashMsg.value = '';
  try {
    const token = localStorage.getItem('pea_access_token');
    const res = await fetch(`${apiBase}/api/portfolio/cash?user_id=${store.userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? 'Bearer ' + token : ''
      },
      body: JSON.stringify({ cash: parsedCash })
    });
    if (res.ok) {
      cashMsg.value = 'Liquidités enregistrées avec succès !';
      store.showToast('Solde espèces mis à jour', 'success');
      store.fetchData();
      setTimeout(() => { cashMsg.value = ''; }, 3000);
    } else {
      cashMsg.value = 'Erreur lors de la sauvegarde';
    }
  } catch (e) {
    store.summary.cash = parsedCash;
    store.recomputeSummaryFromPositions();
    cashMsg.value = 'Liquidités mises à jour localement avec succès !';
  } finally {
    isSavingCash.value = false;
  }
};

const handleFileUpload = (e) => {
  const files = e.target.files;
  if (files && files.length > 0) {
    const file = files[0];
    const fileName = (file.name || '').toLowerCase();
    const validExtensions = ['.csv', '.xlsx', '.xls'];
    if (!validExtensions.some(ext => fileName.endsWith(ext))) {
      uploadError.value = true;
      uploadMsg.value = "Format non supporté. Veuillez sélectionner un fichier .csv ou .xlsx.";
      if (e.target) e.target.value = '';
      return;
    }
    selectedFile.value = file;
    uploadMsg.value = '';
    uploadError.value = false;
  }
};

const uploadFile = async () => {
  if (!selectedFile.value || !store.userId) return;
  
  uploadMsg.value = '';
  uploadError.value = false;

  const res = await store.uploadCsv(selectedFile.value);
  if (res.success) {
    uploadMsg.value = res.message;
    store.showToast('Portefeuille importé avec succès', 'success');
    selectedFile.value = null;
  } else {
    uploadError.value = true;
    uploadMsg.value = res.message;
  }
};

const logout = () => {
  store.logout();
  router.push('/');
};
</script>
