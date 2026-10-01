# etape 1 : on installe juste les dependances
FROM python:3.12.7-slim AS builder

WORKDIR /app

# on copie que requirements.txt pour garder le cache docker si le code change
COPY requirements.txt .
# --user met tout dans /root/.local, plus simple a recuperer apres
RUN pip install --no-cache-dir --user -r requirements.txt

# etape 2 : image finale, on repart d'une image propre
FROM python:3.12.7-slim

# version et commit envoyes par la cd (build-args), valeurs par defaut en local
ARG APP_VERSION=0.0.0-dev
ARG GIT_SHA=unknown
# on les passe en env pour que app.py puisse les lire (metrique app_build_info)
ENV APP_VERSION=${APP_VERSION} \
    GIT_SHA=${GIT_SHA}

WORKDIR /app

# user normal pour pas tourner en root
RUN useradd --create-home appuser

# on recupere les dependances de l'etape 1
COPY --from=builder /root/.local /home/appuser/.local
# on copie le code et on le donne a appuser
COPY --chown=appuser:appuser . .

# pour que les commandes installees par pip soient trouvees
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

# l'app ecoute sur 5000 (c'est juste indicatif, le vrai port est ouvert dans le compose)
EXPOSE 5000

# docker verifie /health toutes les 30s, 3 echecs = unhealthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health').raise_for_status()"

# commande lancee au demarrage du conteneur
CMD ["python", "app.py"]