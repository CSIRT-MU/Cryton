FROM python:3.13-slim-bullseye

ENV PATH="${PATH}:/root/.local/bin"
ENV PIPX_HOME=/opt/pipx
ENV PIPX_BIN_DIR=/root/.local/bin
ENV POETRY_CACHE_DIR=/opt/.cache

# Install pipx
RUN python3 -m pip install --user pipx==1.*

# Install poetry
RUN pipx install poetry==2.*
