from fastapi import APIRouter
from backend.services.portfolio_service import fetch_user_data
from backend.services.dividend_service import get_dividend_history
from backend.utils import resolve_yf_symbol
from datetime import datetime

router = APIRouter(prefix="/api/goals", tags=["goals"])

@router.get("/projections")
async def get_projections(user_id: str):
    df, cash = fetch_user_data(user_id)
    
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
            
        ticker_symbol = resolve_yf_symbol(isin)
        if not ticker_symbol:
            continue
            
        div_data = get_dividend_history(ticker_symbol)
        monthly_hist = div_data.get("monthly_history", {})
        payout_ratio = div_data.get("payout_ratio")
        
        # Calculate safety
        if payout_ratio is not None and len(monthly_hist) > 0:
            # Assuming lower payout ratio is safer (usually < 0.6 is good, > 1.0 is bad)
            safety_score = 100 - min(100, payout_ratio * 100)
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
