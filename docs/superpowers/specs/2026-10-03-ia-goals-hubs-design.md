# Architecture Design: IA & Objectifs Hubs (Rivlo PEA)

## 1. Objectif (Intent)
Faire évoluer le projet "Rivlo PEA" d'un simple tracker vers un véritable assistant de gestion de patrimoine en structurant l'application autour de deux nouveaux pôles majeurs :
- **Hub "Optimisation & IA"** : Maximiser la rentabilité en identifiant les frais cachés et les failles de diversification, assisté par l'IA Groq.
- **Hub "Objectifs & Rente" (FIRE)** : Visualiser la progression de l'investisseur vers la liberté financière via des projections de dividendes et des simulateurs d'intérêts composés.

## 2. Changements Structurels de l'Interface (Vue.js)
Le menu de navigation `App.vue` (`activeTab`) va s'enrichir pour accueillir :
- `dashboard` : Reste la vue "Hélicoptère" (Performance globale, allocation).
- `optimization` (NOUVEAU) : Concentre l'AI Advisor, le Fee Scanner, et l'analyse de risque.
- `goals` (NOUVEAU) : Héberge les projections FIRE, le Dividend Calendar mensuel, et le Dividend Safety.
- `analytics` et `reports` : (Existant - possible fusion/simplification avec `optimization`).

## 3. Détail des Fonctionnalités par Hub

### 3.1. Hub "Optimisation & IA"
- **Composant `FeeScanner.vue`** :
  - **Data flow** : Le backend `portfolio_service.py` ou un nouveau `optimization_service.py` enrichit les positions (surtout les ETFs) avec leur TER (Total Expense Ratio).
  - **Logique** : Si le TER > 0.35%, l'interface lève une alerte ("Frais Élevés") et suggère un ISIN d'ETF alternatif (ex: passage d'Amundi CW8 0.38% vers iShares 0.20%).
- **Composant `RiskRadar.vue` / AI Overexposure** :
  - Graphique Radar (via `echarts`) croisant la pondération par rapport à un benchmark sain.
  - L'IA Groq génère un diagnostic si la dépendance à un seul secteur est trop forte.

### 3.2. Hub "Objectifs & Rente" (FIRE)
- **Composant `MonthlyDividendProjection.vue`** :
  - **Data flow** : Extension du `dividend_service.py` pour récupérer non seulement la *prochaine* ex-date, mais l'historique de distribution (ex: trimestriel) pour projeter un graphique en barres des 12 prochains mois.
- **Composant `DividendSafety.vue`** :
  - Notation (Safety Score 1-100) basée sur le "Payout Ratio" (Bénéfice Net vs Dividende versé). Nécessite l'accès au `payoutRatio` via l'API `yfinance` dans `dividend_service.py`.
- **Composant `FireSimulator.vue`** :
  - **Inputs utilisateur** : Épargne mensuelle prévue (€), Rendement attendu (défaut 7%), Objectif de Rente (ex: 2000€/mois).
  - **Output** : Courbe temporelle simulant la croissance du patrimoine total et la date croisée d'atteinte de l'objectif (Règle des 4% ou rendement dividende).

## 4. Impacts Backend (FastAPI)
- **Nouveau Routeur** : `backend/routers/optimization.py` et `backend/routers/goals.py`.
- **Services** : 
  - `dividend_service.py` : Ajouter la logique de projection sur 12 mois (historique de fréquence) et le calcul du `Payout Ratio`.
  - `optimization_service.py` : Base de données statique/JSON ou appel API pour mapper les TERs des ETFs PEA les plus connus.

## 5. Gestion des Risques & Trade-offs
- **Yahoo Finance Limite (401 Crumb)** : Récupérer le `Payout Ratio` et la fréquence des dividendes pour tout un portefeuille va multiplier les requêtes. Le système de **cache (TTL 24h)** est critique.
- **TER ETFs Data** : Yahoo Finance n'a pas toujours le TER exact des ETFs européens (Amundi, BNP). Solution : Maintenir un dictionnaire statique (`utils/etf_ter_db.json`) pour les 50 ETFs PEA les plus populaires.

## 6. Séquence d'Implémentation Recommandée
1. **Frontend / Navigation** : Créer les coquilles vides des vues `OptimizationView.vue` et `GoalsView.vue` et router le menu.
2. **Backend "Goals"** : Étendre `dividend_service.py` pour la projection FIRE et le Monthly Projection.
3. **Frontend "Goals"** : Implémenter `FireSimulator` et `MonthlyDividendProjection`.
4. **Backend "Optimization"** : Créer le scanner de frais (dictionnaire TER).
5. **Frontend "Optimization"** : Implémenter le `FeeScanner` et y déplacer l'IA.
