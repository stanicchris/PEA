<template>
  <div class="space-y-6">
    <div class="glass-card rounded-36 p-8 border border-white/[0.08]">
      <h2 class="text-2xl font-bold mb-2">Optimisation & IA</h2>
      <p class="text-white/40">Gérez vos frais, analysez vos risques et sollicitez votre conseiller IA.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <FeeScanner :userId="userId" />
      <div class="space-y-6">
        <GroqAiHighlightCard 
          :isLoading="isAiLoading" 
          @trigger-ai="$emit('trigger-ai')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import FeeScanner from '../components/FeeScanner.vue';
import GroqAiHighlightCard from '../components/GroqAiHighlightCard.vue';

const props = defineProps({
  userId: {
    type: String,
    required: true
  },
  isAiLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['trigger-ai']);
</script>
