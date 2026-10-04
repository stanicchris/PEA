import datetime
import pandas as pd

def calculate_xirr(transactions: list[dict], current_portfolio_value: float) -> float:
    """
    Calcule le Taux de Rendement Interne (XIRR) du portefeuille.
    transactions = list of dict with 'date' and 'amount' and 'type'.
    Seuls les DEPOSIT (positifs) et WITHDRAWAL (négatifs) sont utilisés.
    """
    cash_flows = []
    dates = []
    
    for t in transactions:
        if t["type"] == "DEPOSIT":
            cash_flows.append(float(t["amount"]))
            dates.append(pd.to_datetime(t["date"]).date())
        elif t["type"] == "WITHDRAWAL":
            cash_flows.append(-float(t["amount"]))
            dates.append(pd.to_datetime(t["date"]).date())
            
    if not cash_flows or sum(cash_flows) == 0:
        return 0.0
        
    # Ajouter la valeur actuelle comme un retrait théorique aujourd'hui
    cash_flows.append(-current_portfolio_value)
    dates.append(datetime.datetime.now().date())
    
    # Trier par date
    cf_dates = sorted(zip(dates, cash_flows), key=lambda x: x[0])
    sorted_dates = [x[0] for x in cf_dates]
    sorted_cfs = [x[1] for x in cf_dates]

    def xnpv(rate):
        if rate <= -1.0:
            return float('inf')
        d0 = sorted_dates[0]
        return sum([cf / (1.0 + rate)**((d - d0).days / 365.0) for cf, d in zip(sorted_cfs, sorted_dates)])

    def jacobian(rate):
        d0 = sorted_dates[0]
        return sum([-(d - d0).days / 365.0 * cf / (1.0 + rate)**(((d - d0).days / 365.0) + 1.0) for cf, d in zip(sorted_cfs, sorted_dates)])
        
    # Newton-Raphson method
    rate = 0.1
    for _ in range(100):
        fx = xnpv(rate)
        dx = jacobian(rate)
        if abs(dx) < 1e-8:
            break
        new_rate = rate - fx / dx
        if abs(new_rate - rate) < 1e-6:
            return new_rate
        rate = new_rate
        
    return rate

def get_performance_metrics(client, user_id: str, current_value: float):
    # Récupérer les transactions
    res_tx = client.table("transactions").select("*").eq("user_id", user_id).execute()
    transactions = res_tx.data if res_tx.data else []
    
    xirr_value = calculate_xirr(transactions, current_value)
    
    # Calculer le total investi net
    deposits = sum(t["amount"] for t in transactions if t["type"] == "DEPOSIT")
    withdrawals = sum(t["amount"] for t in transactions if t["type"] == "WITHDRAWAL")
    net_invested = deposits - withdrawals
    
    return {
        "xirr": round(xirr_value, 4),
        "net_invested": round(net_invested, 2),
        "total_deposits": round(deposits, 2),
        "total_withdrawals": round(withdrawals, 2)
    }
