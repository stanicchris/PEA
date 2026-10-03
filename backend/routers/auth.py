from fastapi import APIRouter, HTTPException
from backend.database import supabase
from backend.schemas import AuthRequest
from backend.utils import to_synthetic_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login")
async def login(req: AuthRequest):
    if not supabase:
        raise HTTPException(status_code=500, detail="Configuration Supabase manquante dans le backend (.env).")
    try:
        email = to_synthetic_email(req.username)
        res = supabase.auth.sign_in_with_password({"email": email, "password": req.password})
        return {"user_id": res.user.id, "username": req.username, "access_token": res.session.access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Identifiants incorrects.")

@router.post("/register")
async def register(req: AuthRequest):
    if not supabase:
        raise HTTPException(status_code=500, detail="Configuration Supabase manquante.")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Le mot de passe doit faire au moins 6 caractères.")
    try:
        email = to_synthetic_email(req.username)
        res = supabase.auth.sign_up({"email": email, "password": req.password})
        return {"user_id": res.user.id, "username": req.username, "access_token": res.session.access_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
