# 🏛️ Document de Conception Produit (PRD)
## Plateforme PEA Tracker SaaS — Design System Éditorial & Interface « Rivlo-Dark » (Inspiré d'interface.png)

---

## 1. Vision Produit & Direction Artistique

### 1.1 Philosophie Visuelle : *« Luxury FinTech & Minimalist Dark Matte »*
Le **PEA Tracker SaaS** adopte fidèlement les codes esthétiques de l'interface de référence (`interface.png`) :
* **Un châssis sombre ultra-profond** en noir mat texturé (`#0C0E12` / `#101216`), encadré par des bordures extérieures aux rayons galbés de **48px** (`rounded-[48px]`).
* **Des cartes modulaires flottantes** (`#16191E` à `#1A1D24`) aux angles généreux de **32px à 36px**, soulignées d'un liseré discret (`border border-white/[0.06]`) et d'un effet verre translucide feutré (`backdrop-blur-xl`).
* **Un contraste vibrant bicolore signature** :
  * **Vert Pistache / Neon Mint (`#98F794` / `#A3E635`)** pour les gains, les boutons d'action clés, les indicateurs de santé et la méga-carte IA mise en avant.
  * **Violet / Lavande Électrique (`#A78BFA` / `#8B5CF6`)** pour les métriques de performance, les anneaux d'allocation et les flux d'actifs.
  * **Noir Carbone & Ivoire** pour les textes, garantissant une lisibilité absolue.

---

## 2. Décomposition de l'Interface & Grille Bento Asymétrique (Layout d'interface.png)

L'écran principal s'organise en un canevas harmonieux composé d'une **Top Bar en pilule** et d'une **grille asymétrique en 2 étages principaux** :

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  [≡] [🟢 PEA Tracker]        ( (●) Dashboard   📊 Analytics   📁 Reports   ⚙️ Settings )       (🔍) (🔔) (👤) │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                ÉTAGE SUPÉRIEUR                                         │
│ ┌────────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐ │
│ │  CARTE 1 : HERO & LIVE │ │ CARTE 2 : ALLOCATION │ │ CARTE 3 : MÉTÉO/SANTÉ│ │ CARTE 4 : STACK     │ │
│ │  • Valorisation totale │ │ • Double Anneau 43%  │ │ • Equalizer / Ondes  │ │   A. Plafond 150k€   │ │
│ │  • Devises / Actifs    │ │ • Légende sectorielle│ │ • Score Santé & News │ │   B. Fiscalité 5 ans │ │
│ │  • [Refresh] [Import]  │ │ • Bouton Expand ↗    │ │ • Badge "On Track"   │ │   • [Simuler]        │ │
│ └────────────────────────┘ └──────────────────────┘ └──────────────────────┘ └──────────────────────┘ │
│                                                ÉTAGE INFÉRIEUR                                         │
│ ┌────────────────────────────────────────┐ ┌───────────────────────────────┐ ┌──────────────────────┐ │
│ │ CARTE 5 : ANALYTICS PERFORMANCE        │ │ CARTE 6 : RADAR MOUVEMENTS    │ │ CARTE 7 : GROQ AI    │ │
│ │ • Rubans empilés 2024 - 2026           │ │ • Barres LED / Equalizer      │ │   (FOND VERT NEON)   │ │
│ │ • Valorisation vs PRU investi          │ │ • Avatars titres & Volumes    │ │ • ✦ AI Assistant     │ │
│ │ • Sélecteur Actions/ETF/Obligations    │ │ • Sélecteur [Weekly ˅]        │ │ • [Unlock AI Power]  │ │
│ └────────────────────────────────────────┘ └───────────────────────────────┘ └──────────────────────┘ │
│                                          SECTION BASSE DÉROULANTE                                      │
│ ┌────────────────────────────────────────────────────────────────────────────────────────────────────┐ │
│ │ CARTE 8 : TABLEAU DÉTAILLÉ DES POSITIONS (POSITIONS TABLE PRO + ASSET INSPECTOR MODAL)              │ │
│ └────────────────────────────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Spécifications Détaillées des Composants (Mapping interface.png ➔ PEA)

