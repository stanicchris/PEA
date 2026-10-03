<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-md" @click="$emit('close')"></div>
    
    <!-- Modal Content -->
    <div class="relative w-full max-w-lg glass-card border border-white/[0.08] rounded-36 shadow-2xl bg-[#111419] p-7 flex flex-col text-white">
      
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonLime/15 border border-neonLime/30 flex items-center justify-center text-neonLime">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-xl font-bold text-white tracking-tight">Paramètres du PEA</h2>
            <p class="text-white/40 text-xs">Gestion du Cash et Importation de Relevés</p>
          </div>
        </div>

        <button @click="$emit('close')" class="text-white/40 hover:text-white transition-colors bg-white/[0.04] hover:bg-white/[0.08] p-2 rounded-full cursor-pointer">
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Section 1 : Liquidités (Cash) -->
      <div class="bg-[#16191E] rounded-28 p-5 border border-white/[0.06] mb-5">
        <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
          Liquidités Disponibles (Cash)
        </label>
        
        <div class="flex items-center gap-3">
          <div class="relative flex-1">
            <span class="absolute left-4 top-3 text-white/40 font-mono">€</span>
            <input 
              type="number" 
              step="0.01" 
              v-model="cash" 
              placeholder="0.00" 
              class="w-full bg-[#111419] border border-white/[0.08] focus:border-neonLime rounded-2xl pl-8 pr-4 py-3 text-sm font-mono font-bold text-white outline-none transition-all"
            />
          </div>
          
          <button 
            @click="saveCash" 
            :disabled="isSavingCash"
            class="bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] px-6 py-3 rounded-full font-black text-xs transition-all shadow-md active:scale-95 disabled:opacity-50 shrink-0 cursor-pointer"
          >
            {{ isSavingCash ? 'Sauvegarde...' : 'Sauver' }}
          </button>
        </div>
        
        <p v-if="cashMsg" class="text-xs mt-2 font-medium" :class="cashMsg.includes('succès') ? 'text-neonLime' : 'text-roseAcc'">
          {{ cashMsg }}
        </p>
      </div>

      <!-- Section 2 : Import CSV (Boursorama / Courtier) -->
      <div class="bg-[#16191E] rounded-28 p-5 border border-white/[0.06] mb-5">
        <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-3">
          Importer un Portfolio CSV (Boursorama)
        </label>

        <div class="border-2 border-dashed border-white/[0.1] hover:border-neonLime/50 transition-colors rounded-24 p-6 text-center cursor-pointer relative bg-[#111419]/50">
          <input 
            type="file" 
            accept=".csv" 
            @change="handleFileUpload" 
            class="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
          />
          <div class="flex flex-col items-center">
            <svg class="w-8 h-8 text-white/30 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
            </svg>
            <p v-if="!selectedFile" class="text-xs text-white/60 font-medium">Cliquez ou glissez votre fichier CSV ici</p>
            <p v-else class="text-xs text-neonLime font-bold">{{ selectedFile.name }}</p>
          </div>
        </div>

        <button 
          v-if="selectedFile" 
          @click="uploadFile" 
          :disabled="isUploading"
          class="w-full mt-3 bg-neonLime hover:bg-neonLimeHover text-[#0C0E12] py-3 rounded-full font-black text-xs transition-all shadow-md active:scale-95 disabled:opacity-50 cursor-pointer"
        >
          {{ isUploading ? 'Importation en cours...' : 'Envoyer le fichier CSV' }}
        </button>

        <p v-if="uploadMsg" class="text-xs mt-2 font-medium" :class="uploadError ? 'text-roseAcc' : 'text-neonLime'">
          {{ uploadMsg }}
        </p>
      </div>

      <!-- Section 3 : Backend URL Override (Optional) -->
      <div class="bg-[#16191E] rounded-28 p-5 border border-white/[0.06]">
        <label class="text-xs font-mono font-bold text-white/50 uppercase tracking-wider block mb-2">
          URL Backend Render
        </label>
        <div class="flex items-center gap-2">
          <input 
            type="text" 
            v-model="backendUrl" 
            placeholder="https://pea-tpxq.onrender.com" 
            class="flex-1 bg-[#111419] border border-white/[0.08] focus:border-neonLime rounded-2xl px-4 py-3 text-xs font-mono text-white/90 outline-none transition-all"
          />
          <button 
            @click="saveBackendUrl" 
            class="bg-white/[0.08] hover:bg-white/[0.15] text-white px-5 py-3 rounded-full font-bold text-xs transition-all active:scale-95 shrink-0 cursor-pointer"
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
  const apiBase = getApiBase();
  if (!apiBase) {
    cashMsg.value = 'URL API non configurée';
    return;
  }
  isSavingCash.value = true;
  cashMsg.value = '';
  try {
    const token = localStorage.getItem('pea_access_token');
    const res = await fetch(`${apiBase}/api/portfolio/cash?user_id=${props.userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? 'Bearer ' + token : ''
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
  const apiBase = getApiBase();
  if (!apiBase) return;
  
  isUploading.value = true;
  uploadMsg.value = '';
  uploadError.value = false;

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const token = localStorage.getItem('pea_access_token');
    const res = await fetch(`${apiBase}/api/portfolio/upload?user_id=${props.userId}`, {
      method: 'POST',
      headers: token ? { 'Authorization': 'Bearer ' + token } : {},
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
