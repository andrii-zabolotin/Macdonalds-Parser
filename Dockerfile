FROM python:3.11-slim

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=true

RUN pip install poetry

COPY pyproject.toml poetry.lock /app/
WORKDIR /app
EXPOSE 8000

RUN poetry install
RUN /app/.venv/bin/pip install --upgrade pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --no-create-home --system fastapi-user


ENV PATH="/app/.venv/bin:$PATH"
USER fastapi-user
