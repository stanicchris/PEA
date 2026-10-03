<template>
  <div class="rounded-32 p-7 flex flex-col justify-between h-full relative overflow-hidden bg-[#A3E635] text-[#0C0E12] shadow-[0_15px_35px_rgba(163,230,53,0.3)]">
    <!-- Top Row: Rocket Icon in Circle + AI Assistant Pill -->
    <div class="flex justify-between items-center mb-4">
      <div class="w-10 h-10 rounded-2xl bg-black/10 flex items-center justify-center text-black shadow-sm">
        <span class="text-xl">🚀</span>
      </div>

      <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/90 text-black text-xs font-bold shadow-sm">
        <span class="text-xs">✦</span>
        <span>AI assistant</span>
      </div>
    </div>

    <!-- Title & Description -->
    <div class="mb-5">
      <h3 class="text-2xl sm:text-[26px] font-black text-black tracking-tight leading-tight mb-2">
        Advanced AI Analytics
      </h3>
      <p class="text-black/80 text-xs sm:text-sm font-medium leading-relaxed">
        Use our AI assistant to gain deeper insights, advanced analytics, smarter decisions, personalized predictions, and real-time market intelligence.
      </p>
    </div>

    <!-- Social Proof & Hand-drawn style Arrow -->
    <div class="flex items-center justify-between my-2 relative">
      <!-- Avatars Pile -->
      <div class="flex items-center gap-2">
        <div class="flex -space-x-2 overflow-hidden">
          <div class="inline-block h-7 w-7 rounded-full ring-2 ring-[#A3E635] bg-purple-600 flex items-center justify-center text-white text-[10px] font-bold">👩‍💼</div>
          <div class="inline-block h-7 w-7 rounded-full ring-2 ring-[#A3E635] bg-amber-500 flex items-center justify-center text-white text-[10px] font-bold">👨‍💻</div>
          <div class="inline-block h-7 w-7 rounded-full ring-2 ring-[#A3E635] bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold">🧑‍💼</div>
        </div>
        <div class="text-[11px] font-bold leading-tight">
          <div>7.8K+</div>
          <div class="text-[9px] text-black/70 font-semibold">People rely on us daily</div>
        </div>
      </div>

      <!-- Doodle Arrow pointing down to CTA -->
      <svg class="w-8 h-8 text-black/75 -rotate-12 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
      </svg>
    </div>

    <!-- Bottom Action Pill: Unlock AI Power -->
    <button 
      @click="$emit('trigger-ai')" 
      :disabled="isLoading"
      class="w-full bg-[#0C0E12] hover:bg-black text-white font-extrabold text-sm py-3.5 px-6 rounded-full transition-all shadow-md active:scale-98 flex items-center justify-center gap-2 mt-2 disabled:opacity-60"
    >
      <svg v-if="isLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span>{{ isLoading ? 'Groq analyse...' : 'Unlock AI Power' }}</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  isLoading: { type: Boolean, default: false }
});

defineEmits(['trigger-ai']);
</script>
