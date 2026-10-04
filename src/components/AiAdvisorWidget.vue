<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-4">
    <!-- Backdrop with blur -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-xl cursor-pointer" @click="$emit('close')"></div>
    
    <!-- Modal Content (Liquid Glass) -->
    <div class="relative w-full max-w-4xl h-[85vh] overflow-hidden liquid-glass-chassis rounded-36 shadow-2xl flex flex-col text-white specular-highlight border border-white/15">
      
      <!-- Header -->
      <div class="flex justify-between items-center p-5 sm:p-6 border-b border-white/[0.06] bg-[#0A0D14]/80 backdrop-blur-md z-10 shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center text-lavender font-bold shadow-[0_0_15px_rgba(139,92,246,0.3)]">
            ✦
          </div>
          <div>
            <h2 class="text-xl font-black text-white tracking-tight">Directeur Financier Virtuel</h2>
            <p class="text-white/40 text-xs flex items-center gap-1">
              <span class="w-1.5 h-1.5 rounded-full bg-neonLime animate-pulse"></span>
              Propulsé par Groq (Llama-3)
            </p>
          </div>
        </div>

        <button 
          @click="$emit('close')" 
          class="text-white/40 hover:text-white transition-colors liquid-glass-subtle hover:border-white/20 p-2.5 rounded-full cursor-pointer active:scale-95"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <!-- Messages Area -->
      <div class="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6 custom-scrollbar flex flex-col" ref="messagesContainer">
        
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center space-y-4">
          <div class="w-16 h-16 rounded-3xl bg-neonPurple/10 border border-neonPurple/20 flex items-center justify-center text-2xl mb-2">🧠</div>
          <h3 class="text-lg font-bold text-white">Comment puis-je vous aider ?</h3>
          <p class="text-sm text-white/50 max-w-md">Je connais votre portefeuille en temps réel. Posez-moi des questions sur votre diversification, le rendement, ou les risques.</p>
          
          <div class="flex flex-wrap justify-center gap-2 mt-4 max-w-lg">
            <button @click="sendMessage('Fais-moi un diagnostic express de mon portefeuille actuel.')" class="px-4 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 border border-white/10 transition-colors">
              📊 Diagnostic Express
            </button>
            <button @click="sendMessage('Mes dividendes sont-ils sûrs ? Quels sont les risques ?')" class="px-4 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 border border-white/10 transition-colors">
              🛡️ Sûreté des dividendes
            </button>
            <button @click="sendMessage('Si je devais renforcer une ligne, laquelle me conseillerais-tu ?')" class="px-4 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 border border-white/10 transition-colors">
              💡 Idée de renforcement
            </button>
          </div>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
          <div 
            class="max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl relative"
            :class="msg.role === 'user' ? 'bg-white/10 border border-white/10 rounded-tr-sm text-white' : 'liquid-glass-subtle border border-neonPurple/20 rounded-tl-sm text-white/90 shadow-[0_0_15px_rgba(139,92,246,0.05)]'"
          >
            <div class="text-[10px] font-bold uppercase tracking-wider mb-2" :class="msg.role === 'user' ? 'text-white/40 text-right' : 'text-lavender'">
              {{ msg.role === 'user' ? 'Vous' : 'BourseAi' }}
            </div>
            
            <div class="prose prose-sm prose-invert max-w-none text-sm font-medium leading-relaxed" v-html="formatMarkdown(msg.content)"></div>
          </div>
        </div>

        <!-- Typing Indicator -->
        <div v-if="isLoading" class="flex justify-start">
          <div class="liquid-glass-subtle border border-neonPurple/20 rounded-2xl rounded-tl-sm p-4 flex gap-1.5 items-center h-12">
            <span class="w-2 h-2 rounded-full bg-lavender animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 rounded-full bg-lavender animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 rounded-full bg-lavender animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
        
      </div>

      <!-- Input Area -->
      <div class="p-4 sm:p-5 border-t border-white/[0.06] bg-[#0A0D14]/90 backdrop-blur-md shrink-0">
        <form @submit.prevent="handleSubmit" class="relative flex items-center">
          <input 
            type="text" 
            v-model="currentInput"
            placeholder="Posez une question sur votre portefeuille..."
            class="w-full bg-black/40 border border-white/10 rounded-2xl py-3.5 pl-5 pr-14 text-sm text-white placeholder-white/40 focus:outline-none focus:border-neonPurple/50 focus:ring-1 focus:ring-neonPurple/30 transition-all"
            :disabled="isLoading"
          />
          <button 
            type="submit" 
            :disabled="!currentInput.trim() || isLoading"
            class="absolute right-2 w-10 h-10 rounded-xl bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-4 h-4 translate-x-px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
          </button>
        </form>
        <p class="text-[10px] text-center text-white/30 mt-3 font-mono">Les réponses de l'IA ne constituent pas des conseils financiers garantis.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { getApiBase } from '../config';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const messages = ref([]);
const currentInput = ref('');
const isLoading = ref(false);
const messagesContainer = ref(null);

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    emit('close');
  }
};

onMounted(() => window.addEventListener('keydown', handleKeydown));
onUnmounted(() => window.removeEventListener('keydown', handleKeydown));

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    nextTick(() => scrollToBottom());
  }
});

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async (text) => {
  if (!text.trim() || isLoading.value) return;
  
  messages.value.push({ role: 'user', content: text });
  currentInput.value = '';
  isLoading.value = true;
  nextTick(() => scrollToBottom());

  try {
    const apiBase = getApiBase();
    const token = localStorage.getItem('pea_access_token');
    
    // We only send the last 10 messages to keep context window small
    const contextMessages = messages.value.slice(-10);
    
    const res = await fetch(`${apiBase}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': 'Bearer ' + token } : {})
      },
      body: JSON.stringify({ messages: contextMessages })
    });
    
    if (res.ok) {
      const data = await res.json();
      messages.value.push({ role: 'assistant', content: data.content });
    } else {
      messages.value.push({ role: 'assistant', content: "Désolé, je rencontre une erreur de connexion à l'API Groq." });
    }
  } catch (e) {
    console.error(e);
    messages.value.push({ role: 'assistant', content: "Erreur réseau." });
  } finally {
    isLoading.value = false;
    nextTick(() => scrollToBottom());
  }
};

const handleSubmit = () => {
  sendMessage(currentInput.value);
};

const formatMarkdown = (text) => {
  if (!text) return '';
  // Basic markdown to HTML (bold, lists)
  let html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
    
  // Handle lists
  html = html.replace(/<br\/>- (.*?)(?=<br\/>|$)/g, '<li>$1</li>');
  html = html.replace(/(<li>.*?<\/li>)/g, '<ul class="list-disc pl-4 my-2">$1</ul>');
  // Deduplicate nested ul if created
  html = html.replace(/<\/ul><ul class="list-disc pl-4 my-2">/g, '');
  
  return html;
};
</script>
