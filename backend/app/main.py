from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine
from app import models  # noqa: F401  # ensures ORM models are registered

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API FastAPI pour une application de gestion de projets collaboratifs.",
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "list", "defaultModelsExpandDepth": -1},
    openapi_tags=[
        {"name": "auth", "description": "Connexion, inscription et profil utilisateur."},
        {"name": "users", "description": "Gestion du compte utilisateur."},
        {"name": "dashboard", "description": "Vue d’ensemble du compte et des projets."},
        {"name": "projects", "description": "Création, lecture et gestion des projets."},
        {"name": "tasks", "description": "Kanban, tâches et commentaires."},
        {"name": "notifications", "description": "Notifications utilisateur."},
        {"name": "activity", "description": "Historique des actions."},
        {"name": "meta", "description": "Documentation et résumé des routes."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/routes")
def routes_summary(request: Request):
    return JSONResponse(
        {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "api_prefix": settings.API_V1_STR,
            "route_count": len(request.app.routes),
        }
    )
