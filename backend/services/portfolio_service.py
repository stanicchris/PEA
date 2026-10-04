import pandas as pd
from supabase import Client

def fetch_user_data(client: Client):
    if not client: return pd.DataFrame(), 0.0
    
    latest_snap = None
    try:
        # RLS automatically filters to the user's snapshots
        res_snap = client.table("snapshots").select("*").order("snapshot_date", desc=True).limit(1).execute()
        if res_snap and res_snap.data:
            latest_snap = res_snap.data[0]
    except Exception as e:
        print(f"Error querying snapshot: {e}")
            
    cash = 0.0
    if latest_snap and latest_snap.get('cash') is not None:
        try:
            cash = float(latest_snap.get('cash', 0.0) or 0.0)
        except Exception:
            cash = 0.0
    else:
        try:
            res_settings = client.table("user_settings").select("cash").limit(1).execute()
            if res_settings.data and res_settings.data[0].get('cash') is not None:
                cash = float(res_settings.data[0]['cash'] or 0.0)
        except Exception:
            pass

    if not latest_snap:
        return pd.DataFrame(), cash
    
    snap_id = latest_snap['id']
    res_pos = client.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
    df = pd.DataFrame(res_pos.data) if (res_pos and res_pos.data) else pd.DataFrame()
    return df, cash
