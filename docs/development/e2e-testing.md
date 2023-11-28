# Cryton E2E

## Description
Cryton E2E is a project used for End-To-End testing of the Cryton toolset.

Cryton toolset is tested and targeted primarily on **Debian** and **Kali Linux**. Please keep in mind that **only 
the latest version is supported** and issues regarding different OS or distributions may **not** be resolved.

[Link to the repository](https://gitlab.ics.muni.cz/cryton/cryton-e2e).

## Settings
Cryton E2E uses environment variables for its settings. Please update them to your needs.

### Overriding settings
To override the settings, use the `export` command:
```shell
export CRYTON_E2E_TESTS=all
```

!!! note ""

    Use `unset` to remove a variable.

!!! tip ""

    Some settings can be overridden using the CLI. Try using:
    ```
    cryton-e2e --help
    ```

??? tip "Overriding settings with Docker"

    <div id="settings-docker"></div>

    To override a variable use the `-e` or the `--env-file` option:
    ```
    docker run -e CRYTON_E2E_TESTS=all --env-file relative/path/to/.env ...
    ```

    More information can be found [here](https://docs.docker.com/engine/reference/commandline/run/#env){target="_blank"}.

??? tip "Overriding settings with Docker compose"

    <div id="settings-compose"></div>

    Override variables in the `environment` or the `env_file` attribute:
    ```
    services
      service:
        environment:
          - CRYTON_E2E_TESTS=all
        env_file:
          - relative/path/to/.env
    ```

    More information can be found [here](https://docs.docker.com/compose/environment-variables/set-environment-variables/#use-the-environment-attribute){target="_blank"}.

### Available settings

#### CRYTON_E2E_TESTS
What tests to run.

| value  | default | example       |
|--------|---------|---------------|
| string | all     | basic,control |

??? note "Possible tests"

    - `basic`
    - `advanced`
    - `control`
    - `empire`
    - `http_trigger`
    - `msf_trigger`
    - `datetime_trigger`
    - `all`

#### CRYTON_E2E_CRYTON_CLI_EXECUTABLE
Cryton CLI executable.

| value  | default    | example             |
|--------|------------|---------------------|
| string | cryton-cli | /usr/bin/cryton-cli |

#### CRYTON_E2E_WORKER_ADDRESS
Address of the Worker host (used for triggers, MSF and Empire agents).

| value  | default   | example       |
|--------|-----------|---------------|
| string | 127.0.0.1 | 192.168.90.11 |

#### CRYTON_E2E_WORKER_NAME
Name of the Cryton Worker to use.

| value  | default | example   |
|--------|---------|-----------|
| string | Worker  | my_worker |

#### CRYTON_E2E_APP_DIRECTORY
Path to the Cryton E2E directory. **(do not change, if you don't know what you're doing)**

| value  | default                                                                      | example       |
|--------|------------------------------------------------------------------------------|---------------|
| string | relative path from the `cryton-e2e/etc/config.py` file to the root directory | /path/to/app/ |

## Installation

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [Poetry](https://python-poetry.org/docs/#installation){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)
    - You probably don't want to set it all up manually, checkout the [playground](../playground/introduction.md)

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-e2e.git
```

Then go to the correct directory and install the project:
```shell
cd cryton-e2e
poetry install
```

To spawn a shell use:
```shell
poetry shell
```

## Usage

!!! danger "Prerequisites for running the tests"

    - Empire, MSF, and Worker must be running on the same host/address
    - Worker must be able to access the Empire and MSF

To invoke the app use:
```shell
cryton-e2e
```

To run the tests use:
```shell
cryton-e2e run-tests
```

To run specific test(s) use:
```shell
cryton-e2e run-tests -t advanced -t control
```
