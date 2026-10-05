<template>
  <div class="space-y-6 pb-20 max-w-3xl mx-auto">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
        <span class="text-white/80">⚙️</span> Paramètres du Compte
      </h1>
    </div>

    <!-- Section 1 : Liquidités (Cash) -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-white/5">
      <h2 class="text-lg font-bold text-white mb-6">Gestion des Liquidités (PEA)</h2>
      
      <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
        Liquidités Disponibles
      </label>
      
      <div class="flex items-center gap-3">
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

    <!-- Section 2 : Import CSV -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-white/5">
      <h2 class="text-lg font-bold text-white mb-6">Importation (Boursorama)</h2>
      
      <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
        Mettre à jour via un fichier CSV ou Excel (.xlsx)
      </label>

      <div class="border-2 border-dashed border-white/15 hover:border-white/40 transition-colors rounded-24 p-8 text-center cursor-pointer relative liquid-glass-subtle">
        <input 
          type="file" 
          accept="*/*" 
          @change="handleFileUpload" 
          class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
        />
        <div class="flex flex-col items-center">
          <svg class="w-8 h-8 text-white/40 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
          </svg>
          <p v-if="!selectedFile" class="text-sm text-white/70 font-medium">Cliquez ou glissez votre fichier CSV ou Excel ici</p>
          <p v-else class="text-sm text-white font-bold">{{ selectedFile.name }}</p>
        </div>
      </div>

      <button 
        v-if="selectedFile" 
        @click="uploadFile" 
        :disabled="store.isUploadingCsv"
        class="w-full mt-4 bg-white hover:bg-white/90 text-[#0C0E12] py-3 rounded-full font-black text-sm transition-all active:scale-95 disabled:opacity-50 cursor-pointer"
      >
        {{ store.isUploadingCsv ? 'Importation en cours...' : 'Envoyer le fichier' }}
      </button>

      <p v-if="uploadMsg" class="text-xs mt-3 font-medium" :class="uploadError ? 'text-roseAcc' : 'text-neonLime'">
        {{ uploadMsg }}
      </p>
    </div>

    <!-- Section 3 : Danger Zone -->
    <div class="liquid-glass-chassis rounded-36 p-6 sm:p-8 relative overflow-hidden group border border-roseAcc/30">
      <h2 class="text-lg font-bold text-roseAcc mb-2">Zone Danger</h2>
      <p class="text-white/50 text-sm mb-6">Déconnectez-vous de votre session.</p>
      
      <button 
        @click="logout" 
        class="px-6 py-3 rounded-full bg-roseAcc/10 hover:bg-roseAcc/20 border border-roseAcc/30 text-roseAcc font-bold text-xs transition-all active:scale-95"
      >
        Se déconnecter
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

const selectedFile = ref(null);
const isUploading = ref(false);
const uploadMsg = ref('');
const uploadError = ref(false);

onMounted(() => {
  cash.value = store.summary?.cash || 0;
});

const saveCash = async () => {
  if (!store.userId) return;
  const apiBase = getApiBase();
  isSavingCash.value = true;
  cashMsg.value = '';
  try {
    const token = localStorage.getItem('pea_access_token');
    // Note: the original endpoint accepted user_id as query param, but we should just use the token in real implementation
    // We keep the old endpoint format for compatibility with existing backend code if it still expects it
    const res = await fetch(`${apiBase}/api/portfolio/cash?user_id=${store.userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? 'Bearer ' + token : ''
      },
      body: JSON.stringify({ cash: parseFloat(cash.value) || 0 })
    });
    if (res.ok) {
      cashMsg.value = 'Liquidités enregistrées avec succès !';
      store.fetchData(); // Refresh store
      setTimeout(() => { cashMsg.value = ''; }, 3000);
    } else {
      cashMsg.value = 'Erreur lors de la sauvegarde';
    }
  } catch (e) {
    cashMsg.value = 'Erreur réseau';
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
      uploadMsg.value = "Format non supporté. Veuillez sélectionner un fichier .csv ou .xlsx (BoursoBank).";
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
    selectedFile.value = null;
  } else {
    uploadError.value = true;
    uploadMsg.value = res.message;
  }
};

const logout = () => {
  localStorage.removeItem('pea_user_id');
  localStorage.removeItem('pea_username');
  localStorage.removeItem('pea_access_token');
  localStorage.removeItem('pea_refresh_token');
  store.userId = null;
  window.location.href = '/';
};
</script>
