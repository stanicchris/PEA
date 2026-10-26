<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex items-end sm:items-center justify-center p-0 sm:p-4">
    <!-- Backdrop with blur -->
    <div class="absolute inset-0 bg-black/80 backdrop-blur-xl cursor-pointer" @click="$emit('close')"></div>
    
    <!-- Modal Content (Liquid Glass / Mobile Bottom Sheet) -->
    <div class="relative w-full max-w-4xl h-[88vh] sm:h-[85vh] overflow-hidden liquid-glass-chassis rounded-t-36 sm:rounded-36 shadow-2xl flex flex-col text-white specular-highlight border border-white/15 animate-sheet-up sm:animate-fade-up">
      <!-- Mobile Drag Handle -->
      <div class="w-12 h-1.5 bg-white/20 rounded-full mx-auto mt-3 sm:hidden shrink-0"></div>
      
      <!-- Header -->
      <div class="flex justify-between items-center p-4 sm:p-6 border-b border-white/[0.06] bg-[#0A0D14]/80 backdrop-blur-md z-10 shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-neonPurple/15 border border-neonPurple/30 flex items-center justify-center text-lavender font-bold shadow-[0_0_15px_rgba(139,92,246,0.3)]">
            ✦
          </div>
          <div>
            <h2 class="text-lg sm:text-xl font-black text-white tracking-tight">Directeur Financier Virtuel</h2>
            <p class="text-white/40 text-xs flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-neonLime animate-pulse"></span>
              Propulsé par Groq (Llama-3) • Connecté à vos {{ store.positions.length }} lignes
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button 
            v-if="messages.length > 0"
            @click="messages = []" 
            class="text-white/40 hover:text-white transition-colors px-3 py-1.5 rounded-full text-[11px] font-bold bg-white/5 hover:bg-white/10 border border-white/10 cursor-pointer"
            title="Effacer la conversation"
          >
            Effacer
          </button>
          <button 
            @click="$emit('close')" 
            aria-label="Fermer l'assistant IA"
            class="text-white/40 hover:text-white transition-colors liquid-glass-subtle hover:border-white/20 p-2.5 rounded-full cursor-pointer active:scale-95 focus-visible:ring-2 focus-visible:ring-neonPurple focus-visible:outline-none"
          >
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5 custom-scrollbar flex flex-col" ref="messagesContainer">
        
        <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center space-y-4 py-6">
          <div class="w-16 h-16 rounded-3xl bg-neonPurple/10 border border-neonPurple/20 flex items-center justify-center text-2xl mb-1 shadow-[0_0_25px_rgba(139,92,246,0.2)]">🧠</div>
          <h3 class="text-lg font-bold text-white">Comment puis-je optimiser votre PEA aujourd'hui ?</h3>
          <p class="text-xs sm:text-sm text-white/50 max-w-md leading-relaxed">
            J'analyse vos positions, votre exposition géographique X-Ray, vos dividendes et la fiscalité PEA en temps réel.
          </p>
          
          <div class="flex flex-wrap justify-center gap-2 mt-4 max-w-xl">
            <button @click="sendMessage('Fais-moi un diagnostic express de mon portefeuille actuel.')" class="px-3.5 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 border border-white/10 transition-colors cursor-pointer text-white/90 font-medium">
              📊 Diagnostic Express
            </button>
            <button @click="sendMessage('Mes dividendes sont-ils sûrs ? Quels sont mes prochains détachements ?')" class="px-3.5 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 border border-white/10 transition-colors cursor-pointer text-white/90 font-medium">
              🛡️ Sûreté des dividendes
            </button>
            <button @click="sendMessage('Si je devais renforcer une ligne avec mes liquidités, laquelle me conseillerais-tu ?')" class="px-3.5 py-2 rounded-xl text-xs bg-white/5 hover:bg-white/10 border border-white/10 transition-colors cursor-pointer text-white/90 font-medium">
              💡 Idée de renforcement
            </button>
            <button @click="sendMessage('Quelles actions de mon PEA sont éligibles au bonus +10% au Nominatif Administré ?')" class="px-3.5 py-2 rounded-xl text-xs bg-amberAcc/10 hover:bg-amberAcc/20 border border-amberAcc/25 text-amberAcc transition-colors cursor-pointer font-medium">
              🎖️ Bonus Nominatif +10%
            </button>
          </div>
        </div>

        <div v-for="(msg, idx) in messages" :key="idx" class="flex" :class="msg.role === 'user' ? 'justify-end' : 'justify-start'">
          <div 
            class="max-w-[90%] sm:max-w-[78%] p-4 rounded-2xl relative"
            :class="msg.role === 'user' ? 'bg-white/10 border border-white/10 rounded-tr-sm text-white' : 'liquid-glass-subtle border border-neonPurple/25 rounded-tl-sm text-white/90 shadow-[0_0_20px_rgba(139,92,246,0.08)]'"
          >
            <div class="text-[10px] font-bold uppercase tracking-wider mb-2" :class="msg.role === 'user' ? 'text-white/40 text-right' : 'text-lavender flex items-center gap-1.5'">
              <span v-if="msg.role !== 'user'">✦</span>
              {{ msg.role === 'user' ? 'Vous' : 'BourseAi Copilot' }}
            </div>
            
            <div class="prose prose-sm prose-invert max-w-none text-xs sm:text-sm font-medium leading-relaxed" v-html="formatMarkdown(msg.content)"></div>
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
      <div class="p-4 sm:p-5 border-t border-white/[0.06] bg-[#0A0D14]/90 backdrop-blur-md shrink-0 pb-safe">
        <form @submit.prevent="handleSubmit" class="relative flex items-center">
          <input 
            type="text" 
            v-model="currentInput"
            placeholder="Posez une question sur votre portefeuille..."
            class="w-full bg-black/40 border border-white/10 rounded-2xl py-3.5 pl-4 sm:pl-5 pr-14 text-sm text-white placeholder-white/40 focus:outline-none focus:border-neonPurple/50 focus:ring-1 focus:ring-neonPurple/30 transition-all"
            :disabled="isLoading"
          />
          <button 
            type="submit" 
            aria-label="Envoyer le message"
            :disabled="!currentInput.trim() || isLoading"
            class="absolute right-2 w-10 h-10 rounded-xl bg-neonPurple/30 hover:bg-neonPurple/50 border border-neonPurple/40 text-white flex items-center justify-center transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <svg class="w-4 h-4 translate-x-px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
          </button>
        </form>
        <p class="text-[10px] text-center text-white/30 mt-2.5 font-mono">Les réponses de l'IA sont éducatives et ne constituent pas un conseil en investissement réglementé.</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { getApiBase } from '../config';
