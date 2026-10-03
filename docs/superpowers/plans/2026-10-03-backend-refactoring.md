# Backend Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Découper le fichier monolithique `backend/main.py` en routeurs FastAPI distincts et créer une couche de service (Axe 2).

**Architecture:** Mettre en place la structure standard de FastAPI avec `APIRouter` pour séparer les domaines d'affaires (auth, portfolio, market, ai).

**Tech Stack:** FastAPI, Python, Pydantic

**Spec:** PRD (productdesign.md) - Axe 2 (Planification & Qualité)

## Global Constraints

- Ne pas casser l'interface API publique existante (les routes frontend actuelles doivent continuer de fonctionner à l'identique).
- Utiliser `APIRouter(prefix="/api/...", tags=[...])`.

## Review Focus

- Problèmes d'import circulaire entre les modules. Comportement attendu : Utiliser l'injection de dépendances (`Depends()`) au lieu d'imports de fichiers statiques si nécessaire.
- Erreur 404 sur le frontend suite à la migration d'une route. Comportement attendu : Les préfixes de route doivent correspondre *exactement* aux anciens chemins déclarés dans `main.py`.

---

### Task 1: Scaffolding API Routers Structure

**Files:**
- Create: `backend/routers/__init__.py`
- Create: `backend/routers/auth.py`
- Create: `backend/routers/portfolio.py`
- Create: `backend/routers/market.py`
- Create: `backend/routers/ai.py`
- Modify: `backend/main.py`

**Steps:**
- [ ] Create the `routers/` directory and initialize empty modules.
- [ ] In `auth.py`, instantiate an `APIRouter` and migrate auth-related routes from `main.py`.
- [ ] In `portfolio.py`, instantiate an `APIRouter` and migrate portfolio/CRUD routes from `main.py`.
- [ ] In `market.py`, instantiate an `APIRouter` and migrate yfinance/scraping routes from `main.py`.
- [ ] In `ai.py`, instantiate an `APIRouter` and migrate Groq API routes from `main.py`.
- [ ] In `main.py`, remove the old route definitions.
- [ ] In `main.py`, add `app.include_router(...)` for each of the new routers.
- [ ] Test the FastAPI application startup to ensure no import errors exist (`fastapi run backend/main.py`).
- [ ] Commit with message: "refactor(backend): modularize FastAPI application with APIRouter"
