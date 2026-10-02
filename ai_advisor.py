import json
import time
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
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "qwen/qwen3.8-27b"
]
DEFAULT_MODEL = "llama-3.1-8b-instant"

def get_groq_api_key():
    """Récupère la clé API Groq depuis st.secrets ou les variables d'environnement."""
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY", "")

def get_available_groq_models():
    """Retourne la liste des modèles Groq disponibles pour l'analyse."""
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

_LAST_GROQ_CALL_TIME = 0.0
GROQ_MIN_DELAY_SECONDS = 15.0

def enforce_groq_delay(min_delay=GROQ_MIN_DELAY_SECONDS):
    """Garantit un délai d'au moins 15 secondes entre deux appels à l'API Groq pour respecter les limites de quota."""
    global _LAST_GROQ_CALL_TIME
    now = time.time()
    elapsed = now - _LAST_GROQ_CALL_TIME
    if elapsed < min_delay and _LAST_GROQ_CALL_TIME > 0:
        sleep_dur = min_delay - elapsed
        time.sleep(sleep_dur)
    _LAST_GROQ_CALL_TIME = time.time()

def parse_json_from_response(content):
    """Extrait et nettoie le JSON depuis la réponse Groq (supporte <think>, markdown et troncature)."""
    if not content:
        raise ValueError("Réponse Groq vide.")
    # 1. Supprimer les balises de réflexion <think>...</think>
    cleaned = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
    # 2. Supprimer les balises de bloc de code markdown
    cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned).strip()
    
    # 3. Tentative directe
    try:
        return json.loads(cleaned)
    except Exception:
        pass
        
    # 4. Extraction du bloc entre { et }
    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
            
    # 5. Tentative de fermeture si JSON coupé à la fin
    start_brace = cleaned.find('{')
    if start_brace != -1:
        sub = cleaned[start_brace:].strip()
        for suffix in ['"}', '"]}', '"}', '}', ']}']:
            try:
                return json.loads(sub + suffix)
            except Exception:
                continue

    return json.loads(cleaned)

def query_groq_safe(prompt, system_prompt="", model=DEFAULT_MODEL, max_tokens=650):
    """Exécute une requête vers Groq avec extraction JSON robuste (support Llama 3.1, 3.3 et Qwen)."""
    if not HAS_GROQ_PKG:
        raise Exception("Le package 'groq' n'est pas installé.")
    api_key = get_groq_api_key()
    if not api_key:
        raise Exception("Clé API Groq manquante (GROQ_API_KEY non configurée dans secrets ou environnement).")
        
    model = model or DEFAULT_MODEL
    client = Groq(api_key=api_key)

    full_user_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    
    # Llama 3.1 supporte nativement le json_object strict
    use_json = "llama" in model.lower()
    attempts = [
        {"messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "json": use_json},
        {"messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "json": False},
        {"messages": [{"role": "user", "content": full_user_prompt}], "json": False}
    ]
    
    last_err = None
    for attempt in attempts:
        for retry_num in range(3):
            try:
                enforce_groq_delay(15.0)

                kwargs = {
                    "messages": attempt["messages"],
                    "model": model,
                    "temperature": 0.2,
                    "max_tokens": max_tokens
                }
                if attempt.get("json"):
                    kwargs["response_format"] = {"type": "json_object"}
                response = client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                
                # Extraction et parsing JSON résilient
                data = parse_json_from_response(content)
                if data and isinstance(data, dict):
                    return data
            except Exception as e:
                err_str = str(e).lower()
                last_err = e
                # Détection de Rate Limit Groq (429 / OTPM)
                if "rate limit" in err_str or "rate_limit" in err_str or "429" in err_str:
                    wait_sec = 3.5
                    m_wait = re.search(r'try again in ([0-9\.]+)s', str(e), re.IGNORECASE)
                    if m_wait:
                        try:
                            wait_sec = float(m_wait.group(1)) + 0.8
                        except Exception:
                            pass
                    print(f"Notice Groq Rate Limit ({model}) : pause de {wait_sec:.1f}s puis nouvelle tentative ({retry_num + 1}/3)...")
                    time.sleep(wait_sec)
                    continue
                else:
                    break
                    
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
        "Tu es un conseiller financier expert du PEA. "
        "Tu réponds STRICTEMENT avec un objet JSON valide en français, sans aucun texte d'introduction, sans balises markdown ni explication."
    )
    prompt = f"""
    Analyse ce portefeuille PEA :
    {json.dumps(records, indent=2)}

    Réponds UNIQUEMENT avec l'objet JSON ci-dessous rempli (2 phrases concises pour le diagnostic) :
    {{
        "diagnostic_global": "Synthèse courte et percutante du portefeuille en 2 phrases.",
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
