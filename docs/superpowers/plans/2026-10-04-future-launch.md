# Capfolio PEA - Plan de Lancement & Développements Futurs

## 1. Préparation au lancement (Phase de "Go-Live")
- [ ] **Déploiement Backend (Render)** : 
  - Mettre à jour les variables d'environnement (`SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `GROQ_API_KEY`).
  - Déployer l'API via le lien GitHub.
- [ ] **Déploiement Frontend (Vercel / Netlify)** :
  - Lier le dépôt GitHub à Vercel.
  - Définir `VITE_API_URL` pointant vers l'URL de Render.
  - S'assurer que le build PWA passe en production (génération du sw.js).
- [ ] **Tests finaux en prod** :
  - Création d'un compte de test.
  - Vérification de l'import CSV sur l'environnement de production.
  - Test de l'accès PWA sur mobile (iOS / Android).

## 2. Poursuite de la refonte (Étapes restantes de l'audit)
- [ ] **Fiche Valeur Dédiée (`/stock/:ticker`)** :
  - Graphiques de prix avancés (ECharts interactif).
  - Badge clair d'éligibilité PEA.
  - Onglets : Fondamentaux, Dividendes, News (via API tierce).
- [ ] **Watchlist avec Alertes** :
  - Liste de surveillance pour les actions non détenues.
  - Job backend pour envoyer un mail ou une push notif quand le cours cible est atteint.
- [ ] **Simulateur de Rééquilibrage & Optimiseur de Frais** :
  - Calcul du coût des TER sur 20 ans.
  - Algorithme d'allocation cible pour savoir quoi acheter avec le prochain dépôt sans revendre.
- [ ] **Mode Discret & PWA Mobile** :
  - Rendre fonctionnel le toggle "Mode Discret" pour flouter/masquer les montants en €.
  - Finitions UI sur la bottom-nav mobile.

## 3. Marketing & Acquisition (Long terme)
- [ ] Landing page dédiée présentant le "Cockpit 100% PEA" avec des screenshots du Liquid Glass.
- [ ] Ouverture en version bêta fermée (sur invitation) pour récolter des feedbacks de la communauté financière.
