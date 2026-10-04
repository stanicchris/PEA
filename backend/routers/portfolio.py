from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from backend.services.portfolio_service import fetch_user_data
from backend.services.dividend_service import get_upcoming_dividends
from backend.utils import resolve_yf_symbol
from backend.database import get_current_user

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

@router.get("/dividends")
async def get_dividends(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, cash = fetch_user_data(client)
    if df.empty:
        return {"dividends": []}
        
    upcoming = []
    
    for _, row in df.iterrows():
        name = row.get('name', 'Inconnu')
        isin = row.get('isin', '')
        quantity = float(row.get('quantity', 0.0))
        buying_price = float(row.get('buying_price', 0.0))
        
        if quantity <= 0:
            continue
            
        ticker_symbol = resolve_yf_symbol(isin, name)
        if not ticker_symbol:
            continue
            
        div_info = get_upcoming_dividends(ticker_symbol)
        
        if div_info and div_info["amount"] and div_info["ex_date"]:
            amount_per_share = float(div_info["amount"])
            projected_total = amount_per_share * quantity
            
            # calculate yield on cost
            yield_on_cost = None
            if buying_price > 0:
                yield_on_cost = (amount_per_share / buying_price) * 100
                
            upcoming.append({
                "name": name,
                "isin": isin,
                "ticker": ticker_symbol,
                "ex_date": div_info["ex_date"],
                "amount_per_share": round(amount_per_share, 2),
                "quantity": quantity,
                "projected_total": round(projected_total, 2),
                "yield_on_cost": round(yield_on_cost, 2) if yield_on_cost else None
            })
            
    # Sort by ex_date ascending
    upcoming.sort(key=lambda x: x["ex_date"])
    
    return {"dividends": upcoming}