import { useAppStore } from '../stores/app';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);
const store = useAppStore();

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

const generateLocalPortfolioAdvice = (query) => {
  const q = query.toLowerCase();
  const positions = store.positions || [];
  const totalVal = store.summary?.total_value || 0;
  const cash = store.summary?.cash || 0;
  const perfPct = store.summary?.global_performance_pct || 0;
  const divIncome = store.dividendMetrics?.estimated_annual_income || 0;
  const divSafety = store.dividendMetrics?.safety_score || 85;

  if (!positions.length) {
    return "Votre portefeuille ne contient aucune ligne pour le moment. Vous pouvez **ajouter une ligne manuellement** via le bouton **+ Ligne**, importer votre CSV BoursoBank/Fortuneo, ou activer le **Mode Démo** pour tester mes analyses.";
  }

  const sortedByWeight = [...positions].sort((a, b) => (b.quantity * b.current_price) - (a.quantity * a.current_price));
  const topPos = sortedByWeight[0];
  const topWeight = totalVal > 0 ? (((topPos.quantity * topPos.current_price) / totalVal) * 100).toFixed(1) : 0;
  const bestWinner = [...positions].sort((a, b) => b.variation_pct - a.variation_pct)[0];
  const biggestLag = [...positions].sort((a, b) => a.variation_pct - b.variation_pct)[0];
  const nominatifList = positions.filter(p => store.isNominatifEligible(p));

  if (q.includes('nominatif') || q.includes('10%')) {
    if (!nominatifList.length) {
      return "Aucune de vos lignes actuelles ne fait partie de la liste officielle des sociétés françaises offrant la **prime de fidélité +10%** au nominatif administré (Air Liquide, L'Oréal, Engie, Seb).";
    }
    const names = nominatifList.map(p => `**${p.name}** (${p.quantity} titres)`).join(', ');
    return `🎖️ **Optimisation Nominatif Administré (+10%)** :\n- Vos positions éligibles détectées : ${names}\n- **Pourquoi agir avant le 31 décembre ?** En passant ces titres au nominatif administré auprès de votre courtier (gratuit chez BoursoBank et Fortuneo), vous débloquez **+10% sur les dividendes** et sur les attributions d'actions gratuites après 2 années civiles pleines de détention.`;
  }

  if (q.includes('dividende') || q.includes('détachement') || q.includes('rente')) {
    return `🛡️ **Analyse des Dividendes de votre PEA** :\n- **Revenu passif annuel estimé** : **${divIncome.toFixed(0)} € / an** (soit ~${(divIncome / 12).toFixed(0)} € / mois).\n- **Score de sûreté global** : **${divSafety}/100** (payout ratios sains et historique de distribution solide).\n- **Piliers de rendement** : Vos flux sont portés par des valeurs de rendement et de croissance du dividende comme **TotalEnergies** (trimestriel) et **Air Liquide / Sanofi** (annuel au printemps).\n- *Conseil* : Réinvestir ces dividendes au sein du PEA permet de composer en franchise totale d'impôt sans entamer votre plafond de versement de 150 000 €.`;
  }

  if (q.includes('renforcer') || q.includes('acheter') || q.includes('idée') || q.includes('liquidité')) {
    return `💡 **Pistes d'allocation pour vos ${cash.toFixed(0)} € de liquidités** :\n- **1. Socle passif (Core ETF)** : Renforcer votre ligne ETF Monde (**CW8 / WPEA**) reste le moyen le plus efficace de capter la croissance mondiale sans risque spécifique.\n- **2. Opportunité de valorisation** : **${biggestLag.name}** affiche actuellement une variation de **${biggestLag.variation_pct >= 0 ? '+' : ''}${biggestLag.variation_pct.toFixed(1)}%** par rapport à votre PRU (${biggestLag.pru.toFixed(2)} € vs ${biggestLag.current_price.toFixed(2)} €). Si votre thèse fondamentale long terme est intacte, un renforcement progressif (DCA) permet d'améliorer votre PRU.\n- **3. Coussin de sécurité** : Conservez toujours 3 % à 5 % de cash pour saisir les replis de marché.`;
  }

  return `📊 **Diagnostic Express de votre PEA (${totalVal.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} €)** :\n- **Performance Globale** : **${perfPct >= 0 ? '+' : ''}${perfPct.toFixed(2)}%** avec **${cash.toFixed(0)} €** de liquidités disponibles.\n- **Concentration** : Votre première ligne est **${topPos.name}** qui pèse **${topWeight}%** du portefeuille. Votre meilleur moteur de performance est **${bestWinner.name}** (**+${bestWinner.variation_pct.toFixed(1)}%**).\n- **Équilibre & Risque** : L'alliance entre un socle ETF indiciel et des leaders européens à fort pricing power offre un excellent couple rendement/risque.\n- **Action recommandée** : Vérifiez l'onglet **X-Ray Géo** sur la Synthèse pour surveiller votre exposition réelle au dollar américain via vos ETFs.`;
};

