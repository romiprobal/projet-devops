FROM python:3.12.7-slim AS builder

# dossier de travail dans le conteneur
WORKDIR /app

# installe les dépendances dans un dossier temporaire
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


#Image Finale
FROM python:3.12.7-slim

WORKDIR /app

RUN useradd --create-home appuser

# copie des dépendances et du code
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

# configuration des variables d'environnement et passage à l'utilisateur non-root
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

# communiquer port 5000
EXPOSE 5000

# interroge notre endpoint /health toutes les 30 secondes
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health').raise_for_status()"

#lancer l'application quand le conteneur démarre
CMD ["python", "app.py"]