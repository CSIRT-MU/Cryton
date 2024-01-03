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
RUN poetry install --only-root --no-interaction --no-ansi -E cli

FROM python:3.11-alpine as production

# Install necessary packages
RUN apk add --no-cache \
    bash

# Set environment
ENV CRYTON_APP_DIRECTORY=/app

# Copy app
COPY --from=base /app /app

# Make the executable accessible
RUN ln -s /app/.venv/bin/cryton-cli /usr/local/bin/cryton-cli

# Enable shell autocompletion
RUN _CRYTON_CLI_COMPLETE=bash_source cryton-cli > /etc/profile.d/cryton-cli-complete.sh

CMD [ "bash" ]
