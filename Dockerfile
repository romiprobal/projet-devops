FROM python:3.12.7-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12.7-slim

ARG APP_VERSION=0.0.0-dev
ARG GIT_SHA=unknown
ENV APP_VERSION=${APP_VERSION} \
    GIT_SHA=${GIT_SHA}

WORKDIR /app

RUN useradd --create-home appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .

ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/health').raise_for_status()"

CMD ["python", "app.py"]