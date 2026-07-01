# MiniLink — API de raccourcissement d'URL

API REST (FastAPI) qui raccourcit une URL et résout un code court, support d'un
projet DevOps complet : Docker, Jenkins (CI/CD), SonarQube, Trivy, Terraform,
Prometheus & Grafana.

## Endpoints

- `GET /health` — sonde de vivacité (`{"status":"ok"}`)
- `POST /shorten` — reçoit `{"url": "..."}`, retourne un code court
- `GET /resolve/{code}` — résout un code vers l'URL d'origine (404 si inconnu)
- `GET /metrics` — métriques au format Prometheus

## Démarrage rapide

```bash
# Build de l'image
docker build -t minilink-api:latest .

# Tests (dans le conteneur)
docker run --rm minilink-api:latest pytest tests/ -v --cov=src --cov-report=term-missing

# Lancer en local
docker compose up -d
curl http://localhost:8080/health
```

## Arborescence

```
minilink-api/
├── src/           code de l'application (main, store, schemas)
├── tests/         tests pytest
├── infra/         Infrastructure as Code (Terraform)
├── monitoring/    Prometheus + Grafana
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── Jenkinsfile    pipeline CI/CD (11 stages)
```

## Pipeline CI/CD (11 stages)

Checkout → Build → Lint → IaC Validate → Test → Security Scan → SonarQube →
Quality Gate → Push → IaC Apply → Deploy + Smoke Test.

> Le depot utilise le compte GitHub `aflesec` (deja renseigne dans le `Jenkinsfile`
