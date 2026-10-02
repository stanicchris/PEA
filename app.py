import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import os
from urllib.parse import quote
import yfinance as yf

# Module base de données Supabase
from database import (
    get_supabase_client, save_snapshot, get_snapshots_df, 
    get_positions_history_df, delete_snapshot, 
    is_snapshot_saved, extract_date_from_filename
)

# Module BourseAi (ZoneBourse + Synthèse)
from bourse_ai import analyze_stock_with_ai, ZONEBOURSE_URLS

# Module AI Advisor (Groq & News Sentiment)
from ai_advisor import (
    analyze_portfolio_global, fetch_ticker_news, 
    analyze_news_sentiment, compute_portfolio_weather, DEFAULT_MODEL
)

# -------------------------------------------------------------
# CONFIGURATION DE LA PAGE STREAMLIT
# -------------------------------------------------------------
st.set_page_config(
    page_title="PEA Tracker | Dashboard Pro, Live & IA",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# AUTHENTIFICATION SUPABASE
# -------------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

supabase = get_supabase_client()

if not st.session_state["user_id"]:
    st.title("🔐 Connexion PEA Tracker")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Se connecter"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user_id"] = res.user.id
                st.rerun()
            except Exception as e:
                st.error(f"Erreur de connexion : {e}")
    with c2:
        if st.button("S'inscrire"):
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Inscription réussie. Vérifiez vos emails si nécessaire ou connectez-vous.")
            except Exception as e:
                st.error(f"Erreur d'inscription : {e}")
    st.stop()

if st.sidebar.button("Déconnexion"):
    supabase.auth.sign_out()
    st.session_state["user_id"] = None
    st.rerun()


