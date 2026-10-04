from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.database import get_current_user

router = APIRouter()

class WatchlistItemCreate(BaseModel):
    ticker: str
    name: Optional[str] = None
    target_price: Optional[float] = None

class WatchlistItemUpdate(BaseModel):
    target_price: float

@router.get("/")
def get_watchlist(user=Depends(get_current_user)):
    user_id = user["user"].id
    client = user["client"]
    res = client.table("watchlist").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data

@router.post("/")
def add_to_watchlist(item: WatchlistItemCreate, user=Depends(get_current_user)):
    user_id = user["user"].id
    client = user["client"]
    
    # Check if already exists
    existing = client.table("watchlist").select("*").eq("user_id", user_id).eq("ticker", item.ticker).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Action déjà dans la watchlist")
        
    data = {
        "user_id": user_id,
        "ticker": item.ticker,
        "name": item.name,
        "target_price": item.target_price
    }
    res = client.table("watchlist").insert(data).execute()
    if res.data:
        return res.data[0]
    return {}

@router.patch("/{id}")
def update_watchlist(id: str, item: WatchlistItemUpdate, user=Depends(get_current_user)):
    user_id = user["user"].id
    client = user["client"]
    res = client.table("watchlist").update({"target_price": item.target_price}).eq("id", id).eq("user_id", user_id).execute()
    if res.data:
        return res.data[0]
    return {}

@router.delete("/{id}")
def delete_from_watchlist(id: str, user=Depends(get_current_user)):
    user_id = user["user"].id
    client = user["client"]
    client.table("watchlist").delete().eq("id", id).eq("user_id", user_id).execute()
    return {"success": True}
