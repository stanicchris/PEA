from fastapi import APIRouter, Depends
from backend.services.portfolio_service import fetch_user_data
from backend.services.dividend_service import get_dividend_history
from backend.utils import resolve_yf_symbol
from backend.database import get_current_user
from datetime import datetime

from typing import Optional

router = APIRouter(prefix="/api/goals", tags=["goals"])

@router.get("/projections")
async def get_projections(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, cash = fetch_user_data(client)
    
    if df.empty:
        return {"monthly_projections": {}, "safety_scores": [], "total_projected_year": 0.0}
        
    monthly_projections = {str(i): 0.0 for i in range(1, 13)}
    safety_scores = []
    total_projected_year = 0.0
    
    for _, row in df.iterrows():
        isin = row.get('isin', '')
        name = row.get('name', 'Inconnu')
        quantity = float(row.get('quantity', 0.0))
        
        if quantity <= 0:
            continue
            
        ticker_symbol = resolve_yf_symbol(isin, name)
        if not ticker_symbol:
            continue
            
        div_data = get_dividend_history(ticker_symbol)
        monthly_hist = div_data.get("monthly_history", {})
        payout_ratio = div_data.get("payout_ratio")
        
        # Calculate safety
        if payout_ratio is not None and len(monthly_hist) > 0:
            pr = float(payout_ratio)
            if pr < 0:
                safety_score = 0.0
            elif pr <= 0.6:
                safety_score = 100.0 - (pr / 0.6) * 30.0
            elif pr <= 0.85:
                safety_score = 70.0 - ((pr - 0.6) / 0.25) * 20.0
            elif pr <= 1.0:
                safety_score = 50.0 - ((pr - 0.85) / 0.15) * 30.0
            else:
                safety_score = max(0.0, 20.0 - (pr - 1.0) * 20.0)

            safety_scores.append({
                "isin": isin,
                "name": name,
                "payout_ratio": payout_ratio,
                "score": round(safety_score, 1)
            })
        
        # Map to next 12 months (simplified, assumes same payout months)
        for month_str, amount in monthly_hist.items():
            if amount > 0:
                expected_total = amount * quantity
                monthly_projections[month_str] += expected_total
                total_projected_year += expected_total
                
    # Sort safety scores from best to worst
    safety_scores.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "monthly_projections": {k: round(v, 2) for k, v in monthly_projections.items()},
        "safety_scores": safety_scores,
        "total_projected_year": round(total_projected_year, 2)
    }
