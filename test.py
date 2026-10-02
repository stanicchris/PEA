import json
import ollama
import pandas as pd
import streamlit as st
import yfinance as yf

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Suivi PEA & IA Locale", page_icon="📈", layout="wide"
)

# Nom du modèle Ollama installé en local
OLLAMA_MODEL = "llama3.2"  # Tu peux changer par "mistral" ou un autre modèle installé


# --- 1. FONCTIONS DE RÉCUPÉRATION ET TRAITEMENT DES DONNÉES ---


@st.cache_data(ttl=3600)
def get_portfolio_data(portfolio_config):
    """Enrichit le portefeuille avec les données de marché en direct via yfinance."""
    data = []
    for position in portfolio_config:
        ticker_symbol = position["ticker"]
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        price = info.get("currentPrice") or info.get("regularMarketPrice", 0.0)
        total_val = price * position["quantity"]
        pru = position["pru"]
        pnl_pct = ((price - pru) / pru) * 100 if pru > 0 else 0.0

        data.append(
            {
                "ticker": ticker_symbol,
                "name": info.get("shortName", ticker_symbol),
                "sector": info.get("sector", "Inconnu"),
                "quantity": position["quantity"],
                "pru": pru,
                "current_price": round(price, 2),
                "total_value": round(total_val, 2),
                "pnl_pct": round(pnl_pct, 2),
            }
        )
    return pd.DataFrame(data)


@st.cache_data(ttl=1800)
def fetch_ticker_news(ticker_symbol, max_news=3):
    """Récupère les dernières actualités d'une action via yfinance."""
    ticker = yf.Ticker(ticker_symbol)
    news_list = ticker.news or []

    cleaned_news = []
    for item in news_list[:max_news]:
        content = item.get("content", item)
        title = content.get("title", "Sans titre")
        summary = content.get("summary", content.get("description", ""))
        provider = content.get("provider", {}).get(
            "displayName", "Source inconnue"
        )

        cleaned_news.append(
            {
                "title": title,
                "summary": summary,
                "provider": provider,
            }
        )
    return cleaned_news


# --- 2. FONCTIONS DE DIAGNOSTIC ET SENTIMENT VIA OLLAMA ---


def query_ollama_json(prompt, system_prompt=""):
    """Exécute une requête vers Ollama en forçant un retour JSON."""
    response = ollama.chat(
        model=OLLAMA_MODEL,
        format="json",  # Force Ollama à générer un JSON valide
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.2},
    )
    return json.loads(response["message"]["content"])


def analyze_portfolio_global(portfolio_df):
    """Génère un diagnostic d'allocation global du portefeuille via Ollama."""
    portfolio_json = portfolio_df.to_dict(orient="records")

    system_prompt = (
        "Tu es un conseiller en gestion de patrimoine spécialisé dans le PEA. "
        "Tu réponds STRICTEMENT avec un objet JSON valide en français."
    )

    prompt = f"""
    Analyse la composition de ce portefeuille PEA :
    {json.dumps(portfolio_json, indent=2)}

    Génère un JSON respectant EXACTEMENT cette structure :
    {{
        "diagnostic_global": "Résumé court du portefeuille en français.",
        "score_diversification": 7,
        "points_forts": ["Point 1", "Point 2"],
        "alertes_et_risques": ["Alerte 1", "Alerte 2"],
        "recommandations_pea": ["Conseil 1", "Conseil 2"]
    }}
    """

    return query_ollama_json(prompt, system_prompt)


