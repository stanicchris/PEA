import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

from backend.database import get_current_user, get_supabase_service_client
from backend.utils import resolve_sector, resolve_yf_symbol, search_yf_symbol_online, to_synthetic_email
from backend.schemas import AuthRequest

load_dotenv()

try:
    from ai_advisor import analyze_portfolio_global, fetch_ticker_news, analyze_news_sentiment, compute_portfolio_weather
except ImportError as e:
    print(f"Warning: Could not import ai_advisor. {e}")
    def analyze_portfolio_global(*args, **kwargs): return {}
    def fetch_ticker_news(*args, **kwargs): return []
    def analyze_news_sentiment(*args, **kwargs): return {"score": 0}
    def compute_portfolio_weather(*args, **kwargs): return 0, "☁️", "Erreur AI"


app = FastAPI(title="PEA Tracker SaaS API")

import os
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://pea-ebon.vercel.app",
        *(os.environ.get("ALLOWED_ORIGINS", "").split(",") if os.environ.get("ALLOWED_ORIGINS") else [])
    ],
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:.*|http://127\.0\.0\.1:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# We import get_current_user from backend.database

from backend.routers import auth, portfolio, market, ai, optimization, goals, analytics, watchlist

app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(market.router)
app.include_router(ai.router)
app.include_router(optimization.router)
app.include_router(goals.router)
app.include_router(analytics.router)
app.include_router(watchlist.router, prefix="/api/watchlist")

from backend.services.portfolio_service import fetch_user_data

from backend.services.performance_service import get_performance_metrics
from backend.services.tax_service import get_pea_tax_status