# -------------------------------------------------------------
# THÈME ET CSS SUR MESURE (FINTECH STYLE BAGGR)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    
    .dashboard-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 20px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 15px;
    }
    
    .badge-pea {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-block;
        margin-left: 10px;
    }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, border-color 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }
    
    .badge-positive {
        display: inline-flex;
        align-items: center;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-negative {
        display: inline-flex;
        align-items: center;
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .badge-neutral {
        display: inline-flex;
        align-items: center;
        background-color: rgba(148, 163, 184, 0.15);
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
    }
    
    .ranking-card {
        background: #182234;
        border: 1px solid #2d3b52;
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 9px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background-color 0.15s ease;
    }
    .ranking-card:hover {
        background-color: #1e2c44;
    }

    .company-logo {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
        background-color: #334155;
        border: 1px solid #475569;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# LOGOS & CARTOGRAPHIE DYNAMIQUE
# -------------------------------------------------------------
ISIN_METADATA = {
    'FR0000075954': {'domain': 'riber.com', 'yf': 'ALRIB.PA', 'sector': 'Semi-conducteurs & Tech', 'div': 0.0},
    'FR0000131104': {'domain': 'bnpparibas.com', 'yf': 'BNP.PA', 'sector': 'Finance & Banque', 'div': 5.84},
    'FR0011726835': {'domain': 'gtt.fr', 'yf': 'GTT.PA', 'sector': 'Énergie & Gaz', 'div': 2.1},
    'FR0013341781': {'domain': '2crsi.com', 'yf': 'AL2CR.PA', 'sector': 'Technologie & Hardware', 'div': 0.0},
    'FR0014007ND6': {'domain': 'haffner-energy.com', 'yf': 'ALHAF.PA', 'sector': 'Énergie Renouvelable', 'div': 0.0},
    'FR0000121972': {'domain': 'se.com', 'yf': 'SU.PA', 'sector': 'Industrie & Électrique', 'div': 1.3},
    'FR0011550193': {'domain': 'easy.bnpparibas.com', 'yf': 'ETZ.PA', 'sector': 'ETF & Indice Européen', 'div': 2.8},
    'FR0000073272': {'domain': 'safran-group.com', 'yf': 'SAF.PA', 'sector': 'Aéronautique & Défense', 'div': 0.7},
    'FR0000133308': {'domain': 'orange.com', 'yf': 'ORA.PA', 'sector': 'Télécoms', 'div': 5.2},
    'FR0014018PW8': {'domain': 'date-sa.com', 'yf': 'ALDAT.PA', 'sector': 'Technologie & Logiciel', 'div': 0.0},
    'FR0011341205': {'domain': 'nanobiotix.com', 'yf': 'NANO.PA', 'sector': 'Santé & Biotech', 'div': 0.0},
    'FR0011049824': {'domain': 'mediantechnologies.com', 'yf': 'ALMDT.PA', 'sector': 'Santé & Medtech', 'div': 0.0},
    'FR0000120271': {'domain': 'totalenergies.com', 'yf': 'TTE.PA', 'sector': 'Énergie & Pétrole', 'div': 4.5},
    'FR0000121014': {'domain': 'lvmh.com', 'yf': 'MC.PA', 'sector': 'Luxe & Consommation', 'div': 3.2},
    'FR0000120073': {'domain': 'airliquide.com', 'yf': 'AI.PA', 'sector': 'Industrie & Chimie', 'div': 2.0},
    'FR0000120321': {'domain': 'loreal.com', 'yf': 'OR.PA', 'sector': 'Cosmétique', 'div': 1.9},
    'FR0000120578': {'domain': 'sanofi.com', 'yf': 'SAN.PA', 'sector': 'Santé & Pharma', 'div': 4.1},
    'FR0000120628': {'domain': 'axa.com', 'yf': 'CS.PA', 'sector': 'Assurance & Finance', 'div': 5.5},
}

NAME_DOMAINS_KEYWORD = {
    'BNP': 'bnpparibas.com', 'SCHNEIDER': 'se.com', 'SAFRAN': 'safran-group.com',
    'ORANGE': 'orange.com', 'GTT': 'gtt.fr', 'RIBER': 'riber.com',
    '2CRSI': '2crsi.com', 'HAFFNER': 'haffner-energy.com', 'NANOBIOTIX': 'nanobiotix.com',
    'MEDIAN': 'mediantechnologies.com', 'STOXX': 'easy.bnpparibas.com', 'ETF': 'amundietf.fr'
}

def resolve_logo_url(isin, name):
    isin_clean = str(isin).strip().upper() if pd.notna(isin) else ""
    if isin_clean in ISIN_METADATA:
        return f"https://www.google.com/s2/favicons?domain={ISIN_METADATA[isin_clean]['domain']}&sz=128"
    name_clean = str(name).upper() if pd.notna(name) else ""
    for kw, dom in NAME_DOMAINS_KEYWORD.items():
        if kw in name_clean:
            return f"https://www.google.com/s2/favicons?domain={dom}&sz=128"
    safe_name = quote(str(name).strip()[:12])
    return f"https://ui-avatars.com/api/?name={safe_name}&background=1e293b&color=38bdf8&size=128&bold=true"

def resolve_sector(isin, name):
    isin_clean = str(isin).strip().upper() if pd.notna(isin) else ""
    if isin_clean in ISIN_METADATA:
        return ISIN_METADATA[isin_clean]['sector']
    name_u = str(name).upper()
    if 'ETF' in name_u or 'STOXX' in name_u or 'MSCI' in name_u:
        return 'ETF & Indice'
    if 'ENERGY' in name_u or 'PETROL' in name_u:
        return 'Énergie'
    if 'TECH' in name_u or 'SOFT' in name_u:
        return 'Technologie'
    return 'Action'

def resolve_div_yield(isin, name):
    isin_clean = str(isin).strip().upper() if pd.notna(isin) else ""
    if isin_clean in ISIN_METADATA:
        return ISIN_METADATA[isin_clean]['div']
    return 0.0

def resolve_yf_symbol(isin, name):
    isin_clean = str(isin).strip().upper() if pd.notna(isin) else ""
    if isin_clean in ISIN_METADATA:
        return ISIN_METADATA[isin_clean]['yf']
    return None

# -------------------------------------------------------------
# PARSING DU CSV
# -------------------------------------------------------------
def clean_numeric_col(series):
    if series is None:
        return pd.Series(dtype=float)
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(float)
    return (
        series.astype(str)
        .str.replace('\xa0', '', regex=False)
        .str.replace(' ', '', regex=False)
        .str.replace('€', '', regex=False)
        .str.replace('%', '', regex=False)
        .str.replace(',', '.', regex=False)
        .replace('', np.nan)
        .astype(float)
    )

@st.cache_data
def parse_portfolio_csv(file_content, filename="portfolio.csv"):
    try:
        stream = io.BytesIO(file_content) if isinstance(file_content, bytes) else file_content
        df = pd.read_csv(stream, sep=';', decimal=',', thousands=' ')
        if len(df.columns) <= 2:
            if isinstance(file_content, bytes):
                stream.seek(0)
            df = pd.read_csv(stream, sep=',', decimal='.')
    except Exception as e:
        st.error(f"Erreur de lecture du fichier CSV : {e}")
        return None

    mapping = {
        'name': 'name', 'nom': 'name', 'valeur': 'name', 'titre': 'name', 'libellé': 'name', 'libelle': 'name',
        'isin': 'isin', 'code isin': 'isin', 'code': 'isin',
        'quantity': 'quantity', 'quantité': 'quantity', 'qte': 'quantity', 'nb': 'quantity',
        'buyingprice': 'buyingPrice', 'pru': 'buyingPrice', 'prix d\'achat': 'buyingPrice', 'cours d\'achat': 'buyingPrice',
        'lastprice': 'lastPrice', 'cours': 'lastPrice', 'dernier cours': 'lastPrice', 'prix actuel': 'lastPrice',
        'amount': 'amount', 'montant': 'amount', 'valorisation': 'amount', 'valeur actuelle': 'amount', 'total': 'amount',
        'amountvariation': 'amountVariation', '+/- value': 'amountVariation', 'plus/moins value': 'amountVariation', 'gain': 'amountVariation',
        'variation': 'variation', '+/- value (%)': 'variation', 'perf (%)': 'variation', 'performance (%)': 'variation',
        'intradayvariation': 'intradayVariation', 'var jour (%)': 'intradayVariation', 'variation jour': 'intradayVariation'
    }
    
    cleaned_cols = {}
    for c in df.columns:
        key = str(c).strip().lower()
        cleaned_cols[c] = mapping[key] if key in mapping else str(c).strip()
            
    df = df.rename(columns=cleaned_cols)

    if 'name' not in df.columns:
        st.error("Le fichier CSV doit comporter une colonne avec le nom des titres.")
        return None

    numeric_cols = ['quantity', 'buyingPrice', 'lastPrice', 'amount', 'amountVariation', 'variation', 'intradayVariation']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = clean_numeric_col(df[col])

    if 'amount' not in df.columns and 'quantity' in df.columns and 'lastPrice' in df.columns:
        df['amount'] = df['quantity'] * df['lastPrice']

    if 'totalCost' not in df.columns:
        if 'quantity' in df.columns and 'buyingPrice' in df.columns:
            df['totalCost'] = df['quantity'] * df['buyingPrice']
        elif 'amount' in df.columns and 'amountVariation' in df.columns:
            df['totalCost'] = df['amount'] - df['amountVariation']
        else:
            df['totalCost'] = df['amount']

    if 'amountVariation' not in df.columns:
        df['amountVariation'] = df['amount'] - df['totalCost']

    if 'variation' not in df.columns:
        df['variation'] = np.where(df['totalCost'] > 0, (df['amountVariation'] / df['totalCost']) * 100, 0.0)

    if 'intradayVariation' not in df.columns:
        df['intradayVariation'] = 0.0

    df['intradayAmount'] = df['amount'] - (df['amount'] / (1 + df['intradayVariation'] / 100))

    def categorize(name):
        n = str(name).upper()
        if any(w in n for w in ['ETF', 'STOXX', 'MSCI', 'ISHARES', 'AMUNDI', 'LYXOR', 'VANGUARD', 'SP500', 'S&P', 'CORE']):
            return 'ETF'
        return 'Action'

    df['type'] = df['name'].apply(categorize)
    df['logo_url'] = df.apply(lambda r: resolve_logo_url(r.get('isin'), r.get('name')), axis=1)
    df['sector'] = df.apply(lambda r: resolve_sector(r.get('isin'), r.get('name')), axis=1)
    df['div_yield'] = df.apply(lambda r: resolve_div_yield(r.get('isin'), r.get('name')), axis=1)
    df['annual_div_euro'] = df['amount'] * (df['div_yield'] / 100)
    df['yf_symbol'] = df.apply(lambda r: resolve_yf_symbol(r.get('isin'), r.get('name')), axis=1)

    total_val = df['amount'].sum()
    df['weight'] = (df['amount'] / total_val * 100) if total_val > 0 else 0.0

    return df

# -------------------------------------------------------------
# ACTUALISATION YAHOO FINANCE
# -------------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_live_quotes(df):
    updated_df = df.copy()
    symbols = [s for s in updated_df['yf_symbol'].dropna().unique() if s]
    if not symbols:
        return updated_df, "Aucun symbole Yahoo Finance configuré."
    try:
        tickers = yf.Tickers(' '.join(symbols))
        live_count = 0
        for idx, row in updated_df.iterrows():
            sym = row['yf_symbol']
            if sym and sym in tickers.tickers:
                try:
                    t = tickers.tickers[sym]
                    info = t.fast_info
                    live_p = info.last_price
                    prev_close = info.previous_close
                    if live_p and live_p > 0:
                        updated_df.at[idx, 'lastPrice'] = live_p
                        updated_df.at[idx, 'amount'] = row['quantity'] * live_p
                        updated_df.at[idx, 'amountVariation'] = updated_df.at[idx, 'amount'] - row['totalCost']
                        updated_df.at[idx, 'variation'] = (updated_df.at[idx, 'amountVariation'] / row['totalCost'] * 100) if row['totalCost'] > 0 else 0
                        if prev_close and prev_close > 0:
                            intra_pct = (live_p - prev_close) / prev_close * 100
                            updated_df.at[idx, 'intradayVariation'] = intra_pct
                            updated_df.at[idx, 'intradayAmount'] = updated_df.at[idx, 'amount'] - (updated_df.at[idx, 'amount'] / (1 + intra_pct / 100))
                        live_count += 1
                except Exception:
                    pass
        total_val = updated_df['amount'].sum()
        updated_df['weight'] = (updated_df['amount'] / total_val * 100) if total_val > 0 else 0.0
        return updated_df, f"{live_count} cours actualisés en direct !"
    except Exception as e:
        return updated_df, f"Erreur lors du rafraîchissement : {e}"

# -------------------------------------------------------------
# SIDEBAR ET PARAMÈTRES
# -------------------------------------------------------------
DEFAULT_CSV = "export-positions-instantanees-27-09-2026_19-22-41.csv"

st.sidebar.markdown("## 📊 Source de Données")
uploaded_file = st.sidebar.file_uploader("Importer un export CSV", type=["csv"])

raw_bytes = None
source_name = ""

if uploaded_file is not None:
    raw_bytes = uploaded_file.getvalue()
    source_name = uploaded_file.name
    st.sidebar.success(f"Fichier : `{uploaded_file.name}`")
elif os.path.exists(DEFAULT_CSV):
    with open(DEFAULT_CSV, "rb") as f:
        raw_bytes = f.read()
    source_name = DEFAULT_CSV
    st.sidebar.info(f"Fichier par défaut : `{DEFAULT_CSV}`")

st.sidebar.markdown("---")
st.sidebar.markdown("## 💰 Compte Espèces PEA")
cash = st.sidebar.number_input("Liquidités disponibles (€)", min_value=0.0, value=500.0, step=100.0)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧠 Configuration IA (Groq)")

# Modèle Groq
groq_model = st.sidebar.selectbox(
    "Modèle IA (Groq)",
    options=[DEFAULT_MODEL, "llama3-70b-8192", "mixtral-8x7b-32768"],
    index=0,
    help="Sélectionnez le modèle Groq pour l'analyse."
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🤖 Configuration BourseAi")

st.sidebar.markdown("---")
st.sidebar.markdown("## 💾 Base de Données Supabase")
auto_save = st.sidebar.checkbox("⚡ Auto-enregistrer les nouveaux CSV", value=True)
db_snapshots = get_snapshots_df()
nb_snaps_db = len(db_snapshots)
st.sidebar.caption(f"📦 Historique actuel : **{nb_snaps_db} instantané(s)**")

if raw_bytes is None:
    st.error("Aucune donnée disponible. Veuillez importer un fichier CSV.")
    st.stop()

df = parse_portfolio_csv(raw_bytes, source_name)
if df is None or df.empty:
    st.error("Impossible de lire les positions du portefeuille.")
    st.stop()

# Auto-update ou Bouton Live Yahoo Finance
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔴 Cours du Marché en Direct")
if st.sidebar.button("🔄 Rafraîchir les cours (Yahoo Finance)"):
    # Clear cache to force refresh
    st.cache_data.clear()
    
# Always try to fetch live quotes (it uses cache with 60s TTL)
df, msg = fetch_live_quotes(df)
st.sidebar.success(msg)

# Auto-sauvegarde Supabase
snapshot_date_str = extract_date_from_filename(source_name)
already_saved_id = is_snapshot_saved(snapshot_date_str, source_name)

if not already_saved_id and auto_save:
    saved_id = save_snapshot(df, cash=cash, source_filename=source_name, custom_date=snapshot_date_str)
    st.toast(f"✅ Instantané du {snapshot_date_str} enregistré en base !", icon="💾")
    st.rerun()

# -------------------------------------------------------------
# CALCULS STATISTIQUES GLOBAUX
# -------------------------------------------------------------
valeur_titres = df['amount'].sum()
valeur_totale_portefeuille = valeur_titres + cash
cout_total_investi = df['totalCost'].sum()
plus_value_latente_titres = df['amountVariation'].sum()
perf_globale_pct = (plus_value_latente_titres / cout_total_investi * 100) if cout_total_investi > 0 else 0.0

intraday_euro_total = df['intradayAmount'].sum()
valeur_veille = valeur_titres - intraday_euro_total
intraday_pct_total = (intraday_euro_total / valeur_veille * 100) if valeur_veille > 0 else 0.0

total_dividendes_annuels = df['annual_div_euro'].sum()
rendement_div_moyen = (total_dividendes_annuels / valeur_titres * 100) if valeur_titres > 0 else 0.0

nb_positions = len(df)
prelevements_sociaux = max(0.0, plus_value_latente_titres * 0.172)
valeur_nette_apres_ps = valeur_totale_portefeuille - prelevements_sociaux

# -------------------------------------------------------------
# EN-TÊTE PRINCIPAL DU DASHBOARD
# -------------------------------------------------------------
st.markdown(f"""
<div class="dashboard-header">
    <div>
        <div style="display:flex; align-items:center;">
            <h1 style="margin:0; font-size: 1.85rem; font-weight:800; color:#f8fafc; letter-spacing:-0.02em;">
                💼 Mon Portefeuille PEA
            </h1>
            <span class="badge-pea">Plan d'Épargne en Actions</span>
        </div>
        <p style="margin:6px 0 0 0; color:#94a3b8; font-size:0.92rem;">
            Dashboard inspiré de <b>Baggr</b> & <b>Groq ({groq_model})</b> • {nb_positions} positions • Supabase ({nb_snaps_db} instantanés)
        </p>
    </div>
    <div style="text-align:right;">
        <span style="font-size:0.82rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">
            Valorisation Totale (avec liquidités)
        </span>
        <div style="font-size:2rem; font-weight:800; color:#38bdf8; letter-spacing:-0.03em;">
            {valeur_totale_portefeuille:,.2f} €
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Cartes KPIs
kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div>
            <div class="metric-title">📊 Valeur Titres</div>
            <div class="metric-value">{valeur_titres:,.2f} €</div>
        </div>
        <div class="badge-neutral">+{cash:,.2f} € en espèces</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div>
            <div class="metric-title">💳 Total Investi (PRU)</div>
            <div class="metric-value">{cout_total_investi:,.2f} €</div>
        </div>
        <div class="badge-neutral">Capital d'origine</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    badge_pv_cls = "badge-positive" if plus_value_latente_titres >= 0 else "badge-negative"
    sign_pv = "+" if plus_value_latente_titres >= 0 else ""
    color_pv = "#10b981" if plus_value_latente_titres >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <div>
            <div class="metric-title">📈 Plus-Value Latente</div>
            <div class="metric-value" style="color: {color_pv};">
                {sign_pv}{plus_value_latente_titres:,.2f} €
            </div>
        </div>
        <div>
            <span class="{badge_pv_cls}">{sign_pv}{perf_globale_pct:.2f} %</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    badge_intra_cls = "badge-positive" if intraday_euro_total >= 0 else "badge-negative"
    sign_intra = "+" if intraday_euro_total >= 0 else ""
    color_intra = "#10b981" if intraday_euro_total >= 0 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card">
        <div>
            <div class="metric-title">⚡ Variation Jour</div>
            <div class="metric-value" style="color: {color_intra};">
                {sign_intra}{intraday_euro_total:,.2f} €
            </div>
        </div>
        <div>
            <span class="{badge_intra_cls}">{sign_intra}{intraday_pct_total:.2f} %</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="metric-card">
        <div>
            <div class="metric-title">💰 Dividendes / An</div>
            <div class="metric-value" style="color: #38bdf8;">~ {total_dividendes_annuels:,.0f} €/an</div>
        </div>
        <div class="badge-neutral">Rendement : {rendement_div_moyen:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ONGLETS DE L'APPLICATION
# -------------------------------------------------------------
tab_baggr, tab_ollama, tab_bourseai, tab_history, tab_sectors, tab_inspector, tab_charts, tab_positions, tab_fiscal = st.tabs([
    "📊 Vue d'ensemble (Baggr)",
    f"🧠 Diagnostic & Météo IA ({groq_model})",
    "🤖 Synthèse IA (BourseAi)",
    "📈 Historique & Évolution DB",
    "🏢 Secteurs & Dividendes",
    "🔍 Fiche Titre (Inspecteur)",
    "📊 Analyses & Performance",
    "📋 Positions Détaillées",
    "🧮 Fiscalité PEA & Projections"
])

# =============================================================
# ONGLET 1 : DASHBOARD STYLE BAGGR
# =============================================================
with tab_baggr:
    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.subheader("🗺️ Carte thermique des positions (Treemap)")
        fig_tree = px.treemap(
            df,
            path=[px.Constant("Portefeuille PEA"), 'type', 'name'],
            values='amount', color='variation',
            color_continuous_scale=[[0.0, '#ef4444'], [0.45, '#7f1d1d'], [0.50, '#334155'], [0.55, '#065f46'], [1.0, '#10b981']],
            color_continuous_midpoint=0,
            hover_data={'amount': ':.2f €', 'variation': ':.2f %', 'amountVariation': ':.2f €', 'lastPrice': ':.2f €'}
        )
        fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10), paper_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), height=370)
        st.plotly_chart(fig_tree, use_container_width=True)

    with c2:
        st.subheader("🍩 Allocation du Portefeuille")
        fig_donut = px.pie(df, names='name', values='amount', hole=0.62, color_discrete_sequence=px.colors.qualitative.Prism)
        fig_donut.update_traces(textposition='inside', textinfo='percent', marker=dict(line=dict(color='#0b0f19', width=2)))
        fig_donut.update_layout(
            margin=dict(t=10, l=10, r=10, b=10), showlegend=True,
            legend=dict(orientation="v", x=1.05, y=0.5, font=dict(size=10, color="#94a3b8")),
            paper_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), height=370,
            annotations=[dict(text=f"Total<br><b>{valeur_titres:,.0f} €</b>", x=0.5, y=0.5, font_size=15, showarrow=False, font_color="#38bdf8")]
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
    c_gainers, c_losers, c_type = st.columns([1.2, 1.2, 1])
    sorted_pv = df.sort_values(by='variation', ascending=False)
    
    with c_gainers:
        st.markdown("### 🚀 Top Plus-Values")
        for _, row in sorted_pv.head(3).iterrows():
            st.markdown(f"""
            <div class="ranking-card">
                <div style="display:flex; align-items:center; gap:12px;">
                    <img src="{row['logo_url']}" class="company-logo" alt="logo" />
                    <div>
                        <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{row['name']}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">Val: {row['amount']:,.2f} € • PV: +{row['amountVariation']:,.2f} €</div>
                    </div>
                </div>
                <div class="badge-positive" style="font-size:0.88rem;">+{row['variation']:.2f} %</div>
            </div>
            """, unsafe_allow_html=True)
            
    with c_losers:
        st.markdown("### 🔻 Moins-Values / Flops")
        for _, row in sorted_pv.tail(3).sort_values(by='variation', ascending=True).iterrows():
            b_cls = "badge-negative" if row['variation'] < 0 else "badge-positive"
            prefix = "+" if row['variation'] >= 0 else ""
            st.markdown(f"""
            <div class="ranking-card">
                <div style="display:flex; align-items:center; gap:12px;">
                    <img src="{row['logo_url']}" class="company-logo" alt="logo" />
                    <div>
                        <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{row['name']}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">Val: {row['amount']:,.2f} € • Var: {prefix}{row['amountVariation']:,.2f} €</div>
                    </div>
                </div>
                <div class="{b_cls}" style="font-size:0.88rem;">{prefix}{row['variation']:.2f} %</div>
            </div>
            """, unsafe_allow_html=True)

    with c_type:
        st.markdown("### 🏷️ Allocation Actions vs ETF")
        type_agg = df.groupby('type')['amount'].sum().reset_index()
        fig_type = px.bar(
            type_agg, x='type', y='amount', color='type',
            text=type_agg['amount'].apply(lambda x: f"{x:,.0f} € ({x/valeur_titres*100:.1f}%)"),
            color_discrete_map={'ETF': '#38bdf8', 'Action': '#818cf8'}
        )
        fig_type.update_layout(
            margin=dict(t=10, l=10, r=10, b=10), paper_bgcolor="#1e293b", plot_bgcolor="#1e293b",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"), height=200,
            xaxis=dict(title=None, showgrid=False), yaxis=dict(title=None, showgrid=False, visible=False), showlegend=False
        )
        fig_type.update_traces(textposition='outside')
        st.plotly_chart(fig_type, use_container_width=True)

# =============================================================
# ONGLET 2 : DIAGNOSTIC & MÉTÉO ACTUS IA (GROQ)
# =============================================================
with tab_ollama:
    st.subheader(f"🧠 Diagnostic Global PEA & Météo Synthétique avec `{groq_model}`")
    st.caption("Analyse en temps réel via l'API Groq (très légère en RAM).")

    subtab_diag, subtab_weather = st.tabs(["📋 Diagnostic Global Allocation", "🌡️ Météo Synthétique & Actus"])

    with subtab_diag:
        if st.button(f"🤖 Lancer le Diagnostic Global avec {groq_model}", type="primary"):
            with st.spinner(f"Analyse globale en cours avec le modèle {groq_model}..."):
                diag_res = analyze_portfolio_global(df, model=groq_model)
                st.session_state['global_diag_res'] = diag_res

        if 'global_diag_res' in st.session_state:
            d_res = st.session_state['global_diag_res']
            
            c_score, c_sum = st.columns([1, 3])
            with c_score:
                st.metric("Score Diversification", f"{d_res.get('score_diversification', 0)}/10")
            with c_sum:
                st.info(d_res.get('diagnostic_global', 'Analyse réalisée par IA.'))

            c_pf, c_al = st.columns(2)
            with c_pf:
                st.markdown("#### ✅ Points Forts du Portefeuille")
                for pt in d_res.get("points_forts", []):
                    st.success(f"• {pt}")

                st.markdown("#### 💡 Recommandations PEA")
                for rec in d_res.get("recommandations_pea", []):
                    st.write(f"👉 {rec}")

            with c_al:
                st.markdown("#### ⚠️ Alertes & Risques de Concentration")
                for alt in d_res.get("alertes_et_risques", []):
                    st.error(f"• {alt}")

    with subtab_weather:
        if st.button(f"🔎 Analyser l'Actualité avec {groq_model}", type="primary"):
            sentiments_results = {}
            p_text = st.empty()
            p_bar = st.progress(0)

            for idx, row in df.iterrows():
                tk_sym = row.get('yf_symbol') or row.get('name')
                p_text.text(f"Analyse des actualités de {row['name']} ({tk_sym}) avec {groq_model}...")
                news_items = fetch_ticker_news(tk_sym)
                try:
                    analysis = analyze_news_sentiment(tk_sym, news_items, model=groq_model)
                except Exception:
                    analysis = {"sentiment_global": "Neutre", "score_global": 0.0, "analyse_news": []}
                sentiments_results[tk_sym] = analysis
                p_bar.progress((idx + 1) / len(df))

            p_text.empty()
            p_bar.empty()
            st.session_state["sentiments_results"] = sentiments_results

        if "sentiments_results" in st.session_state:
            s_dict = st.session_state["sentiments_results"]
            score_w, icon_w, label_w = compute_portfolio_weather(df, s_dict)

            st.markdown("#### 🌡️ Météo Synthétique du Portefeuille")
            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                st.metric(
                    label=f"Météo Portefeuille : {label_w}",
                    value=f"{icon_w} {score_w:+.2f}",
                    delta="Score pondéré par le poids des positions"
                )
            with col_m2:
                st.write("**Impact de l'actualité par position :**")
                total_val_weather = df["amount"].sum()
                for _, r in df.iterrows():
                    tk_name = r.get('yf_symbol') or r.get('name')
                    wt = (r["amount"] / total_val_weather) * 100 if total_val_weather > 0 else 0
                    s_score = s_dict.get(tk_name, {}).get("score_global", 0.0)
                    st.caption(f"• **{r['name']}** ({wt:.1f}% du PEA) : Sentiment {s_score:+.2f}")

            st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
            st.markdown("#### 📰 Détail des Actualités par Action")

            stock_names_list = df['name'].tolist()
            selected_t_name = st.selectbox("Consulter les actualités d'une action :", stock_names_list, key="sb_news_stock")
            selected_row = df[df['name'] == selected_t_name].iloc[0]
            tk_key = selected_row.get('yf_symbol') or selected_row.get('name')

            if tk_key in s_dict:
                res_news = s_dict[tk_key]
                st.write(f"**Sentiment Global ({selected_t_name}) :** {res_news.get('sentiment_global', 'Neutre')} ({res_news.get('score_global', 0.0):+.2f})")

                for news_item in res_news.get("analyse_news", []):
                    with st.expander(f"**{news_item.get('titre', 'News')}**"):
                        st.write(f"**Impact :** {news_item.get('resume_impact', '')}")
                        s_val = news_item.get("sentiment", "Neutre")
                        s_score = news_item.get("score", 0.0)
                        if s_val == "Positif":
                            st.success(f"Score : {s_score:+.2f} 🟢")
                        elif s_val == "Négatif":
                            st.error(f"Score : {s_score:+.2f} 🔴")
                        else:
                            st.info(f"Score : {s_score:+.2f} ⚪")

# =============================================================
# ONGLET 3 : SYNTHÈSE IA & ZONEBOURSE (BOURSEAI INTEGRATION)
# =============================================================
with tab_bourseai:
    st.subheader("🤖 Générateur de Synthèses Boursières & Recommandation IA")
    st.caption("Implémentation inspirée du projet open-source **[YR72dpi/BourseAi](https://github.com/YR72dpi/BourseAi)** : Analyse automatique à partir d'un lien ZoneBourse ou d'un actif du PEA.")

    ai_c1, ai_c2 = st.columns([1.5, 1])
    with ai_c1:
        selected_ai_stock = st.selectbox("Choisir un actif de votre portefeuille", options=df['name'].tolist(), key="sb_ai_stock")
    with ai_c2:
        custom_zb_link = st.text_input("Ou coller un lien personnalisé ZoneBourse", placeholder="https://www.zonebourse.fr/cours/action/...")

    btn_analyze = st.button("🚀 Lancer la Synthèse BourseAi", type="primary")

    if btn_analyze or 'last_ai_res' in st.session_state:
        if btn_analyze:
            selected_row = df[df['name'] == selected_ai_stock].iloc[0]
            with st.spinner("Analyse en cours via BourseAi (ZoneBourse + Yahoo Finance + IA)..."):
                ai_res = analyze_stock_with_ai(
                    stock_name=selected_ai_stock,
                    isin=selected_row.get('isin'),
                    yf_symbol=selected_row.get('yf_symbol'),
                    custom_url=custom_zb_link if custom_zb_link else None
                )
                st.session_state['last_ai_res'] = ai_res
        else:
            ai_res = st.session_state['last_ai_res']

        st.markdown("<hr style='border-color: #334155; margin: 20px 0;'>", unsafe_allow_html=True)
        rec_badge = "🟢 Faut-il investir ? OUI (Opportunité)" if ai_res['should_invest'] else "🔴 Faut-il investir ? NON (Prudence)"
        rec_color = "#10b981" if ai_res['should_invest'] else "#ef4444"
        
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #3b82f6; border-radius:16px; padding:24px;">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <h2 style="margin:0; color:#f8fafc; font-size:1.5rem;">Analyse BourseAi : {ai_res['company_name']}</h2>
                    <span style="color:#94a3b8; font-size:0.85rem;">Source : {ai_res['source']}</span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.4rem; font-weight:800; color:{rec_color};">{rec_badge}</div>
                    <span style="font-size:0.95rem; color:#f8fafc;">Score Qualité : <b>{ai_res['score_percent']}/100</b></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.progress(ai_res['score_percent'] / 100)

        col_pros, col_cons = st.columns(2)
        with col_pros:
            st.markdown("#### 🚀 Pourquoi Investir (Points Forts)")
            st.success(ai_res['pros'])
        with col_cons:
            st.markdown("#### ⚠️ Risques & Points Faibles (Pourquoi être Prudent)")
            st.error(ai_res['cons'])

        st.markdown("#### 📋 Synthèse du Profil & Données Clés (Tableau BourseAi)")
        st.info(ai_res['summary'])

        m = ai_res['metrics']
        m_c1, m_c2, m_c3, m_c4, m_c5 = st.columns(5)
        m_c1.metric("Cours Actuel", f"{m['price']:.2f} €")
        m_c2.metric("Ratio PER", f"{m['per']:.1f}x")
        m_c3.metric("Rendement Div.", f"{m['div_yield']:.2f}%")
        m_c4.metric("Objectif Analystes", f"{m['target_price']:.2f} €")
        m_c5.metric("Consensus", m['recommendation'])

        if ai_res.get('target_url'):
            st.markdown(f"🔗 [Consulter la fiche complète sur ZoneBourse]({ai_res['target_url']})")

# =============================================================
# ONGLET 4 : HISTORIQUE & ÉVOLUTION TEMPORELLE (BASE SQLITE)
# =============================================================
with tab_history:
    st.subheader("📈 Évolution du Portefeuille dans le Temps")
    st.caption("Suivi historique automatisé basé sur la base de données SQLite `portfolio.db`.")
    snaps_df = get_snapshots_df()
    
    if snaps_df.empty:
        st.info("Aucun instantané enregistré dans l'historique pour le moment. Téléversez de nouveaux fichiers CSV pour alimenter la base de données.")
    else:
        snaps_df['snapshot_date_dt'] = pd.to_datetime(snaps_df['snapshot_date'])
        snaps_df = snaps_df.sort_values(by='snapshot_date_dt')
        
        fig_hist_val = go.Figure()
        fig_hist_val.add_trace(go.Scatter(
            x=snaps_df['snapshot_date_dt'], y=snaps_df['total_valeur'],
            mode='lines+markers', name="Valorisation Totale (€)",
            line=dict(color="#38bdf8", width=3), fill='tonexty', fillcolor='rgba(56, 189, 248, 0.1)'
        ))
        fig_hist_val.add_trace(go.Scatter(
            x=snaps_df['snapshot_date_dt'], y=snaps_df['cout_investi'],
            mode='lines+markers', name="Capital Investi (PRU Total)",
            line=dict(color="#94a3b8", width=2, dash='dash')
        ))
        fig_hist_val.update_layout(
            paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
            margin=dict(t=20, l=10, r=10, b=20), height=380,
            xaxis=dict(title="Date de l'instantané", gridcolor="#334155"), yaxis=dict(title="Montant (€)", gridcolor="#334155"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_hist_val, use_container_width=True)

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("#### 💶 Plus-Value Latente (€)")
            fig_hist_pv = px.line(snaps_df, x='snapshot_date_dt', y='plus_value', markers=True)
            fig_hist_pv.update_traces(line_color="#10b981", line_width=3)
            fig_hist_pv.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=10, b=10), height=280, xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"))
            st.plotly_chart(fig_hist_pv, use_container_width=True)

        with col_h2:
            st.markdown("#### 📊 Performance Globale (%)")
            fig_hist_pct = px.line(snaps_df, x='snapshot_date_dt', y='plus_value_pct', markers=True)
            fig_hist_pct.update_traces(line_color="#a78bfa", line_width=3)
            fig_hist_pct.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=10, b=10), height=280, xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"))
            st.plotly_chart(fig_hist_pct, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🗄️ Liste des Instantanés enregistrés en Base")
        table_snaps = snaps_df[['id', 'snapshot_date', 'total_valeur', 'cout_investi', 'plus_value', 'plus_value_pct', 'source_filename']].copy()
        table_snaps.columns = ['ID', 'Date Snapshot', 'Valorisation (€)', 'Investi (€)', 'Plus-Value (€)', 'Perf (%)', 'Fichier Source']
        st.dataframe(table_snaps.style.format({'Valorisation (€)': '{:,.2f} €', 'Investi (€)': '{:,.2f} €', 'Plus-Value (€)': '{:+,.2f} €', 'Perf (%)': '{:+.2f} %'}), use_container_width=True)

# =============================================================
# ONGLET 5 : SECTEURS & DIVIDENDES
# =============================================================
with tab_sectors:
    st.subheader("🏢 Répartition Sectorielle & Revenus Passifs")
    sec_col1, sec_col2 = st.columns([1.5, 1])
    with sec_col1:
        st.markdown("#### 🌐 Allocation par Secteur d'Activité")
        sec_agg = df.groupby('sector')['amount'].sum().reset_index()
        fig_sec = px.pie(sec_agg, names='sector', values='amount', hole=0.45, color_discrete_sequence=px.colors.qualitative.Dark24)
        fig_sec.update_layout(paper_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=10, b=10), height=360)
        st.plotly_chart(fig_sec, use_container_width=True)

    with sec_col2:
        st.markdown("#### 💰 Estimation des Dividendes Annuels par Ligne")
        div_df = df[df['annual_div_euro'] > 0].sort_values(by='annual_div_euro', ascending=False)
        if not div_df.empty:
            fig_div_bar = px.bar(
                div_df, x='name', y='annual_div_euro',
                text=div_df['annual_div_euro'].apply(lambda x: f"{x:,.1f} €/an"),
                color='annual_div_euro', color_continuous_scale=['#38bdf8', '#10b981']
            )
            fig_div_bar.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=10, b=30), height=360, xaxis=dict(title=None, tickangle=-30, gridcolor="#334155"), yaxis=dict(title="Dividende estimé (€/an)", gridcolor="#334155"), coloraxis_showscale=False)
            st.plotly_chart(fig_div_bar, use_container_width=True)

# =============================================================
# ONGLET 6 : FICHE TITRE (INSPECTEUR D'ACTIF)
# =============================================================
with tab_inspector:
    st.subheader("🔍 Inspecteur d'Actif / Fiche Entreprise")
    selected_stock_name = st.selectbox("Choisir une position en portefeuille", options=df['name'].tolist())
    stock_row = df[df['name'] == selected_stock_name].iloc[0]
    
    inspect_c1, inspect_c2 = st.columns([1, 2])
    with inspect_c1:
        st.markdown(f"""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:14px; padding:20px;">
            <div style="display:flex; align-items:center; gap:14px; margin-bottom:15px;">
                <img src="{stock_row['logo_url']}" style="width:48px; height:48px; border-radius:50%;" />
                <div>
                    <h3 style="margin:0; color:#f8fafc; font-size:1.25rem;">{stock_row['name']}</h3>
                    <span style="color:#94a3b8; font-size:0.85rem;">ISIN: {stock_row['isin']} • {stock_row['type']}</span>
                </div>
            </div>
            <hr style="border-color:#334155; margin:12px 0;" />
            <div style="font-size:0.9rem; color:#cbd5e1; line-height:1.8;">
                • <b>Quantité :</b> {stock_row['quantity']:,.2f} titres<br>
                • <b>PRU :</b> {stock_row['buyingPrice']:,.2f} €<br>
                • <b>Dernier Cours :</b> {stock_row['lastPrice']:,.2f} €<br>
                • <b>Valorisation :</b> <span style="color:#38bdf8; font-weight:700;">{stock_row['amount']:,.2f} €</span><br>
                • <b>Poids :</b> {stock_row['weight']:.2f}%<br>
                • <b>Plus/Moins-value :</b> <span style="color:{'#10b981' if stock_row['amountVariation']>=0 else '#ef4444'}; font-weight:700;">{'+' if stock_row['amountVariation']>=0 else ''}{stock_row['amountVariation']:,.2f} € ({'+' if stock_row['variation']>=0 else ''}{stock_row['variation']:.2f}%)</span><br>
                • <b>Secteur :</b> {stock_row['sector']}<br>
                • <b>Dividende estimé :</b> {stock_row['div_yield']:.2f}% (~{stock_row['annual_div_euro']:,.1f} €/an)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with inspect_c2:
        yf_sym = stock_row['yf_symbol']
        st.markdown(f"#### 📉 Graphique Boursier (1 An) - `{yf_sym if yf_sym else stock_row['name']}`")
        if yf_sym:
            try:
                hist_data = yf.Ticker(yf_sym).history(period="1y")
                if not hist_data.empty:
                    fig_stock_hist = px.line(hist_data, x=hist_data.index, y='Close', labels={'Close': 'Cours (€)', 'Date': 'Date'})
                    fig_stock_hist.update_traces(line_color="#38bdf8", line_width=2)
                    fig_stock_hist.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=10, b=20), height=350, xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"))
                    st.plotly_chart(fig_stock_hist, use_container_width=True)
            except Exception:
                st.info("Historique boursier indisponible.")

# =============================================================
# ONGLET 7 : ANALYSES VISUELLES & PERFORMANCE
# =============================================================
with tab_charts:
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.subheader("💶 Contribution aux Gains / Pertes (€)")
        df_sorted_gains = df.sort_values(by='amountVariation', ascending=True)
        colors_pv = ['#10b981' if v >= 0 else '#ef4444' for v in df_sorted_gains['amountVariation']]
        fig_bars = go.Figure(go.Bar(x=df_sorted_gains['amountVariation'], y=df_sorted_gains['name'], orientation='h', marker_color=colors_pv, text=df_sorted_gains['amountVariation'].apply(lambda x: f"{'+' if x>0 else ''}{x:,.2f} €"), textposition='outside'))
        fig_bars.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=60, b=10), height=420, xaxis=dict(title="Plus/Moins-value (€)", gridcolor="#334155"), yaxis=dict(title=None))
        st.plotly_chart(fig_bars, use_container_width=True)

    with col_a2:
        st.subheader("🎯 Comparatif PRU vs Dernier Cours (€)")
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(x=df['name'], y=df['buyingPrice'], name="PRU (Prix d'achat)", marker_color="#64748b"))
        fig_compare.add_trace(go.Bar(x=df['name'], y=df['lastPrice'], name="Dernier Cours", marker_color="#38bdf8"))
        fig_compare.update_layout(barmode='group', paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=10, l=10, r=10, b=50), height=420, xaxis=dict(tickangle=-45, gridcolor="#334155"), yaxis=dict(title="Prix (€)", gridcolor="#334155"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_compare, use_container_width=True)

    st.subheader("⚖️ Matrice Poids vs Performance")
    fig_matrix = px.scatter(df, x='variation', y='weight', size='amount', color='variation', hover_name='name', color_continuous_scale=['#ef4444', '#f1f5f9', '#10b981'], color_continuous_midpoint=0, text='name')
    fig_matrix.update_traces(textposition='top center')
    fig_matrix.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=20, l=10, r=10, b=20), height=450, xaxis=dict(title="Performance globale (%)", gridcolor="#334155"), yaxis=dict(title="Poids (%)", gridcolor="#334155"))
    st.plotly_chart(fig_matrix, use_container_width=True)

