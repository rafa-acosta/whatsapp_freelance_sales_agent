# Application image for the web and worker services (plan.md, R-017).
# No secrets are copied into the image; configuration comes from the environment at run time.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 app
WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY manage.py ./
COPY config ./config
COPY knowledge ./knowledge
COPY content ./content

RUN pip install --upgrade pip && pip install .

USER app
EXPOSE 8000
CMD ["gunicorn", "salesagent.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
