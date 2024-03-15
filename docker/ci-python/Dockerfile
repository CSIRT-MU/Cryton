# In case you update this image, build and push it.
FROM alpine:3

# Update the default environment
ENV PATH="${PATH}:/root/.pyenv/bin:/root/.local/bin"
# Configure pipx
ENV PIPX_HOME=/opt/pipx
ENV PIPX_BIN_DIR=/root/.local/bin
# Configure Poetry
ENV POETRY_CACHE_DIR=/opt/.cache

# Install the required packages
RUN apk add --no-cache \
    bash \
    curl \
    git \
    build-base \
    libffi-dev \
    openssl-dev \
    bzip2-dev \
    zlib-dev \
    xz-dev \
    readline-dev \
    sqlite-dev

# Install pyenv
RUN curl https://pyenv.run | bash

RUN eval "$(pyenv init -)"
RUN eval "$(pyenv virtualenv-init -)"

# Enable pyenv for interactive shell
COPY pyenv.sh /etc/profile.d/pyenv.sh

# Install the required Python versions
RUN pyenv install 3.9
RUN pyenv install 3.10
RUN pyenv install 3.11
RUN pyenv install 3.12

# Link Python versions to /usr/bin
RUN ln -s "$(find /root/.pyenv/versions/ -name "3.9.*")/bin/python3" /usr/bin/python3.9
RUN ln -s "$(find /root/.pyenv/versions/ -name "3.10.*")/bin/python3" /usr/bin/python3.10
RUN ln -s "$(find /root/.pyenv/versions/ -name "3.11.*")/bin/python3" /usr/bin/python3.11
RUN ln -s "$(find /root/.pyenv/versions/ -name "3.12.*")/bin/python3" /usr/bin/python3.12

# Link the highest Python and pip version to /usr/bin
RUN ln -s "$(find /root/.pyenv/versions/ -name "3.12.*")/bin/python3" /usr/bin/python3
RUN ln -s "$(find /root/.pyenv/versions/ -name "3.12.*")/bin/pip3" /usr/bin/pip3

# Install pipx
RUN python3 -m pip install --user pipx==1.*

# Install Poetry
RUN pipx install poetry==1.*

# Install tox
RUN pipx install tox==4.*
