import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    from ai_advisor import analyze_portfolio_global, fetch_ticker_news, analyze_news_sentiment, compute_portfolio_weather
except ImportError as e:
    print(f"Warning: Could not import ai_advisor. {e}")
    def analyze_portfolio_global(*args, **kwargs): return {}
    def fetch_ticker_news(*args, **kwargs): return []
    def analyze_news_sentiment(*args, **kwargs): return {"score": 0}
    def compute_portfolio_weather(*args, **kwargs): return 0, "☁️", "Erreur AI"

def resolve_sector(isin, name):
    name_u = str(name).upper()
    if 'ETF' in name_u or 'STOXX' in name_u or 'MSCI' in name_u or 'AMUNDI' in name_u:
        return 'ETF & Indice'
    if 'LVMH' in name_u or 'HERMES' in name_u or 'KERING' in name_u or 'L\'OREAL' in name_u:
        return 'Luxe'
    if 'TOTAL' in name_u or 'ENERGY' in name_u:
        return 'Énergie'
    if 'APPLE' in name_u or 'MICROSOFT' in name_u or 'TECH' in name_u:
        return 'Technologie'
    return 'Action'

import urllib.request
from urllib.parse import quote
import json

def search_yf_symbol_online(query):
    if not query: return None
    try:
        q_clean = quote(str(query).strip())
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q_clean}&newsCount=0"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            quotes = data.get('quotes', [])
            if not quotes: return None
            for q in quotes:
                sym = q.get('symbol', '')
                if sym.endswith('.PA'): return sym
            for q in quotes:
                sym = q.get('symbol', '')
                if sym and not sym.startswith('^'): return sym
    except Exception:
        pass
    return None

def resolve_yf_symbol(isin, name):
    isin_clean = str(isin).strip().upper() if isin else ""
    if isin_clean == 'FR0000121014': return 'MC.PA'
    if isin_clean == 'FR0000120271': return 'TTE.PA'
    if isin_clean == 'US0378331005': return 'AAPL'
    if isin_clean == 'US5949181045': return 'MSFT'
    if isin_clean == 'LU1681043599': return 'CW8.PA'
    
    if isin_clean and len(isin_clean) >= 9:
        online = search_yf_symbol_online(isin_clean)
        if online: return online
        
    if name:
        online = search_yf_symbol_online(name)
        if online: return online
        
    if isin_clean.startswith('FR'): return str(name).split()[0] + '.PA'
    if isin_clean.startswith('US'): return str(name).split()[0]
    return name

from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app = FastAPI(title="PEA Tracker SaaS API")

import os
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuthRequest(BaseModel):
    username: str
    password: str

def to_synthetic_email(uname: str) -> str:
    cleaned = re.sub(r'[^a-zA-Z0-9_\-\.]', '', uname.strip().lower())
    return f"{cleaned}@pea.local"


security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        res = supabase.auth.get_user(credentials.credentials)
        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Token invalide")
        return res.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Non autorisé: {str(e)}")

