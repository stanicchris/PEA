import pandas as pd
from datetime import datetime
import re
import streamlit as st
from supabase import create_client, Client

# Initialisation du client Supabase par session utilisateur
def get_supabase_client() -> Client:
    if "supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        st.session_state["supabase_client"] = create_client(url, key)
    return st.session_state["supabase_client"]

def extract_date_from_filename(filename):
    """
    Extrait la date et l'heure à partir de noms de fichiers types.
    """
    if not filename:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    match = re.search(r'(\d{2})-(\d{2})-(\d{4})_(\d{2})-(\d{2})-(\d{2})', filename)
    if match:
        day, month, year, h, m, s = match.groups()
        return f"{year}-{month}-{day} {h}:{m}:{s}"
        
    match_date = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
    if match_date:
        year, month, day = match_date.groups()
        return f"{year}-{month}-{day} 12:00:00"

    match_fr = re.search(r'(\d{2})-(\d{2})-(\d{4})', filename)
    if match_fr:
        day, month, year = match_fr.groups()
        return f"{year}-{month}-{day} 12:00:00"
        
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def is_snapshot_saved(snapshot_date, filename=""):
    """Vérifie si un instantané existe déjà pour cette date ou ce fichier via Supabase."""
    supabase = get_supabase_client()
    user_id = st.session_state.get("user_id")
    if not user_id: return None
    
    response = supabase.table("snapshots").select("id").eq("user_id", user_id).or_(f"snapshot_date.eq.{snapshot_date},source_filename.eq.{filename}").execute()
    return response.data[0]['id'] if response.data else None

def save_snapshot(df, cash=0.0, source_filename="export.csv", custom_date=None):
    """
    Enregistre un nouvel instantané de portefeuille et toutes ses lignes en base Supabase.
    """
    supabase = get_supabase_client()
    user_id = st.session_state.get("user_id")
    if not user_id: return None
    
    snapshot_date = custom_date if custom_date else extract_date_from_filename(source_filename)
    
    valeur_titres = float(df['amount'].sum())
    valeur_totale = valeur_titres + float(cash)
    cout_investi = float(df['totalCost'].sum())
    plus_value = float(df['amountVariation'].sum())
    plus_value_pct = (plus_value / cout_investi * 100) if cout_investi > 0 else 0.0
    intraday_pv = float(df['intradayAmount'].sum()) if 'intradayAmount' in df.columns else 0.0
    nb_pos = len(df)
    
    # Check if exists and delete
    existing_id = is_snapshot_saved(snapshot_date, source_filename)
    if existing_id:
        delete_snapshot(existing_id)
        
    # Insert snapshot
    snapshot_data = {
        "user_id": user_id,
        "snapshot_date": snapshot_date,
        "total_valeur": valeur_totale,
        "valeur_titres": valeur_titres,
        "cash": cash,
        "cout_investi": cout_investi,
        "plus_value": plus_value,
        "plus_value_pct": plus_value_pct,
        "intraday_pv": intraday_pv,
        "nb_positions": nb_pos,
        "source_filename": source_filename
    }
    
    res = supabase.table("snapshots").insert(snapshot_data).execute()
    if not res.data: return None
    snapshot_id = res.data[0]['id']
    
    # Insert positions
    positions_data = []
    for _, row in df.iterrows():
        positions_data.append({
            "user_id": user_id,
            "snapshot_id": snapshot_id,
            "snapshot_date": snapshot_date,
            "name": str(row.get('name', '')),
            "isin": str(row.get('isin', '')),
            "type": str(row.get('type', 'Action')),
            "quantity": float(row.get('quantity', 0.0)),
            "buying_price": float(row.get('buyingPrice', 0.0)),
            "last_price": float(row.get('lastPrice', 0.0)),
            "amount": float(row.get('amount', 0.0)),
            "amount_variation": float(row.get('amountVariation', 0.0)),
            "variation": float(row.get('variation', 0.0)),
            "weight": float(row.get('weight', 0.0))
        })
        
    supabase.table("snapshot_positions").insert(positions_data).execute()
    return snapshot_id

def get_snapshots_df():
    """Récupère l'historique complet des instantanés sous forme de DataFrame (Supabase)."""
    supabase = get_supabase_client()
    user_id = st.session_state.get("user_id")
    if not user_id: return pd.DataFrame()
    
    response = supabase.table("snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=False).execute()
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()

def get_positions_history_df():
    """Récupère l'historique détaillé des positions au fil du temps (Supabase)."""
    supabase = get_supabase_client()
    user_id = st.session_state.get("user_id")
    if not user_id: return pd.DataFrame()
    
    response = supabase.table("snapshot_positions").select("*").eq("user_id", user_id).order("snapshot_date", desc=False).execute()
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()

def delete_snapshot(snapshot_id):
    """Supprime un instantané et ses positions de la base de données Supabase."""
    supabase = get_supabase_client()
    user_id = st.session_state.get("user_id")
    if not user_id: return
    
    # RLS ensures we only delete our own, but we can also add eq filter just in case
    supabase.table("snapshot_positions").delete().eq("snapshot_id", snapshot_id).eq("user_id", user_id).execute()
    supabase.table("snapshots").delete().eq("id", snapshot_id).eq("user_id", user_id).execute()
