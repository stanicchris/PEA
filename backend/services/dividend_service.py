import yfinance as yf
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone

from backend.database import get_supabase_service_client

# Custom session to fix "Invalid Crumb" 401 Unauthorized errors from Yahoo Finance
_yf_session = requests.Session()
_yf_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
})

CACHE_TTL_DAYS = 7  # Refresh dividend data once a week

def _fetch_and_cache_dividend_data(ticker_symbol: str):
    """
    Fetches all dividend-related data (upcoming + history + payout ratio)
    and caches it in Supabase to avoid hitting Yahoo Finance repeatedly.
    """
    supabase = get_supabase_service_client()
    if supabase:
        try:
            res = supabase.table("dividend_data").select("*").eq("ticker_symbol", ticker_symbol).execute()
            if res.data:
                row = res.data[0]
                # Ensure last_updated is properly parsed (Supabase returns ISO with Z or +00:00)
                lu_str = row.get("last_updated", "")
                if lu_str.endswith("Z"):
                    lu_str = lu_str[:-1] + "+00:00"
                last_updated = datetime.fromisoformat(lu_str)
                age_days = (datetime.now(timezone.utc) - last_updated).days
                
                if age_days < CACHE_TTL_DAYS:
                    return row
        except Exception as e:
            print(f"Error reading from Supabase for {ticker_symbol}: {e}")

    # Not in DB or too old, fetch from yfinance
    try:
        import time
        # Anti rate-limit sleep for Render servers
        time.sleep(1.5)
        
        ticker = yf.Ticker(ticker_symbol, session=_yf_session)
        info = ticker.info
        
        # If info is completely empty or missing basic fields, Yahoo Finance is blocking us
        # Do not cache this response so we can try again later
        if not info or ("symbol" not in info and "shortName" not in info and "regularMarketPrice" not in info):
            print(f"Warning: yfinance returned empty info for {ticker_symbol}. Rate limited?")
            return {"payout_ratio": None, "monthly_history": {}}
            
        ex_date_timestamp = info.get("exDividendDate")
        amount = info.get("dividendRate")
        payout_ratio = info.get("payoutRatio")
        
        ex_date = None
        if ex_date_timestamp:
            ex_date = datetime.fromtimestamp(ex_date_timestamp).strftime('%Y-%m-%d')
            
        # Get history
        hist_div = ticker.dividends
        projected = {}
        if not hist_div.empty:
            now = datetime.now(timezone.utc)
            one_year_ago = now - timedelta(days=365)
            if hist_div.index.tz is None:
                one_year_ago = one_year_ago.replace(tzinfo=None)
            
            try:
                last_year = hist_div[hist_div.index >= one_year_ago]
            except Exception:
                last_year = hist_div.tail(4)
                
            for date, amt in last_year.items():
                projected[str(date.month)] = float(amt)
        else:
            # Fallback if historical chart data is empty or blocked by Yahoo,
            # but we still got the annual amount and ex_date from the basic info.
            if amount and ex_date:
                try:
                    # Place the entire annual dividend in the ex-date month as a fallback
                    month_str = str(datetime.strptime(ex_date, '%Y-%m-%d').month)
                    projected[month_str] = float(amount)
                except Exception:
                    pass

        data_to_save = {
            "ticker_symbol": ticker_symbol,
            "ex_date": ex_date,
            "amount": amount,
            "payout_ratio": payout_ratio,
            "monthly_history": projected,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        if supabase:
            try:
                supabase.table("dividend_data").upsert(data_to_save).execute()
            except Exception as e:
                print(f"Error saving to Supabase for {ticker_symbol}: {e}")
                
        return data_to_save
    except Exception as e:
        print(f"Error fetching from yfinance for {ticker_symbol}: {e}")
        # Try returning old data if exists
        try:
            if supabase and res and res.data:
                return res.data[0]
        except NameError:
            pass
        return None

def get_upcoming_dividends(ticker_symbol: str):
    data = _fetch_and_cache_dividend_data(ticker_symbol)
    if not data or not data.get("amount"):
        return None
    return {
        "ex_date": data.get("ex_date"),
        "amount": data.get("amount")
    }

def get_dividend_history(ticker_symbol: str):
    data = _fetch_and_cache_dividend_data(ticker_symbol)
    if not data:
        return {"payout_ratio": None, "monthly_history": {}}
    return {
        "payout_ratio": data.get("payout_ratio"),
        "monthly_history": data.get("monthly_history", {})
    }

def get_dividend_metrics(df: pd.DataFrame, client, user_id: str):
    """
    Calcule les métriques de dividendes :
    - Revenu annuel estimé (Estimated Annual Income)
    - Rendement moyen (Average Yield)
    - Yield on Cost (YoC) global
    - Score de sûreté (mock/simple)
    """
    if df.empty:
        return {
            "estimated_annual_income": 0.0,
            "average_yield": 0.0,
            "yield_on_cost": 0.0,
            "safety_score": 0,
            "positions": [],
            "received_dividends": []
        }

    total_value = float((df['quantity'] * df['current_price']).sum())
    total_invested = float((df['quantity'] * df['buying_price']).sum())

    total_income = 0.0
    positions_metrics = []
    
    try:
        res_tx = client.table("transactions").select("amount, isin, date").eq("user_id", user_id).eq("type", "DIVIDEND").execute()
        received_dividends = res_tx.data if res_tx.data else []
    except Exception:
        received_dividends = []

    for idx, row in df.iterrows():
        ticker = row.get('ticker')
        quantity = float(row.get('quantity', 0))
        current_price = float(row.get('current_price', 0))
        buying_price = float(row.get('buying_price', 0))
        
        position_value = quantity * current_price
        position_cost = quantity * buying_price
        
        annual_income = 0.0
        default_yield = 0.0
        safety = 50
        
        if ticker and str(ticker).strip() != 'None':
            # Use cached data if available
            div_data = _fetch_and_cache_dividend_data(ticker)
            if div_data and div_data.get('amount'):
                annual_income = quantity * float(div_data['amount'])
                default_yield = (annual_income / position_value) if position_value > 0 else 0
                total_income += annual_income
                
                payout = div_data.get('payout_ratio')
                if payout:
                    safety = max(0, min(100, 100 - (float(payout) * 100)))
                else:
                    safety = 70
        else:
            # Fallback estimation for missing tickers
            is_etf = row.get('sector') == 'ETF & Indice' or 'ETF' in str(row.get('name', ''))
            default_yield = 0.015 if is_etf else 0.0
            annual_income = position_value * default_yield
            total_income += annual_income
        
        yoc = (annual_income / position_cost) if position_cost > 0 else 0
        
        if annual_income > 0:
            positions_metrics.append({
                "ticker": ticker,
                "name": row.get('name'),
                "quantity": quantity,
                "annual_income": round(annual_income, 2),
                "yield": round(default_yield * 100, 2),
                "yield_on_cost": round(yoc * 100, 2),
                "safety_score": int(safety)
            })

    avg_yield = (total_income / total_value) if total_value > 0 else 0
    yoc_global = (total_income / total_invested) if total_invested > 0 else 0
    
    valid_safety = [p["safety_score"] for p in positions_metrics if p["safety_score"] > 0]
    avg_safety = sum(valid_safety) / len(valid_safety) if valid_safety else 0

    return {
        "estimated_annual_income": round(total_income, 2),
        "average_yield": round(avg_yield * 100, 2),
        "yield_on_cost": round(yoc_global * 100, 2),
        "safety_score": int(avg_safety),
        "positions": positions_metrics,
        "received_dividends": received_dividends
    }
