# les-mosquitos

API REST pour l’application de **cartographie terrain** et le suivi de points (avaloires, traitements anti-moustiques, etc.) : **parcours** (cartographies), **points** géolocalisés, **étiquettes**, **interventions** et **traces de mission**.

## Stack

- **Python 3.12+**, **Django 6**, **Django REST Framework**
- **PostGIS** (PostgreSQL + extension spatiale)
- Authentification **token** (`rest_framework.authtoken`) : en-tête `Authorization: Token <clé>`
- **CORS** ouvert pour une app mobile (Flutter, etc.)
- **Mapbox** (Optimized Trips) pour l’itinéraire piéton optimisé sur un parcours

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose  
  **ou**
- [uv](https://docs.astral.sh/uv/) et une base PostgreSQL avec **PostGIS** accessible

## Démarrage avec Docker

À la racine du dépôt `les-mosquitos` :

```bash
docker compose up --build
```

Puis, dans le conteneur `web` (ou en local avec les mêmes variables d’environnement) :

```bash
uv run python manage.py migrate
```

L’API est exposée sur **http://localhost:8000**. Le préfixe des routes REST est **`/api/`** (ex. `http://localhost:8000/api/login/`).

Création d’un compte admin (optionnel) :

```bash
docker exec -it django_app uv run python manage.py createsuperuser
```

Interface d’administration Django : **http://localhost:8000/admin/**

## Variables d’environnement

| Variable       | Description |
|----------------|-------------|
| `DB_NAME`      | Nom de la base PostgreSQL |
| `DB_USER`      | Utilisateur PostgreSQL |
| `DB_PASSWORD`  | Mot de passe |
| `DB_HOST`      | Hôte (ex. `db` avec Docker Compose) |
| `DB_PORT`      | Port (ex. `5432`) |
| `MAPBOX_TOKEN` | Jeton d’accès Mapbox (`pk.…`) pour `GET /api/parcours/<id>/optimize/` |

Avec **Docker Compose**, les variables de base de données sont déjà définies dans `docker-compose.yml`. Pour **`MAPBOX_TOKEN`**, préférez :

- une variable d’environnement injectée proprement (fichier `.env` lu par Compose, ou secret), **ou**
- une ligne **quotée** dans le YAML si vous mettez le jeton dans `docker-compose.yml` (les jetons JWT contiennent souvent `=`, ce qui peut casser un scalaire YAML non quoté et laisser la variable vide côté conteneur).

Sans jeton Mapbox valide, l’endpoint **`optimize`** renverra une erreur côté Mapbox ; l’app cliente peut alors retomber sur un tracé simplifié (selon implémentation).

## Authentification

1. **`POST /api/register/`** ou **`POST /api/login/`** avec un corps JSON `{"username": "...", "password": "..."}`.
2. Réponse : champ **`token`** à réutiliser sur les routes protégées.
3. En-tête : **`Authorization: Token <token>`**.

La plupart des ressources (points, parcours, etc.) exigent un utilisateur authentifié.

## Points d’entrée utiles de l’API

Base : **`http://localhost:8000/api/`**

| Méthode | Chemin | Rôle |
|---------|--------|------|
| POST | `/login/`, `/register/` | Connexion / inscription |
| CRUD | `/parcours/` | Cartographies (parcours) |
| POST | `/parcours/<uuid>/add_point/` | Lier un point existant au parcours (`{"point_id": "..."}`) |
| GET | `/parcours/<uuid>/optimize/` | Itinéraire piéton optimisé (Mapbox, **≥ 2 points** dans le parcours) |
| CRUD | `/points/` | Points terrain |
| CRUD | `/labels/` | Étiquettes |
| CRUD | `/parcours-points/` | Liaisons parcours ↔ point |
| CRUD | `/interventions/` | Interventions sur les points |
| CRUD | `/mission-tracks/` | Traces GPS de mission |
| CRUD | `/points/<uuid>/photos/` | Photos associées à un point (imbrication REST) |

Une description plus formelle des schémas est disponible dans **`openapi.yaml`** à la racine du projet.

## Développement local sans Docker

1. Installer les dépendances : `uv sync`
2. Configurer `DB_*` (base PostGIS locale) et éventuellement `MAPBOX_TOKEN` dans l’environnement ou un fichier chargé par vos outils.
3. Migrations : `uv run python manage.py migrate`
4. Serveur : `uv run python manage.py runserver`

## Tests

```bash
uv run pytest
```

(`DJANGO_SETTINGS_MODULE` est défini dans `pyproject.toml`.)