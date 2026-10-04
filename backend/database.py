import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_KEY") # Current fallback

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_supabase_service_client() -> Client:
    """Returns a Supabase client with the service_role key, bypassing RLS."""
    return create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates the JWT token and returns a request-scoped Supabase client."""
    if not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Missing SUPABASE_ANON_KEY")
        
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    try:
        # Depending on supabase-python version, we might just need to pass the access token
        client.auth.set_session(access_token=token, refresh_token="")
        user = client.auth.get_user()
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return {"user": user.user, "client": client}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )
