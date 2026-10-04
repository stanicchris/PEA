<template>
  <div class="space-y-6">
    <div class="glass-card rounded-36 p-8 border border-white/[0.08]">
      <h2 class="text-2xl font-bold mb-2">Objectifs & Rente</h2>
      <p class="text-white/40">Visualisez vos futures rentes, la sûreté de vos dividendes et projetez votre FIRE.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <MonthlyDividendProjection 
          :projections="monthlyProjections" 
          :isLoading="isLoading" 
        />
      </div>
      <div class="lg:col-span-1">
        <DividendSafety 
          :scores="safetyScores" 
          :isLoading="isLoading" 
        />
      </div>
    </div>

    <FireSimulator :currentCapital="currentCapital" />

  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { getApiBase } from '../config';
import MonthlyDividendProjection from '../components/MonthlyDividendProjection.vue';
import DividendSafety from '../components/DividendSafety.vue';
import FireSimulator from '../components/FireSimulator.vue';

const props = defineProps({
  userId: {
    type: String,
    required: false
  }
});

const isLoading = ref(false);
const monthlyProjections = ref({});
const safetyScores = ref([]);
const currentCapital = ref(0);

const fetchGoalsData = async () => {
  const uid = props.userId || localStorage.getItem('pea_user_id') || '';
  const token = localStorage.getItem('pea_access_token');
  const headers = token ? { Authorization: 'Bearer ' + token } : {};
  
  isLoading.value = true;
  try {
    // Fetch projections
    const projUrl = uid ? `${getApiBase()}/api/goals/projections?user_id=${uid}` : `${getApiBase()}/api/goals/projections`;
    const resProj = await fetch(projUrl, { headers });
    if (resProj.ok) {
      const data = await resProj.json();
      monthlyProjections.value = data.monthly_projections || {};
      safetyScores.value = data.safety_scores || [];
    }

    // Fetch current capital from summary
    const sumUrl = uid ? `${getApiBase()}/api/portfolio/summary?user_id=${uid}` : `${getApiBase()}/api/portfolio/summary`;
    const resSum = await fetch(sumUrl, { headers });
    if (resSum.ok) {
      const sumData = await resSum.json();
      currentCapital.value = sumData.total_value || 0;
    }
  } catch (e) {
    console.error("Failed to fetch goals data", e);
  } finally {
    isLoading.value = false;
  }
};

watch(() => props.userId, fetchGoalsData);
onMounted(fetchGoalsData);
</script>
