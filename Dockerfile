FROM python:3.11-slim

# Mise a jour securite des paquets systeme
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Etape 1 : copier UNIQUEMENT les dependances (couche mise en cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Etape 2 : copier le code source
COPY src/ ./src/
COPY tests/ ./tests/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
