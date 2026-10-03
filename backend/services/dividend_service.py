import yfinance as yf
from datetime import datetime, timedelta, timezone
import requests

from backend.database import supabase

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
        ticker = yf.Ticker(ticker_symbol, session=_yf_session)
        info = ticker.info
        
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
