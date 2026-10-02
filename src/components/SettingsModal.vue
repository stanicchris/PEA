<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
    <div class="glass w-full max-w-md rounded-3xl p-6 border border-white/10 shadow-2xl relative">
      <button @click="$emit('close')" class="absolute top-4 right-4 text-white/50 hover:text-white transition-colors">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
      </button>

      <h2 class="text-2xl font-bold mb-6 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        Paramètres du PEA
      </h2>

      <!-- Liquidités -->
      <div class="mb-8">
        <label class="block text-xs font-semibold text-white/70 uppercase tracking-widest mb-2">Liquidités (Cash)</label>
        <div class="flex gap-2">
          <div class="relative flex-1">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-white/50 font-bold">€</span>
            <input v-model="cash" type="number" step="10" class="w-full bg-[#0E1117]/50 border border-white/10 rounded-xl pl-8 pr-4 py-3 text-white focus:outline-none focus:border-blue-500 font-medium font-mono" />
          </div>
          <button @click="saveCash" :disabled="isSavingCash" class="bg-blue-600 hover:bg-blue-500 text-white px-5 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50">
            {{ isSavingCash ? '...' : 'Sauver' }}
          </button>
        </div>
        <p v-if="cashMsg" class="text-xs text-emerald-400 mt-2 font-medium">{{ cashMsg }}</p>
      </div>

      <!-- Import CSV -->
      <div>
        <label class="block text-xs font-semibold text-white/70 uppercase tracking-widest mb-2">Importer un Portfolio (CSV)</label>
        <div class="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:bg-white/5 transition-colors cursor-pointer relative" :class="selectedFile ? 'border-emerald-500/50 bg-emerald-500/5' : ''">
          <input type="file" accept=".csv" @change="handleFileUpload" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" />
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mx-auto mb-2" :class="selectedFile ? 'text-emerald-400' : 'text-white/30'" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
          <div class="text-sm font-medium" :class="selectedFile ? 'text-emerald-400' : 'text-white/60'">
            {{ selectedFile ? selectedFile.name : 'Cliquez ou glissez un CSV Boursorama' }}
          </div>
        </div>
        
        <button v-if="selectedFile" @click="uploadFile" :disabled="isUploading" class="w-full mt-4 bg-emerald-600 hover:bg-emerald-500 text-white py-3 rounded-xl font-bold transition-all shadow-lg shadow-emerald-600/20 disabled:opacity-50 flex items-center justify-center gap-2">
           <svg v-if="isUploading" class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
           {{ isUploading ? 'Importation en cours...' : 'Importer et Analyser' }}
        </button>
        <p v-if="uploadMsg" class="text-xs text-center mt-3 font-medium" :class="uploadError ? 'text-rose-400' : 'text-emerald-400'">{{ uploadMsg }}</p>
      </div>

    </div>
  </div>
</template>

<script setup>
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
import { ref, watch } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  userId: String,
  currentCash: Number
});

const emit = defineEmits(['close', 'refresh']);

const cash = ref(0);
const cashMsg = ref('');
const isSavingCash = ref(false);

const selectedFile = ref(null);
const isUploading = ref(false);
const uploadMsg = ref('');
const uploadError = ref(false);

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    cash.value = props.currentCash || 0;
    selectedFile.value = null;
    uploadMsg.value = '';
  }
});

const saveCash = async () => {
  if (!props.userId) return;
  isSavingCash.value = true;
  cashMsg.value = '';
  try {
    const res = await fetch(`${API_BASE}/api/portfolio/cash?user_id=${props.userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cash: cash.value })
    });
    if (!res.ok) throw new Error("Erreur serveur");
    cashMsg.value = 'Liquidités mises à jour !';
    emit('refresh');
  } catch (err) {
    cashMsg.value = "Erreur de sauvegarde";
  } finally {
    isSavingCash.value = false;
    setTimeout(() => cashMsg.value = '', 3000);
  }
};

const handleFileUpload = (e) => {
  if (e.target.files.length > 0) {
    selectedFile.value = e.target.files[0];
    uploadError.value = false;
    uploadMsg.value = '';
  }
};

const uploadFile = async () => {
  if (!selectedFile.value || !props.userId) return;
  isUploading.value = true;
  uploadError.value = false;
  uploadMsg.value = '';
  
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  
  try {
    const res = await fetch(`${API_BASE}/api/portfolio/upload?user_id=${props.userId}`, {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + localStorage.getItem('pea_access_token') }, body: formData
    });
    
    if (!res.ok) throw new Error("Format CSV invalide ou non supporté");
    
    uploadMsg.value = 'Portefeuille synchronisé avec succès !';
    emit('refresh');
    setTimeout(() => {
      emit('close');
    }, 1500);
  } catch (err) {
    uploadError.value = true;
    uploadMsg.value = err.message;
  } finally {
    isUploading.value = false;
  }
};
</script>
