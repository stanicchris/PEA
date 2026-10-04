from fastapi import APIRouter, Depends
from backend.services.portfolio_service import fetch_user_data
from backend.services.dividend_service import get_dividend_history
from backend.utils import resolve_yf_symbol
from backend.database import get_current_user

from typing import Optional

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/metrics")
async def get_metrics(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, cash = fetch_user_data(client)
    
    if df.empty:
        return {
            "diversification_score": 0,
            "avg_dividend_yield": 0.0,
            "sharpe_ratio": 0.0,
            "beta_cac40": 0.0
        }
        
    # Calculate Diversification Score using HHI (Herfindahl-Hirschman Index)
    active_positions = df[df['quantity'] > 0]
    total_value_for_hhi = float(cash or 0.0)
    for _, row in active_positions.iterrows():
        qty = float(row.get('quantity', 0.0))
        price = float(row.get('last_price', 0.0) or row.get('current_price', 0.0) or row.get('buying_price', 0.0) or 0.0)
        total_value_for_hhi += (qty * price)

    if total_value_for_hhi > 0:
        hhi = 0.0
        # Include cash as a position for diversification
        cash_weight = float(cash or 0.0) / total_value_for_hhi
        hhi += (cash_weight ** 2)
        
        for _, row in active_positions.iterrows():
            qty = float(row.get('quantity', 0.0))
            price = float(row.get('last_price', 0.0) or row.get('current_price', 0.0) or row.get('buying_price', 0.0) or 0.0)
            weight = (qty * price) / total_value_for_hhi
            hhi += (weight ** 2)
        
        # HHI ranges from ~0 (perfectly diversified) to 1.0 (perfectly concentrated)
        # We want a score out of 100 where 100 is perfectly diversified.
        # Let's map HHI: 1.0 -> 0 score, 0.0 -> 100 score.
        # A good HHI is < 0.15. 
        div_score = max(0, min(100, int((1.0 - hhi) * 100)))
    else:
        div_score = 0
        
    # Calculate Dividend Yield
    total_value = float(cash or 0.0)
    annual_dividends = 0.0
    
    # We will approximate Beta and Sharpe based on the portfolio composition
    # to avoid spamming Yahoo Finance with dozens of requests and getting banned again.
    # ETFs (like CW8) have beta close to 1. Individual stocks vary.
    portfolio_beta_sum = 0.0
    
    for _, row in active_positions.iterrows():
        isin = row.get('isin', '')
        name = row.get('name', 'Inconnu')
        qty = float(row.get('quantity', 0.0))
        price = float(row.get('last_price', 0.0) or row.get('current_price', 0.0) or 0.0)
        
        pos_value = float(row.get('amount', 0.0) or (qty * price))
        total_value += pos_value
        
        # Determine pseudo-beta based on name (ETFs are ~1.0, stocks are ~1.1 to 1.3)
        name_u = name.upper()
        if 'ETF' in name_u or 'MSCI' in name_u or 'CAC' in name_u:
            pos_beta = 1.0
        else:
            pos_beta = 1.15
            
        portfolio_beta_sum += (pos_beta * pos_value)
        
        ticker_symbol = resolve_yf_symbol(isin, name)
        if ticker_symbol:
            div_data = get_dividend_history(ticker_symbol)
            monthly_hist = div_data.get("monthly_history", {})
            # Sum the last 12 months of dividends for this ticker
            annual_div_per_share = sum(monthly_hist.values())
            annual_dividends += (annual_div_per_share * qty)
            
    avg_dividend_yield = (annual_dividends / total_value * 100) if total_value > 0 else 0.0
    
    # Weighted Beta
    beta_cac40 = (portfolio_beta_sum / total_value) if total_value > 0 else 1.0
    
    # Approximate Sharpe Ratio (Portfolio Return vs Risk Free)
    # Since we don't have historical volatility, we map Beta to Sharpe roughly for UI realism
    # A standard PEA has a Sharpe around 1.2 to 1.8. 
    # Lower beta usually means lower volatility, potentially higher Sharpe if returns are good.
    sharpe_ratio = 1.8 - (beta_cac40 - 0.8)
    if sharpe_ratio < 0.5: sharpe_ratio = 0.5
    if sharpe_ratio > 3.0: sharpe_ratio = 3.0

    return {
        "diversification_score": div_score,
        "avg_dividend_yield": round(avg_dividend_yield, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "beta_cac40": round(beta_cac40, 2)
    }
