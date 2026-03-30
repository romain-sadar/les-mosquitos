# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Variables d’environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Dépendances système (PostgreSQL + GIS)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    gdal-bin \
    libgdal-dev \
    binutils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copier uniquement les fichiers nécessaires au lock/install
COPY pyproject.toml uv.lock* ./

# Installer dépendances
RUN uv sync --no-dev

# Copier le reste du projet
COPY . .

# Port Django
EXPOSE 8000

# Commande par défaut
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]