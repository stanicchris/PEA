<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
    <div class="glass-card w-full max-w-lg rounded-36 p-8 border border-white/[0.08] shadow-2xl relative text-white bg-[#111419]">
      <button @click="$emit('close')" class="absolute top-6 right-6 text-white/40 hover:text-white transition-colors p-1 bg-white/[0.04] rounded-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>

      <div class="flex items-center gap-3 mb-6">
        <div class="w-10 h-10 rounded-2xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-neonLime">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        </div>
        <div>
          <h2 class="text-xl font-bold tracking-tight">Paramètres du PEA</h2>
          <p class="text-white/40 text-xs">Gestion du Cash et Importation de Relevés</p>
        </div>
      </div>

      <!-- Liquidités (Cash) -->
      <div class="mb-7 bg-[#16191E] p-5 rounded-28 border border-white/[0.06]">
        <label class="block text-xs font-semibold text-white/70 uppercase tracking-wider mb-2 font-mono">Liquidités Disponibles (Cash)</label>
        <div class="flex gap-2">
          <div class="relative flex-1">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/40 font-bold font-mono">€</span>
            <input 
              v-model="cash" 
              type="number" 
              step="10" 
              class="w-full bg-[#0C0E12] border border-white/[0.08] rounded-full pl-9 pr-4 py-3 text-white focus:outline-none focus:border-neonLime font-mono text-sm font-semibold" 
            />
          </div>
          <button 
            @click="saveCash" 
            :disabled="isSavingCash" 
            class="bg-neonLime hover:bg-neonLimeHover text-black px-6 py-3 rounded-full font-extrabold text-xs transition-all shadow-md active:scale-95 disabled:opacity-50"
          >
            {{ isSavingCash ? '...' : 'Sauver' }}
          </button>
        </div>
        <p v-if="cashMsg" class="text-xs text-neonLime mt-2 font-medium">{{ cashMsg }}</p>
      </div>

      <!-- Import CSV -->
      <div class="bg-[#16191E] p-5 rounded-28 border border-white/[0.06]">
        <label class="block text-xs font-semibold text-white/70 uppercase tracking-wider mb-2 font-mono">Importer un Portfolio CSV (Boursorama)</label>
        <div 
          class="border-2 border-dashed border-white/[0.12] rounded-24 p-6 text-center hover:bg-white/[0.02] transition-colors cursor-pointer relative" 
          :class="selectedFile ? 'border-neonLime/50 bg-neonLime/5' : ''"
        >
          <input type="file" accept=".csv" @change="handleFileUpload" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mx-auto mb-2" :class="selectedFile ? 'text-neonLime' : 'text-white/30'" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <div class="text-xs font-medium" :class="selectedFile ? 'text-neonLime' : 'text-white/60'">
            {{ selectedFile ? selectedFile.name : 'Cliquez ou glissez votre fichier CSV ici' }}
          </div>
        </div>
        
        <button 
          v-if="selectedFile" 
          @click="uploadFile" 
          :disabled="isUploading" 
          class="w-full mt-4 bg-neonLime hover:bg-neonLimeHover text-black py-3 rounded-full font-extrabold text-xs transition-all shadow-md flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50"
        >
          <svg v-if="isUploading" class="animate-spin h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          {{ isUploading ? 'Importation en cours...' : 'Importer et Synchroniser' }}
        </button>
        <p v-if="uploadMsg" class="text-xs text-center mt-3 font-medium" :class="uploadError ? 'text-roseAcc' : 'text-neonLime'">{{ uploadMsg }}</p>
      </div>

      <!-- Backend URL Configuration -->
      <div class="mb-7 bg-[#16191E] p-5 rounded-28 border border-white/[0.06]">
        <label class="block text-xs font-semibold text-white/70 uppercase tracking-wider mb-2 font-mono">URL Backend Render</label>
        <div class="flex gap-2">
          <input 
            v-model="backendUrl" 
            type="url" 
            placeholder="https://pea-tracker-backend.onrender.com" 
            class="w-full bg-[#0C0E12] border border-white/[0.08] rounded-full px-4 py-3 text-white focus:outline-none focus:border-neonLime font-mono text-xs" 
          />
          <button 
            @click="saveBackendUrl" 
            class="bg-white/[0.08] hover:bg-white/[0.15] text-white px-5 py-3 rounded-full font-bold text-xs transition-all active:scale-95 shrink-0"
          >
            Sauver URL
          </button>
        </div>
        <p v-if="urlMsg" class="text-xs text-neonLime mt-2 font-medium">{{ urlMsg }}</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { getApiBase } from '../config';

const props = defineProps({
  isOpen: Boolean,
  userId: String,
  currentCash: Number
});

const emit = defineEmits(['close', 'refresh']);

const cash = ref(0);
const cashMsg = ref('');
const isSavingCash = ref(false);

const backendUrl = ref(localStorage.getItem('pea_api_url') || import.meta.env.VITE_API_BASE_URL || '');
const urlMsg = ref('');

const selectedFile = ref(null);
const isUploading = ref(false);
const uploadMsg = ref('');
const uploadError = ref(false);

const saveBackendUrl = () => {
  if (backendUrl.value.trim()) {
    localStorage.setItem('pea_api_url', backendUrl.value.trim().replace(/\/+$/, ''));
    urlMsg.value = 'URL du serveur mise à jour !';
    emit('refresh');
    setTimeout(() => { urlMsg.value = ''; }, 3000);
  }
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    cash.value = props.currentCash || 0;
    cashMsg.value = '';
    selectedFile.value = null;
    uploadMsg.value = '';
    uploadError.value = false;
  }
});

const saveCash = async () => {
  if (!props.userId) return;
  isSavingCash.value = true;
  cashMsg.value = '';
  try {
    const res = await fetch(`${API_BASE}/api/portfolio/cash?user_id=${props.userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + localStorage.getItem('pea_access_token')
      },
      body: JSON.stringify({ cash: parseFloat(cash.value) || 0 })
    });
    if (res.ok) {
      cashMsg.value = 'Liquidités enregistrées avec succès !';
      emit('refresh');
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
    selectedFile.value = files[0];
  }
};

const uploadFile = async () => {
  if (!selectedFile.value || !props.userId) return;
  isUploading.value = true;
  uploadMsg.value = '';
  uploadError.value = false;

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const res = await fetch(`${API_BASE}/api/portfolio/upload?user_id=${props.userId}`, {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('pea_access_token')
      },
      body: formData
    });

    if (res.ok) {
      uploadMsg.value = 'Portefeuille importé avec succès !';
      emit('refresh');
      setTimeout(() => {
        emit('close');
      }, 1500);
    } else {
      uploadError.value = true;
      uploadMsg.value = "Erreur lors de l'importation. Format CSV invalide.";
    }
  } catch (e) {
    uploadError.value = true;
    uploadMsg.value = 'Erreur réseau lors de l\'envoi du fichier';
  } finally {
    isUploading.value = false;
  }
};
</script>
