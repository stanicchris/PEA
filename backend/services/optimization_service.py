import pandas as pd

# Static database of known TERs for popular PEA eligible ETFs
# Key: ISIN
ETF_TER_DB = {
    "LU1681043599": {"name": "Amundi MSCI World UCITS ETF (CW8)", "ter": 0.38, "alternative_isin": "IE0002XZSHO1", "alternative_name": "iShares MSCI World Swap PEA UCITS ETF", "alternative_ter": 0.25},
    "IE0002XZSHO1": {"name": "iShares MSCI World Swap PEA UCITS ETF (WPEA)", "ter": 0.25, "alternative_isin": None, "alternative_name": None, "alternative_ter": None},
    "LU1681045537": {"name": "Amundi PEA S&P 500 (PSP5)", "ter": 0.15, "alternative_isin": "FR0011550185", "alternative_name": "BNP Paribas Easy S&P 500 UCITS ETF", "alternative_ter": 0.15},
    "FR0011550185": {"name": "BNP Paribas Easy S&P 500 UCITS ETF (ESE)", "ter": 0.15, "alternative_isin": None, "alternative_name": None, "alternative_ter": None},
    "LU1861136247": {"name": "Amundi STOXX Europe 600", "ter": 0.18, "alternative_isin": None, "alternative_name": None, "alternative_ter": None},
    "LU1834983477": {"name": "Amundi MSCI Emerging Markets", "ter": 0.20, "alternative_isin": None, "alternative_name": None, "alternative_ter": None},
    "FR0013412020": {"name": "Amundi MSCI Water", "ter": 0.60, "alternative_isin": None, "alternative_name": None, "alternative_ter": None},
    "FR0011550193": {"name": "BNP Paribas Easy STOXX Europe 600 UCITS ETF", "ter": 0.18, "alternative_isin": None, "alternative_name": None, "alternative_ter": None},
    "LU1681045370": {"name": "Amundi PEA Nasdaq-100", "ter": 0.30, "alternative_isin": None, "alternative_name": None, "alternative_ter": None}
}

def scan_portfolio_fees(df: pd.DataFrame):
    """
    Scans the user's portfolio and checks ETF TERs against the static DB.
    Flags TER > 0.35% and returns suggested alternatives if available.
    """
    if df.empty:
        return {"scanned_assets": [], "total_annual_fees": 0.0, "total_potential_savings": 0.0}
        
    scanned = []
    total_fees = 0.0
    total_savings = 0.0
    
    for _, row in df.iterrows():
        isin = row.get('isin', '')
        name = row.get('name', 'Inconnu')
        quantity = float(row.get('quantity', 0.0))
        value = float(row.get('amount', 0.0) or (quantity * float(row.get('last_price', 0.0) or 0.0)))
        
        if value <= 0:
            continue
            
        # Only check known ETFs in our DB
        if isin in ETF_TER_DB:
            etf_data = ETF_TER_DB[isin]
            ter = etf_data["ter"]
            annual_fee_euros = (value * ter) / 100
            total_fees += annual_fee_euros
            
            is_high_fee = ter > 0.35
            
            alternative = None
            if etf_data["alternative_isin"]:
                alt_ter = etf_data["alternative_ter"]
                potential_savings = annual_fee_euros - ((value * alt_ter) / 100)
                total_savings += max(0, potential_savings)
                
                alternative = {
                    "isin": etf_data["alternative_isin"],
                    "name": etf_data["alternative_name"],
                    "ter": alt_ter,
                    "savings_euros": round(potential_savings, 2)
                }
            
            scanned.append({
                "isin": isin,
                "name": name,
                "value": round(value, 2),
                "ter": ter,
                "annual_fee_euros": round(annual_fee_euros, 2),
                "is_high_fee": is_high_fee,
                "alternative": alternative
            })
            
    # Sort by highest fees first
    scanned.sort(key=lambda x: x["annual_fee_euros"], reverse=True)
    
    return {
        "scanned_assets": scanned,
        "total_annual_fees": round(total_fees, 2),
        "total_potential_savings": round(total_savings, 2)
    }
