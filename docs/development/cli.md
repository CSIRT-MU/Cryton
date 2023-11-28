## Settings
The best thing you can do is to change the app directory to `path/to/cryton-cli/`. That way, you can edit the default .env file
and use it for the compose files.
```shell
export CRYTON_CLI_APP_DIRECTORY=path/to/cryton-cli/
```

[Link to the settings](../components/cli.md#settings).

## Installation

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [Poetry](https://python-poetry.org/docs/#installation){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-cli.git
```

Then go to the correct directory and install the project:
```shell
cd cryton-cli
poetry install
```

To spawn a shell use:
```shell
poetry shell
```

## Usage
```shell
cryton-cli
```

[Link to the usage](../components/cli.md#usage).


## Testing

### Pytest
```
pytest --cov=cryton_cli tests/unit_tests --cov-config=.coveragerc-unit --cov-report html
```

```
pytest --cov=cryton_cli tests/integration_tests --cov-config=.coveragerc-integration --cov-report html
```

???+ "Run specific test" 

    ```
    my_test_file.py::MyTestClass::my_test
    ```

### tox
Use in combination with [pyenv](https://github.com/pyenv/pyenv){target="_blank"}.

```shell
tox -- tests/unit_tests/ --cov=cryton_cli --cov-config=.coveragerc-unit
```

```shell
tox -- tests/integration_tests/ --cov=cryton_cli --cov-config=.coveragerc-integration
```

## Build a Docker image
If you want to build a custom Docker image, clone the repository, and switch to the correct directory:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-cli.git
cd cryton-cli
```

Build the image:
```shell
docker build -t custom-cli-image .
```

Test your docker image:
```shell
docker run -it --rm custom-cli-image
```
