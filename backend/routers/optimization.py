from fastapi import APIRouter, Depends
from backend.services.portfolio_service import fetch_user_data
from backend.services.optimization_service import scan_portfolio_fees
from backend.database import get_current_user

from typing import Optional

router = APIRouter(prefix="/api/optimization", tags=["optimization"])

@router.get("/fee-scan")
async def get_fee_scan(auth_context: dict = Depends(get_current_user)):
    client = auth_context["client"]
    df, cash = fetch_user_data(client)
    scan_results = scan_portfolio_fees(df)
    return scan_results
