import json
import pandas as pd
import yfinance as yf
import re
import streamlit as st
import os

try:
    from groq import Groq
    HAS_GROQ_PKG = True
except ImportError:
    HAS_GROQ_PKG = False

AVAILABLE_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it"
]
DEFAULT_MODEL = "llama-3.3-70b-versatile"

def get_available_groq_models():
    """Récupère dynamiquement la liste des modèles Groq actifs."""
    api_key = st.secrets.get("GROQ_API_KEY")
    if api_key and HAS_GROQ_PKG:
        try:
            client = Groq(api_key=api_key)
            remote = [m.id for m in client.models.list().data if 'llama' in m.id or 'deepseek' in m.id or 'gemma' in m.id]
            if remote:
                # Prioriser les modèles validés
                ordered = [m for m in AVAILABLE_GROQ_MODELS if m in remote]
                for r in remote:
                    if r not in ordered and not r.startswith("whisper") and not r.startswith("distil-whisper"):
                        ordered.append(r)
                return ordered
        except Exception:
            pass
    return AVAILABLE_GROQ_MODELS

def fetch_ticker_news(ticker_symbol, max_news=3):
    """Récupère les dernières actualités d'un ticker boursier via yfinance."""
    if not ticker_symbol:
        return []
    try:
        ticker = yf.Ticker(ticker_symbol)
        news_list = ticker.news or []

        cleaned_news = []
        for item in news_list[:max_news]:
            content = item.get("content", item)
            title = content.get("title", "Actualité Boursière")
            summary = content.get("summary", content.get("description", "Pas de résumé disponible."))
            provider = content.get("provider", {}).get("displayName", "Yahoo Finance")
            link = content.get("canonicalUrl", {}).get("url", "") or item.get("link", "")

            cleaned_news.append({
                "title": title,
                "summary": summary,
                "provider": provider,
                "link": link
            })
        return cleaned_news
    except Exception as e:
        print(f"Erreur actualités pour {ticker_symbol}: {e}")
        return []

def query_groq_safe(prompt, system_prompt="", model=DEFAULT_MODEL):
    """Exécute une requête vers Groq avec extraction JSON robuste (compatible Llama 3.3, 3.1 & DeepSeek R1)."""
    if not HAS_GROQ_PKG:
        raise Exception("Le package 'groq' n'est pas installé.")
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        raise Exception("Clé API Groq manquante dans st.secrets.")
        
    client = Groq(api_key=api_key)
    try:
        # 1. Tentative avec response_format JSON
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content
        except Exception:
            # 2. Fallback sans format strict (ex: DeepSeek ou modèles spécifiques)
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                temperature=0.2,
            )
            content = response.choices[0].message.content
            
        # Extraction regex du JSON (gère les balises <think> de DeepSeek-R1)
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(content)
    except Exception as e:
        raise Exception(f"Erreur Groq ({model}): {e}")

def analyze_portfolio_global(portfolio_df, model=DEFAULT_MODEL, openai_key=None):
    """Génère un diagnostic d'allocation global du portefeuille via Groq ou algorithme."""
    records = []
    total_val = portfolio_df['amount'].sum() if 'amount' in portfolio_df.columns else 0.0
    
    for _, row in portfolio_df.iterrows():
        name = row.get('name', 'Inconnu')
        weight = (row.get('amount', 0.0) / total_val * 100) if total_val > 0 else 0.0
        records.append({
            "ticker": row.get('yf_symbol') or row.get('isin') or name,
            "name": name,
            "sector": row.get('sector', 'Inconnu'),
            "weight_pct": round(weight, 1),
            "pnl_pct": round(row.get('variation', 0.0), 2)
        })

    system_prompt = (
        "Tu es un conseiller en gestion de patrimoine spécialiste du PEA. "
        "Tu réponds STRICTEMENT avec un objet JSON valide en français."
    )
    prompt = f"""
    Analyse la composition de ce portefeuille PEA :
    {json.dumps(records, indent=2)}

    Génère un JSON respectant EXACTEMENT cette structure :
    {{
        "diagnostic_global": "Résumé court et percutant du portefeuille en français.",
        "score_diversification": 8,
        "points_forts": ["Point fort 1", "Point fort 2"],
        "alertes_et_risques": ["Risque 1", "Risque 2"],
        "recommandations_pea": ["Conseil 1", "Conseil 2"]
    }}
    """

    try:
        return query_groq_safe(prompt, system_prompt, model=model)
    except Exception as e_groq:
        print(f"Groq non disponible ({e_groq}), tentative de secours algorithmique...")

    # Fallback Algorithmique Financier
    nb_pos = len(portfolio_df)
    top_weight = portfolio_df.sort_values(by='amount', ascending=False).head(3)['amount'].sum() / total_val * 100 if total_val > 0 else 0
    div_score = min(10, max(2, int(nb_pos * 0.8) if top_weight < 50 else 5))
    
    pts_forts = [
        f"Portefeuille comportant {nb_pos} positions diversifiées.",
        f"Plus-value latente globale positive ({portfolio_df['amountVariation'].sum():,.2f} €)." if portfolio_df['amountVariation'].sum() >= 0 else "Présence d'actions à fort potentiel de rebond."
    ]
    
    risques = []
    if top_weight > 50:
        risques.append(f"Concentration élevée : les 3 premières lignes représentent {top_weight:.1f}% des encours.")
    if nb_pos < 5:
        risques.append("Nombre limité de lignes (risque d'exposition spécifique).")
    if not risques:
        risques.append("Exposition sectorielle à surveiller selon l'évolution macroéconomique.")

    recommandations = [
        "Conserver une poche de liquidités pour profiter des opportunités de marché.",
        "Renforcer progressivement les positions ETF pour lisser le risque."
    ]

    return {
        "diagnostic_global": f"Portefeuille PEA comprenant {nb_pos} actifs. Le Top 3 représente {top_weight:.1f}% du capital.",
        "score_diversification": div_score,
        "points_forts": pts_forts,
        "alertes_et_risques": risques,
        "recommandations_pea": recommandations
    }

