# 📈 PEA Tracker SaaS

Application web complète de suivi, d'analyse, de diagnostic par IA et de projection pour **PEA** (Plan d'Épargne en Actions). Cette application a été entièrement refondue d'une architecture locale Streamlit vers une architecture SaaS moderne, scalable et prête pour la production.

![Vue.js](https://img.shields.io/badge/Vue.js-3.0-4FC08D?style=for-the-badge&logo=vuedotjs)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-009688?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css)
![Groq](https://img.shields.io/badge/Groq-AI-f55036?style=for-the-badge)

---

## ✨ Fonctionnalités Principales

- 🔐 **Authentification Sécurisée** : Inscription et connexion gérées par Supabase Auth avec Tokens JWT (Bearer).
- 🔴 **Données en Direct (Yahoo Finance)** : Actualisation instantanée des cours de bourse et de la valorisation globale du portefeuille.
- 🤖 **Intelligence Artificielle Financière (Groq)** : 
  - *Météo des Marchés* : Analyse du sentiment des actualités financières pour chaque action.
  - *Asset Inspector (BourseAi)* : Synthèse fondamentale, score d'investissement (0-100%), points forts et risques pour n'importe quelle action ou recherche personnalisée.
  - *Diagnostic Global* : Analyse de la diversification et de l'allocation stratégique de votre PEA.
- 📊 **Tableaux de bord avancés (ECharts)** : Graphiques interactifs (Évolution temporelle, Treemap de la Heatmap sectorielle, Comparatif PRU vs Cours, Matrice Poids/Performance, Dividendes).
- 🏢 **Gestion Boursorama** : Import direct des relevés de portefeuille (BoursoBank) formatés en CSV.
- 📱 **Mobile-First & Responsive** : Interface "Glassmorphism" ultra-fluide avec barre de navigation mobile intuitive.

---

## 🛠️ Stack Technique

### Frontend (Interface)
- **Vue 3** (Composition API) & **Vite**
- **Tailwind CSS** (Design System, Mode sombre, Effets vitrés)
- **Vue-ECharts** (Visualisation de données et graphiques complexes)

### Backend (API)
- **FastAPI** (Framework Python 3 asynchrone)
- **Supabase-py** (Base de données PostgreSQL & Gestion Auth des utilisateurs)
- **yfinance** (Récupération des flux de cotation en direct)
- **Groq** (API LLM ultra-rapide pour l'analyse IA)
- **BeautifulSoup4** (Scraping d'actualités financières et requêtes ZoneBourse)
---

## 🚀 Installation Locale

### 1. Prérequis
- Node.js & npm
- Python 3.9+
- Un compte [Supabase](https://supabase.com)
- Une clé API [Groq](https://groq.com)
---

## 🌍 Déploiement en Production (Cloud)

L'architecture du dépôt est conçue pour être déployée instantanément :
- **Frontend** : Déployable sur **Vercel** (`vercel.json` inclus pour la gestion du routage SPA).
- **Backend** : Déployable sur **Render** (`render.yaml` inclus comme blueprint d'infrastructure).
