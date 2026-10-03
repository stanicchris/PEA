from fastapi import APIRouter
from backend.services.portfolio_service import fetch_user_data
from backend.services.optimization_service import scan_portfolio_fees

router = APIRouter(prefix="/api/optimization", tags=["optimization"])

@router.get("/fee-scan")
async def get_fee_scan(user_id: str):
    df, cash = fetch_user_data(user_id)
    scan_results = scan_portfolio_fees(df)
    return scan_results
