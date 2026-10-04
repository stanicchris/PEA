# Plan d'implémentation - Étape 7 : Recherche & Agent IA (Groq)

## Contexte
Capfolio doit offrir des conseils d'investissement et une analyse de portefeuille personnalisée propulsée par un LLM très rapide. L'API Groq (exécutant Llama 3) est idéale pour une expérience conversationnelle fluide.

## Étapes

### Tâche 1 : Service IA Backend (Groq)
- **Objectif** : Créer un endpoint backend pour communiquer avec Groq.
- **Détails** : 
  - Ajouter `groq` aux dépendances (`requirements.txt`).
  - Créer `backend/services/ai_service.py` (ou modifier existant).
  - Fournir le contexte du portefeuille (Solde, Top 3 lignes, PRU, Dividendes) dans le prompt système.
  - Exposer `/api/ai/chat` pour échanger avec le "Directeur Financier Virtuel".

### Tâche 2 : Interface Frontend (AiAdvisorWidget & Research Vue)
- **Objectif** : Offrir une interface de chat riche et réactive.
- **Détails** :
  - Mettre à jour `AiAdvisorWidget.vue` avec une messagerie type chat (Bulles utilisateur / Bulles IA).
  - Ajouter un effet "typing" rapide (puisque Groq génère > 800 tokens/seconde).
  - Mettre à jour `Research.vue` pour suggérer des prompts rapides (Ex: "Analyse mon exposition à la tech", "Est-ce que mon rendement sur dividende est sûr ?").
