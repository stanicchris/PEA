import yfinance as yf
from datetime import datetime
import time
import requests

# Custom session to fix "Invalid Crumb" 401 Unauthorized errors from Yahoo Finance
_yf_session = requests.Session()
_yf_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
})

# Simple in-memory cache to prevent rate-limiting from Yahoo Finance
_dividend_cache = {}
CACHE_TTL = 3600 * 12 # 12 hours

def get_upcoming_dividends(ticker_symbol: str):
    now = time.time()
    
    # Check cache
    if ticker_symbol in _dividend_cache:
        cached_data, timestamp = _dividend_cache[ticker_symbol]
        if now - timestamp < CACHE_TTL:
            return cached_data
            
    try:
        ticker = yf.Ticker(ticker_symbol, session=_yf_session)
        info = ticker.info
        
        ex_date_timestamp = info.get("exDividendDate")
        dividend_rate = info.get("dividendRate")
        
        if not dividend_rate:
            result = None
        else:
            ex_date = datetime.fromtimestamp(ex_date_timestamp).strftime('%Y-%m-%d') if ex_date_timestamp else None
            
            result = {
                "ex_date": ex_date,
                "amount": dividend_rate
            }
            
        _dividend_cache[ticker_symbol] = (result, now)
        return result
    except Exception as e:
        print(f"Error fetching dividend for {ticker_symbol}: {e}")
        # Cache failure for 1 hour to prevent spamming
        _dividend_cache[ticker_symbol] = (None, now - CACHE_TTL + 3600)
        return None

def get_dividend_history(ticker_symbol: str):
    """
    Fetches the historical dividends over the last year to project 12 months of payments.
    """
    try:
        ticker = yf.Ticker(ticker_symbol, session=_yf_session)
        info = ticker.info
        payout_ratio = info.get("payoutRatio", None)
        
        # Get last 1 year of dividends
        hist_div = ticker.dividends
        
        projected = {}
        if not hist_div.empty:
            # We assume the last 12 months repeat the same pattern for the next 12 months
            last_year = hist_div.tail(12)
            for date, amount in last_year.items():
                month = date.month
                projected[str(month)] = amount
                
        return {
            "payout_ratio": payout_ratio,
            "monthly_history": projected
        }
    except Exception as e:
        print(f"Error fetching dividend history for {ticker_symbol}: {e}")
        return {"payout_ratio": None, "monthly_history": {}}
