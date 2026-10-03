<template>
  <div class="space-y-6">
    <!-- Top Action Banner -->
    <div class="liquid-glass-card rounded-32 p-7 flex flex-col sm:flex-row justify-between sm:items-center gap-4 specular-highlight">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="px-2.5 py-0.5 rounded-full bg-neonLime/15 border border-neonLime/30 text-neonLime text-xs font-mono font-bold shadow-[0_0_10px_rgba(163,230,53,0.15)]">Rapports & Conformité</span>
          <span class="text-white/40 text-xs font-mono">Export PEA Pro 2026</span>
        </div>
        <h2 class="text-2xl font-black text-white tracking-tight">Rapports Financiers & Déclarations</h2>
        <p class="text-white/40 text-xs mt-1">Générez et exportez vos états de portefeuille, relevés de plus-values et attestations fiscales en formats Excel, CSV ou JSON.</p>
      </div>

      <div class="flex items-center gap-3 flex-wrap">
        <!-- Excel Pro Export (.XLSX) -->
        <button 
          @click="exportExcel" 
          :disabled="isExporting"
          class="flex items-center gap-2 px-5 py-2.5 rounded-full bg-neonLime hover:bg-neonLimeHover text-black font-black text-xs transition-all shadow-[0_4px_20px_rgba(163,230,53,0.3)] active:scale-95 cursor-pointer disabled:opacity-50"
          title="Génère un classeur Excel complet multi-onglets avec formules dynamiques"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <span>{{ isExporting ? 'Génération...' : '📊 Exporter Excel (.XLSX)' }}</span>
        </button>

        <button 
          @click="exportCsv" 
          class="flex items-center gap-2 px-4 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 border border-white/10 text-white font-bold text-xs transition-all active:scale-95 cursor-pointer"
        >
          <svg class="w-4 h-4 text-white/70" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          <span>Export CSV</span>
        </button>

        <button 
          @click="exportJson" 
          class="flex items-center gap-2 px-4 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 border border-white/10 text-white/80 hover:text-white text-xs font-semibold transition-all cursor-pointer active:scale-95"
        >
          <svg class="w-4 h-4 text-lavender" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          <span>Export JSON</span>
        </button>

        <button 
          @click="printReport" 
          class="flex items-center gap-2 px-3.5 py-2.5 rounded-full liquid-glass-subtle hover:bg-white/10 border border-white/10 text-white/60 hover:text-white text-xs transition-all cursor-pointer active:scale-95"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
          <span>Imprimer</span>
        </button>
      </div>
    </div>

    <!-- Fiscal Statement Card -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="liquid-glass-card rounded-32 p-6 flex flex-col justify-between specular-highlight group">
        <div>
          <span class="text-xs font-mono font-bold text-neonLime uppercase">Statut Fiscal PEA</span>
          <h3 class="text-xl font-black text-white mt-1">Exonération IR Valide</h3>
          <p class="text-white/50 text-xs mt-2 leading-relaxed">
            Votre compte PEA a dépassé le cap des 5 ans. Tout retrait partiel s'effectue sans clôturer le plan et bénéficie d'une dispense totale d'impôt sur le revenu (IR 0%).
          </p>
        </div>
        <div class="pt-4 border-t border-white/[0.08] mt-4 flex justify-between items-center text-xs font-mono">
          <span class="text-white/40">Prélèvement social</span>
          <span class="text-lavender font-bold">17,20 % sur gain</span>
        </div>
      </div>

      <div class="liquid-glass-card rounded-32 p-6 flex flex-col justify-between specular-highlight group">
        <div>
          <span class="text-xs font-mono font-bold text-lavender uppercase">Plafond des Versements</span>
          <h3 class="text-xl font-black text-white mt-1">{{ investedAmount.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</h3>
          <p class="text-white/50 text-xs mt-2 leading-relaxed">
            Total des sommes versées en numéraire depuis l'ouverture du compte sur le plafond réglementaire de 150 000 €.
          </p>
        </div>
        <div class="pt-4 border-t border-white/[0.08] mt-4 flex justify-between items-center text-xs font-mono">
          <span class="text-white/40">Capacité de versement</span>
          <span class="text-neonLime font-bold">{{ (150000 - investedAmount).toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</span>
        </div>
      </div>

      <div class="liquid-glass-card rounded-32 p-6 flex flex-col justify-between specular-highlight group">
        <div>
          <span class="text-xs font-mono font-bold text-white/60 uppercase">Plus-Value Nette Latente</span>
          <h3 class="text-xl font-black text-neonLime mt-1">+ {{ gainTotal.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) }} €</h3>
          <p class="text-white/50 text-xs mt-2 leading-relaxed">
            Gain total non matérialisé généré par les lignes du portefeuille et les liquidités disponibles.
          </p>
        </div>
        <div class="pt-4 border-t border-white/[0.08] mt-4 flex justify-between items-center text-xs font-mono">
          <span class="text-white/40">Économie Flat Tax vs CTO</span>
          <span class="text-neonLime font-bold">+ {{ (gainTotal * 0.128).toFixed(2) }} €</span>
        </div>
      </div>
    </div>

    <!-- Printable & Detailed Statement Table -->
    <div class="liquid-glass-card rounded-32 p-7 overflow-hidden specular-highlight">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h3 class="text-white font-bold text-lg tracking-tight">État Inventaire Détaillé des Lignes</h3>
          <p class="text-white/40 text-xs font-mono">Date de valorisation : {{ todayFormatted }}</p>
        </div>
        <span class="text-xs font-mono text-neonLime bg-neonLime/10 border border-neonLime/20 px-2.5 py-0.5 rounded-full font-bold">{{ positions.length }} Titres en Portefeuille</span>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs whitespace-nowrap">
          <thead class="text-white/40 uppercase font-mono tracking-wider border-b border-white/[0.06]">
            <tr>
              <th class="pb-3 px-3">Titre</th>
              <th class="pb-3 px-3">ISIN / Ticker</th>
              <th class="pb-3 px-3">Secteur</th>
              <th class="pb-3 px-3 text-right">Quantité</th>
              <th class="pb-3 px-3 text-right">PRU (€)</th>
              <th class="pb-3 px-3 text-right">Dernier Cours (€)</th>
              <th class="pb-3 px-3 text-right">Investi (€)</th>
              <th class="pb-3 px-3 text-right">Valorisation (€)</th>
              <th class="pb-3 px-3 text-right">Plus-Value (€)</th>
              <th class="pb-3 px-3 text-right">Perf (%)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-white/[0.04] font-mono">
            <tr v-for="pos in positions" :key="pos.ticker || pos.name" class="hover:bg-white/[0.04] transition-colors">
              <td class="py-3 px-3 font-sans font-bold text-white">{{ pos.name }}</td>
              <td class="py-3 px-3 text-white/40">{{ pos.ticker || pos.isin }}</td>
              <td class="py-3 px-3 font-sans text-white/60">{{ pos.sector || 'Général' }}</td>
              <td class="py-3 px-3 text-right text-white/80">{{ pos.quantity }}</td>
              <td class="py-3 px-3 text-right text-white/70">{{ pos.pru.toFixed(2) }} €</td>
              <td class="py-3 px-3 text-right font-bold text-white">{{ pos.current_price.toFixed(2) }} €</td>
              <td class="py-3 px-3 text-right text-white/60">{{ (pos.quantity * pos.pru).toFixed(2) }} €</td>
              <td class="py-3 px-3 text-right font-bold text-white">{{ (pos.quantity * pos.current_price).toFixed(2) }} €</td>
              <td class="py-3 px-3 text-right font-bold" :class="pos.variation_pct >= 0 ? 'text-neonLime' : 'text-roseAcc'">
                {{ pos.variation_pct >= 0 ? '+' : '' }}{{ ((pos.current_price - pos.pru) * pos.quantity).toFixed(2) }} €
              </td>
              <td class="py-3 px-3 text-right font-bold" :class="pos.variation_pct >= 0 ? 'text-neonLime' : 'text-roseAcc'">
                {{ pos.variation_pct >= 0 ? '+' : '' }}{{ pos.variation_pct.toFixed(2) }}%
              </td>
            </tr>
          </tbody>
          <tfoot class="border-t-2 border-white/[0.1] font-mono font-bold text-xs bg-white/[0.03]">
            <tr>
              <td colspan="6" class="py-3.5 px-3 text-white uppercase">Total Valorisation Titres</td>
              <td class="py-3.5 px-3 text-right text-white/80">{{ investedAmount.toFixed(2) }} €</td>
              <td class="py-3.5 px-3 text-right text-neonLime text-sm">{{ totalVal.toFixed(2) }} €</td>
              <td class="py-3.5 px-3 text-right text-neonLime text-sm">+ {{ gainTotal.toFixed(2) }} €</td>
              <td class="py-3.5 px-3 text-right text-neonLime">+ {{ (summary?.global_performance_pct || 0).toFixed(2) }}%</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { getApiBase } from '../config';

const props = defineProps({
  positions: { type: Array, default: () => [] },
  summary: { type: Object, default: () => ({}) }
});

const isExporting = ref(false);

const totalVal = computed(() => props.summary?.total_value || 36100);
const investedAmount = computed(() => props.summary?.total_invested || 30000);
const gainTotal = computed(() => Math.max(0, (props.summary?.global_performance_value || 6100)));

const todayFormatted = computed(() => {
  return new Date().toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });
});

const exportExcel = async () => {
  isExporting.value = true;
  const userId = localStorage.getItem('pea_user_id');
  const token = localStorage.getItem('pea_access_token');
  const apiBase = getApiBase();

  try {
    if (apiBase && userId) {
      const res = await fetch(`${apiBase}/api/portfolio/export/excel?user_id=${userId}`, {
        headers: token ? { Authorization: 'Bearer ' + token } : {}
      });
      if (res.ok) {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', `Rapport_PEA_Complet_${new Date().toISOString().slice(0, 10)}.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        return;
      }
    }
  } catch (err) {
    console.warn("Backend excel export fallback to CSV/XML:", err);
  } finally {
    isExporting.value = false;
  }

  // Fallback direct CSV export
  exportCsv();
};

const exportCsv = () => {
  if (!props.positions || !props.positions.length) return;
  
  const headers = ['Nom', 'Ticker', 'Secteur', 'Quantite', 'PRU', 'Dernier_Cours', 'Montant_Investi', 'Valeur_Actuelle', 'Plus_Value_EUR', 'Variation_PCT'];
  
  const rows = props.positions.map(p => [
    `"${p.name.replace(/"/g, '""')}"`,
    `"${p.ticker || ''}"`,
    `"${p.sector || ''}"`,
    p.quantity,
    p.pru.toFixed(2),
    p.current_price.toFixed(2),
    (p.quantity * p.pru).toFixed(2),
    (p.quantity * p.current_price).toFixed(2),
    ((p.current_price - p.pru) * p.quantity).toFixed(2),
    p.variation_pct.toFixed(2)
  ]);

  const csvContent = '\uFEFF' + [headers.join(';'), ...rows.map(r => r.join(';'))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `Rapport_PEA_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const exportJson = () => {
  const data = {
    exportDate: new Date().toISOString(),
    summary: props.summary,
    positions: props.positions
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `Export_PEA_${new Date().toISOString().slice(0, 10)}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const printReport = () => {
  window.print();
};
</script>
