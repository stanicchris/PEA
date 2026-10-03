<template>
  <div class="glass-card rounded-36 p-6 md:p-8 border border-white/[0.08] specular-highlight relative overflow-hidden group">
    <div class="absolute inset-0 bg-gradient-to-br from-neonLime/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none"></div>
    
    <div class="flex items-center justify-between mb-8 relative z-10">
      <div>
        <h3 class="text-xl font-bold text-white flex items-center gap-3">
          <span class="w-10 h-10 rounded-2xl bg-neonLime/10 text-neonLime flex items-center justify-center border border-neonLime/20 shadow-[0_0_15px_rgba(163,230,53,0.15)]">📅</span>
          Calendrier des Dividendes
        </h3>
        <p class="text-white/40 text-xs mt-1 font-medium">Prévisions basées sur vos positions actuelles et les annonces ex-date.</p>
      </div>
      
      <div class="text-right">
        <p class="text-xs text-white/40 uppercase tracking-widest font-mono font-bold mb-1">Total Projeté</p>
        <p class="text-2xl font-black text-neonLime tabular-nums tracking-tight">
          {{ formatCurrency(totalProjected) }}
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="py-12 flex justify-center items-center">
      <div class="w-8 h-8 rounded-full border-2 border-neonLime border-t-transparent animate-spin"></div>
    </div>

    <div v-else-if="!dividends.length" class="py-12 text-center text-white/40 border border-dashed border-white/10 rounded-2xl">
      <span class="text-2xl mb-2 block opacity-50">💸</span>
      <p class="text-sm font-medium">Aucun dividende annoncé pour vos actions.</p>
    </div>

    <div v-else class="space-y-4 relative z-10">
      <div 
        v-for="(div, idx) in dividends" 
        :key="idx"
        class="liquid-glass-subtle p-4 rounded-2xl border border-white/5 hover:border-neonLime/30 transition-all group/item flex items-center justify-between gap-4"
      >
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex flex-col items-center justify-center shrink-0 group-hover/item:bg-neonLime/10 group-hover/item:border-neonLime/20 transition-colors">
            <span class="text-[10px] uppercase font-bold text-white/50 group-hover/item:text-neonLime">{{ getMonth(div.ex_date) }}</span>
            <span class="text-lg font-black text-white group-hover/item:text-neonLime leading-none mt-0.5">{{ getDay(div.ex_date) }}</span>
          </div>
          
          <div>
            <h4 class="font-bold text-white text-sm sm:text-base line-clamp-1">{{ div.name }}</h4>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-white/70 border border-white/10">{{ div.ticker }}</span>
              <span v-if="div.yield_on_cost" class="text-[10px] text-neonLime font-bold flex items-center gap-1">
                Yield: {{ div.yield_on_cost }}%
              </span>
            </div>
          </div>
        </div>

        <div class="text-right shrink-0">
          <p class="font-black text-white text-base sm:text-lg tabular-nums">
            +{{ formatCurrency(div.projected_total) }}
          </p>
          <p class="text-[10px] text-white/40 mt-0.5 font-medium">
            {{ formatCurrency(div.amount_per_share) }} / action
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { getApiBase } from '../config';

const props = defineProps({
  userId: {
    type: String,
    required: true
  }
});

const isLoading = ref(false);
const dividends = ref([]);

const totalProjected = computed(() => {
  return dividends.value.reduce((sum, d) => sum + (d.projected_total || 0), 0);
});

const fetchDividends = async () => {
  if (!props.userId) return;
  isLoading.value = true;
  try {
    const res = await fetch(`${getApiBase()}/api/portfolio/dividends?user_id=${props.userId}`);
    if (res.ok) {
      const data = await res.json();
      dividends.value = data.dividends || [];
    }
  } catch (e) {
    console.error("Failed to fetch dividends", e);
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.userId, fetchDividends);
onMounted(fetchDividends);

const formatCurrency = (val) => {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(val || 0);
};

const getMonth = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleString('fr-FR', { month: 'short' }).replace('.', '');
};

const getDay = (dateStr) => {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.getDate();
};
</script>
