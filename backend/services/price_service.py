import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def sync_prices_for_instruments(client):
    """
    Fetch closing prices from Yahoo Finance for all instruments in the database
    and insert/update them in prices_daily.
    Also updates instrument fundamentals.
    """
    res_inst = client.table("instruments").select("isin, ticker, name").execute()
    if not res_inst.data:
        return {"status": "no instruments"}
        
    instruments = res_inst.data
    results = {"updated": 0, "failed": 0, "errors": []}
    
    # We could batch fetch with yf.download(tickers_list), but let's keep it simple first
    # or use yf.Tickers
    tickers_list = [inst["ticker"] for inst in instruments if inst.get("ticker")]
    if not tickers_list:
        return {"status": "no tickers"}
        
    try:
        # Download last 5 days to ensure we get the latest close
        data = yf.download(tickers_list, period="5d", group_by="ticker")
    except Exception as e:
        return {"status": "error", "error": str(e)}
        
    prices_to_insert = []
    
    for inst in instruments:
        ticker = inst.get("ticker")
        isin = inst.get("isin")
        if not ticker:
            continue
            
        try:
            # If multiple tickers, data is a MultiIndex dataframe
            if len(tickers_list) > 1:
                ticker_data = data[ticker]
            else:
                ticker_data = data
                
            if ticker_data.empty:
                continue
                
            # Drop NaNs
            ticker_data = ticker_data['Close'].dropna()
            
            for date, close_price in ticker_data.items():
                if pd.isna(close_price):
                    continue
                # Date might be a timestamp
                date_str = date.strftime('%Y-%m-%d')
                
                prices_to_insert.append({
                    "isin": isin,
                    "date": date_str,
                    "close": float(close_price)
                })
                
        except Exception as e:
            results["failed"] += 1
            results["errors"].append(f"{ticker}: {str(e)}")
            
    if prices_to_insert:
        # Upsert prices
        # prices_daily has PK (isin, date)
        try:
            client.table("prices_daily").upsert(prices_to_insert).execute()
            results["updated"] += len(prices_to_insert)
        except Exception as e:
            results["error"] = f"DB Upsert Error: {str(e)}"
            
    return results