# =============================================================
# ONGLET 8 : TABLEAU DÉTAILLÉ DES POSITIONS (AVEC LOGOS)
# =============================================================
with tab_positions:
    st.subheader("📋 Liste des Positions Détaillées")
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1: search_kw = st.text_input("🔍 Recherche rapide", placeholder="Ex: BNP, LVMH, FR00...")
    with f2: type_filter = st.selectbox("Type d'instrument", ["Tous", "Action", "ETF"])
    with f3: perf_filter = st.selectbox("Filtre performance", ["Toutes", "En Plus-Value", "En Moins-Value"])

    filtered = df.copy()
    if search_kw:
        mask = filtered['name'].str.contains(search_kw, case=False, na=False) | filtered['isin'].str.contains(search_kw, case=False, na=False)
        filtered = filtered[mask]
    if type_filter != "Tous": filtered = filtered[filtered['type'] == type_filter]
    if perf_filter == "En Plus-Value": filtered = filtered[filtered['amountVariation'] >= 0]
    elif perf_filter == "En Moins-Value": filtered = filtered[filtered['amountVariation'] < 0]

    cols_to_show = ['logo_url', 'name', 'isin', 'sector', 'quantity', 'buyingPrice', 'lastPrice', 'amount', 'weight', 'amountVariation', 'variation', 'intradayVariation']
    st.data_editor(
        filtered[cols_to_show],
        column_config={
            "logo_url": st.column_config.ImageColumn("Logo"),
            "name": st.column_config.TextColumn("Titre"),
            "isin": st.column_config.TextColumn("Code ISIN"),
            "sector": st.column_config.TextColumn("Secteur"),
            "quantity": st.column_config.NumberColumn("Quantité", format="%.2f"),
            "buyingPrice": st.column_config.NumberColumn("PRU d'achat", format="%.2f €"),
            "lastPrice": st.column_config.NumberColumn("Dernier cours", format="%.2f €"),
            "amount": st.column_config.NumberColumn("Valorisation", format="%.2f €"),
            "weight": st.column_config.ProgressColumn("Poids (%)", format="%.1f%%", min_value=0, max_value=100),
            "amountVariation": st.column_config.NumberColumn("+/- Value (€)", format="%+,.2f €"),
            "variation": st.column_config.ProgressColumn("+/- Value (%)", format="%+.2f%%", min_value=-100, max_value=100),
            "intradayVariation": st.column_config.NumberColumn("Var. Jour (%)", format="%+.2f%%")
        },
        hide_index=True, use_container_width=True, height=450
    )

    csv_bytes = filtered.to_csv(index=False, sep=';').encode('utf-8')
    st.download_button("📥 Télécharger les positions en CSV", data=csv_bytes, file_name=f"export_portefeuille_pea_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

# =============================================================
# ONGLET 9 : FISCALITÉ PEA & SIMULATEUR DE PROJECTION
# =============================================================
with tab_fiscal:
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        st.subheader("⚖️ Fiscalité Spécifique au PEA")
        st.markdown("""
        Le **Plan d'Épargne en Actions (PEA)** permet d'optimiser la fiscalité de ses investissements :
        - **Avant 5 ans** : Tout retrait entraîne la clôture du plan et Flat Tax à 30%.
        - **Après 5 ans** : Exonération totale d'IR (0%) et 17,2% de Prélèvements Sociaux sur les gains uniquement.
        """)
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.8); border: 1px solid #3b82f6; border-radius: 12px; padding: 18px; margin-top: 15px;">
            <h4 style="margin-top:0; color:#38bdf8;">📊 Bilan Fiscal de vos Plus-Values</h4>
            <table style="width:100%; border-collapse:collapse; font-size:0.92rem;">
                <tr><td style="padding:6px 0; color:#94a3b8;">Total Plus-Value Latente :</td><td style="text-align:right; font-weight:700; color:{'#10b981' if plus_value_latente_titres>=0 else '#ef4444'};">{plus_value_latente_titres:,.2f} €</td></tr>
                <tr><td style="padding:6px 0; color:#94a3b8;">Prélèvements Sociaux estimés (17.2%) :</td><td style="text-align:right; font-weight:700; color:#ef4444;">-{prelevements_sociaux:,.2f} €</td></tr>
                <tr style="border-top: 1px solid #334155;"><td style="padding:8px 0; font-weight:700; color:#f8fafc;">Gain Réel Net d'Impôt :</td><td style="text-align:right; font-weight:800; color:#10b981; font-size:1.05rem;">+{plus_value_latente_titres - prelevements_sociaux:,.2f} €</td></tr>
                <tr><td style="padding:6px 0; font-weight:700; color:#f8fafc;">Capital Retirable Net (Titres + Cash) :</td><td style="text-align:right; font-weight:800; color:#38bdf8; font-size:1.05rem;">{valeur_nette_apres_ps:,.2f} €</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("#### 🎯 Plafond des versements (150 000 €)")
        plafond = 150000.0
        pct_plafond = min(100.0, (cout_total_investi / plafond) * 100)
        st.progress(pct_plafond / 100)
        st.caption(f"Capacité de versement restante : **{plafond - cout_total_investi:,.2f} €** ({pct_plafond:.1f}% du plafond utilisé)")

    with f_col2:
        st.subheader("🚀 Simulateur d'Intérêts Composés")
        horizon_ans = st.slider("Horizon de placement (Années)", min_value=1, max_value=30, value=10)
        epargne_mensuelle = st.number_input("Versement mensuel supplémentaire (€)", min_value=0.0, value=250.0, step=50.0)
        rendement_annuel = st.slider("Rendement annuel moyen espéré (%)", min_value=1.0, max_value=15.0, value=7.5, step=0.5)
        
        r_mensuel = (1 + rendement_annuel / 100) ** (1/12) - 1
        nb_mois = horizon_ans * 12
        annees_list, val_list, versements_list = [0], [valeur_totale_portefeuille], [cout_total_investi]
        curr_val, curr_verse = valeur_totale_portefeuille, cout_total_investi
        
        for m in range(1, nb_mois + 1):
            curr_val = curr_val * (1 + r_mensuel) + epargne_mensuelle
            curr_verse += epargne_mensuelle
            if m % 12 == 0:
                annees_list.append(m // 12)
                val_list.append(curr_val)
                versements_list.append(curr_verse)
                
        fig_compound = go.Figure()
        fig_compound.add_trace(go.Scatter(x=annees_list, y=val_list, mode='lines+markers', name="Valeur Portefeuille Projetée", line=dict(color="#10b981", width=3)))
        fig_compound.add_trace(go.Scatter(x=annees_list, y=versements_list, mode='lines', name="Capital Total Versé", line=dict(color="#94a3b8", dash='dash')))
        fig_compound.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font=dict(color="#f8fafc", family="Plus Jakarta Sans"), margin=dict(t=20, l=10, r=10, b=20), height=320, xaxis=dict(title="Années", gridcolor="#334155"), yaxis=dict(title="Montant (€)", gridcolor="#334155"), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_compound, use_container_width=True)
        gain_projeté = val_list[-1] - versements_list[-1]
        st.success(f"🎯 Dans **{horizon_ans} ans**, votre portefeuille atteindrait **{val_list[-1]:,.2f} €**, dont **{gain_projeté:,.2f} €** d'intérêts !")

