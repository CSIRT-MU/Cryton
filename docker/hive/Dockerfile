FROM registry.gitlab.ics.muni.cz:443/cryton/configurations/production-base:latest as base

LABEL authors="Jiri Raja <raja@ics.muni.cz>, Milan Bohacek <bohacek@ics.muni.cz>"

# Set environment
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev --no-root --no-interaction --no-ansi

# Install app
COPY . /app/
RUN poetry install --only-root --no-interaction --no-ansi -E hive

FROM python:3.11-slim-bullseye as production

# Set environment
ENV CRYTON_APP_DIRECTORY=/app

# Copy app
COPY --from=base /app /app

# Make the executable accessible
RUN ln -s /app/.venv/bin/cryton-core /usr/local/bin/cryton-core

ENTRYPOINT [ "/app/docker/entrypoint.sh" ]
CMD [ "cryton-core", "start" ]