### 3.1 Top Navigation Bar Flottante
* **Gauche** :
  * Bouton Menu hamburger (`[≡]`) dans un carré arrondi noir mat (`bg-white/5 border border-white/10`).
  * Logo PEA Tracker avec badge icône carré vert néon `[P]` et typographie blanche bold épurée.
* **Centre (Pill Navigation)** :
  * Barre de navigation flottante en capsule (`bg-[#16191E] border border-white/10 rounded-full px-2 py-1.5 flex gap-1`).
  * Onglets avec icônes :
    * `Dashboard` (Onglet actif avec fond blanc/gris clair transparent `bg-white/10 text-white rounded-full px-4 py-2`).
    * `Analytics` (`text-white/60 hover:text-white px-4 py-2`).
    * `Reports` (Exports fiscaux et historiques).
    * `Settings` (Configuration liquidités, devises, clés API).
* **Droite** :
  * Bouton recherche rapide `(🔍)` avec raccourci `Cmd+K`.
  * Cloche de notifications `(🔔)` avec pastille rouge active (alertes de marché / seuils de cours).
  * Avatar utilisateur circulaire avec bordure fine.

---

### 3.2 Carte 1 : Hero & Valorisation Live (`Total Balance`)
* **Localisation** : Haut Gauche (Largeur 30%).
* **Structure Visuelle** :
  * En-tête : Icône portefeuille dans un carré noir arrondi + icône de flèche diagonale `↗`.
  * Label : `Total Balance / Valorisation PEA` en gris ardoise (`#94A3B8`, text-sm).
  * **Chiffre Monumental** : Montant total investi et valorisé en typographie ultra-nette (ex: `128 721.48 €` avec centimes en exposant ou taille réduite).
  * **Pill-bars de répartition d'actifs** : Trois segments horizontaux aux extrémités arrondies :
    * Segment 1 (Vert Neon) : `85 450.00 € Actions`
    * Segment 2 (Violet) : `32 475.20 € ETF World`
    * Segment 3 (Blanc/Gris) : `10 796.28 € Liquidités / Cash`
  * **Boutons d'Action (Dual Pills)** :
    * Bouton Principal (Fond plein Vert Neon `#A3E635`, texte noir bold, `rounded-full`) : **`Refresh Live`** (Actualisation instantanée Yahoo Finance avec spinner discret).
    * Bouton Secondaire (Fond sombre `#1F232B`, texte blanc, `rounded-full`) : **`Import CSV`** (Import Boursorama / Relevés).

---

### 3.3 Carte 2 : Donut d'Allocation Concentrique (`Transfer / Asset Allocation`)
* **Localisation** : Haut Centre-Gauche (Largeur 23%).
* **Structure Visuelle** :
  * Titre : `Asset Allocation` + bouton d'agrandissement plein écran `⤢`.
  * **Double Anneau Concentrique (Radial Gauge ECharts)** :
    * Anneau extérieur : Violet / Lavande (`#8B5CF6`) représentant les Actions vives (ex: 57%).
    * Anneau intérieur : Vert Pistache (`#A3E635`) représentant les ETF & Liquidités (ex: 43%).
    * Centre du cercle : `43%` en grand texte gras avec sous-titre `Poids ETF/Cash`.
  * **Légende Verticale à Puces Colorées** :
    * 🟣 Actions Euronext / Tech : `54 457.15 €`
    * ⚪ ETF MSCI World CW8 : `42 345.75 €`
    * 🟢 Liquidités disponibles : `12 124.75 €`

---

### 3.4 Carte 3 : Météo des Marchés & Sentiment (`Financial Health / Market Weather`)
* **Localisation** : Haut Centre-Droit (Largeur 23%).
* **Structure Visuelle** :
  * Titre : `Financial Health / Météo PEA` + menu 3 points `⋮`.
  * Badge d'état : Capsule violette translucide **`On track`** ou **`Bullish ☀️`**.
  * Chiffre clé : Performance nette récente (ex: `+1 374.84 €`) avec tag de tendance (`+8.4% ce mois-ci` en vert ou `-2.4%` en rose).
  * **Graphique Ondes / Equalizer Vert & Violet** :
    * Série de barres verticales arrondies oscillantes combinant violet (`#A78BFA`) et vert néon (`#98F794`), symbolisant le flux de sentiment analysé par l'IA sur les actualités Google News.
  * Footer informatif : Icône `(i)` + texte discret : *"Score de sentiment calculé par IA Groq d'après 24 actualités financières récentes."*

