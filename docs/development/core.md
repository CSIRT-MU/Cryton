## Settings
The best thing you can do is to change the app directory to `path/to/cryton-core/`. That way, you can edit the default .env file
and use it for the compose files.
```shell
export CRYTON_CORE_APP_DIRECTORY=path/to/cryton-core/
```

[Link to the settings](../components/core.md#settings).

## Installation

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [Poetry](https://python-poetry.org/docs/#installation){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-core.git
```

Start the prerequisites:
```shell
docker compose -f docker-compose.prerequisites.yml up -d
```

??? tip "Clean up and rebuild the prerequisites"

    !!! warning

        The following script removes unused images and volumes. Make sure you know what you're doing!

    ```
    docker compose -f docker-compose.prerequisites.yml down -t 0 && docker system prune --volumes -f && docker compose -f docker-compose.prerequisites.yml up -d 
    ```

Then go to the correct directory and install the project:
```shell
cd cryton-core
poetry install
```

To spawn a shell use:
```shell
poetry shell
```

## Usage
```shell
cryton-core start
```

[Link to the usage](../components/core.md#usage).

## Testing

### Pytest
```
pytest --cov=cryton_core tests/unit_tests --cov-config=.coveragerc-unit --cov-report html
```

```
pytest --cov=cryton_core tests/integration_tests --cov-config=.coveragerc-integration --cov-report html
```

???+ "Run specific test" 

    ```
    my_test_file.py::MyTestClass::my_test
    ```

### tox
Use in combination with [pyenv](https://github.com/pyenv/pyenv){target="_blank"}.

```shell
tox -- tests/unit_tests/ --cov=cryton_core --cov-config=.coveragerc-unit
```

```shell
tox -- tests/integration_tests/ --cov=cryton_core --cov-config=.coveragerc-integration
```

## django setup for testing scripts

```
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cryton_core.settings")
import django
django.setup()
```

## Django migrations  

### Apply migrations
```
cryton-core migrate
```

### Init migrations
Migrations in `cryton_core/cryton_app/migrations/` must be empty
```
cryton-core makemigrations cryton_app
```

## Build a Docker image
If you want to build a custom Docker image, clone the repository, and switch to the correct directory:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-core.git
cd cryton-core
```

Build the (Core) image:
```shell
docker build -t custom-core-image --target production .
```

!!! tip ""

    To build the Apache proxy image use:
    ```shell
    docker build -t custom-proxy-image --target proxy .
    ```

Test your docker image:
```shell
docker run --rm custom-core-image
```
