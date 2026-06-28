# Backend

API FastAPI pour l'application de gestion de projets.

## Démarrage rapide

1. Copier `.env.example` vers `.env`
2. Installer les dépendances
3. Lancer l'API

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Base de données

Par défaut, le backend utilise SQLite pour le développement local.
Tu peux passer à PostgreSQL en remplaçant `DATABASE_URL` dans `.env`.

## API

La version API est exposée sous `/api/v1`.

