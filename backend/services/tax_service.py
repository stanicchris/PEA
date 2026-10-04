from datetime import datetime
from dateutil.relativedelta import relativedelta

def get_pea_tax_status(client, user_id: str):
    """
    Récupère le statut fiscal du PEA : horloge fiscale (5 ans), plafond légal, etc.
    """
    # 1. Obtenir la date d'ouverture du PEA
    res_acc = client.table("accounts").select("opened_at").eq("user_id", user_id).eq("type", "PEA").limit(1).execute()
    
    if not res_acc.data or not res_acc.data[0].get("opened_at"):
        # Par défaut, aujourd'hui si non défini
        opened_at = datetime.now().date()
    else:
        try:
            opened_at = datetime.strptime(res_acc.data[0]["opened_at"], "%Y-%m-%d").date()
        except Exception:
            opened_at = datetime.now().date()
            
    maturity_date = opened_at + relativedelta(years=5)
    now_date = datetime.now().date()
    
    days_to_maturity = (maturity_date - now_date).days
    is_mature = days_to_maturity <= 0
    
    # Plafond légal pour un PEA classique = 150 000 € de versements
    legal_limit = 150000.0
    
    # 2. Obtenir les versements nets depuis performance_service via main
    # Ou les recalculer ici
    res_tx = client.table("transactions").select("type, amount").eq("user_id", user_id).execute()
    deposits = sum(t["amount"] for t in res_tx.data if t["type"] == "DEPOSIT") if res_tx.data else 0
    withdrawals = sum(t["amount"] for t in res_tx.data if t["type"] == "WITHDRAWAL") if res_tx.data else 0
    
    net_invested = deposits - withdrawals
    capacity_left = legal_limit - net_invested
    
    # Prélèvements sociaux en vigueur (ex: 18.6%)
    # On pourrait requêter la table tax_rules, mais pour simplifier on le met ici ou on l'interroge
    social_taxes = 18.6
    
    return {
        "opened_at": opened_at.strftime("%Y-%m-%d"),
        "maturity_date": maturity_date.strftime("%Y-%m-%d"),
        "days_to_maturity": max(0, days_to_maturity),
        "is_mature": is_mature,
        "net_invested": round(net_invested, 2),
        "legal_limit": legal_limit,
        "capacity_left": round(capacity_left, 2),
        "social_taxes_pct": social_taxes
    }

def simulate_withdrawal(net_invested: float, current_value: float, withdrawal_amount: float, is_mature: bool):
    """
    Simulateur de retrait officiel.
    Part imposable du retrait = Montant du retrait * (Gain Net / Valeur Actuelle)
    """
    if current_value <= 0 or withdrawal_amount <= 0:
        return {"imposable_base": 0, "social_taxes": 0, "income_taxes": 0, "net_withdrawal": withdrawal_amount}
        
    total_gain = current_value - net_invested
    if total_gain <= 0:
        # Moins-value = pas d'impôt
        return {"imposable_base": 0, "social_taxes": 0, "income_taxes": 0, "net_withdrawal": withdrawal_amount}
        
    taxable_ratio = total_gain / current_value
    taxable_base = withdrawal_amount * taxable_ratio
    
    social_taxes = taxable_base * 0.186
    
    # PFU (12.8%) + clôture si < 5 ans, sinon 0%
    income_taxes = taxable_base * 0.128 if not is_mature else 0.0
    
    net_withdrawal = withdrawal_amount - social_taxes - income_taxes
    
    return {
        "withdrawal_amount": withdrawal_amount,
        "taxable_base": round(taxable_base, 2),
        "social_taxes": round(social_taxes, 2),
        "income_taxes": round(income_taxes, 2),
        "net_withdrawal": round(net_withdrawal, 2),
        "closes_account": not is_mature
    }
