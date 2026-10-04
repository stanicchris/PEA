import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import get_supabase_service_client

load_dotenv()

def run_migration():
    client = get_supabase_service_client()
    if not client:
        print("Erreur: Supabase client non initialisé.")
        return

    # 1. Fetch all users who have snapshots
    res_users = client.table("snapshots").select("user_id").execute()
    if not res_users.data:
        print("Aucun snapshot trouvé.")
        return
        
    user_ids = list(set([row["user_id"] for row in res_users.data]))
    print(f"Trouvé {len(user_ids)} utilisateurs à migrer.")
    
    for uid in user_ids:
        print(f"Migration pour l'utilisateur {uid}...")
        
        # Check if an account already exists
        res_acc = client.table("accounts").select("id").eq("user_id", uid).limit(1).execute()
        if res_acc.data:
            print(f"  Compte déjà existant pour {uid}, on passe.")
            continue
            
        # Get earliest snapshot date to use as opened_at
        res_first_snap = client.table("snapshots").select("snapshot_date").eq("user_id", uid).order("snapshot_date", desc=False).limit(1).execute()
        opened_at = res_first_snap.data[0]["snapshot_date"].split("T")[0] if res_first_snap.data else None
        
        # Create a default PEA account
        acc_data = {
            "user_id": uid,
            "type": "PEA",
            "label": "PEA Principal",
            "opened_at": opened_at
        }
        res_new_acc = client.table("accounts").insert(acc_data).execute()
        account_id = res_new_acc.data[0]["id"]
        
        # Get latest snapshot to build current positions
        res_latest = client.table("snapshots").select("*").eq("user_id", uid).order("snapshot_date", desc=True).limit(1).execute()
        if not res_latest.data:
            continue
            
        snap = res_latest.data[0]
        snap_id = snap["id"]
        cash = float(snap.get("cash") or 0.0)
        
        # Insert initial DEPOSIT transaction for cash
        if cash > 0:
            client.table("transactions").insert({
                "user_id": uid,
                "account_id": account_id,
                "date": snap["snapshot_date"],
                "type": "DEPOSIT",
                "amount": cash,
                "currency": "EUR",
                "note": "Migration: Cash initial"
            }).execute()
            
        # Get positions
        res_pos = client.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
        if not res_pos.data:
            continue
            
        transactions = []
        instruments = {}
        for pos in res_pos.data:
            qty = float(pos.get("quantity", 0.0))
            if qty <= 0: continue
            
            pru = float(pos.get("buying_price", 0.0))
            total_invested = qty * pru
            
            transactions.append({
                "user_id": uid,
                "account_id": account_id,
                "date": snap["snapshot_date"],
                "type": "BUY",
                "isin": pos.get("isin"),
                "quantity": qty,
                "price": pru,
                "amount": total_invested,
                "fees": 0,
                "currency": "EUR",
                "note": "Migration: Achat initial"
            })
            
            if pos.get("isin"):
                instruments[pos["isin"]] = {
                    "isin": pos["isin"],
                    "name": pos.get("name")
                }
                
        if transactions:
            # Upsert instruments (basic info only, detailed info will be fetched by price job)
            for isin, inst in instruments.items():
                try:
                    client.table("instruments").upsert(inst).execute()
                except Exception as e:
                    print(f"  Warning: Could not upsert instrument {isin}: {e}")
            
            # Insert transactions
            client.table("transactions").insert(transactions).execute()
            
        print(f"  Migration terminée pour {uid}: {len(transactions)} transactions créées.")

if __name__ == "__main__":
    run_migration()