@app.post("/api/auth/login")
async def login(req: AuthRequest):
    if not supabase:
        raise HTTPException(status_code=500, detail="Configuration Supabase manquante dans le backend (.env).")
    try:
        email = to_synthetic_email(req.username)
        res = supabase.auth.sign_in_with_password({"email": email, "password": req.password})
        return {"user_id": res.user.id, "username": req.username, "access_token": res.session.access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Identifiants incorrects.")

@app.post("/api/auth/register")
async def register(req: AuthRequest):
    if not supabase:
        raise HTTPException(status_code=500, detail="Configuration Supabase manquante.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit faire au moins 6 caractères.")
    try:
        email = to_synthetic_email(req.username)
        res = supabase.auth.sign_up({"email": email, "password": req.password})
        return {"user_id": res.user.id, "username": req.username, "access_token": res.session.access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def fetch_user_data(user_id: str):
    if not supabase: return pd.DataFrame(), 0.0
    res_snap = supabase.table("snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    if not res_snap.data:
        return pd.DataFrame(), 0.0
    
    latest_snap = res_snap.data[0]
    snap_id = latest_snap['id']
    cash = float(latest_snap.get('cash', 0.0))
    
    res_pos = supabase.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
    df = pd.DataFrame(res_pos.data) if res_pos.data else pd.DataFrame()
    return df, cash

@app.get("/api/portfolio/summary")
async def get_summary(user_id: str):
    df, cash = fetch_user_data(user_id)
    if df.empty:
        return {"total_value": cash, "total_invested": 0, "global_performance_pct": 0, "global_performance_value": 0, "last_updated": datetime.now().isoformat()}
    
    val_titres = float(df['amount'].sum())
    total_value = val_titres + cash
    total_invested = float(df['buying_price'].multiply(df['quantity']).sum())
    global_performance_value = float(df['amount_variation'].sum())
    global_performance_pct = (global_performance_value / total_invested * 100) if total_invested > 0 else 0.0
    
    return {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "global_performance_pct": round(global_performance_pct, 2),
        "global_performance_value": round(global_performance_value, 2),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/portfolio/positions")
async def get_positions(user_id: str):
    df, _ = fetch_user_data(user_id)
    positions = []
    if not df.empty:
        for _, row in df.iterrows():
            name = row.get('name', '')
            isin = row.get('isin', '')
            
            try:
                sector = resolve_sector(isin, name)
                yf_sym = resolve_yf_symbol(isin, name)
            except:
                sector = "Action"
                yf_sym = name
                
            positions.append({
                "name": name,
                "ticker": yf_sym or isin,
                "isin": isin,
                "quantity": float(row.get('quantity', 0.0)),
                "pru": float(row.get('buying_price', 0.0)),
                "current_price": float(row.get('last_price', 0.0)),
                "variation_pct": float(row.get('variation', 0.0)),
                "sector": sector,
                "asset_type": str(row.get('type', 'Action'))
            })
    return {"positions": positions}

from fastapi import UploadFile, File
import io

class CashUpdateRequest(BaseModel):
    cash: float

@app.post("/api/portfolio/cash")
async def update_cash(req: CashUpdateRequest, user_id: str):
    if not supabase: raise HTTPException(500, "DB not configured")
    res_snap = supabase.table("snapshots").select("id, valeur_titres").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    if res_snap.data:
        snap_id = res_snap.data[0]['id']
        val_titres = float(res_snap.data[0].get("valeur_titres") or 0.0)
        supabase.table("snapshots").update({
            "cash": req.cash, 
            "total_valeur": val_titres + req.cash
        }).eq("id", snap_id).execute()
    return {"status": "ok", "cash": req.cash}

@app.post("/api/portfolio/upload")
async def upload_csv(user_id: str, file: UploadFile = File(...)):
    if not supabase: raise HTTPException(500, "DB not configured")
    
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content), sep=';', decimal=',', thousands=' ')
        if len(df.columns) <= 2:
            df = pd.read_csv(io.BytesIO(content), sep=',', decimal='.')
    except Exception as e:
        raise HTTPException(400, "Invalid CSV format")
        
    mapping = {
        'nom': 'name', 'valeur': 'name', 'libelle': 'name', 'libellé': 'name', 
        'code isin': 'isin', 'isin': 'isin',
        'quantité': 'quantity', 'quantite': 'quantity',
        'prix de revient': 'buying_price', 'pru': 'buying_price', 
        'dernier cours': 'last_price', 
        'montant': 'amount', 'valorisation': 'amount',
        '+/- value': 'amount_variation', 'plus/moins value': 'amount_variation',
        '+/- value (%)': 'variation', 'perf (%)': 'variation', 'performance': 'variation'
    }
    
    cleaned_cols = {}
    for c in df.columns:
        key = str(c).strip().lower()
        cleaned_cols[c] = mapping.get(key, key)
    df = df.rename(columns=cleaned_cols)
    
    if 'name' not in df.columns: 
        raise HTTPException(400, "CSV must contain a 'nom' or 'valeur' column")
    
    for col in ['quantity', 'buying_price', 'last_price', 'amount', 'amount_variation', 'variation']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(' ', '').str.replace('€', '').str.replace('%', '').str.replace(',', '.'), errors='coerce').fillna(0.0)

    if 'amount' not in df.columns and 'quantity' in df.columns and 'last_price' in df.columns:
        df['amount'] = df['quantity'] * df['last_price']
        
    snapshot_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    valeur_titres = float(df['amount'].sum()) if 'amount' in df.columns else 0.0
    
    res_cash = supabase.table("snapshots").select("cash").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    cash = float(res_cash.data[0]['cash']) if res_cash.data else 0.0
    
    snap_data = {
        "user_id": user_id,
        "snapshot_date": snapshot_date,
        "total_valeur": valeur_titres + cash,
        "valeur_titres": valeur_titres,
        "cash": cash,
        "cout_investi": float((df['quantity'] * df['buying_price']).sum()) if 'buying_price' in df.columns else 0.0,
        "source_filename": file.filename
    }
    res = supabase.table("snapshots").insert(snap_data).execute()
    snap_id = res.data[0]['id']
    
    pos_data = []
    for _, row in df.iterrows():
        pos_data.append({
            "user_id": user_id,
            "snapshot_id": snap_id,
            "snapshot_date": snapshot_date,
            "name": row.get('name', ''),
            "isin": row.get('isin', ''),
            "quantity": float(row.get('quantity', 0.0)),
            "buying_price": float(row.get('buying_price', 0.0)),
            "last_price": float(row.get('last_price', 0.0)),
            "amount": float(row.get('amount', 0.0)),
            "amount_variation": float(row.get('amount_variation', 0.0)),
            "variation": float(row.get('variation', 0.0)),
        })
    if pos_data:
        supabase.table("snapshot_positions").insert(pos_data).execute()
        
    return {"status": "ok", "snapshot_id": snap_id}

@app.get("/api/portfolio/history")
async def get_portfolio_history(user_id: str = Depends(get_current_user)):
    if not supabase: return {"history": []}
    res = supabase.table("snapshots").select("snapshot_date, total_valeur, cout_investi, plus_value").eq("user_id", user_id).order("snapshot_date", desc=False).execute()
    history = []
    if res.data:
        for row in res.data:
            date_str = row.get("snapshot_date", "")
            history.append({
                "date": date_str.split(" ")[0] if date_str else "",
                "total_valeur": float(row.get("total_valeur") or 0.0),
                "cout_investi": float(row.get("cout_investi") or 0.0),
                "plus_value": float(row.get("plus_value") or 0.0)
            })
    return {"history": history}

@app.get("/api/portfolio/ai-diagnostic")
async def get_ai_diagnostic(user_id: str = Depends(get_current_user)):
    df, _ = fetch_user_data(user_id)
    if df.empty: return {}
    df['yf_symbol'] = df['isin'] 
    return analyze_portfolio_global(df)

@app.get("/api/portfolio/weather")
async def get_portfolio_weather(user_id: str = Depends(get_current_user)):
    df, _ = fetch_user_data(user_id)
    if df.empty: return {"score": 0, "emoji": "☁️", "text": "Vide", "details": {}}
    
    news_dict = {}
    for _, row in df.iterrows():
        try:
            ticker = resolve_yf_symbol(row.get('isin'), row.get('name')) or row.get('name')
            news = fetch_ticker_news(ticker_symbol=ticker, company_name=row.get('name'), max_news=2)
            sentiment = analyze_news_sentiment(ticker_symbol=ticker, news_list=news, company_name=row.get('name'))
            news_dict[ticker] = sentiment
        except:
            pass
            
    df['yf_symbol'] = df['isin']
    score, emoji, text = compute_portfolio_weather(df, news_dict)
    return {"score": score, "emoji": emoji, "text": text, "details": news_dict}

import yfinance as yf

@app.post("/api/portfolio/refresh")
async def refresh_portfolio(user_id: str = Depends(get_current_user)):
    if not supabase: return {"status": "error", "message": "Supabase non configuré"}
    
    # Récupérer le dernier snapshot
    res_snap = supabase.table("snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    if not res_snap.data: return {"status": "ok"}
    
    latest_snap = res_snap.data[0]
    snap_id = latest_snap['id']
    cash = float(latest_snap.get('cash', 0.0))
    
    # Récupérer les positions
    res_pos = supabase.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
    if not res_pos.data: return {"status": "ok"}
    
    valeur_titres = 0.0
    plus_value_totale = 0.0
    
    positions_to_insert = []
    
    for pos in res_pos.data:
        ticker = resolve_yf_symbol(pos.get('isin', ''), pos.get('name', ''))
        current_price = pos.get('last_price', 0.0)
        
        # Interrogation de Yahoo Finance pour le cours en direct
        try:
            if ticker:
                info = yf.Ticker(ticker).fast_info
                if info.last_price: 
                    current_price = info.last_price
        except Exception:
            pass
            
        qty = float(pos.get('quantity', 0.0))
        pru = float(pos.get('buying_price', 0.0))
        
        amount = qty * current_price
        variation = ((current_price - pru) / pru * 100) if pru > 0 else 0.0
        amount_var = (current_price - pru) * qty
        
        valeur_titres += amount
        plus_value_totale += amount_var
        
        pos['last_price'] = round(current_price, 2)
        pos['amount'] = round(amount, 2)
        pos['variation'] = round(variation, 2)
        pos['amount_variation'] = round(amount_var, 2)
        
        # Supprimer les champs générés automatiquement par la DB pour la réinsertion
        if 'id' in pos: del pos['id']
        if 'created_at' in pos: del pos['created_at']
        
        positions_to_insert.append(pos)

    # Mise à jour Supabase : Supprimer les anciennes lignes et insérer les nouvelles actualisées
    if positions_to_insert:
        supabase.table("snapshot_positions").delete().eq("snapshot_id", snap_id).execute()
        supabase.table("snapshot_positions").insert(positions_to_insert).execute()
    
    # Mise à jour des totaux du snapshot
    supabase.table("snapshots").update({
        "valeur_titres": round(valeur_titres, 2),
        "total_valeur": round(valeur_titres + cash, 2),
        "plus_value": round(plus_value_totale, 2)
    }).eq("id", snap_id).execute()
    
    return {"status": "ok", "message": "Cours en direct mis à jour dans Supabase"}

try:
    from bourse_ai import analyze_stock_with_ai
except ImportError as e:
    print(f"Warning: Could not import bourse_ai. {e}")
    def analyze_stock_with_ai(*args, **kwargs): return {"error": "Import failed"}

@app.get("/api/stock/analyze/{ticker}")
async def analyze_stock(ticker: str, name: str = ""):
    resolved_ticker = ticker
    
    # Si le ticker n'a pas de point (ex: LVMH, AAPL), on essaie de le résoudre pour être sûr
    if "." not in ticker:
        found = search_yf_symbol_online(ticker)
        if found: resolved_ticker = found
            
    resolved_name = name or ticker
    if resolved_ticker:
        try:
            info = yf.Ticker(resolved_ticker).fast_info
            # We don't have shortName in fast_info, so let's stick to the query name or fetch info
            # Just keeping it simple to avoid slow Yahoo queries
        except Exception:
            pass
            
    analysis = analyze_stock_with_ai(stock_name=resolved_name, yf_symbol=resolved_ticker)
    return analysis
