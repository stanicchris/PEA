# Dividend Calendar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implémenter un calendrier prévisionnel des dividendes (Axe 1) affichant les versements à venir et calculant le Yield on Cost.

**Architecture:** Le backend FastAPI s'interfacera avec Yahoo Finance (via `yfinance`) pour récupérer la date d'ex-dividende et le montant estimé pour chaque position du portefeuille. Ces données seront exposées via une route API dédiée et affichées dans Vue.js via un nouveau composant ECharts (frise chronologique).

**Tech Stack:** FastAPI, yfinance, Vue 3, Vue-ECharts, Tailwind CSS

**Spec:** PRD (productdesign.md) - Axe 1 (Fonctionnalités & Valeur Ajoutée)

## Global Constraints

- Backend : Python 3.9+, FastAPI, pydantic.
- Frontend : Vue 3 Composition API, Tailwind CSS.
- Données : Mise en cache obligatoire pour éviter le rate-limiting de Yahoo Finance.

## Review Focus

- Titres sans historique de dividendes (ex: valeurs de croissance). Comportement attendu : Affichage de "N/A" sans crasher le calcul global.
- Changement de devise pour les actions US/Étrangères. Comportement attendu : Conversion du dividende en EUR selon le taux de change du jour.
- Titres dont le symbole Yahoo est mal formaté (ex: `.PA`). Comportement attendu : Fallback propre ou exclusion du titre pour ce calcul.
- Dates d'ex-dividendes passées ou nulles. Comportement attendu : Exclusion des mois passés de la frise chronologique future.

---

### Task 1: Backend - Dividend Data Service & Cache

**Files:**
- Create: `backend/services/dividend_service.py`
- Modify: `backend/routers/portfolio.py` (assuming refactoring from Axe 2 is done)
- Create: `tests/backend/test_dividend_service.py`

**Steps:**
- [ ] Write a failing test for `dividend_service.get_upcoming_dividends(ticker)` ensuring it returns an expected dict structure `{ "ex_date": "...", "amount": "...", "yield_on_cost": "..." }`.
- [ ] Write a failing test for the caching mechanism (ensure repeated calls don't hit the external API).
- [ ] Run the tests to verify failure.
- [ ] Implement `get_upcoming_dividends` in `dividend_service.py` using `yfinance.Ticker(ticker).dividends` and `.info` (for forward yield).
- [ ] Implement an in-memory or simple TTL cache wrapper for this service.
- [ ] Register a new API route `GET /api/portfolio/dividends` in `routers/portfolio.py` that aggregates dividend data for all user positions.
- [ ] Run the tests and ensure they pass.
- [ ] Commit with message: "feat(backend): implement dividend data service and API route with cache"

### Task 2: Frontend - Dividend Store & API Integration

**Files:**
- Create: `src/store/dividendStore.js`
- Modify: `src/components/AnalyticsView.vue`

**Steps:**
- [ ] Create a Pinia store module `dividendStore.js` with an action `fetchDividends` that calls the new backend route.
- [ ] Add state variables for `upcomingDividends`, `totalEstimatedYield`, and `loading` status.
- [ ] Connect the store to `AnalyticsView.vue` to trigger the fetch on component mount.
- [ ] Commit with message: "feat(frontend): create dividend store and API integration"

### Task 3: Frontend - Dividend Timeline Component

**Files:**
- Create: `src/components/DividendTimeline.vue`
- Modify: `src/components/AnalyticsView.vue`

**Steps:**
- [ ] Create `DividendTimeline.vue` implementing an ECharts bar chart or custom Tailwind CSS timeline showing dividends aggregated by month.
- [ ] Pass the data from `dividendStore.upcomingDividends` as props or compute it directly within the component.
- [ ] Include an empty state for portfolios with no dividend-paying stocks.
- [ ] Integrate `DividendTimeline.vue` into the main grid layout of `AnalyticsView.vue`.
- [ ] Test the UI responsiveness (Mobile and Desktop views).
- [ ] Commit with message: "feat(frontend): implement and integrate DividendTimeline component"
