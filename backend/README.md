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

Par défaut, l'API démarre sur `http://127.0.0.1:8000`.

## URLs utiles

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Healthcheck: `http://127.0.0.1:8000/health`
- Résumé des routes: `http://127.0.0.1:8000/routes`
- Résumé métier des routes: `http://127.0.0.1:8000/api/v1/meta/routes`

## Base de données

Par défaut, le backend utilise SQLite pour le développement local.
Tu peux passer à PostgreSQL en remplaçant `DATABASE_URL` dans `.env`.

## API

La version API est exposée sous `/api/v1`.

### Blocs exposés

- `auth`
- `users`
- `dashboard`
- `projects`
- `tasks`
- `notifications`
- `activity`
- `meta`
