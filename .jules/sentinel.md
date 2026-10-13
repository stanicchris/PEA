## 2024-05-28 - Missing Authentication on AI Analysis Endpoint
**Vulnerability:** The endpoint `/api/stock/analyze/{ticker}` in `backend/main.py` was missing authentication, allowing unauthenticated users to trigger AI analysis.
**Learning:** This could lead to resource exhaustion (API rate limits, billing) as the endpoint calls external services (Groq AI and Yahoo Finance) without verifying the user.
**Prevention:** Always use `Depends(get_current_user)` for any endpoint that consumes external API credits or performs non-trivial processing, even if it's primarily a GET request.
