import yfinance as yf
from datetime import datetime
import time

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
        ticker = yf.Ticker(ticker_symbol)
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
