"""backend/web_server.py — FastAPI app for Web Application Tracer (workplan T09).

Listens on :8100 (config.SERVICE_PORT). Phase 1 ships the system routes only;
other domains are registered here as their phases land. Routes live in
backend/routes/* and every path string is defined in engine.config.ENDPOINTS.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from engine import config
from backend.routes import system as system_routes
from backend.routes import browser as browser_routes
from backend.routes import java as java_routes
from backend.routes import correlation as correlation_routes

app = FastAPI(title=config.PROJECT_NAME, version=config.PROJECT_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_routes.router)
app.include_router(browser_routes.router)
app.include_router(java_routes.router)
app.include_router(correlation_routes.router)