def analyze_news_sentiment(ticker_symbol, news_list, model=DEFAULT_MODEL, openai_key=None):
    """Analyse le sentiment des actualités d'une action via Groq ou analyse de mots-clés."""
    if not news_list:
        return {
            "sentiment_global": "Neutre",
            "score_global": 0.0,
            "analyse_news": []
        }

    system_prompt = (
        "Tu es un analyste financier senior. "
        "Tu réponds STRICTEMENT avec un objet JSON valide en français."
    )
    prompt = f"""
    Analyse les actualités suivantes pour l'action {ticker_symbol} :
    {json.dumps(news_list, indent=2)}

    Génère un JSON respectant EXACTEMENT cette structure :
    {{
        "sentiment_global": "Positif",
        "score_global": 0.4,
        "analyse_news": [
            {{
                "titre": "Titre",
                "sentiment": "Positif",
                "score": 0.4,
                "resume_impact": "Explication courte de l'impact en 1 sentence en français."
            }}
        ]
    }}
    Note : 'score_global' et 'score' doivent être compris entre -1.0 (très négatif) et +1.0 (très positif).
    """

    try:
        return query_groq_safe(prompt, system_prompt, model=model)
    except Exception:
        pass

    # Fallback sentiment mots-clés
    analyzed_items = []
    total_score = 0.0

    pos_words = ['gain', 'profit', 'rise', 'jump', 'up', 'beat', 'growth', 'bull', 'record', 'hausse', 'croissance', 'bénéfice', 'cible', 'recommand']
    neg_words = ['fall', 'drop', 'down', 'loss', 'bear', 'cut', 'risk', 'warn', 'baisse', 'perte', 'chute', 'risque', 'alerte', 'dégrade']

    for n in news_list:
        text = (n.get('title', '') + " " + n.get('summary', '')).lower()
        pos_count = sum(1 for w in pos_words if w in text)
        neg_count = sum(1 for w in neg_words if w in text)
        
        if pos_count > neg_count:
            score = 0.5
            sentiment = "Positif"
            impact = "Actualité favorable orientée hausse."
        elif neg_count > pos_count:
            score = -0.5
            sentiment = "Négatif"
            impact = "Tensions ou incertitudes signalées."
        else:
            score = 0.0
            sentiment = "Neutre"
            impact = "Information neutre ou factuelle."
            
        total_score += score
        analyzed_items.append({
            "titre": n.get('title', 'Actu'),
            "sentiment": sentiment,
            "score": score,
            "resume_impact": impact
        })

    avg_score = round(total_score / len(news_list), 2) if news_list else 0.0
    global_sent = "Positif" if avg_score > 0.1 else ("Négatif" if avg_score < -0.1 else "Neutre")

    return {
        "sentiment_global": global_sent,
        "score_global": avg_score,
        "analyse_news": analyzed_items
    }

def compute_portfolio_weather(portfolio_df, news_sentiments_dict):
    """Calcule la météo globale du portefeuille pondérée par la valeur de chaque position."""
    total_val = portfolio_df['amount'].sum() if 'amount' in portfolio_df.columns else 0.0
    if total_val == 0:
        return 0.0, "☁️", "Neutre"

    weighted_sentiment = 0.0
    for _, row in portfolio_df.iterrows():
        ticker = row.get('yf_symbol') or row.get('name')
        weight = row.get('amount', 0.0) / total_val
        score = news_sentiments_dict.get(ticker, {}).get("score_global", 0.0)
        weighted_sentiment += score * weight

    weighted_sentiment = round(weighted_sentiment, 2)

    if weighted_sentiment > 0.3:
        return weighted_sentiment, "☀️", "Ensoleillé"
    elif weighted_sentiment > 0.1:
        return weighted_sentiment, "⛅", "Éclaircies"
    elif weighted_sentiment >= -0.1:
        return weighted_sentiment, "☁️", "Nuageux"
    elif weighted_sentiment >= -0.3:
        return weighted_sentiment, "🌧️", "Pluie"
    else:
        return weighted_sentiment, "⛈️", "Orageux"
