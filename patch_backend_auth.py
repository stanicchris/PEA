import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
if 'HTTPBearer' not in content:
    content = content.replace('from fastapi import FastAPI, HTTPException, BackgroundTasks', 
                              'from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header\nfrom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials')

# 2. Update login & register to return access_token
content = content.replace('return {"user_id": res.user.id, "username": req.username}', 
                          'return {"user_id": res.user.id, "username": req.username, "access_token": res.session.access_token}')

# 3. Add get_current_user dependency
dependency_code = '''
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        res = supabase.auth.get_user(credentials.credentials)
        if not res or not res.user:
            raise HTTPException(status_code=401, detail="Token invalide")
        return res.user.id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Non autorisé: {str(e)}")
'''
if 'security = HTTPBearer()' not in content:
    content = content.replace('@app.post("/api/auth/login")', dependency_code + '\n@app.post("/api/auth/login")')

# 4. Replace `user_id: str` with `user_id: str = Depends(get_current_user)` in all protected endpoints
endpoints = [
    'async def get_portfolio_summary(user_id: str):',
    'async def get_portfolio_positions(user_id: str):',
    'async def get_portfolio_history(user_id: str):',
    'async def get_ai_diagnostic(user_id: str):',
    'async def get_portfolio_weather(user_id: str):',
    'async def refresh_portfolio(user_id: str):'
]
for ep in endpoints:
    content = content.replace(ep, ep.replace('user_id: str', 'user_id: str = Depends(get_current_user)'))

# For upload and cash, it's inside Form() or body.
# For upload: async def upload_csv(file: UploadFile = File(...), user_id: str = Form(...)):
content = content.replace('user_id: str = Form(...)', 'user_id: str = Depends(get_current_user)')

# For cash: async def update_cash(req: CashRequest): 
# we need to add user_id inside the function, or extract it.
# Let's change CashRequest to not require user_id, and pass user_id as dependency.
content = content.replace('class CashRequest(BaseModel):\n    user_id: str\n    cash: float', 'class CashRequest(BaseModel):\n    cash: float')
content = content.replace('async def update_cash(req: CashRequest):', 'async def update_cash(req: CashRequest, user_id: str = Depends(get_current_user)):')
content = content.replace('req.user_id', 'user_id')

# 5. Update CORS
cors_code = '''
import os
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
'''
content = re.sub(r'app\.add_middleware\([\s\S]*?allow_headers=\["\*"\]\,\n\)', cors_code.strip(), content)

with open('backend/main.py', 'w', encoding='utf-8') as f:
    f.write(content)