def analyze_news_sentiment(ticker_symbol, news_list):
    """Analyse le sentiment des actualités d'un ticker spécifique via Ollama."""
    if not news_list:
        return {
            "sentiment_global": "Neutre",
            "score_global": 0.0,
            "analyse_news": [],
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
        "sentiment_global": "Positif" ou "Neutre" ou "Négatif",
        "score_global": 0.5,
        "analyse_news": [
            {{
                "titre": "Titre",
                "sentiment": "Positif" ou "Neutre" ou "Négatif",
                "score": 0.5,
                "resume_impact": "Explication courte en 1 phrase en français."
            }}
        ]
    }}
    Note : 'score_global' et 'score' doivent être un nombre entre -1.0 (très négatif) et +1.0 (très positif).
    """

    return query_ollama_json(prompt, system_prompt)


def compute_portfolio_weather(df_portfolio, news_sentiments_dict):
    """Calcule le score météo global pondéré par la valeur des positions."""
    total_val = df_portfolio["total_value"].sum()
    if total_val == 0:
        return 0.0, "☁️", "Neutre"

    weighted_sentiment = 0.0
    for _, row in df_portfolio.iterrows():
        ticker = row["ticker"]
        weight = row["total_value"] / total_val
        score = news_sentiments_dict.get(ticker, {}).get("score_global", 0.0)
        weighted_sentiment += score * weight

    if weighted_sentiment > 0.3:
        return round(weighted_sentiment, 2), "☀️", "Ensoleillé"
    elif weighted_sentiment > 0.1:
        return round(weighted_sentiment, 2), "⛅", "Éclaircies"
    elif weighted_sentiment >= -0.1:
        return round(weighted_sentiment, 2), "☁️", "Nuageux"
    elif weighted_sentiment >= -0.3:
        return round(weighted_sentiment, 2), "🌧️", "Pluie"
    else:
        return round(weighted_sentiment, 2), "⛈️", "Orageux"


# --- 3. INTERFACE STREAMLIT ---

st.title("📊 Suivi de Portefeuille PEA (IA Locale avec Ollama)")

# Portefeuille exemple
sample_portfolio = [
    {"ticker": "MC.PA", "quantity": 5, "pru": 720.0},
    {"ticker": "TTE.PA", "quantity": 50, "pru": 55.0},
    {"ticker": "AIR.PA", "quantity": 20, "pru": 130.0},
    {"ticker": "SOIT.PA", "quantity": 15, "pru": 110.0},
]

df = get_portfolio_data(sample_portfolio)

st.subheader("💼 Composition du Portefeuille")
st.dataframe(df, use_container_width=True)

st.divider()

tab1, tab2 = st.tabs(
    ["🧠 Diagnostic Global IA", "🌡️ Météo & Sentiment de l'Actualité"]
)

# --- ONGLET 1 : DIAGNOSTIC GLOBAL ---
with tab1:
    if st.button("🤖 Lancer le diagnostic complet (Ollama)"):
        with st.spinner(
            f"Analyse en cours par le modèle local ({OLLAMA_MODEL})..."
        ):
            try:
                diag = analyze_portfolio_global(df)

                c1, c2 = st.columns([1, 3])
                with c1:
                    st.metric(
                        "Score Diversification",
                        f"{diag.get('score_diversification', 0)}/10",
                    )
                with c2:
                    st.info(
                        diag.get("diagnostic_global", "Analyse indisponible.")
                    )

                col_a, col_b = st.columns(2)
                with col_a:
                    st.subheader("✅ Points Forts")
                    for pt in diag.get("points_forts", []):
                        st.success(pt)

                    st.subheader("💡 Recommandations PEA")
                    for rec in diag.get("recommandations_pea", []):
                        st.write(f"• {rec}")

                with col_b:
                    st.subheader("⚠️ Alertes & Risques")
                    for alt in diag.get("alertes_et_risques", []):
                        st.error(alt)
            except Exception as e:
                st.error(
                    f"Erreur avec Ollama. Assure-toi que le service tourne (`ollama serve`) : {e}"
                )

# --- ONGLET 2 : MÉTÉO & ACTUALITÉS ---
with tab2:
    if st.button("🔎 Analyser l'actualité & Météo (Ollama)"):
        sentiments_results = {}
        tickers_list = df["ticker"].tolist()

        progress_text = st.empty()
        progress_bar = st.progress(0)

        for idx, t_sym in enumerate(tickers_list):
            progress_text.text(f"Analyse Ollama des actualités de {t_sym}...")
            news_items = fetch_ticker_news(t_sym)
            try:
                analysis = analyze_news_sentiment(t_sym, news_items)
            except Exception:
                analysis = {
                    "sentiment_global": "Neutre",
                    "score_global": 0.0,
                    "analyse_news": [],
                }
            sentiments_results[t_sym] = analysis
            progress_bar.progress((idx + 1) / len(tickers_list))

        progress_text.empty()
        progress_bar.empty()

        st.session_state["sentiments_results"] = sentiments_results

    if "sentiments_results" in st.session_state:
        sentiments_dict = st.session_state["sentiments_results"]

        score_w, icon_w, label_w = compute_portfolio_weather(
            df, sentiments_dict
        )

        st.subheader("🌡️ Météo Synthétique du Portefeuille")
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            st.metric(
                label=f"Météo : {label_w}",
                value=f"{icon_w} {score_w:+.2f}",
                delta="Score pondéré par le poids des lignes",
            )
        with col_m2:
            st.write("**Impact par ligne :**")
            total_val = df["total_value"].sum()
            for _, r in df.iterrows():
                tk = r["ticker"]
                wt = (r["total_value"] / total_val) * 100
                s_score = sentiments_dict.get(tk, {}).get("score_global", 0.0)
                st.caption(
                    f"• **{tk}** ({wt:.0f}% du PEA) : Sentiment {s_score:+.2f}"
                )

        st.divider()
        st.subheader("📰 Détail des Actualités par Action")

        selected_t = st.selectbox(
            "Consulter les actualités d'une action :", df["ticker"].tolist()
        )
        if selected_t in sentiments_dict:
            res = sentiments_dict[selected_t]
            st.write(
                f"**Sentiment Global :** {res.get('sentiment_global', 'Neutre')} ({res.get('score_global', 0.0):+.2f})"
            )

            for news_item in res.get("analyse_news", []):
                with st.expander(f"**{news_item.get('titre', 'News')}**"):
                    st.write(
                        f"**Impact :** {news_item.get('resume_impact', '')}"
                    )
                    s_val = news_item.get("sentiment", "Neutre")
                    s_score = news_item.get("score", 0.0)
                    if s_val == "Positif":
                        st.success(f"Score : {s_score:+.2f} 🟢")
                    elif s_val == "Négatif":
                        st.error(f"Score : {s_score:+.2f} 🔴")
                    else:
                        st.info(f"Score : {s_score:+.2f} ⚪")