---

### 3.5 Carte 4 : Stack Latérale Droite (Vérification & Plafond Fiscal PEA)
* **Localisation** : Haut Droite (Largeur 24%).
* **Composant 4A : Maturité Fiscale & Retrait PEA (`Account Verification / Taxes`)** :
  * Icône Bouclier de protection dans un cercle noir.
  * Titre : `Fiscalité & Retrait PEA`.
  * Description : *"Votre plan a plus de 5 ans : vos gains sont totalement exonérés d'impôt sur le revenu (seuls les 17,2% de PS s'appliquent)."*
  * Bouton Pillule Vert Néon : **`Simuler un Retrait`** (Ouvre le modal de calcul net en poche).
* **Composant 4B : Plafond des Versements PEA (`Monthly Budget Limit`)** :
  * Titre : `Plafond Légal des Versements (150 000 €)`.
  * Barre de progression bicolore segmentée (Violette pleine + Ardoise vide).
  * Montants : `112 458.78 € versés sur` ... `150 000.00 € max`.

---

### 3.6 Carte 5 : Performance Graphique par Rubans Empilés (`Analytics Performance`)
* **Localisation** : Bas Gauche (Largeur 40%).
* **Structure Visuelle** :
  * En-tête : Titre `Analytics Performance` + Filtres à pastilles cliquables :
    * 🟣 `Stocks` | 🟣 `ETFs` | ⚪ `Liquidités`.
    * Bouton switch graphique à droite (Courbe / Rubans / Treemap).
  * **Graphique ECharts en Rubans Empilés (Stacked Isometric Streamchart)** :
    * 3 couches de surfaces géométriques interconnectées en nuances de violet / lavande (`#6366F1`, `#8B5CF6`, `#C4B5FD`).
    * Étiquettes de jalons financiers flottantes : `2 487.85 €` (2024), `5 745.29 €` (2025), `12 987.12 €` (2026).
    * Permet de distinguer immédiatement l'évolution du capital propre investi vs la croissance organique par plus-values.

---

### 3.7 Carte 6 : Radar d'Activité & Barres LED des Titres (`Transaction Count / Movers`)
* **Localisation** : Bas Centre (Largeur 35%).
* **Structure Visuelle** :
  * En-tête : Titre `Performance par Titre` + sélecteur de période déroulant en pilule `[Weekly ˅]` ou `[1 Mois ˅]`.
  * Chiffre d'ensemble : `+6 721.48 €` de gains cumulés.
  * **Graphique en Colonnes LED / Equalizer Segmenté** :
    * Colonnes verticales constituées de petits segments LED horizontaux empilés (vert émeraude pour les fortes hausses, violet pour les hausses modérées, gris/noir pour les valeurs stables).
  * **Axe X avec Avatars Circulaires des Entreprises** :
    * Sous chaque colonne, mini-avatar ou logo rond du titre (LVMH, TotalEnergies, Schneider, Apple, Safran, Air Liquide, etc.).
    * Survol d'une colonne : infobulle avec cours en direct, PRU et variation journalière.

---

### 3.8 Carte 7 : Méga-Carte Groq AI Verte Néon (`Advanced AI Analytics`)
* **Localisation** : Bas Droite (Largeur 25%).
* **Structure Visuelle Signature** :
  * **Fond Plein Vert Pistache / Neon Mint Éclatant (`#A3E635` / `#98F794`)** avec texte noir profond.
  * En-tête : Icône Fusée noire dans un cercle + badge capsule blanche `✦ AI assistant`.
  * **Titre Impactant** : `Advanced AI Analytics` (Font bold 24px, noir).
  * **Texte d'accroche** : *"Utilisez notre moteur Groq IA pour analyser vos positions, anticiper les catalyseurs de marché et optimiser votre allocation stratégique."*
  * **Preuve Sociale & Graphisme Ludique** :
    * Avatars circulaires d'analystes + mention *"7.8K+ Portefeuilles analysés"*.
    * Flèche dessinée à la main pointant vers le bouton d'action.
  * **Bouton Noir Plein (Capsule)** : **`Lancer l'Analyse IA`** (Déclenche le diagnostic global et la météo financière).

