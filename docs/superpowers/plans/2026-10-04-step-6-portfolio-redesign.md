# Plan d'implémentation - Étape 6 : Refonte de la vue Portefeuille

## Contexte
La vue actuelle du portefeuille manque de dataviz et d'outils d'exploration. Nous allons transformer cette page pour qu'elle offre une vision claire de l'allocation (secteurs, géographie) et une table filtrable des positions.

## Étapes

### Tâche 1 : Composant de Graphique d'Allocation
- **Objectif** : Améliorer ou intégrer le composant `AllocationChart.vue`.
- **Détails** : 
  - S'assurer que le graphique s'appuie sur `store.positions`.
  - Extraire l'allocation par `sector`.
  - Mettre à jour le design pour correspondre à l'esthétique Liquid Glass (couleurs Neon Lime, etc.).

### Tâche 2 : Refonte de la vue Portfolio.vue
- **Objectif** : Créer un tableau de bord des positions esthétique.
- **Détails** :
  - Ajouter des filtres (Recherche par ticker, Filtre Secteur, Tri par Poids/Plus-Value).
  - Inclure le composant `AllocationChart.vue`.
  - Redesigner le tableau des positions pour qu'il soit interactif (clic pour ouvrir l'AssetInspector) et riche en informations (PRU, Cours Actuel, Performance Latente).
