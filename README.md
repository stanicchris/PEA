# 💼 Dashboard PEA Pro, Live, SQLite & IA (Inspiré de Baggr, BourseAi & Ollama)

Application web complète de suivi, d'analyse, de diagnostic par IA et de projection de portefeuille **PEA** (Plan d'Épargne en Actions), développée en **Python, Streamlit, Plotly, SQLite, yfinance & Ollama**.

---

## ✨ Fonctionnalités Avancées

### 1. 🧠 Diagnostic Global IA & Météo des Actualités (Inspiré de `test.py`)
- **Nouvel onglet `🧠 Diagnostic & Météo IA (Ollama)`** :
  - **Diagnostic Global d'Allocation** : Analyse par modèle IA local (Ollama `llama3.2`, `mistral`...) ou moteur de secours. Génère un score de diversification sur 10, un résumé d'allocation, la liste des points forts, des alertes de concentration et des conseils PEA.
  - **Météo Synthétique du Portefeuille (☀️ ⛅ ☁️ 🌧️ ⛈️)** : Calcule un score météo global (-1.0 à +1.0) en analysant le sentiment des actualités récentes de chaque action, pondéré par leur poids en capital.
  - **Détail des Actualités par Titre** : Consultation des news récentes avec badges de sentiment (Vert/Rouge/Gris) et résumés d'impact.

### 2. 🤖 Synthèse IA & Analyse ZoneBourse (BourseAi)
- **Nouvel onglet `🤖 Synthèse IA (BourseAi)`** :
  - Analyse automatique à partir du nom d'un actif du PEA ou d'un lien personnalisé **ZoneBourse.fr**.
  - Recommandation d'investissement : **Faut-il investir ? (OUI / NON)** avec Score de Qualité (0-100%).
  - Synthèse structurée : **Pourquoi Investir (Points forts)** vs **Pourquoi être Prudent (Risques)**.

### 3. 🔴 Actualisation des Cours en Direct (Yahoo Finance)
- Bouton **`⚡ Actualiser les cours (Yahoo Finance)`** dans la barre latérale.
- Connexion en direct aux marchés Euronext pour réévaluer les cours, les valorisations et les variations du jour.

### 4. 🏢 Analyse Sectorielle & Dividendes
- Ventilation automatique par secteur d'activité (Finance, Énergie, Tech, Santé, Luxe...).
- Estimation du revenu passif annuel (`~ €/an`) et du rendement moyen.

### 5. 🔍 Fiche Titre & Inspecteur d'Actif
- Fiche détaillée pour chaque ligne avec **graphique boursier sur 1 an (1Y)**.

### 6. 🖼️ Logos d'Entreprises
- Affichage des logos officiels dans le tableau (`ImageColumn`) et dans les cartes Top 3 Gagnants & Flops.

### 7. 🗄️ Historique & Évolution Temporelle (`portfolio.db`)
- Moteur SQLite enregistrant automatiquement chaque instantané CSV.
- Graphiques d'évolution temporelle de la valorisation, du capital investi et des plus-values.

---

## 🚀 Lancement

### Option 1 : Double-clic
Double-cliquez sur [`lancer_dashboard.bat`](file:///c:/Users/chris/Desktop/code/lancer_dashboard.bat).

### Option 2 : Ligne de commande
```bash
streamlit run app.py
```
Accès web : **[http://localhost:8501](http://localhost:8501)**
