## Description
Cryton Core is the center point of the Cryton toolset. It is used for:

- Creating, planning, and scheduling attack scenarios
- Generating reports
- Controlling Workers and scenarios execution

[Link to the repository](https://gitlab.ics.muni.cz/cryton/cryton-core){target="_blank"}.

## Settings
Cryton Core uses environment variables for its settings. Please update them to your needs.

### Overriding settings
To override the settings, use the `export` command:
```shell
export CRYTON_CORE_RABBIT_USERNAME=cryton
```

!!! note ""

    Use `unset` to remove a variable.

!!! tip ""

    Some settings can be overridden using the CLI. Try using:
    ```
    cryton-core help <your command>
    ```

??? tip "Overriding settings permanently"

    <div id="settings-permanent"></div>

    First, make sure the [app directory](#cryton_core_app_directory) exists:
    ```shell
    mkdir -p ~/.local/cryton-core/
    ```
    
    Download the default settings into the app directory:
    
    === "curl"
    
        ```shell
        curl -o ~/.local/cryton-core/.env https://gitlab.ics.muni.cz/cryton/cryton-core/-/raw/{{{ git_release }}}/.env
        ```
    
    === "wget"
    
        ```shell
        wget -O ~/.local/cryton-core/.env https://gitlab.ics.muni.cz/cryton/cryton-core/-/raw/{{{ git_release }}}/.env
        ```

    Open the file and update it to your needs.

??? tip "Overriding settings with Docker"

    <div id="settings-docker"></div>

    To override a variable use the `-e` or the `--env-file` option:
    ```
    docker run -e CRYTON_CORE_RABBIT_USERNAME=cryton --env-file relative/path/to/.env ...
    ```

    More information can be found [here](https://docs.docker.com/engine/reference/commandline/run/#env){target="_blank"}.

??? tip "Overriding settings with Docker compose"

    <div id="settings-compose"></div>

    Override variables in the `environment` or the `env_file` attribute:
    ```
    services
      service:
        environment:
          - CRYTON_CORE_RABBIT_USERNAME=cryton
        env_file:
          - relative/path/to/.env
    ```

    More information can be found [here](https://docs.docker.com/compose/environment-variables/set-environment-variables/#use-the-environment-attribute){target="_blank"}.

### Available settings

#### CRYTON_CORE_RABBIT_HOST
RabbitMQ server host.

| value  | default   | example       |
|--------|-----------|---------------|
| string | 127.0.0.1 | cryton-rabbit |

#### CRYTON_CORE_RABBIT_PORT
RabbitMQ server port.

| value | default | example |
|-------|---------|---------|
| int   | 5672    | 15672   |

#### CRYTON_CORE_RABBIT_USERNAME
Username for RabbitMQ server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | admin   |

#### CRYTON_CORE_RABBIT_PASSWORD
Password for RabbitMQ server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | mypass  |

#### CRYTON_CORE_DB_HOST
Postgres server host.

| value  | default   | example          |
|--------|-----------|------------------|
| string | 127.0.0.1 | cryton-pgbouncer |

#### CRYTON_CORE_DB_PORT
Postgres server port.

| value | default | example |
|-------|---------|---------|
| int   | 5432    | 15432   |

#### CRYTON_CORE_DB_NAME
Used Postgres database name. **(do not change, if you don't know what you're doing)**

| value  | default | example   |
|--------|---------|-----------|
| string | cryton  | cryton_db |

#### CRYTON_CORE_DB_USERNAME
Username for Postgres server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | user    |

#### CRYTON_CORE_DB_PASSWORD
Password for Postgres server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | passwd  |

#### CRYTON_CORE_Q_ATTACK_RESPONSE
Queue name for processing attack responses. **(do not change, if you don't know what you're doing)**

| value  | default                     | example                        |
|--------|-----------------------------|--------------------------------|
| string | cryton_core.attack.response | cryton_core.attack.response.id |

#### CRYTON_CORE_Q_AGENT_RESPONSE
Queue name for processing agent responses. **(do not change, if you don't know what you're doing)**

| value  | default                    | example                       |
|--------|----------------------------|-------------------------------|
| string | cryton_core.agent.response | cryton_core.agent.response.id |

#### CRYTON_CORE_Q_EVENT_RESPONSE
Queue name for processing event responses. **(do not change, if you don't know what you're doing)**

| value  | default                    | example                       |
|--------|----------------------------|-------------------------------|
| string | cryton_core.event.response | cryton_core.event.response.id |

#### CRYTON_CORE_Q_CONTROL_REQUEST
Queue name for processing control requests. **(do not change, if you don't know what you're doing)**

| value  | default                     | example                        |
|--------|-----------------------------|--------------------------------|
| string | cryton_core.control.request | cryton_core.control.request.id |

#### CRYTON_CORE_DEBUG
Make Core run with debug output.

| value   | default | example |
|---------|---------|---------|
| boolean | false   | true    |

#### CRYTON_CORE_MESSAGE_TIMEOUT
Timeout (in seconds) for RabbitMQ RPC requests and messages.

| value | default | example |
|-------|---------|---------|
| int   | 180     | 300     |

!!! warning ""

    If you choose a lower timeout value and the Worker's IP changes during runtime, the messages may time out. 
    This is because the Worker tries to reconnect to RabbitMQ server after two minutes of silence.

#### CRYTON_CORE_API_SECRET_KEY
Key (64 chars) used by REST API for cryptographic signing.  
More information can be found [here](https://docs.djangoproject.com/en/4.1/ref/settings/#secret-key){target="_blank"}.

| value  | default | example              |
|--------|---------|----------------------|
| string | cryton  | XF37..56 chars..6HB3 |

#### CRYTON_CORE_API_ALLOWED_HOSTS
Domain names that the site can serve. **(do not change, if you don't know what you're doing)**  
More information can be found [here](https://docs.djangoproject.com/en/4.1/ref/settings/#allowed-hosts){target="_blank"}.

| value                              | default | example    |
|------------------------------------|---------|------------|
| list of strings separated by space | *       | host host2 |

#### CRYTON_CORE_API_STATIC_ROOT
Directory for storing static files. **(do not change, if you don't know what you're doing)**  
More information can be found [here](https://docs.djangoproject.com/en/4.0/ref/settings/#static-root){target="_blank"}.

| value  | default                        | example                      |
|--------|--------------------------------|------------------------------|
| string | /usr/local/apache2/web/static/ | /var/www/example.com/static/ |

#### CRYTON_CORE_API_USE_STATIC_FILES
Whether to serve static files or not. **(do not change, if you don't know what you're doing)**

| value   | default | example |
|---------|---------|---------|
| boolean | false   | true    |

#### CRYTON_CORE_CPU_CORES
The maximum number of CPU cores (processes) Cryton Core can utilize. **(do not change, if you don't know what you're doing)**  
This affects the speed of starting/consuming Steps/Rabbit requests. Set the value to `auto` for the best CPU utilization.

| value | default | example |
|-------|---------|---------|
| int   | 3       | 2       |

#### CRYTON_CORE_EXECUTION_THREADS_PER_PROCESS
How some payloads or Rabbit's channel consumers should be distributed. **(do not change, if you don't know what you're doing)**  
This affects the speed of starting/consuming Steps/Rabbit requests.

| value | default | example |
|-------|---------|---------|
| int   | 7       | 5       |

#### CRYTON_CORE_APP_DIRECTORY
Path to the Cryton Core directory. **(do not change, if you don't know what you're doing)**

| value  | default               | example       |
|--------|-----------------------|---------------|
| string | ~/.local/cryton-core/ | /path/to/app/ |

!!! info ""

    The default value in Docker is set to `/app`.

## Prerequisites
Cryton Core requires the following technologies to run properly:

- [PostgreSQL database](https://www.postgresql.org/download/){target="_blank"}
- [RabbitMQ server](https://www.rabbitmq.com/download.html){target="_blank"}
- [PgBouncer](https://www.pgbouncer.org/install.html){target="_blank"}

To make the installation process smoother the prerequisites are bundled within the [Docker Compose](#with-docker-compose) installation.

??? question "Want to use pipx or Docker, but don't want to install and set up the prerequisites on your own?"

    !!! danger "Requirements"
    
        - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
        - Create [permanent settings](#settings-permanent)
    
    !!! tip "Recommendations"
    
        - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}

    Switch to the app directory:
    ```shell
    cd ~/.local/cryton-core/
    ```
    
    Download the Compose configuration:
    
    === "curl"
    
        ```shell
        curl -O https://gitlab.ics.muni.cz/cryton/cryton-core/-/raw/{{{ git_release }}}/docker-compose.prerequisites.yml
        ```
    
    === "wget"
    
        ```shell
        wget https://gitlab.ics.muni.cz/cryton/cryton-core/-/raw/{{{ git_release }}}/docker-compose.prerequisites.yml
        ```
    
    Run the Compose configuration:
    ```
    docker compose -f docker-compose.prerequisites.yml up -d
    ```

## Installation

### With Docker Compose
The easiest way to install Cryton Core (and its prerequisites) is to use the example Docker Compose configuration.

!!! danger "Requirements"

    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
    - Create [permanent settings](#settings-permanent)
    - Update the following settings:
        1. CRYTON_CORE_RABBIT_HOST=cryton-rabbit
        2. CRYTON_CORE_DB_HOST=cryton-pgbouncer
        3. CRYTON_CORE_API_USE_STATIC_FILES=true

!!! tip "Recommendations"

    - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - Override the [settings](#settings)

First, switch to the app directory:
```shell
cd ~/.local/cryton-core/
```

Download the Compose configuration:

=== "curl"

    ```shell
    curl -O https://gitlab.ics.muni.cz/cryton/cryton-core/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

=== "wget"

    ```shell
    wget https://gitlab.ics.muni.cz/cryton/cryton-core/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

Run the Compose configuration:
```
docker compose up -d
```

??? question "What should the output look like?"

    ```
    [+] Running 6/6
     ⠿ Network cryton-core_default  Created
     ⠿ Container cryton-rabbit      Healthy
     ⠿ Container cryton-db          Healthy
     ⠿ Container cryton-pgbouncer   Healthy
     ⠿ Container cryton-core        Started
     ⠿ Container cryton-proxy       Started
    ```

Check if the installation was successful and the app is running with curl:
```
curl localhost:8000/api/
```

??? question "What should the output look like?"

    ```
    {"runs":"http://localhost:8000/cryton/api/v1/runs/","plans":"http://localhost:8000/cryton/api/v1/plans/",
    "plan_executions":"http://localhost:8000/cryton/api/v1/plan_executions/","stages":"http://localhost:8000/cryton/api/v1/stages/",
    "stage_executions":"http://localhost:8000/cryton/api/v1/stage_executions/","steps":"http://localhost:8000/cryton/api/v1/steps/",
    "step_executions":"http://localhost:8000/cryton/api/v1/step_executions/","workers":"http://localhost:8000/cryton/api/v1/workers/"}
    ```

### With pipx
Cryton Core is available in the [PyPI](https://pypi.org/project/cryton-core/) and can be installed using *pip*. 
However, we **highly recommend** installing the app in an isolated environment using [pipx](https://pypa.github.io/pipx/).

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [pipx](https://pypa.github.io/pipx/){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)

Install the app:

=== "pipx"

    ```shell
    pipx install cryton-core=={{{ release_version }}}.*
    ```

=== "pip"

    ```shell
    pip install --user cryton-core=={{{ release_version }}}.*
    ```

### With Docker
Cryton Core is available as a Docker image and can be installed using Docker.

!!! danger "Requirements"

    - [Docker](https://docs.docker.com/engine/install/){target="_blank"}

!!! tip "Recommendations"

    - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - Override the [settings](#settings)
    - If you're using persistent settings, switch to the [app directory](#cryton_core_app_directory) and [pass the settings](#settings-docker)

Run the container:
```shell
docker run -d registry.gitlab.ics.muni.cz:443/cryton/cryton-core:{{{ release_version }}}
```

!!! warning "Limitations"

    The easiest way to make the container accessible from the outside and to allow the container to access the prerequisites is to use the `--network host` option:
    ```shell
    docker run --network host -d registry.gitlab.ics.muni.cz:443/cryton/cryton-core:{{{ release_version }}}
    ```

## Usage

!!! info ""

    If you're using Docker (Compose) to install the app, you don't need to migrate the database or start the services mentioned in this section.

Use the following to invoke the app:
```shell
cryton-core
```

You should see a help page:
```
Type 'cryton-core help <subcommand>' for help on a specific subcommand.

Available subcommands:
...
```

To learn about each command's options use:
```shell
cryton-core help <your command>
```

Before we do anything, **we need to migrate the database**:
```shell
cryton-core migrate
```

To be able to use Cryton Core, we need to start the REST API and RabbitMQ listener. We can do both using:
```shell
cryton-core start
```

??? question "How to change the default API host/port?"
    
    To change the default API host/port use the *--bind* option.
    ```shell
    cryton-core start --bind <address>:<port>
    ```

### REST API and control
REST API is the only way to communicate with Cryton Core. It is by default running at 
[http://0.0.0.0:8000](http://0.0.0.0:8000){target="_blank"}. Interactive documentation can be found at 
[http://0.0.0.0:8000/doc](http://0.0.0.0:8000/doc){target="_blank"}.

To be able to control Cryton Core, you have to send requests to its REST API. This can be done manually, or via [Cryton CLI](cli.md) or [Cryton Frontend](frontend.md).

## Troubleshooting

???+ question "Unable to load the interactive REST API?"

    If you're not using a reverse proxy, set `CRYTON_CORE_API_USE_STATIC_FILES=false`.