@app.get("/api/portfolio/summary")
async def get_summary(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    user_id = auth_context["user"].id
    df, cash = fetch_user_data(client)
    if df.empty:
        return {
            "total_value": round(cash, 2), 
            "total_invested": 0, 
            "global_performance_pct": 0, 
            "global_performance_value": 0, 
            "cash": round(cash, 2),
            "last_updated": datetime.now().isoformat(),
            "performance": {"xirr": 0, "net_invested": 0, "total_deposits": 0, "total_withdrawals": 0},
            "tax_status": get_pea_tax_status(client, user_id)
        }
    
    val_titres = float((df['last_price'] * df['quantity']).sum())
    total_value = val_titres + cash
    total_invested = float((df['buying_price'] * df['quantity']).sum())
    global_performance_value = val_titres - total_invested
    global_performance_pct = (global_performance_value / total_invested * 100) if total_invested > 0 else 0.0
    
    perf_metrics = get_performance_metrics(client, user_id, total_value)
    tax_status = get_pea_tax_status(client, user_id)
    
    return {
        "total_value": round(total_value, 2),
        "total_invested": round(total_invested, 2),
        "global_performance_pct": round(global_performance_pct, 2),
        "global_performance_value": round(global_performance_value, 2),
        "cash": round(cash, 2),
        "last_updated": datetime.now().isoformat(),
        "performance": perf_metrics,
        "tax_status": tax_status
    }

from backend.services.dividend_service import get_dividend_metrics

@app.get("/api/dividends/metrics")
async def get_dividends_metrics_endpoint(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    user_id = auth_context["user"].id
    df, cash = fetch_user_data(client)
    
    if df.empty:
        return {
            "estimated_annual_income": 0.0,
            "average_yield": 0.0,
            "yield_on_cost": 0.0,
            "safety_score": 0,
            "positions": [],
            "received_dividends": []
        }
        
    metrics = get_dividend_metrics(df, client, user_id)
    return metrics

@app.get("/api/portfolio/positions")
async def get_positions(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, _ = fetch_user_data(client)
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
async def update_cash(req: CashUpdateRequest, auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    user_id = auth_context["user"].id
    
    # 1. Update in snapshots table (latest snapshot)
    res_snap = client.table("snapshots").select("id, valeur_titres").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    if res_snap.data:
        snap_id = res_snap.data[0]['id']
        val_titres = float(res_snap.data[0].get("valeur_titres") or 0.0)
        client.table("snapshots").update({
            "cash": req.cash, 
            "total_valeur": round(val_titres + req.cash, 2)
        }).eq("id", snap_id).execute()
        
    # 2. Update/upsert in user_settings table
    try:
        client.table("user_settings").upsert({
            "user_id": user_id,
            "cash": req.cash,
            "updated_at": datetime.now().isoformat()
        }).execute()
    except Exception as err:
        print(f"user_settings update note: {err}")
        
    return {"status": "ok", "cash": req.cash}

@app.post("/api/cron/daily-refresh")
async def cron_daily_refresh(request: Request):
    auth_header = request.headers.get("Authorization")
    cron_secret = os.environ.get("CRON_SECRET", "dummy_secret_for_local")
    if not auth_header or auth_header != f"Bearer {cron_secret}":
        raise HTTPException(status_code=401, detail="Invalid cron secret")
    
    # In a real scenario, this would loop over all users and call refresh_portfolio logic
    client = get_supabase_service_client()
    if not client:
        return {"status": "error", "message": "Service client not configured"}
        
    print("Triggering daily prices sync for global market...")
    from backend.services.price_service import sync_prices_for_instruments
    sync_prices_for_instruments(client)
        
    print("Daily refresh triggered by cron. Fetching all distinct users...")
    
    # Get all distinct users by getting the latest snapshot for each user
    # For simplicity, we just fetch all users from user_settings (or from snapshots)
    try:
        # Assuming we have a limited number of users for now
        res_users = client.table("user_settings").select("user_id").execute()
        user_ids = [row["user_id"] for row in res_users.data] if res_users.data else []
        
        users_updated = 0
        for uid in user_ids:
            # Let's call the internal refresh logic for each user
            # We must duplicate a bit of logic or create a helper.
            res_snap = client.table("snapshots").select("*").eq("user_id", uid).order("snapshot_date", desc=True).limit(1).execute()
            if not res_snap.data: continue
            
            latest_snap = res_snap.data[0]
            snap_id = latest_snap['id']
            cash = float(latest_snap.get('cash', 0.0))
            cout_investi = float(latest_snap.get('cout_investi', 0.0))
            
            res_pos = client.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
            if not res_pos.data: continue
            
            valeur_titres = 0.0
            plus_value_totale = 0.0
            
            now = datetime.now()
            today_date = now.strftime("%Y-%m-%d")
            latest_snap_date_str = str(latest_snap.get('snapshot_date', ''))
            is_same_day = today_date in latest_snap_date_str
            
            positions_to_insert = []
            
            for pos in res_pos.data:
                ticker = resolve_yf_symbol(pos.get('isin', ''), pos.get('name', ''))
                current_price = pos.get('last_price', 0.0)
                
                try:
                    if ticker:
                        import yfinance as yf
                        info = yf.Ticker(ticker).fast_info
                        if info.last_price: current_price = info.last_price
                except:
                    pass
                    
                qty = float(pos.get('quantity', 0.0))
                pru = float(pos.get('buying_price', 0.0))
                pos_amount = current_price * qty
                pos_var_amount = pos_amount - (pru * qty)
                pos_var_pct = ((current_price - pru) / pru) * 100 if pru > 0 else 0.0
                
                positions_to_insert.append({
                    "user_id": uid, "snapshot_date": latest_snap_date_str,
                    "snapshot_id": snap_id, "isin": pos.get('isin', ''), "name": pos.get('name', ''),
                    "type": pos.get('type', 'Action'), "quantity": qty, "buying_price": pru,
                    "last_price": current_price, "amount": pos_amount, 
                    "amount_variation": pos_var_amount, "variation": pos_var_pct, "weight": 0
                })
                valeur_titres += pos_amount
                plus_value_totale += pos_var_amount
                
            if positions_to_insert:
                total_valeur = valeur_titres + cash
                if is_same_day:
                    client.table("snapshot_positions").delete().eq("snapshot_id", snap_id).execute()
                    client.table("snapshot_positions").insert(positions_to_insert).execute()
                    client.table("snapshots").update({
                        "valeur_titres": round(valeur_titres, 2),
                        "plus_value": round(plus_value_totale, 2),
                        "total_valeur": round(total_valeur, 2)
                    }).eq("id", snap_id).execute()
                else:
                    new_snap = client.table("snapshots").insert({
                        "user_id": uid, "snapshot_date": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "cash": cash, "valeur_titres": round(valeur_titres, 2),
                        "plus_value": round(plus_value_totale, 2),
                        "cout_investi": cout_investi, "total_valeur": round(total_valeur, 2)
                    }).execute()
                    if new_snap.data:
                        new_snap_id = new_snap.data[0]['id']
                        new_date = new_snap.data[0]['snapshot_date']
                        for p in positions_to_insert: 
                            p["snapshot_id"] = new_snap_id
                            p["snapshot_date"] = new_date
                        client.table("snapshot_positions").insert(positions_to_insert).execute()
                        
            users_updated += 1
            import time
            time.sleep(1) # Prevent rate limiting on YF
            
        return {"status": "ok", "message": f"Global portfolio refresh triggered. Updated {users_updated} users."}
    except Exception as e:
        print(f"Cron error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/portfolio/upload")
async def upload_csv(file: UploadFile = File(...), auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    user_id = auth_context["user"].id
    
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
        'prix de revient': 'buying_price', 'pru': 'buying_price', 'buyingprice': 'buying_price',
        'dernier cours': 'last_price', 'lastprice': 'last_price',
        'montant': 'amount', 'valorisation': 'amount',
        '+/- value': 'amount_variation', 'plus/moins value': 'amount_variation', 'amountvariation': 'amount_variation',
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
            df[col] = df[col].astype(str).str.replace(r'\s+', '', regex=True).str.replace('€', '').str.replace('%', '').str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    if 'amount' not in df.columns and 'quantity' in df.columns and 'last_price' in df.columns:
        df['amount'] = df['quantity'] * df['last_price']
        
    snapshot_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    valeur_titres = float(df['amount'].sum()) if 'amount' in df.columns else 0.0
    
    res_cash = client.table("snapshots").select("cash").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
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
    res = client.table("snapshots").insert(snap_data).execute()
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
        client.table("snapshot_positions").insert(pos_data).execute()
        
    # Populer la table instruments avec les nouveautés
    instruments_to_upsert = []
    for _, row in df.iterrows():
        isin = row.get('isin', '')
        name = row.get('name', '')
        if isin:
            ticker = resolve_yf_symbol(isin, name)
            instruments_to_upsert.append({
                "isin": isin,
                "name": name,
                "ticker": ticker
            })
    if instruments_to_upsert:
        try:
            client.table("instruments").upsert(instruments_to_upsert, on_conflict="isin").execute()
        except:
            pass
        
    return {"status": "ok", "snapshot_id": snap_id}

from pydantic import BaseModel
from backend.services.ai_service import generate_financial_advice

class ChatRequest(BaseModel):
    messages: list

@app.post("/api/ai/chat")
async def ai_chat_endpoint(req: ChatRequest, auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, cash = fetch_user_data(client)
    
    res = generate_financial_advice(df, cash, req.messages)
    if "error" in res:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return res

@app.get("/api/portfolio/history")
async def get_portfolio_history(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    target_user_id = auth_context["user"].id

    try:
        res = client.table("snapshots").select("id, snapshot_date, total_valeur, valeur_titres, cash, cout_investi, plus_value").eq("user_id", target_user_id).order("snapshot_date", desc=False).execute()
        history = []
        if res.data:
            for row in res.data:
                date_str = str(row.get("snapshot_date", "") or "")
                total_val = float(row.get("total_valeur") or 0.0)
                val_titres = float(row.get("valeur_titres") or 0.0)
                cash = float(row.get("cash") or 0.0)
                cout_investi = float(row.get("cout_investi") or 0.0)
                plus_value = float(row.get("plus_value") or (total_val - cout_investi if cout_investi > 0 else 0.0))
                
                history.append({
                    "id": row.get("id"),
                    "snapshot_date": date_str,
                    "date": date_str.split(" ")[0] if " " in date_str else date_str.split("T")[0] if "T" in date_str else date_str,
                    "total_valeur": round(total_val, 2),
                    "valeur_titres": round(val_titres, 2),
                    "cash": round(cash, 2),
                    "cout_investi": round(cout_investi, 2),
                    "plus_value": round(plus_value, 2)
                })
        return {"history": history}
    except Exception as e:
        print(f"Error fetching history: {e}")
        return {"history": []}

@app.get("/api/portfolio/ai-diagnostic")
async def get_ai_diagnostic(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, _ = fetch_user_data(client)
    if df.empty: return {}
    df['yf_symbol'] = df['isin'] 
    return analyze_portfolio_global(df)

@app.get("/api/portfolio/weather")
async def get_portfolio_weather(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, _ = fetch_user_data(client)
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
async def refresh_portfolio(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    user_id = auth_context["user"].id
    
    # Récupérer le dernier snapshot
    res_snap = client.table("snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    if not res_snap.data: return {"status": "ok"}
    
    latest_snap = res_snap.data[0]
    snap_id = latest_snap['id']
    cash = float(latest_snap.get('cash', 0.0))
    cout_investi = float(latest_snap.get('cout_investi', 0.0))
    
    # Récupérer les positions
    res_pos = client.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
    if not res_pos.data: return {"status": "ok"}
    
    valeur_titres = 0.0
    plus_value_totale = 0.0
    
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    today_date = now.strftime("%Y-%m-%d")
    
    latest_snap_date_str = str(latest_snap.get('snapshot_date', ''))
    is_same_day = today_date in latest_snap_date_str
    
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
            try:
                import requests
                url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    current_price = data['chart']['result'][0]['meta'].get('regularMarketPrice', current_price)
            except:
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
        
        # Supprimer les champs auto de la DB
        if 'id' in pos: del pos['id']
        if 'created_at' in pos: del pos['created_at']
        
        positions_to_insert.append(pos)

    # Gestion de l'archivage temporel dans Supabase
    if not is_same_day:
        # Nouveau jour : créer un nouveau snapshot pour tracer l'historique sur la durée
        snap_data = {
            "user_id": user_id,
            "snapshot_date": now_str,
            "total_valeur": round(valeur_titres + cash, 2),
            "valeur_titres": round(valeur_titres, 2),
            "cash": cash,
            "cout_investi": cout_investi,
            "plus_value": round(plus_value_totale, 2),
            "source_filename": "Live Refresh Yahoo Finance"
        }
        res_new = client.table("snapshots").insert(snap_data).execute()
        target_snap_id = res_new.data[0]['id'] if res_new.data else snap_id
    else:
        # Même jour : mettre à jour le snapshot du jour
        target_snap_id = snap_id
        client.table("snapshots").update({
            "valeur_titres": round(valeur_titres, 2),
            "total_valeur": round(valeur_titres + cash, 2),
            "plus_value": round(plus_value_totale, 2),
            "snapshot_date": now_str
        }).eq("id", target_snap_id).execute()

    for p in positions_to_insert:
        p['snapshot_id'] = target_snap_id
        p['user_id'] = user_id
        p['snapshot_date'] = now_str
        
    if not is_same_day:
        client.table("snapshot_positions").insert(positions_to_insert).execute()
    else:
        client.table("snapshot_positions").delete().eq("snapshot_id", target_snap_id).execute()
        client.table("snapshot_positions").insert(positions_to_insert).execute()
    
    return {
        "status": "ok", 
        "message": "Cours en direct et historique mis à jour dans Supabase",
        "total_valeur": round(valeur_titres + cash, 2),
        "is_new_day_snapshot": not is_same_day
    }

try:
    from bourse_ai import analyze_stock_with_ai
except ImportError as e:
    print(f"Warning: Could not import bourse_ai. {e}")
    def analyze_stock_with_ai(*args, **kwargs): return {"error": "Import failed"}

@app.get("/api/stock/analyze/{ticker}")
async def analyze_stock(ticker: str, name: str = ""):
    resolved_ticker = ticker.strip()
    resolved_name = (name or ticker).strip()
    
    # 1. Try resolving symbol from known list
    direct_sym = resolve_yf_symbol("", resolved_ticker) or resolve_yf_symbol("", resolved_name)
    if direct_sym:
        resolved_ticker = direct_sym
    else:
        # 2. Search Yahoo Finance online for the ticker/name
        found_sym = search_yf_symbol_online(resolved_ticker) or search_yf_symbol_online(resolved_name)
        if found_sym:
            resolved_ticker = found_sym
            
    analysis = analyze_stock_with_ai(stock_name=resolved_name, yf_symbol=resolved_ticker)
    return analysis


import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from fastapi.responses import Response

@app.get("/api/portfolio/export/excel")
async def export_portfolio_excel(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    user_id = auth_context["user"].id
    
    res_snap = client.table("snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    snap = res_snap.data[0] if res_snap.data else {}
    snap_id = snap.get('id')
    
    positions = []
    if snap_id:
        res_pos = client.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
        positions = res_pos.data or []
        
    wb = openpyxl.Workbook()
    ws_pos = wb.active
    ws_pos.title = "Positions & Valorisation"
    ws_pos.views.sheetView[0].showGridLines = True
    
    header_fill = PatternFill(start_color="16191E", end_color="16191E", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="A3E635")
    align_center = Alignment(horizontal="center", vertical="center")
    
    headers = ["Titre", "ISIN / Ticker", "Secteur", "Quantité", "PRU (€)", "Cours Actuel (€)", "Montant Investi (€)", "Valeur Actuelle (€)", "+/- Value (€)", "Performance (%)"]
    ws_pos.append(headers)
    
    for col_num in range(1, len(headers) + 1):
        cell = ws_pos.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center
        
    for i, p in enumerate(positions, start=2):
        name = p.get('name', '')
        isin = p.get('ticker') or p.get('isin', '')
        sector = p.get('sector', 'Actions')
        qty = float(p.get('quantity', 0))
        pru = float(p.get('buying_price') or p.get('pru', 0))
        price = float(p.get('last_price') or p.get('current_price', 0))
        
        invested_formula = f"=D{i}*E{i}"
        val_formula = f"=D{i}*F{i}"
        gain_formula = f"=H{i}-G{i}"
        perf_formula = f"=IF(E{i}>0, (F{i}-E{i})/E{i}, 0)"
        
        ws_pos.append([name, isin, sector, qty, pru, price, invested_formula, val_formula, gain_formula, perf_formula])
        
        ws_pos.cell(row=i, column=4).number_format = '#,##0'
        ws_pos.cell(row=i, column=5).number_format = '#,##0.00 €'
        ws_pos.cell(row=i, column=6).number_format = '#,##0.00 €'
        ws_pos.cell(row=i, column=7).number_format = '#,##0.00 €'
        ws_pos.cell(row=i, column=8).number_format = '#,##0.00 €'
        ws_pos.cell(row=i, column=9).number_format = '+#,##0.00 €;-#,##0.00 €;0.00 €'
        ws_pos.cell(row=i, column=10).number_format = '+0.00%;-0.00%;0.00%'
        
    total_row = len(positions) + 2
    if len(positions) > 0:
        ws_pos.cell(row=total_row, column=1, value="TOTAL PORTEFEUILLE").font = Font(name="Arial", size=11, bold=True)
        ws_pos.cell(row=total_row, column=7, value=f"=SUM(G2:G{total_row-1})").font = Font(name="Arial", size=11, bold=True)
        ws_pos.cell(row=total_row, column=7).number_format = '#,##0.00 €'
        ws_pos.cell(row=total_row, column=8, value=f"=SUM(H2:H{total_row-1})").font = Font(name="Arial", size=11, bold=True)
        ws_pos.cell(row=total_row, column=8).number_format = '#,##0.00 €'
        ws_pos.cell(row=total_row, column=9, value=f"=H{total_row}-G{total_row}").font = Font(name="Arial", size=11, bold=True)
        ws_pos.cell(row=total_row, column=9).number_format = '+#,##0.00 €;-#,##0.00 €;0.00 €'
        ws_pos.cell(row=total_row, column=10, value=f"=IF(G{total_row}>0, I{total_row}/G{total_row}, 0)").font = Font(name="Arial", size=11, bold=True)
        ws_pos.cell(row=total_row, column=10).number_format = '+0.00%;-0.00%;0.00%'
    
    for col in ws_pos.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_pos.column_dimensions[col_letter].width = max(max_len + 4, 14)
        
    ws_fisc = wb.create_sheet(title="Synthèse Fiscale PEA")
    ws_fisc.views.sheetView[0].showGridLines = True
    ws_fisc.append(["Métrique Fiscale", "Valeur", "Commentaires"])
    for col_num in range(1, 4):
        ws_fisc.cell(row=1, column=col_num).fill = header_fill
        ws_fisc.cell(row=1, column=col_num).font = header_font
        
    cash = float(snap.get('cash', 0.0))
    ws_fisc.append(["Liquidités Disponibles (Espèces)", cash, "Disponibles pour arbitrage"])
    ws_fisc.cell(row=2, column=2).number_format = '#,##0.00 €'
    ws_fisc.append(["Plafond Légal de Versement", 150000.0, "Article L221-30 du CMF"])
    ws_fisc.cell(row=3, column=2).number_format = '#,##0.00 €'
    ws_fisc.append(["Total Versements Effectués", float(snap.get('cout_investi', 0.0)), "Total des apports en numéraire"])
    ws_fisc.cell(row=4, column=2).number_format = '#,##0.00 €'
    ws_fisc.append(["Capacité de Versement Restante", "=B3-B4", "Plafond restant à utiliser"])
    ws_fisc.cell(row=5, column=2).number_format = '#,##0.00 €'
    ws_fisc.append(["Régime Fiscal (Ancienneté > 5 ans)", "0,00 % IR", "Exonération totale d'impôt sur les plus-values"])
    ws_fisc.append(["Prélèvements Sociaux (CSG/CRDS)", "17,20 %", "Applicables uniquement lors des rachats"])
    
    for col in ws_fisc.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws_fisc.column_dimensions[col_letter].width = max(max_len + 5, 20)
        
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Export_PEA_Complet.xlsx"}
    )

from backend.services.price_service import sync_prices_for_instruments

@app.post("/api/jobs/sync-prices")
async def sync_prices(auth_context: dict = Depends(get_current_user)):
    # Should probably be protected by a service role key for cron, but we allow manual trigger for now
    client = auth_context["client"]
    results = sync_prices_for_instruments(client)
    return results
