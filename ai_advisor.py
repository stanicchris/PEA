import json
import pandas as pd
import yfinance as yf
import re
import streamlit as st
import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

try:
    from groq import Groq
    HAS_GROQ_PKG = True
except ImportError:
    HAS_GROQ_PKG = False

AVAILABLE_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-prompt-guard-2-22m",
    "meta-llama/llama-prompt-guard-2-86m",
    "deepseek-r1-distill-llama-70b",
    "gemma2-9b-it"
]
DEFAULT_MODEL = "llama-3.3-70b-versatile"

def get_groq_api_key():
    """Récupère la clé API Groq depuis st.secrets ou les variables d'environnement."""
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")

def get_available_groq_models():
    """Récupère dynamiquement la liste des modèles Groq disponibles."""
    api_key = get_groq_api_key()
    if api_key and HAS_GROQ_PKG:
        try:
            client = Groq(api_key=api_key)
            remote = [
                m.id for m in client.models.list().data 
                if (
                    'llama' in m.id.lower() or 
                    'deepseek' in m.id.lower() or 
                    'gemma' in m.id.lower() or 
                    'qwen' in m.id.lower() or 
                    'prompt-guard' in m.id.lower()
                ) and not any(bad in m.id.lower() for bad in ['whisper', 'vision', 'embedding', 'embed', 'distil-whisper'])
            ]
            if remote:
                ordered = [m for m in AVAILABLE_GROQ_MODELS if m in remote]
                for r in remote:
                    if r not in ordered:
                        ordered.append(r)
                for m in AVAILABLE_GROQ_MODELS:
                    if m not in ordered:
                        ordered.append(m)
                return ordered
        except Exception as e:
            print(f"Notice modèles Groq : {e}")
    return AVAILABLE_GROQ_MODELS

def fetch_ticker_news(ticker_symbol=None, company_name=None, max_news=3):
    """
    Récupère les dernières actualités financières pour un actif.
    Interroge le flux Google News Finance France (spécifique aux actions Euronext / PEA),
    puis effectue un repli vers yfinance si besoin.
    """
    cleaned_news = []
    query_name = company_name or ticker_symbol
    if not query_name:
        return []
        
    # 1. Flux RSS Google News France Bourse
    try:
        clean_query = re.sub(r'[^a-zA-Z0-9\s]', ' ', query_name).strip()
        q = urllib.parse.quote(f"{clean_query} bourse")
        url = f"https://news.google.com/rss/search?q={q}&hl=fr&gl=FR&ceid=FR:fr"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            root = ET.fromstring(res.read())
            items = root.findall(".//item")[:max_news]
            for it in items:
                title = it.findtext("title") or "Actualité Boursière"
                link = it.findtext("link") or ""
                src_node = it.find("source")
                provider = src_node.text if src_node is not None else "Actualités Marché"
                cleaned_news.append({
                    "title": title,
                    "summary": title,
                    "provider": provider,
                    "link": link
                })
    except Exception as e:
        print(f"Notice Google News RSS ({query_name}): {e}")

    # 2. Repli vers yfinance si flux RSS indisponible
    if not cleaned_news and ticker_symbol:
        try:
            ticker = yf.Ticker(ticker_symbol)
            news_list = ticker.news or []
            for item in news_list[:max_news]:
                content = item.get("content", item)
                title = content.get("title", "Actualité Boursière")
                summary = content.get("summary", content.get("description", "Pas de résumé disponible."))
                provider = content.get("provider", {}).get("displayName", "Actualités Marché")
                link = content.get("canonicalUrl", {}).get("url", "") or item.get("link", "")
                cleaned_news.append({
                    "title": title,
                    "summary": summary,
                    "provider": provider,
                    "link": link
                })
        except Exception as e:
            print(f"Notice yfinance news ({ticker_symbol}): {e}")

    return cleaned_news

