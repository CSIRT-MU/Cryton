## Settings
The best thing you can do is to change the app directory to `path/to/cryton-worker/`. That way, you can edit the default .env file
and use it for the compose files.
```shell
export CRYTON_WORKER_APP_DIRECTORY=path/to/cryton-worker/
```

[Link to the settings](../components/worker.md#settings).

## Installation

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [Poetry](https://python-poetry.org/docs/#installation){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-worker.git
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
cd cryton-worker
poetry install
```

To spawn a shell use:
```shell
poetry shell
```

## Usage
```shell
cryton-worker start
```

[Link to the usage](../components/worker.md#usage).

## Testing

### Pytest
```
pytest --cov=cryton_worker tests/unit_tests --cov-config=.coveragerc-unit --cov-report html
```

???+ "Run specific test" 

    ```
    my_test_file.py::MyTestClass::my_test
    ```

### tox
Use in combination with [pyenv](https://github.com/pyenv/pyenv){target="_blank"}.

```shell
tox -- tests/unit_tests/ --cov=cryton_worker --cov-config=.coveragerc-unit
```

## Bending the RabbitMQ API
It is possible to use Cryton Worker as a standalone application and control it using your requests. 
It is also possible to create your Worker and use Core to control it.

## Build a Docker image
If you want to build a custom Docker image, clone the repository, and switch to the correct directory:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-worker.git
cd cryton-worker
```

Build the (Kali) image (with preinstalled modules and dependencies):
```shell
docker build -t custom-worker-image --target kali .
```

!!! tip ""

    To build the bare Worker image use:
    ```shell
    docker build -t custom-worker-bare-image --target production .
    ```

Test your docker image:
```shell
docker run --rm custom-worker-image
```
