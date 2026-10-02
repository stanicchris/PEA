import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import os
import re
from urllib.parse import quote
import yfinance as yf

# Module base de données Supabase
from database import (
    get_supabase_client, save_snapshot, get_snapshots_df, 
    get_positions_history_df, delete_snapshot, 
    is_snapshot_saved, extract_date_from_filename,
    get_latest_portfolio, update_snapshot_data,
    get_now_paris, get_user_cash, update_user_cash
)

# Module BourseAi (ZoneBourse + Synthèse)
from bourse_ai import analyze_stock_with_ai, ZONEBOURSE_URLS

# Module AI Advisor (Groq & News Sentiment)
from ai_advisor import (
    analyze_portfolio_global, fetch_ticker_news, 
    analyze_news_sentiment, compute_portfolio_weather,
    get_available_groq_models, DEFAULT_MODEL
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
# AUTHENTIFICATION SUPABASE (NOM DE COMPTE + MOT DE PASSE)
# -------------------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

supabase = get_supabase_client()

def to_synthetic_email(uname: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\.]', '', uname.strip().lower())
    return f"{cleaned}@pea.local"

if not st.session_state["user_id"]:
    col_l1, col_l2, col_l3 = st.columns([1, 1.8, 1])
    with col_l2:
        st.markdown("""
        <div style="background:#1e293b; border:1px solid #334155; border-radius:14px; padding:25px; margin-top:40px; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
            <h2 style="margin:0 0 10px 0; color:#f8fafc; font-size:1.6rem; font-weight:800;">🔐 Connexion PEA Tracker</h2>
            <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:20px;">Accédez à votre portefeuille en toute sécurité.</p>
        </div>
        """, unsafe_allow_html=True)
        
        username = st.text_input("👤 Nom de compte (identifiant)", placeholder="Ex: chris, portfolio1...", key="input_username")
        password = st.text_input("🔑 Mot de passe", type="password", key="input_pwd")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Se connecter", type="primary", width="stretch"):
                if not username.strip():
                    st.warning("Veuillez saisir votre nom de compte.")
                elif not password:
                    st.warning("Veuillez saisir votre mot de passe.")
                else:
                    try:
                        email_alias = to_synthetic_email(username)
                        res = supabase.auth.sign_in_with_password({"email": email_alias, "password": password})
                        if res.user:
                            st.session_state["user_id"] = res.user.id
                            st.session_state["username"] = username.strip()
                            st.rerun()
                        else:
                            st.error("Identifiants invalides.")
                    except Exception as e:
                        st.error(f"Erreur de connexion : {e}")
        with c2:
            if st.button("Créer ce compte", width="stretch"):
                if not username.strip():
                    st.warning("Veuillez saisir un nom de compte.")
                elif len(password) < 6:
                    st.warning("Le mot de passe doit comporter au moins 6 caractères.")
                else:
                    try:
                        email_alias = to_synthetic_email(username)
                        res = supabase.auth.sign_up({"email": email_alias, "password": password})
                        if res.user:
                            st.session_state["user_id"] = res.user.id
                            st.session_state["username"] = username.strip()
                            st.success(f"Compte '{username.strip()}' créé avec succès !")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la création : {e}")
    st.stop()

st.sidebar.markdown(f"👤 Connecté : **{st.session_state.get('username', 'Mon Compte')}**")
if st.sidebar.button("🚪 Déconnexion"):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    if "pea_cash" in st.session_state:
        del st.session_state["pea_cash"]
    if "pea_cash_input" in st.session_state:
        del st.session_state["pea_cash_input"]
    st.rerun()


# -------------------------------------------------------------
# THÈME ET CSS SUR MESURE (FINTECH DARK)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Masquer le menu hamburger, la barre Streamlit et le footer pour un effet 100% SaaS */
    #MainMenu, header, footer {
        visibility: hidden !important;
        height: 0 !important;
    }
    
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 4rem !important;
        max-width: 1280px !important;
    }
    
    /* Fond Luxury Dark OLED */
    .stApp {
        background-color: #06080d !important;
        background-image: 
            radial-gradient(at 15% 0%, rgba(14, 165, 233, 0.08) 0px, transparent 55%),
            radial-gradient(at 85% 15%, rgba(99, 102, 241, 0.06) 0px, transparent 55%) !important;
        color: #f8fafc !important;
    }
    
    /* Barre latérale */
    [data-testid="stSidebar"] {
        background-color: #090c12 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Hero Header */
    .portfolio-hero {
        background: linear-gradient(180deg, rgba(17, 23, 34, 0.8) 0%, rgba(10, 14, 22, 0.95) 100%);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 24px;
        padding: 28px 34px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        flex-wrap: wrap;
        gap: 20px;
    }
    .portfolio-hero-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .portfolio-hero-value {
        font-size: 2.9rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: #ffffff;
        line-height: 1.05;
    }
    
    /* Badges & Pills */
    .pill-blue {
        display: inline-flex;
        align-items: center;
        background: rgba(14, 165, 233, 0.14);
        color: #38bdf8;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(56, 189, 248, 0.25);
    }
    .pill-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(52, 211, 153, 0.25);
    }
    .pulsing-dot {
        width: 7px;
        height: 7px;
        background-color: #10b981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10b981;
        animation: pulse-live 2s infinite;
    }
    @keyframes pulse-live {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.35; transform: scale(0.85); }
    }
    .pill-green {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .pill-red {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        background: rgba(244, 63, 94, 0.12);
        color: #f43f5e;
        font-size: 0.82rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(244, 63, 94, 0.25);
    }
    .pill-neutral {
        display: inline-flex;
        align-items: center;
        background: rgba(148, 163, 184, 0.08);
        color: #94a3b8;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        border: 1px solid rgba(148, 163, 184, 0.15);
    }

    /* Cartes KPIs */
    [data-testid="stMetric"], .kpi-card {
        background: linear-gradient(165deg, rgba(18, 24, 35, 0.75) 0%, rgba(11, 15, 23, 0.85) 100%) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        padding: 20px 22px !important;
        box-shadow: 0 10px 25px -10px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.06) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        min-height: 125px;
    }
    [data-testid="stMetric"]:hover, .kpi-card:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(56, 189, 248, 0.35) !important;
        box-shadow: 0 16px 35px -10px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.1) !important;
    }
    
    .kpi-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: #f8fafc;
        margin-bottom: 6px;
    }

    /* Onglets du tableau de bord (Segmented Pills Bar) */
    [data-baseweb="tab-list"] {
        background: rgba(11, 15, 23, 0.8) !important;
        padding: 6px !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        gap: 6px !important;
        margin-bottom: 24px !important;
    }
    [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 10px 22px !important;
        color: #64748b !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    [data-baseweb="tab"]:hover {
        color: #cbd5e1 !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background: #171f2d !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(56, 189, 248, 0.25) !important;
    }

    /* Boutons Modernes */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
        padding: 10px 22px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 22px rgba(14, 165, 233, 0.5) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(17, 24, 39, 0.8) !important;
        color: #f1f5f9 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(30, 41, 59, 0.9) !important;
        border-color: #38bdf8 !important;
        transform: translateY(-1px) !important;
    }

    /* Ranking Cards (Top Gainers / Flops) */
    .ranking-card {
        background: linear-gradient(145deg, #10141d 0%, #0b0e14 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 18px;
        padding: 14px 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }
    .ranking-card:hover {
        background: #141a26;
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateX(4px);
    }

    .company-logo {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        object-fit: cover;
        background-color: #171f2d;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 3px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }

    /* Optimisations Mobiles */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        .portfolio-hero {
            padding: 22px 20px !important;
            flex-direction: column !important;
            align-items: flex-start !important;
            gap: 16px !important;
        }
        .portfolio-hero-value {
            font-size: 2.2rem !important;
        }
        .portfolio-hero > div:last-child {
            align-items: flex-start !important;
            width: 100% !important;
            border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
            padding-top: 14px !important;
        }
        [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 10px !important;
        }
        [data-testid="stHorizontalBlock"] > [data-testid="column"] {
            flex: 1 1 calc(50% - 10px) !important;
            min-width: 140px !important;
        }
        .kpi-value {
            font-size: 1.35rem !important;
        }
        .kpi-label {
            font-size: 0.68rem !important;
        }
        [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            scrollbar-width: none !important;
        }
        [data-baseweb="tab"] {
            padding: 8px 14px !important;
            font-size: 0.82rem !important;
            white-space: nowrap !important;
        }
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
# ACTUALISATION DES COURS EN DIRECT (MIS EN CACHE DYNAMIQUE)
# -------------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_market_prices(symbols_tuple):
    """Récupère les derniers cours de marché en direct (cache TTL 60s)."""
    if not symbols_tuple:
        return {}
    results = {}
    try:
        tickers = yf.Tickers(' '.join(symbols_tuple))
        for sym in symbols_tuple:
            if sym in tickers.tickers:
                try:
                    info = tickers.tickers[sym].fast_info
                    live_p = info.last_price
                    prev_close = info.previous_close
                    if live_p and live_p > 0:
                        results[sym] = {
                            'last_price': float(live_p),
                            'prev_close': float(prev_close) if prev_close else float(live_p)
                        }
                except Exception:
                    pass
    except Exception as e:
        print(f"Erreur marché en direct : {e}")
    return results

def apply_live_quotes(df, force_refresh=False):
    """Applique les cours en direct au DataFrame de portefeuille sans altérer les données de base."""
    updated_df = df.copy()
    symbols = tuple(sorted([s for s in updated_df['yf_symbol'].dropna().unique() if s]))
    if not symbols:
        return updated_df, "Aucun symbole configuré."
        
    if force_refresh:
        fetch_market_prices.clear()
        
    quotes = fetch_market_prices(symbols)
    live_count = 0
    for idx, row in updated_df.iterrows():
        sym = row.get('yf_symbol')
        if sym and sym in quotes:
            live_p = quotes[sym]['last_price']
            prev_close = quotes[sym]['prev_close']
            updated_df.at[idx, 'lastPrice'] = live_p
            updated_df.at[idx, 'amount'] = row['quantity'] * live_p
            updated_df.at[idx, 'amountVariation'] = updated_df.at[idx, 'amount'] - row['totalCost']
            updated_df.at[idx, 'variation'] = (updated_df.at[idx, 'amountVariation'] / row['totalCost'] * 100) if row['totalCost'] > 0 else 0.0
            if prev_close and prev_close > 0:
                intra_pct = (live_p - prev_close) / prev_close * 100
                updated_df.at[idx, 'intradayVariation'] = intra_pct
                updated_df.at[idx, 'intradayAmount'] = updated_df.at[idx, 'amount'] - (updated_df.at[idx, 'amount'] / (1 + intra_pct / 100))
            live_count += 1
            
    total_val = updated_df['amount'].sum()
    updated_df['weight'] = (updated_df['amount'] / total_val * 100) if total_val > 0 else 0.0
    return updated_df, f"⚡ {live_count} cours actualisés en direct !"

# -------------------------------------------------------------
# SIDEBAR ET PARAMÈTRES
# -------------------------------------------------------------
st.sidebar.markdown("## 📊 Source de Données")
uploaded_file = st.sidebar.file_uploader("Importer un nouvel export CSV", type=["csv"], help="Importez un nouveau CSV pour enregistrer ou mettre à jour votre portefeuille en base.")

# -------------------------------------------------------------
# CHARGEMENT DU PORTEFEUILLE (BASE DE DONNÉES EN PRIORITÉ)
# -------------------------------------------------------------
# Récupération persistante des liquidités depuis Supabase
if "pea_cash" not in st.session_state:
    st.session_state["pea_cash"] = get_user_cash()

current_cash = float(st.session_state["pea_cash"])
df = None
source_label = ""

# Cas 1 : L'utilisateur a uploadé un nouveau fichier CSV
if uploaded_file is not None:
    raw_bytes = uploaded_file.getvalue()
    source_name = uploaded_file.name
    parsed_df = parse_portfolio_csv(raw_bytes, source_name)
    if parsed_df is not None and not parsed_df.empty:
        df = parsed_df
        source_label = f"Fichier importé : `{uploaded_file.name}`"
        st.sidebar.success(source_label)
        
        # Enregistrement automatique dans Supabase avec les liquidités actuelles de l'utilisateur
        snapshot_date_str = extract_date_from_filename(source_name)
        if not is_snapshot_saved(snapshot_date_str, source_name):
            saved_id = save_snapshot(df, cash=current_cash, source_filename=source_name, custom_date=snapshot_date_str)
            st.session_state["current_snapshot_id"] = saved_id
            st.toast(f"✅ Instantané du {snapshot_date_str} sauvegardé dans Supabase !", icon="💾")
        else:
            st.session_state["current_snapshot_id"] = is_snapshot_saved(snapshot_date_str, source_name)

# Cas 2 : Aucun fichier uploadé dans la session -> chargement depuis Supabase
if df is None:
    db_df, saved_cash, latest_snap = get_latest_portfolio()
    if db_df is not None and not db_df.empty:
        df = db_df
        # Si pea_cash était à 0 et qu'un solde positif existe dans le snapshot
        if current_cash == 0.0 and saved_cash > 0:
            current_cash = saved_cash
            st.session_state["pea_cash"] = saved_cash
            update_user_cash(saved_cash)
        if latest_snap:
            st.session_state["current_snapshot_id"] = latest_snap['id']
            
        # Reconstituer les métadonnées (logos, secteurs, yf_symbols) si nécessaire
        if 'logo_url' not in df.columns or df['logo_url'].isna().all():
            df['logo_url'] = df.apply(lambda r: resolve_logo_url(r.get('isin'), r.get('name')), axis=1)
        if 'sector' not in df.columns or df['sector'].isna().all():
            df['sector'] = df.apply(lambda r: resolve_sector(r.get('isin'), r.get('name')), axis=1)
        if 'div_yield' not in df.columns or df['div_yield'].isna().all():
            df['div_yield'] = df.apply(lambda r: resolve_div_yield(r.get('isin'), r.get('name')), axis=1)
        if 'annual_div_euro' not in df.columns or df['annual_div_euro'].isna().all():
            df['annual_div_euro'] = df['amount'] * (df['div_yield'] / 100)
        if 'yf_symbol' not in df.columns or df['yf_symbol'].isna().all():
            df['yf_symbol'] = df.apply(lambda r: resolve_yf_symbol(r.get('isin'), r.get('name')), axis=1)
        
        snap_date_str = latest_snap.get('snapshot_date', '') if latest_snap else ''
        source_label = f"Base Supabase (Instantané du {snap_date_str})"
        st.sidebar.info(f"📦 {source_label}")

# Cas 3 : Ni fichier ni BDD -> invite à l'import
if df is None or df.empty:
    st.info("👋 **Bienvenue sur votre PEA Tracker !**\n\nVotre compte ne contient encore aucun portefeuille en base de données.\n\nVeuillez importer votre premier fichier CSV (ex: export Boursorama / BoursoBank) dans la barre latérale pour initialiser vos positions.")
    st.stop()

# -------------------------------------------------------------
# COMPTE ESPÈCES PEA (SAUVEGARDE AUTOMATIQUE EN BDD)
# -------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("## 💰 Compte Espèces PEA")

def on_cash_change():
    new_val = float(st.session_state.get("pea_cash_input", 0.0))
    st.session_state["pea_cash"] = new_val
    update_user_cash(new_val)
    st.toast(f"💾 Liquidités enregistrées en base : {new_val:,.2f} €", icon="💰")

# Initialiser le champ avec la valeur persistée
if "pea_cash_input" not in st.session_state:
    st.session_state["pea_cash_input"] = float(st.session_state.get("pea_cash", 0.0))

cash = st.sidebar.number_input(
    "Liquidités disponibles (€)",
    min_value=0.0,
    step=100.0,
    key="pea_cash_input",
    on_change=on_cash_change,
    help="Modifiez ce montant à tout moment : il est immédiatement sauvegardé dans votre base de données Supabase."
)
cash = float(st.session_state.get("pea_cash", cash))

st.sidebar.markdown("---")
st.sidebar.markdown("## 🧠 Configuration IA (Groq)")

# Modèle Groq
available_groq_models = get_available_groq_models()
groq_model = st.sidebar.selectbox(
    "Modèle IA (Groq)",
    options=available_groq_models,
    index=0,
    help="Sélectionnez le modèle Groq pour l'analyse financière (ex: Llama 3.3 70B, Llama 3.1 8B, DeepSeek R1)."
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🤖 Configuration BourseAi")

st.sidebar.markdown("---")
st.sidebar.markdown("## 💾 Base de Données Supabase")
db_snapshots = get_snapshots_df()
nb_snaps_db = len(db_snapshots)
st.sidebar.caption(f"📦 Historique actuel : **{nb_snaps_db} instantané(s)**")

# Auto-update ou Bouton Live
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔴 Cours du Marché en Direct")
force_refresh = st.sidebar.button("🔄 Rafraîchir les cours en direct")
df, msg = apply_live_quotes(df, force_refresh=force_refresh)
if force_refresh:
    # Créer automatiquement un NOUVEL instantané dans Supabase à l'heure locale française (Europe/Paris)
    now_dt = get_now_paris()
    now_iso = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    now_label = f"Actualisation en direct ({now_dt.strftime('%d/%m/%Y %H:%M:%S')})"
    new_snap_id = save_snapshot(df, cash=cash, source_filename=now_label, custom_date=now_iso)
    update_user_cash(cash)
    st.session_state["current_snapshot_id"] = new_snap_id
    st.toast(f"✅ Nouvel instantané du {now_dt.strftime('%d/%m à %H:%M:%S')} créé dans l'historique !", icon="📈")
    # Forcer la réévaluation immédiate pour que l'onglet Historique trace le nouveau point
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
<div class="portfolio-hero">
    <div>
        <div style="display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:10px;">
            <h1 style="margin:0; font-size: 2.1rem; font-weight:800; color:#ffffff; letter-spacing:-0.03em;">
                Mon Portefeuille PEA
            </h1>
            <span class="pill-blue">PEA ACTIF</span>
            <span class="pill-live"><span class="pulsing-dot"></span> MARCHÉ EN DIRECT</span>
        </div>
        <p style="margin:0; color:#94a3b8; font-size:0.92rem; font-weight:500;">
            Suivi de portefeuille en temps réel • Moteur IA <b style="color:#38bdf8;">Groq ({groq_model})</b> • {nb_positions} positions en portefeuille
        </p>
    </div>
    <div style="text-align:right;">
        <div class="portfolio-hero-label">Patrimoine Total (avec liquidités)</div>
        <div class="portfolio-hero-value">{valeur_totale_portefeuille:,.2f} €</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Cartes KPIs
kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Valeur Titres</div>
            <div class="kpi-value">{valeur_titres:,.2f} €</div>
        </div>
        <div>
            <span class="pill-neutral">+{cash:,.2f} € liquidités</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Total Investi</div>
            <div class="kpi-value">{cout_total_investi:,.2f} €</div>
        </div>
        <div>
            <span class="pill-neutral">Prix de Revient (PRU)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    sign_pv = "+" if plus_value_latente_titres >= 0 else ""
    color_pv = "#10b981" if plus_value_latente_titres >= 0 else "#f43f5e"
    badge_pv_pill = "pill-green" if plus_value_latente_titres >= 0 else "pill-red"
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Plus-Value Latente</div>
            <div class="kpi-value" style="color: {color_pv};">{sign_pv}{plus_value_latente_titres:,.2f} €</div>
        </div>
        <div>
            <span class="{badge_pv_pill}">{sign_pv}{perf_globale_pct:.2f} %</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    sign_intra = "+" if intraday_euro_total >= 0 else ""
    color_intra = "#10b981" if intraday_euro_total >= 0 else "#f43f5e"
    badge_intra_pill = "pill-green" if intraday_euro_total >= 0 else "pill-red"
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Variation du Jour</div>
            <div class="kpi-value" style="color: {color_intra};">{sign_intra}{intraday_euro_total:,.2f} €</div>
        </div>
        <div>
            <span class="{badge_intra_pill}">{sign_intra}{intraday_pct_total:.2f} %</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Dividendes Est.</div>
            <div class="kpi-value" style="color: #38bdf8;">~ {total_dividendes_annuels:,.0f} €<span style="font-size:1rem; font-weight:600; color:#94a3b8;">/an</span></div>
        </div>
        <div>
            <span class="pill-neutral">Rendement : {rendement_div_moyen:.2f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# ONGLETS DU DASHBOARD
# -------------------------------------------------------------
tab_overview, tab_positions, tab_analytics, tab_history, tab_ai_tax = st.tabs([
    "Vue d'ensemble",
    "Positions & Titres",
    "Analyses & Performance",
    "Historique",
    "Intelligence IA & Fiscalité"
])

# =============================================================
# ONGLET 1 : VUE D'ENSEMBLE
# =============================================================
with tab_overview:
    c1, c2 = st.columns([1.6, 1])
    with c1:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Carte thermique des positions (Treemap)</h3>", unsafe_allow_html=True)
        fig_tree = px.treemap(
            df,
            path=[px.Constant("Portefeuille PEA"), 'type', 'name'],
            values='amount', color='variation',
            color_continuous_scale=[[0.0, '#f43f5e'], [0.48, '#881337'], [0.50, '#1e293b'], [0.52, '#064e3b'], [1.0, '#10b981']],
            color_continuous_midpoint=0,
            hover_data={'amount': ':.2f €', 'variation': ':.2f %', 'amountVariation': ':.2f €', 'lastPrice': ':.2f €'}
        )
        fig_tree.update_layout(
            margin=dict(t=8, l=8, r=8, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
            height=370
        )
        st.plotly_chart(fig_tree, width="stretch")

    with c2:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Allocation du Portefeuille</h3>", unsafe_allow_html=True)
        fig_donut = px.pie(
            df, names='name', values='amount', hole=0.66,
            color_discrete_sequence=['#0ea5e9', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6', '#14b8a6', '#f43f5e', '#a855f7', '#38bdf8']
        )
        fig_donut.update_traces(
            textposition='inside', textinfo='percent',
            marker=dict(line=dict(color='#06080d', width=2))
        )
        fig_donut.update_layout(
            margin=dict(t=8, l=8, r=8, b=8),
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5, font=dict(size=10, color="#94a3b8")),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
            height=370,
            annotations=[dict(
                text=f"<span style='font-size:10px; color:#64748b; text-transform:uppercase; letter-spacing:0.08em; font-weight:700;'>TOTAL ACTIFS</span><br><b style='font-size:18px; color:#ffffff;'>{valeur_titres:,.0f} €</b>",
                x=0.5, y=0.5, showarrow=False
            )]
        )
        st.plotly_chart(fig_donut, width="stretch")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    c_gainers, c_losers, c_type = st.columns([1.2, 1.2, 1])
    sorted_pv = df.sort_values(by='variation', ascending=False)
    
    with c_gainers:
        st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#10b981; margin-bottom:12px; letter-spacing:0.04em; text-transform:uppercase;'>Top Plus-Values</h4>", unsafe_allow_html=True)
        for _, row in sorted_pv.head(3).iterrows():
            st.markdown(f"""
            <div class="ranking-card">
                <div style="display:flex; align-items:center; gap:12px;">
                    <img src="{row['logo_url']}" class="company-logo" alt="logo" />
                    <div>
                        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem;">{row['name']}</div>
                        <div style="font-size:0.78rem; color:#94a3b8;">Val: {row['amount']:,.2f} € • +{row['amountVariation']:,.2f} €</div>
                    </div>
                </div>
                <div class="pill-green" style="font-size:0.8rem;">+{row['variation']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
    with c_losers:
        st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#f43f5e; margin-bottom:12px; letter-spacing:0.04em; text-transform:uppercase;'>Moins-Values</h4>", unsafe_allow_html=True)
        for _, row in sorted_pv.tail(3).sort_values(by='variation', ascending=True).iterrows():
            b_pill = "pill-red" if row['variation'] < 0 else "pill-green"
            prefix = "+" if row['variation'] >= 0 else ""
            st.markdown(f"""
            <div class="ranking-card">
                <div style="display:flex; align-items:center; gap:12px;">
                    <img src="{row['logo_url']}" class="company-logo" alt="logo" />
                    <div>
                        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem;">{row['name']}</div>
                        <div style="font-size:0.78rem; color:#94a3b8;">Val: {row['amount']:,.2f} € • {prefix}{row['amountVariation']:,.2f} €</div>
                    </div>
                </div>
                <div class="{b_pill}" style="font-size:0.8rem;">{prefix}{row['variation']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

    with c_type:
        st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#94a3b8; margin-bottom:12px; letter-spacing:0.04em; text-transform:uppercase;'>Actions vs ETF</h4>", unsafe_allow_html=True)
        type_agg = df.groupby('type')['amount'].sum().reset_index()
        fig_type = px.bar(
            type_agg, x='type', y='amount', color='type',
            text=type_agg['amount'].apply(lambda x: f"{x:,.0f} € ({x/valeur_titres*100:.1f}%)"),
            color_discrete_map={'ETF': '#0ea5e9', 'Action': '#6366f1'}
        )
        fig_type.update_layout(
            margin=dict(t=8, l=8, r=8, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
            height=200,
            xaxis=dict(title=None, showgrid=False),
            yaxis=dict(title=None, showgrid=False, visible=False),
            showlegend=False
        )
        fig_type.update_traces(textposition='outside')
        st.plotly_chart(fig_type, width="stretch")


# =============================================================
# ONGLET 2 : POSITIONS & TITRES (TABLEAU + FICHE TITRE)
# =============================================================
with tab_positions:
    st.markdown("<h3 style='font-size:1.2rem; font-weight:700; color:#f8fafc; margin-bottom:16px;'>Positions en Portefeuille</h3>", unsafe_allow_html=True)
    
    # Barre de filtre et de recherche
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1: search_kw = st.text_input("Recherche rapide", placeholder="Rechercher par libellé ou code ISIN...")
    with f2: type_filter = st.selectbox("Type d'instrument", ["Tous", "Action", "ETF"])
    with f3: perf_filter = st.selectbox("Filtre performance", ["Toutes", "En Plus-Value", "En Moins-Value"])

    filtered = df.copy()
    if search_kw:
        mask = filtered['name'].str.contains(search_kw, case=False, na=False) | filtered['isin'].str.contains(search_kw, case=False, na=False)
        filtered = filtered[mask]
    if type_filter != "Tous":
        filtered = filtered[filtered['type'] == type_filter]
    if perf_filter == "En Plus-Value":
        filtered = filtered[filtered['amountVariation'] >= 0]
    elif perf_filter == "En Moins-Value":
        filtered = filtered[filtered['amountVariation'] < 0]

    cols_to_show = ['logo_url', 'name', 'isin', 'sector', 'quantity', 'buyingPrice', 'lastPrice', 'amount', 'weight', 'amountVariation', 'variation', 'intradayVariation']
    st.data_editor(
        filtered[cols_to_show],
        column_config={
            "logo_url": st.column_config.ImageColumn("Logo", width="small"),
            "name": st.column_config.TextColumn("Titre", width="medium"),
            "isin": st.column_config.TextColumn("ISIN", width="small"),
            "sector": st.column_config.TextColumn("Secteur", width="small"),
            "quantity": st.column_config.NumberColumn("Quantité", format="%.2f"),
            "buyingPrice": st.column_config.NumberColumn("PRU", format="%.2f €"),
            "lastPrice": st.column_config.NumberColumn("Dernier cours", format="%.2f €"),
            "amount": st.column_config.NumberColumn("Valorisation", format="%.2f €"),
            "weight": st.column_config.ProgressColumn("Poids (%)", format="%.1f%%", min_value=0, max_value=100),
            "amountVariation": st.column_config.NumberColumn("+/- Value (€)", format="%+,.2f €"),
            "variation": st.column_config.ProgressColumn("+/- Value (%)", format="%+.2f%%", min_value=-100, max_value=100),
            "intradayVariation": st.column_config.NumberColumn("Var. Jour (%)", format="%+.2f%%")
        },
        hide_index=True,
        width="stretch",
        height=420
    )

    csv_bytes = filtered.to_csv(index=False, sep=';').encode('utf-8')
    st.download_button("Télécharger les positions (CSV)", data=csv_bytes, file_name=f"export_portefeuille_pea_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 32px 0 24px 0;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.2rem; font-weight:700; color:#f8fafc; margin-bottom:14px;'>Inspecteur d'Actif / Fiche Titre</h3>", unsafe_allow_html=True)
    
    selected_stock_name = st.selectbox("Sélectionner une position à inspecter", options=df['name'].tolist(), key="sb_inspector_stock")
    stock_row = df[df['name'] == selected_stock_name].iloc[0]
    
    inspect_c1, inspect_c2 = st.columns([1, 1.8])
    with inspect_c1:
        st.markdown(f"""
        <div style="background: rgba(18, 24, 35, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 24px;">
            <div style="display:flex; align-items:center; gap:16px; margin-bottom:18px;">
                <img src="{stock_row['logo_url']}" style="width:52px; height:52px; border-radius:14px; object-fit:contain; background:#ffffff; padding:4px;" />
                <div>
                    <h3 style="margin:0; color:#ffffff; font-size:1.25rem; font-weight:700;">{stock_row['name']}</h3>
                    <span style="color:#64748b; font-size:0.8rem; font-weight:600;">{stock_row['isin']} • {stock_row['type']}</span>
                </div>
            </div>
            <div style="font-size:0.9rem; color:#cbd5e1; line-height:2.1;">
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Quantité :</span> <b>{stock_row['quantity']:,.2f} titres</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">PRU d'achat :</span> <b>{stock_row['buyingPrice']:,.2f} €</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Dernier Cours :</span> <b>{stock_row['lastPrice']:,.2f} €</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Valorisation :</span> <b style="color:#38bdf8;">{stock_row['amount']:,.2f} €</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Poids Portefeuille :</span> <b>{stock_row['weight']:.2f}%</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Performance :</span> <b style="color:{'#10b981' if stock_row['amountVariation']>=0 else '#f43f5e'};">{'+' if stock_row['amountVariation']>=0 else ''}{stock_row['amountVariation']:,.2f} € ({'+' if stock_row['variation']>=0 else ''}{stock_row['variation']:.2f}%)</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Secteur :</span> <b>{stock_row['sector']}</b></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Rendement Div. :</span> <b style="color:#38bdf8;">{stock_row['div_yield']:.2f}% (~{stock_row['annual_div_euro']:,.1f} €/an)</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with inspect_c2:
        yf_sym = stock_row.get('yf_symbol')
        st.markdown(f"<div style='font-size:0.95rem; font-weight:700; color:#94a3b8; margin-bottom:8px;'>Historique Boursier (1 An) • <code>{yf_sym if yf_sym else stock_row['name']}</code></div>", unsafe_allow_html=True)
        if yf_sym:
            try:
                hist_data = yf.Ticker(yf_sym).history(period="1y")
                if not hist_data.empty:
                    fig_stock_hist = px.line(hist_data, x=hist_data.index, y='Close', labels={'Close': 'Cours (€)', 'Date': 'Date'})
                    fig_stock_hist.update_traces(line_color="#0ea5e9", line_width=2.5)
                    fig_stock_hist.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                        margin=dict(t=10, l=10, r=10, b=20),
                        height=350,
                        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=None),
                        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=None)
                    )
                    st.plotly_chart(fig_stock_hist, width="stretch")
                else:
                    st.info("Données historiques non disponibles pour ce titre.")
            except Exception:
                st.info("Historique boursier indisponible.")
        else:
            st.info("Symbole boursier non renseigné.")


# =============================================================
# ONGLET 3 : ANALYSES & PERFORMANCE
# =============================================================
with tab_analytics:
    sec_col1, sec_col2 = st.columns([1.3, 1.2])
    with sec_col1:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Allocation par Secteur</h3>", unsafe_allow_html=True)
        sec_agg = df.groupby('sector')['amount'].sum().reset_index()
        fig_sec = px.pie(sec_agg, names='sector', values='amount', hole=0.62, color_discrete_sequence=px.colors.qualitative.Prism)
        fig_sec.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#06080d', width=2)))
        fig_sec.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc", family="Plus Jakarta Sans"), 
            margin=dict(t=10, l=10, r=10, b=10),
            height=340,
            showlegend=False
        )
        st.plotly_chart(fig_sec, width="stretch")

    with sec_col2:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Dividendes Annuels Estimés (€/an)</h3>", unsafe_allow_html=True)
        div_df = df[df['annual_div_euro'] > 0].sort_values(by='annual_div_euro', ascending=False)
        if not div_df.empty:
            fig_div_bar = px.bar(
                div_df, x='name', y='annual_div_euro',
                text=div_df['annual_div_euro'].apply(lambda x: f"{x:,.1f} €"),
                color='annual_div_euro', color_continuous_scale=['#0ea5e9', '#10b981']
            )
            fig_div_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                margin=dict(t=10, l=10, r=10, b=30),
                height=340,
                xaxis=dict(title=None, tickangle=-30, gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(title=None, gridcolor="rgba(255,255,255,0.06)"),
                coloraxis_showscale=False
            )
            fig_div_bar.update_traces(textposition='outside')
            st.plotly_chart(fig_div_bar, width="stretch")
        else:
            st.info("Aucun dividende détecté sur les positions actuelles.")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 24px 0;'>", unsafe_allow_html=True)

    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Contribution aux Gains & Pertes (€)</h3>", unsafe_allow_html=True)
        df_sorted_gains = df.sort_values(by='amountVariation', ascending=True).copy()
        df_sorted_gains['status'] = np.where(df_sorted_gains['amountVariation'] >= 0, 'Plus-Value', 'Moins-Value')
        fig_bars = px.bar(
            df_sorted_gains,
            x='amountVariation',
            y='name',
            orientation='h',
            color='status',
            color_discrete_map={'Plus-Value': '#10b981', 'Moins-Value': '#f43f5e'},
            text=df_sorted_gains['amountVariation'].apply(lambda x: f"{'+' if x>0 else ''}{x:,.2f} €"),
            labels={'amountVariation': 'Plus/Moins-value (€)', 'name': 'Titre'}
        )
        fig_bars.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            margin=dict(t=10, l=10, r=60, b=10),
            height=400,
            showlegend=False,
            xaxis=dict(title=None, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title=None, gridcolor="rgba(255,255,255,0.06)")
        )
        fig_bars.update_traces(textposition='outside')
        st.plotly_chart(fig_bars, width="stretch")

    with col_a2:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Comparatif PRU vs Dernier Cours (€)</h3>", unsafe_allow_html=True)
        fig_compare = go.Figure()
        fig_compare.add_trace(go.Bar(x=df['name'], y=df['buyingPrice'], name="PRU (Prix d'achat)", marker_color="#475569"))
        fig_compare.add_trace(go.Bar(x=df['name'], y=df['lastPrice'], name="Dernier Cours", marker_color="#0ea5e9"))
        fig_compare.update_layout(
            barmode='group',
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            margin=dict(t=10, l=10, r=10, b=50),
            height=400,
            xaxis=dict(tickangle=-40, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title=None, gridcolor="rgba(255,255,255,0.06)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_compare, width="stretch")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Matrice Poids (%) vs Performance (%)</h3>", unsafe_allow_html=True)
    fig_matrix = px.scatter(
        df, x='variation', y='weight', size='amount', color='variation',
        hover_name='name', color_continuous_scale=['#f43f5e', '#64748b', '#10b981'],
        color_continuous_midpoint=0, text='name'
    )
    fig_matrix.update_traces(textposition='top center')
    fig_matrix.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
        margin=dict(t=20, l=10, r=10, b=20),
        height=420,
        xaxis=dict(title="Performance globale (%)", gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(title="Poids dans le portefeuille (%)", gridcolor="rgba(255,255,255,0.06)")
    )
    st.plotly_chart(fig_matrix, width="stretch")


# =============================================================
# ONGLET 4 : HISTORIQUE TEMPOREL (SUPABASE)
# =============================================================
with tab_history:
    st.markdown("<h3 style='font-size:1.2rem; font-weight:700; color:#f8fafc; margin-bottom:8px;'>Évolution du Patrimoine & Instantanés</h3>", unsafe_allow_html=True)
    st.caption("Données horodatées enregistrées en direct dans la base Supabase.")
    snaps_df = get_snapshots_df()
    
    if snaps_df.empty:
        st.info("Aucun instantané enregistré dans l'historique pour le moment. Cliquez sur 'Rafraîchir les cours' dans la barre latérale pour enregistrer vos premiers points.")
    else:
        if len(snaps_df) == 1:
            st.info("💡 **1 seul instantané est actuellement enregistré en base.** Pour visualiser une courbe d'évolution dans le temps, cliquez sur **'🔄 Rafraîchir les cours'** dans la barre latérale : chaque rafraîchissement crée un nouvel instantané horodaté !")

        snaps_df['snapshot_date_dt'] = pd.to_datetime(snaps_df['snapshot_date'])
        snaps_df = snaps_df.sort_values(by='snapshot_date_dt')
        
        fig_hist_val = go.Figure()
        fig_hist_val.add_trace(go.Scatter(
            x=snaps_df['snapshot_date_dt'], y=snaps_df['total_valeur'],
            mode='lines+markers', name="Valorisation Totale (€)",
            line=dict(color="#0ea5e9", width=3), fill='tonexty', fillcolor='rgba(14, 165, 233, 0.08)'
        ))
        fig_hist_val.add_trace(go.Scatter(
            x=snaps_df['snapshot_date_dt'], y=snaps_df['cout_investi'],
            mode='lines+markers', name="Capital Investi (PRU Total)",
            line=dict(color="#64748b", width=2, dash='dash')
        ))
        fig_hist_val.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
            margin=dict(t=20, l=10, r=10, b=20),
            height=380,
            xaxis=dict(title=None, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title="Montant (€)", gridcolor="rgba(255,255,255,0.06)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_hist_val, width="stretch")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#10b981; margin-bottom:8px;'>Plus-Value Latente (€)</h4>", unsafe_allow_html=True)
            fig_hist_pv = px.line(snaps_df, x='snapshot_date_dt', y='plus_value', markers=True)
            fig_hist_pv.update_traces(line_color="#10b981", line_width=2.5)
            fig_hist_pv.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                margin=dict(t=10, l=10, r=10, b=10),
                height=260,
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=None),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=None)
            )
            st.plotly_chart(fig_hist_pv, width="stretch")

        with col_h2:
            st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#8b5cf6; margin-bottom:8px;'>Performance Globale (%)</h4>", unsafe_allow_html=True)
            fig_hist_pct = px.line(snaps_df, x='snapshot_date_dt', y='plus_value_pct', markers=True)
            fig_hist_pct.update_traces(line_color="#8b5cf6", line_width=2.5)
            fig_hist_pct.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                margin=dict(t=10, l=10, r=10, b=10),
                height=260,
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=None),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title=None)
            )
            st.plotly_chart(fig_hist_pct, width="stretch")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 24px 0;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:1rem; font-weight:700; color:#f8fafc; margin-bottom:12px;'>Instantanés enregistrés en Base de Données</h4>", unsafe_allow_html=True)
        table_snaps = snaps_df[['id', 'snapshot_date', 'total_valeur', 'cout_investi', 'plus_value', 'plus_value_pct', 'source_filename']].copy()
        table_snaps.columns = ['ID', 'Date Snapshot', 'Valorisation (€)', 'Investi (€)', 'Plus-Value (€)', 'Perf (%)', 'Fichier Source']
        st.dataframe(
            table_snaps.style.format({
                'Valorisation (€)': '{:,.2f} €',
                'Investi (€)': '{:,.2f} €',
                'Plus-Value (€)': '{:+,.2f} €',
                'Perf (%)': '{:+.2f} %'
            }),
            width="stretch"
        )


# =============================================================
# ONGLET 5 : INTELLIGENCE IA & FISCALITÉ
# =============================================================
with tab_ai_tax:
    sub_tab_diag, sub_tab_weather, sub_tab_bourseai, sub_tab_fiscal = st.tabs([
        "Diagnostic Global (Groq)",
        "Météo Synthétique & Actus",
        "Synthèse BourseAi",
        "Fiscalité PEA & Projection"
    ])

    # 1. DIAGNOSTIC GLOBAL
    with sub_tab_diag:
        st.markdown(f"<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:6px;'>Diagnostic Portefeuille avec <code>{groq_model}</code></h3>", unsafe_allow_html=True)
        st.caption("Évaluation de la diversification, détection des risques et recommandations PEA.")

        if st.button(f"Lancer le Diagnostic Global avec {groq_model}", type="primary"):
            with st.spinner(f"Analyse globale en cours avec {groq_model}..."):
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
                st.markdown("#### Points Forts du Portefeuille")
                for pt in d_res.get("points_forts", []):
                    st.success(f"• {pt}")

                st.markdown("#### Recommandations PEA")
                for rec in d_res.get("recommandations_pea", []):
                    st.write(f"👉 {rec}")

            with c_al:
                st.markdown("#### Alertes & Risques de Concentration")
                for alt in d_res.get("alertes_et_risques", []):
                    st.error(f"• {alt}")

    # 2. MÉTÉO SYNTHÉTIQUE
    with sub_tab_weather:
        st.markdown(f"<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:6px;'>Météo & Sentiment des Actualités</h3>", unsafe_allow_html=True)
        st.caption("Analyse NLP des dernières actualités boursières sur vos positions.")

        if st.button(f"Analyser l'Actualité des Titres avec {groq_model}", type="primary"):
            sentiments_results = {}
            p_text = st.empty()
            p_bar = st.progress(0)

            for idx, row in df.iterrows():
                comp_name = row.get('name', 'Action')
                tk_sym = row.get('yf_symbol') or comp_name
                p_text.text(f"Analyse des actualités de {comp_name} avec {groq_model}...")
                news_items = fetch_ticker_news(ticker_symbol=tk_sym, company_name=comp_name)
                try:
                    analysis = analyze_news_sentiment(
                        ticker_symbol=tk_sym,
                        news_list=news_items,
                        company_name=comp_name,
                        model=groq_model
                    )
                except Exception as e_news:
                    print(f"Notice analyse sentiment {comp_name}: {e_news}")
                    analysis = {"sentiment_global": "Neutre", "score_global": 0.0, "analyse_news": []}
                
                sentiments_results[comp_name] = analysis
                if tk_sym:
                    sentiments_results[tk_sym] = analysis
                p_bar.progress((idx + 1) / len(df))

            p_text.empty()
            p_bar.empty()
            st.session_state["sentiments_results"] = sentiments_results
            st.success(f"Analyse des actualités terminée avec succès via {groq_model} !")

        if "sentiments_results" in st.session_state:
            s_dict = st.session_state["sentiments_results"]
            score_w, icon_w, label_w = compute_portfolio_weather(df, s_dict)

            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                st.metric(
                    label=f"Météo Portefeuille : {label_w}",
                    value=f"{icon_w} {score_w:+.2f}",
                    delta="Score pondéré par les poids"
                )
            with col_m2:
                st.write("**Impact de l'actualité par position :**")
                total_val_weather = df["amount"].sum()
                for _, r in df.iterrows():
                    c_name = r.get('name', '')
                    tk_name = r.get('yf_symbol') or c_name
                    wt = (r["amount"] / total_val_weather) * 100 if total_val_weather > 0 else 0
                    s_score = s_dict.get(c_name, s_dict.get(tk_name, {})).get("score_global", 0.0)
                    st.caption(f"• **{c_name}** ({wt:.1f}% du PEA) : Sentiment {s_score:+.2f}")

            st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 20px 0;'>", unsafe_allow_html=True)
            stock_names_list = df['name'].tolist()
            selected_t_name = st.selectbox("Consulter les actualités d'une action :", stock_names_list, key="sb_news_stock_tab5")
            selected_row = df[df['name'] == selected_t_name].iloc[0]
            tk_key = selected_row.get('yf_symbol') or selected_row.get('name')

            res_news = s_dict.get(selected_t_name) or s_dict.get(tk_key)
            if res_news:
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

    # 3. BOURSEAI
    with sub_tab_bourseai:
        st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:6px;'>Générateur de Synthèses Boursières BourseAi</h3>", unsafe_allow_html=True)
        st.caption("Inspiré du projet open-source YR72dpi/BourseAi : Scraping ZoneBourse + Modèle Groq.")

        ai_c1, ai_c2 = st.columns([1.5, 1])
        with ai_c1:
            selected_ai_stock = st.selectbox("Choisir un actif de votre portefeuille", options=df['name'].tolist(), key="sb_ai_stock_tab5")
        with ai_c2:
            custom_zb_link = st.text_input("Ou coller un lien personnalisé ZoneBourse", placeholder="https://www.zonebourse.fr/cours/action/...")

        btn_analyze = st.button("Lancer la Synthèse BourseAi", type="primary")

        if btn_analyze or 'last_ai_res' in st.session_state:
            if btn_analyze:
                selected_row = df[df['name'] == selected_ai_stock].iloc[0]
                with st.spinner("Analyse en cours via BourseAi (ZoneBourse + Données de marché + Groq)..."):
                    ai_res = analyze_stock_with_ai(
                        stock_name=selected_ai_stock,
                        isin=selected_row.get('isin'),
                        yf_symbol=selected_row.get('yf_symbol'),
                        custom_url=custom_zb_link if custom_zb_link else None,
                        model=groq_model
                    )
                    st.session_state['last_ai_res'] = ai_res
            else:
                ai_res = st.session_state['last_ai_res']

            rec_badge = "Faut-il investir ? OUI (Opportunité)" if ai_res['should_invest'] else "Faut-il investir ? NON (Prudence)"
            rec_color = "#10b981" if ai_res['should_invest'] else "#f43f5e"
            
            st.markdown(f"""
            <div style="background: rgba(18, 24, 35, 0.75); border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 18px; padding: 22px; margin: 18px 0;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <h2 style="margin:0; color:#f8fafc; font-size:1.35rem; font-weight:700;">{ai_res['company_name']}</h2>
                        <span style="color:#64748b; font-size:0.8rem;">Source : {ai_res['source']}</span>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.2rem; font-weight:800; color:{rec_color};">{rec_badge}</div>
                        <span style="font-size:0.88rem; color:#f8fafc;">Score Qualité : <b>{ai_res['score_percent']}/100</b></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(ai_res['score_percent'] / 100)

            col_pros, col_cons = st.columns(2)
            with col_pros:
                st.markdown("#### Points Forts (Pourquoi Investir)")
                st.success(ai_res['pros'])
            with col_cons:
                st.markdown("#### Risques & Vigilance")
                st.error(ai_res['cons'])

            st.markdown("#### Synthèse du Profil & Données Clés")
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

    # 4. FISCALITÉ PEA & SIMULATEUR
    with sub_tab_fiscal:
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:8px;'>Cadre Fiscal du PEA</h3>", unsafe_allow_html=True)
            st.markdown("""
            Le **Plan d'Épargne en Actions (PEA)** permet une exonération d'impôt sur le revenu après 5 ans :
            - **Avant 5 ans** : Tout retrait entraîne la clôture et Flat Tax de 30%.
            - **Après 5 ans** : Exonération d'IR (0%), seuls les prélèvements sociaux (17,2%) s'appliquent sur les gains nets.
            """)
            st.markdown(f"""
            <div style="background: rgba(18, 24, 35, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; margin-top: 15px;">
                <h4 style="margin-top:0; color:#38bdf8; font-size:1rem; font-weight:700;">Bilan Fiscal des Plus-Values</h4>
                <table style="width:100%; border-collapse:collapse; font-size:0.9rem;">
                    <tr><td style="padding:6px 0; color:#94a3b8;">Total Plus-Value Latente :</td><td style="text-align:right; font-weight:700; color:{'#10b981' if plus_value_latente_titres>=0 else '#f43f5e'};">{plus_value_latente_titres:,.2f} €</td></tr>
                    <tr><td style="padding:6px 0; color:#94a3b8;">Prélèvements Sociaux estimés (17.2%) :</td><td style="text-align:right; font-weight:700; color:#f43f5e;">-{prelevements_sociaux:,.2f} €</td></tr>
                    <tr style="border-top: 1px solid rgba(255,255,255,0.08);"><td style="padding:8px 0; font-weight:700; color:#f8fafc;">Gain Réel Net d'Impôt :</td><td style="text-align:right; font-weight:800; color:#10b981; font-size:1.05rem;">+{plus_value_latente_titres - prelevements_sociaux:,.2f} €</td></tr>
                    <tr><td style="padding:6px 0; font-weight:700; color:#f8fafc;">Capital Retirable Net (Titres + Cash) :</td><td style="text-align:right; font-weight:800; color:#38bdf8; font-size:1.05rem;">{valeur_nette_apres_ps:,.2f} €</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            st.markdown("<h4 style='font-size:0.95rem; font-weight:700; color:#94a3b8;'>Plafond des versements (150 000 €)</h4>", unsafe_allow_html=True)
            plafond = 150000.0
            pct_plafond = min(100.0, (cout_total_investi / plafond) * 100)
            st.progress(pct_plafond / 100)
            st.caption(f"Capacité de versement restante : **{plafond - cout_total_investi:,.2f} €** ({pct_plafond:.1f}% du plafond atteint)")

        with f_col2:
            st.markdown("<h3 style='font-size:1.15rem; font-weight:700; color:#f8fafc; margin-bottom:8px;'>Simulateur d'Intérêts Composés</h3>", unsafe_allow_html=True)
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
            fig_compound.add_trace(go.Scatter(x=annees_list, y=val_list, mode='lines+markers', name="Valeur Projetée", line=dict(color="#10b981", width=3)))
            fig_compound.add_trace(go.Scatter(x=annees_list, y=versements_list, mode='lines', name="Capital Versé", line=dict(color="#64748b", dash='dash')))
            fig_compound.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", family="Plus Jakarta Sans"),
                margin=dict(t=20, l=10, r=10, b=20),
                height=320,
                xaxis=dict(title="Années", gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(title="Montant (€)", gridcolor="rgba(255,255,255,0.06)"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_compound, width="stretch")
            gain_projeté = val_list[-1] - versements_list[-1]
            st.success(f"🎯 Dans **{horizon_ans} ans**, votre portefeuille atteindrait **{val_list[-1]:,.2f} €**, dont **{gain_projeté:,.2f} €** d'intérêts générés !")


