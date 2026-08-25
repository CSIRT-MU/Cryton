FROM ghcr.io/astral-sh/uv:0.12.5-python3.12-trixie-slim AS base

# Set environment
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON=3.12 \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install dependencies
COPY uv.lock pyproject.toml ./
RUN uv sync --locked --no-dev --no-install-project --all-extras

# Install app
COPY . .
RUN uv sync --locked --no-dev --no-editable --all-extras

FROM python:3.12-slim-trixie AS production

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