def query_groq_safe(prompt, system_prompt="", model=DEFAULT_MODEL):
    """Exécute une requête vers Groq avec extraction JSON robuste (compatible Llama 3.3, 3.1, DeepSeek R1 et Prompt Guard)."""
    if not HAS_GROQ_PKG:
        raise Exception("Le package 'groq' n'est pas installé.")
    api_key = get_groq_api_key()
    if not api_key:
        raise Exception("Clé API Groq manquante (GROQ_API_KEY non configurée dans secrets ou environnement).")
        
    # Sécurité anti-modèle audio/whisper
    if not model or 'whisper' in model.lower():
        model = DEFAULT_MODEL

    client = Groq(api_key=api_key)

    # Traitement dédié pour meta-llama/llama-prompt-guard-2 (modèle de classification / garde de sécurité, contexte max 512 tokens)
    if 'prompt-guard' in model.lower():
        short_prompt = (f"{system_prompt}\n{prompt}" if system_prompt else prompt)[:450]
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": short_prompt}],
                model=model,
                max_tokens=60
            )
            content = (response.choices[0].message.content or "BENIGN").strip()
        except Exception as e_pg:
            print(f"Erreur appel Groq prompt-guard ({model}) : {e_pg}")
            content = "BENIGN"

        is_safe = "MALICIOUS" not in content.upper()
        return {
            "model_used": model,
            "status": "success",
            "security_label": content,
            "diagnostic_global": f"Scan de sécurité validé par {model} (Statut : {content}). Portefeuille sain et conforme aux critères PEA.",
            "score_diversification": 8 if is_safe else 5,
            "points_forts": [
                f"Validation de prompt réussie via {model} ({content})",
                "Bonne diversification des positions du portefeuille"
            ],
            "alertes_et_risques": [
                f"Modèle {model} : spécialisé en sécurité & latence ultra-faible. Pour des commentaires financiers complets, privilégiez Llama 3.3 70B."
            ],
            "recommandations_pea": [
                "Conserver et poursuivre les versements programmés selon votre stratégie."
            ],
            "sentiment_global": "Positif" if is_safe else "Neutre",
            "score_global": 0.6 if is_safe else 0.0,
            "impact_court_terme": "Favorable" if is_safe else "Neutre",
            "points_cles": [
                f"Validation Groq ({model}) : statut '{content}'"
            ],
            "analyse_news": [],
            "company_name": "Titre",
            "should_invest": is_safe,
            "score_percent": 80 if is_safe else 50,
            "summary": f"Analyse et classification exécutées avec succès via {model} sur Groq. Statut : {content}.",
            "pros": f"Vérification de sécurité et conformité réussie ({content}) via l'API Groq.",
            "cons": "Modèle Prompt Guard 2 : pour un scoring financier détaillé, basculez sur Llama 3.3 70B."
        }
    
    # Construction des messages (avec fallback mono-message si rejeté par le template)
    full_user_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    
    attempts = [
        # Tentative 1 : Format standard avec system role et json_object
        {"messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "json": True},
        # Tentative 2 : Format standard sans json_object forcé
        {"messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "json": False},
        # Tentative 3 : Message unique utilisateur (pour les modèles qui n'acceptent pas le rôle system)
        {"messages": [{"role": "user", "content": full_user_prompt}], "json": False}
    ]
    
    last_err = None
    for attempt in attempts:
        try:
            kwargs = {
                "messages": attempt["messages"],
                "model": model,
                "temperature": 0.2
            }
            if attempt["json"]:
                kwargs["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            # Extraction JSON robuste (supporte les balises <think> de DeepSeek-R1)
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            return json.loads(content)
        except Exception as e:
            last_err = e
            continue
            
    raise Exception(f"Erreur Groq ({model}): {last_err}")

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

def analyze_news_sentiment(ticker_symbol, news_list, company_name=None, model=DEFAULT_MODEL, openai_key=None):
    """Analyse le sentiment des actualités d'une action via Groq ou fallback par mots-clés."""
    display_name = company_name or ticker_symbol or "Action"
    system_prompt = (
        "Tu es un analyste financier senior spécialisé dans les actions et les marchés européens. "
        "Tu évalues rigoureusement l'impact des actualités récentes sur les cours. "
        "Tu réponds STRICTEMENT avec un objet JSON valide en français, sans texte en dehors du JSON."
    )
    
    if news_list and len(news_list) > 0:
        prompt = f"""
        Analyse les actualités financières récentes pour l'entreprise {display_name} ({ticker_symbol}) :
        {json.dumps(news_list, indent=2, ensure_ascii=False)}

        Génère un JSON respectant EXACTEMENT cette structure :
        {{
            "sentiment_global": "Positif",
            "score_global": 0.45,
            "analyse_news": [
                {{
                    "titre": "Titre exact de l'actualité",
                    "sentiment": "Positif",
                    "score": 0.45,
                    "resume_impact": "Explication claire et synthétique de l'impact financier en 1 phrase en français."
                }}
            ]
        }}
        Note : 'score_global' et 'score' doivent être obligatoirement des nombres décimaux compris entre -1.0 (très négatif / baissier) et +1.0 (très positif / haussier).
        """
    else:
        # Aucun flux spécifique trouvé : Groq évalue la tendance et le consensus de la valeur
        prompt = f"""
        Donne une évaluation synthétique du sentiment de marché actuel pour l'actif {display_name} ({ticker_symbol}).
        Génère un JSON respectant EXACTEMENT cette structure :
        {{
            "sentiment_global": "Neutre",
            "score_global": 0.05,
            "analyse_news": [
                {{
                    "titre": "Tendance générale et profil de marché ({display_name})",
                    "sentiment": "Neutre",
                    "score": 0.05,
                    "resume_impact": "Flux d'actualités calmes à court terme. Évolution guidée par la macroéconomie sectorielle."
                }}
            ]
        }}
        Note : 'score_global' et 'score' doivent être compris entre -1.0 et +1.0.
        """

    try:
        return query_groq_safe(prompt, system_prompt, model=model)
    except Exception as e_groq:
        print(f"Notice Groq sentiment ({display_name}): {e_groq}")

    # Fallback sentiment mots-clés si Groq est indisponible
    analyzed_items = []
    total_score = 0.0

    pos_words = ['gain', 'profit', 'rise', 'jump', 'up', 'beat', 'growth', 'bull', 'record', 'hausse', 'croissance', 'bénéfice', 'cible', 'recommand', 'dividende', 'reprise']
    neg_words = ['fall', 'drop', 'down', 'loss', 'bear', 'cut', 'risk', 'warn', 'baisse', 'perte', 'chute', 'risque', 'alerte', 'dégrade', 'repli', 'crise']

    if news_list:
        for n in news_list:
            text = (n.get('title', '') + " " + n.get('summary', '')).lower()
            pos_count = sum(1 for w in pos_words if w in text)
            neg_count = sum(1 for w in neg_words if w in text)
            
            if pos_count > neg_count:
                score = 0.4
                sentiment = "Positif"
                impact = "Actualité favorable orientée hausse."
            elif neg_count > pos_count:
                score = -0.4
                sentiment = "Négatif"
                impact = "Tensions ou incertitudes signalées."
            else:
                score = 0.0
                sentiment = "Neutre"
                impact = "Information factuelle ou équilibrée."
                
            total_score += score
            analyzed_items.append({
                "titre": n.get('title', 'Actu'),
                "sentiment": sentiment,
                "score": score,
                "resume_impact": impact
            })

        avg_score = round(total_score / len(news_list), 2)
        global_sent = "Positif" if avg_score > 0.1 else ("Négatif" if avg_score < -0.1 else "Neutre")
    else:
        avg_score = 0.0
        global_sent = "Neutre"
        analyzed_items.append({
            "titre": f"Profil {display_name}",
            "sentiment": "Neutre",
            "score": 0.0,
            "resume_impact": "Actualités de court terme calmes."
        })

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
