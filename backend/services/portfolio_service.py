import pandas as pd
from backend.database import supabase

def fetch_user_data(user_id: str):
    if not supabase: return pd.DataFrame(), 0.0
    res_snap = supabase.table("snapshots").select("*").eq("user_id", user_id).order("snapshot_date", desc=True).limit(1).execute()
    
    cash = 0.0
    latest_snap = res_snap.data[0] if (res_snap and res_snap.data) else None
    
    if latest_snap and latest_snap.get('cash') is not None:
        try:
            cash = float(latest_snap.get('cash', 0.0) or 0.0)
        except Exception:
            cash = 0.0
    else:
        try:
            res_settings = supabase.table("user_settings").select("cash").eq("user_id", user_id).limit(1).execute()
            if res_settings.data and res_settings.data[0].get('cash') is not None:
                cash = float(res_settings.data[0]['cash'] or 0.0)
        except Exception:
            pass

    if not latest_snap:
        return pd.DataFrame(), cash
    
    snap_id = latest_snap['id']
    res_pos = supabase.table("snapshot_positions").select("*").eq("snapshot_id", snap_id).execute()
    df = pd.DataFrame(res_pos.data) if (res_pos and res_pos.data) else pd.DataFrame()
    return df, cash