---

### 3.9 Carte 8 : Tableau des Positions Pro & Inspecteur d'Actif (Asset Inspector)
* **Localisation** : Section inférieure pleine largeur (défilement vertical fluide).
* **Tableau Moderne Épuré** :
  * Lignes aux coins arrondis flottantes (`hover:bg-white/5 transition-all`).
  * Colonnes : Titre (avec mini-logo), Type (Action/ETF), Quantité, PRU, Cours Live, Montant Total, Plus-Value (€ et badge %).
  * **Clic sur une ligne ➔ Ouverture de l'Asset Inspector Modal** :
    * Score BourseAi (Jauge 0-100%).
    * Verdict : *Opportunité Favorable*, *Neutre*, *À surveiller*.
    * Données ZoneBourse (PER, dividende, consensus analystes).
    * Synthèse Groq des Points Forts et Risques majeurs en français.

---

## 4. Spécifications Techniques & Tokens CSS (Tailwind)

### 4.1 Variables de Couleur & Thème
```css
:root {
  --bg-app: #0C0E12;
  --bg-card: #16191E;
  --bg-card-hover: #1D2128;
  --border-card: rgba(255, 255, 255, 0.07);
  
  /* Accents d'interface.png */
  --accent-neon-green: #A3E635;      /* Vert Pistache / Neon Mint */
  --accent-neon-green-light: #B4F59E;
  --accent-purple: #8B5CF6;          /* Violet Lavande */
  --accent-purple-light: #A78BFA;
  --accent-rose: #F43F5E;
  
  /* Rayons de courbure */
  --radius-container: 48px;
  --radius-card: 32px;
  --radius-pill: 9999px;
}
```

### 4.2 Configuration Tailwind
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkBase: '#0C0E12',
        cardMatte: '#16191E',
        cardBorder: 'rgba(255, 255, 255, 0.07)',
        neonLime: '#A3E635',
        neonMint: '#98F794',
        neonPurple: '#8B5CF6',
        lavender: '#A78BFA',
      },
      borderRadius: {
        '48': '48px',
        '36': '36px',
        '32': '32px',
      }
    }
  }
}
```

---

## 5. Plan de Migration & Implémentation Front-End

1. **Phase 1 : Restructuration du Layout Principal (`App.vue`)**
   - Mise en place du conteneur parent noir mat à bords de `48px`.
   - Création de la barre de navigation supérieure en pilule flottante (`Dashboard`, `Analytics`, `Reports`, `Settings`).
   - Réorganisation de la grille Bento asymétrique selon les 7 cartes principales d'interface.png.

2. **Phase 2 : Refonte des Cartes & Composants**
   - **Hero (`HeroSection.vue`)** : Intégration de la valorisation, des pilules de sous-devises et des boutons capsule *Refresh Live* (vert néon) et *Import CSV*.
   - **Allocation (`AllocationChart.vue`)** : Création du double anneau ECharts et de la liste à puces colorées.
   - **Météo / Santé (`AiAdvisorWidget.vue` / Soundwave)** : Création du graphique en barres equalizer vert/violet.
   - **Plafond & Fiscalité (`PeaTaxes.vue`)** : Intégration du module 150k€ et de la vérification des 5 ans.
   - **Graphique Performance (`AnalyticsCharts.vue`)** : Graphique de rubans empilés isométriques violet/lavande.
   - **Radar Mouvements (`TopMovers.vue`)** : Colonnes LED segmentées avec avatars des titres.
   - **Carte IA (`AiAdvisorHighlight.vue`)** : Carte vert néon intégrale avec CTA noir plein.
   - **Tableau des Positions (`PositionsTable.vue`)** : Lignes flottantes et modal Asset Inspector BourseAi.

3. **Phase 3 : Connexion Backend & Tests en Direct**
   - Vérification des appels FastAPI (`/api/portfolio/refresh`, `/api/portfolio/summary`, `/api/portfolio/weather`, `/api/stock/analyze/{ticker}`).
   - Synchronisation fluide avec la base de données Supabase.
