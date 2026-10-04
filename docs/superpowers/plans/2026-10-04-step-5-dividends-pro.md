# Plan d'implémentation - Étape 5 : Dividendes Pro

## Contexte
La gestion des dividendes est le nerf de la guerre pour de nombreux investisseurs PEA (stratégie à rendement). Ce plan vise à transformer la section Dividendes en un véritable cockpit de pilotage de rente.

## Étapes

### Tâche 1 : Service Backend Dividendes (Yield on Cost & Payout)
- **Objectif** : Exposer des métriques avancées sur les dividendes.
- **Détails** :
  - Créer `backend/services/dividend_service.py`.
  - Calculer le Yield on Cost (Rendement sur PRU) pour chaque ligne.
  - Calculer un "Score de sûreté" (/10) très simple (basé sur le payout ratio ou l'historique si possible, ou via Groq/Yahoo).
  - Fournir les dividendes projetés (12 mois glissants).

### Tâche 2 : Vue "Dividendes" (Frontend)
- **Objectif** : Implémenter la vue `src/views/Dividends.vue`.
- **Détails** :
  - Ajouter des KPIs de haut de page (Revenu Annuel Estimé, Rendement Moyen, Rendement sur PRU).
  - Inclure un calendrier (prochains détachements) basé sur `DividendCalendar.vue` existant ou nouveau.
  - Inclure le widget `MonthlyDividendProjection.vue` (ou le fusionner).

### Tâche 3 : Simulateur d'objectif de rente (FIRE)
- **Objectif** : Permettre à l'utilisateur de simuler son indépendance financière.
- **Détails** :
  - Permettre de saisir un objectif (ex: 500 € / mois).
  - Afficher une jauge "Avancement de l'objectif".
  - Estimer le capital manquant en utilisant le rendement moyen actuel de son portefeuille.
