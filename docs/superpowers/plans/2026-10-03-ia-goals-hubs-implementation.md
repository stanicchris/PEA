# IA & Objectifs Hubs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformer l'application en un véritable assistant patrimonial en créant deux nouveaux onglets : "Optimisation & IA" et "Objectifs & Rente".

**Architecture:** Extraction des vues lourdes (IA, Analytics) hors du composant principal `App.vue` vers des sous-composants dédiés. Création de routeurs backend séparés (`optimization.py`, `goals.py`) pour alléger le charge cognitive et structurer les futurs développements.

**Tech Stack:** Vue 3 (Composition API), FastAPI, yfinance, requests.

**Spec:** `docs/superpowers/specs/2026-10-03-ia-goals-hubs-design.md`

## Global Constraints

- Vue 3: Use script setup and Composition API.
- TailwindCSS for styling.
- Backend modules should not introduce circular dependencies. Use `APIRouter` in separate files.
- `yfinance` requests must use the custom session with a user-agent to bypass 401 Crumb errors.

## Review Focus

- Invalid ticker symbols causing Yahoo Finance to crash instead of failing gracefully.
- Dividend history missing for certain stocks causing `MonthlyDividendProjection` to throw undefined errors.
- Missing TER values in the ETF Dictionary gracefully degrading instead of blocking the `FeeScanner`.
- Extreme values in the Fire Simulator (e.g. 0€ savings or 100% yield) causing infinity/NaN graph projections.

---

### Task 1: Scaffolding Routing and Views (Frontend)

**Files:**
- Modify: `src/App.vue`
- Create: `src/views/OptimizationView.vue`
- Create: `src/views/GoalsView.vue`

**Interfaces:**
- Consumes: The `activeTab` ref in `App.vue`.
- Produces: Two new empty views capable of hosting the new components.

- [ ] **Step 1: Write OptimizationView.vue placeholder**
Create a Vue component `src/views/OptimizationView.vue` with a simple title to ensure routing works.

- [ ] **Step 2: Write GoalsView.vue placeholder**
Create a Vue component `src/views/GoalsView.vue` with a simple title.

- [ ] **Step 3: Update App.vue routing**
Modify `App.vue` to import and render `OptimizationView` when `activeTab === 'optimization'` and `GoalsView` when `activeTab === 'goals'`. Update the Navigation Bar to include these two new tabs.

- [ ] **Step 4: Commit**
`git add src/App.vue src/views/ && git commit -m "feat(frontend): setup views and navigation for new hubs"`

---

### Task 2: Optimization Hub - Backend & Data

**Files:**
- Create: `backend/routers/optimization.py`
- Create: `backend/services/optimization_service.py`
- Modify: `backend/main.py`

**Interfaces:**
- Produces: `GET /api/optimization/fee-scan` returning a list of assets with their TER and a suggested alternative if TER > 0.35%.

- [ ] **Step 1: Implement `optimization_service.py`**
Create a static dictionary mapping common PEA ETF ISINs (Amundi, BNP) to their TERs (e.g., CW8 = 0.38%, WPEA = 0.25%). Write a function `scan_portfolio_fees(portfolio_df)` that flags TERs > 0.35%.

- [ ] **Step 2: Implement `routers/optimization.py`**
Create the router with `GET /fee-scan` that uses `fetch_user_data` and returns the optimization payload.

- [ ] **Step 3: Register router in `main.py`**
Add `app.include_router(optimization.router)` in `main.py`.

- [ ] **Step 4: Commit**
`git add backend/ && git commit -m "feat(backend): add optimization service and router"`

---

### Task 3: Optimization Hub - Frontend

**Files:**
- Modify: `src/views/OptimizationView.vue`
- Create: `src/components/FeeScanner.vue`
- Modify: `src/App.vue`

**Interfaces:**
- Consumes: `GET /api/optimization/fee-scan`

- [ ] **Step 1: Build `FeeScanner.vue` component**
Create the UI fetching the fee data and displaying a warning for high-TER ETFs and listing suggested alternatives.

- [ ] **Step 2: Move AI components to Optimization Hub**
Move `<GroqAiHighlightCard>` and `<AiAdvisorWidget>` from `App.vue` (dashboard tab) into `OptimizationView.vue`.

- [ ] **Step 3: Render components in `OptimizationView.vue`**
Mount `FeeScanner.vue` and the AI components in a grid layout.

- [ ] **Step 4: Commit**
`git add src/ && git commit -m "feat(frontend): build Optimization Hub UI"`

---

### Task 4: Goals Hub - Extended Dividends Backend

**Files:**
- Modify: `backend/services/dividend_service.py`
- Modify: `backend/routers/goals.py` (Create)
- Modify: `backend/main.py`

**Interfaces:**
- Produces: `GET /api/goals/projections` returning 12-month projections and Safety Scores (Payout ratio).

- [ ] **Step 1: Extend `dividend_service.py`**
Add `get_dividend_history(ticker)` fetching `ticker.dividends` to extrapolate the 12 next months of payments. Add `payoutRatio` extraction from `ticker.info`.

- [ ] **Step 2: Implement `routers/goals.py`**
Create the router returning the aggregated projections and scores for a given `user_id`.

- [ ] **Step 3: Register router in `main.py`**
Add `app.include_router(goals.router)`.

- [ ] **Step 4: Commit**
`git add backend/ && git commit -m "feat(backend): add goals router and monthly dividend projections"`

---

### Task 5: Goals Hub - Frontend Simulators

**Files:**
- Modify: `src/views/GoalsView.vue`
- Create: `src/components/MonthlyDividendProjection.vue`
- Create: `src/components/FireSimulator.vue`
- Create: `src/components/DividendSafety.vue`

**Interfaces:**
- Consumes: `GET /api/goals/projections`

- [ ] **Step 1: Implement `MonthlyDividendProjection.vue`**
A bar chart (ECharts) showing the 12-month dividend timeline.

- [ ] **Step 2: Implement `DividendSafety.vue`**
A UI showing the safety score (based on Payout Ratio) of the top dividend payers in the portfolio.

- [ ] **Step 3: Implement `FireSimulator.vue`**
A compound interest calculator with sliders for Monthly Contribution, showing the curve crossing a target "Financial Independence" monthly income.

- [ ] **Step 4: Assembly in `GoalsView.vue`**
Import and arrange these three components in a clean, high-tech dashboard layout.

- [ ] **Step 5: Commit**
`git add src/ && git commit -m "feat(frontend): build Goals Hub and Fire Simulator"`
