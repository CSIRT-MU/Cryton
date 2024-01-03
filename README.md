![Coverage](https://gitlab.ics.muni.cz/cryton/cryton/badges/master/coverage.svg)

[//]: # (TODO: add badges for python versions, black, pylint, flake8, unit tests, integration tests)

# Cryton
Advanced (attack) orchestrator and scheduler.

Cryton is tested and targeted primarily on **Debian** and **Kali Linux**. Please keep in mind that **only 
the latest version is supported** and issues regarding different OS or distributions may **not** be resolved.

For more information see the [documentation](https://cryton.gitlab-pages.ics.muni.cz/).

## Quick-start
Install [Poetry](https://python-poetry.org/docs/).

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton.git
```

Go to the correct directory:
```shell
cd cryton
```

Install Cryton:
```shell
poetry install --all-extras --with docs
```

Run Hive:
```shell
poetry run cryton-hive start
```

Run Worker:
```shell
poetry run cryton-worker start
```

Run CLI:
```shell
poetry run cryton-cli
```

### Local documentation
Serve the documentation locally:
```shell
mkdocs serve -a localhost:8001
```

## Quick-start with Docker compose
Install [Docker Compose](https://docs.docker.com/compose/install/).  
Optionally, check out these Docker [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/).

Run the Compose configuration:
```shell
docker compose up -d
```

Now the Hive, Worker, and their prerequisites (RabbitMQ, Postgres, Metasploit, Empire, PGBouncer) are running. To use CLI, enter its container:
```shell
docker exec -it cryton-cli bash
```
