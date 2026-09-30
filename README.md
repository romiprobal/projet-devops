Projet DevOps

Objectif

- CI/CD complet
- Conteneurisation Docker
- Tests automatisés
- Observabilité

Ce projet adapte une stratégie Trunk-Based donc branches courtes et intégration fréquente sur la branche principale 'main' (donc créer branches courtes pour ql heure). Contrairement à Git Flow qui alourdit le processus avec pls branches (dev, feature, release) pls lourd, difficile à lire les logs, conflit etc...

Trunk-based favorise l'intégration continue et s'aligne avec DORA, donc performant car en DevOps se mesure à travers 4 indicateurs :

- Deployment Frequency - fréquence du push du code en production
- Lead Time for Changes - temps d'un commit pour arriver en prod
- Change Failure Rate - pourcentage déploiement erreur
- Time to Restore Service (MTTR) - temps pour réparer le prbl


prérequis
docker
python
python-venv
pip
git

L'application

Une API Flask avec une base PostgreSQL. 3 routes :

- /health : vérifie que la base répond (200 si ok, 503 sinon)
- /metrics : les métriques pour Prometheus
- /boom : renvoie une erreur 500 (pour tester les alertes)

Lancer en local

```bash
git clone https://github.com/romiprobal/projet-devops.git
cd projet-devops
python3 -m venv .venv
source .venv/bin/activate
docker compose up -d --build
curl http://localhost:5000/health
```

Services :
- App : http://localhost:5000
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000

Lancer les tests

```bash
docker compose up -d db
export DATABASE_URL="postgresql://user:password@localhost:5432/mydb"
pip install -r requirements.txt
python3 -m pytest -v
```

Docker

Dockerfile en multi-stage (image plus légère), non-root (utilisateur appuser), avec un HEALTHCHECK qui appelle /health. Le .dockerignore exclut .git et .env.

CI

Se déclenche à chaque push et pull request sur main. Jobs : lint (ruff + yamllint), test (matrix Python 3.11/3.12 + service Postgres), report (download-artifact), build, et ci-ok qui bloque le merge si un job échoue. Cache des dépendances via une action locale réutilisable (setup-env).

CD

Se déclenche sur push main après une CI verte. Il build l'image, la push sur ghcr.io avec 3 tags (latest, sha, semver), puis déploie sur un runner self-hosted. Vérification avec curl /health (3 essais), et rollback vers le SHA précédent si ça échoue. Authentification avec GITHUB_TOKEN.

Observabilité

/metrics expose un compteur (http_requests_total), un histogramme de latence (http_request_duration_seconds) et une jauge de version (app_build_info). 2 alertes dans observability/alert_rules.yml : taux d'erreurs 5xx > 5% (for 1min) et latence p95 > 500ms (for 2min).

Pour tester une alerte :

```bash
while true; do curl -s http://localhost:5000/boom > /dev/null; sleep 0.3; done
```
Au bout de ql minutes l'alerte passe en firing sur http://localhost:9090/alerts
