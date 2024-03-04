FROM registry.gitlab.ics.muni.cz:443/cryton/configurations/production-base:latest as base

# Set environment
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev --no-root --no-interaction --no-ansi --all-extras

# Install app
COPY . .
RUN poetry install --only-root --no-interaction --no-ansi --all-extras

FROM python:3.12-slim-bullseye as production

# Set environment
ENV CRYTON_APP_DIRECTORY=/app

# Copy app
COPY --from=base /app /app

# Make the executable accessible
RUN ln -s /app/.venv/bin/cryton-cli /usr/local/bin/cryton-cli
RUN ln -s /app/.venv/bin/cryton-hive /usr/local/bin/cryton-hive
RUN ln -s /app/.venv/bin/cryton-worker /usr/local/bin/cryton-worker

# Enable shell autocompletion
RUN _CRYTON_CLI_COMPLETE=bash_source cryton-cli > /etc/profile.d/cryton-cli-complete.sh
RUN echo ". /etc/profile.d/cryton-cli-complete.sh" >> ~/.bashrc

RUN _CRYTON_HIVE_COMPLETE=bash_source cryton-hive > /etc/profile.d/cryton-hive-complete.sh
RUN echo ". /etc/profile.d/cryton-hive-complete.sh" >> ~/.bashrc

RUN _CRYTON_WORKER_COMPLETE=bash_source cryton-worker > /etc/profile.d/cryton-worker-complete.sh
RUN echo ". /etc/profile.d/cryton-worker-complete.sh" >> ~/.bashrc

CMD [ "bash" ]