const sendMessage = async (text) => {
  if (!text.trim() || isLoading.value) return;
  
  messages.value.push({ role: 'user', content: text });
  currentInput.value = '';
  isLoading.value = true;
  nextTick(() => scrollToBottom());

  if (store.isDemoMode) {
    setTimeout(() => {
      messages.value.push({
        role: 'assistant',
        content: generateLocalPortfolioAdvice(text)
      });
      isLoading.value = false;
      nextTick(() => scrollToBottom());
    }, 550);
    return;
  }

  try {
    const apiBase = getApiBase();
    const token = localStorage.getItem('pea_access_token');
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
      messages.value.push({ role: 'assistant', content: data.content || generateLocalPortfolioAdvice(text) });
    } else {
      messages.value.push({ role: 'assistant', content: generateLocalPortfolioAdvice(text) });
    }
  } catch (e) {
    console.warn("AI chat fallback to local advisor:", e);
    messages.value.push({ role: 'assistant', content: generateLocalPortfolioAdvice(text) });
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
  let html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
    
  html = html.replace(/<br\/>- (.*?)(?=<br\/>|$)/g, '<li>$1</li>');
  html = html.replace(/(<li>.*?<\/li>)/g, '<ul class="list-disc pl-4 my-2 space-y-1">$1</ul>');
  html = html.replace(/<\/ul><ul class="list-disc pl-4 my-2 space-y-1">/g, '');
  
  return html;
};
</script>
