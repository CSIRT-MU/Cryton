By default, settings, logs, and other important files are stored in the application directory (`APP_DIRECTORY`) located at `~/.local/cryton/` (`/app/` in case you are in a Docker image).

There are multiple ways to update the settings (the higher the number the higher the priority):

1. [YAML configuration](https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/settings.yml){target="_blank"} in the application directory (`APP_DIRECTORY/settings.yml`)
2. [File with environment variables](https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/settings){target="_blank"} in the application directory (`APP_DIRECTORY/settings`)
3. Temporary override using environment variables
4. Temporary override using options in each CLI application

## Overriding settings
To override the settings (using environment variables), use the `export` command:
```shell
export CRYTON_CLI_API_HOST=127.0.0.1
```

The environment variables must be prefixed by `CRYTON_` and are comprised of the uppercase path of the setting and with dots replaced by underscores, as in the example above for setting `cli.api.host`.

!!! note ""

    Use `unset` to remove a variable.

!!! tip ""

    Some settings can be overridden using the CLI. Try using:
    ```
    cryton-cli --help
    ```
    ```
    cryton-hive --help
    ```
    ```
    cryton-worker --help
    ```

??? tip "Overriding settings with Docker"

    <div id="settings-docker"></div>

    To override a variable use the `-e` or the `--env-file` option:
    ```
    docker run -e CRYTON_CLI_API_HOST=127.0.0.1 --env-file relative/path/to/settings ...
    ```

    More information can be found [here](https://docs.docker.com/engine/reference/commandline/run/#env){target="_blank"}.

??? tip "Overriding settings with Docker compose"

    <div id="settings-compose"></div>

    Override variables in the `environment` or the `env_file` attribute:
    ```
    services
      service:
        environment:
          - CRYTON_CLI_API_HOST=127.0.0.1
        env_file:
          - relative/path/to/settings
    ```

    More information can be found [here](https://docs.docker.com/compose/environment-variables/set-environment-variables/#use-the-environment-attribute){target="_blank"}.

??? question "How do I change the location of the application directory"

    <div id="settings-application-directory"></div>

    Simply update the value of the `CRYTON_APP_DIRECTORY` environment variable to the path you desire. Don't forget that environment variables are not permanent.

## Available settings

[//]: # (| type | default | example | YAML variable path | Environment variable |)
[//]: # (|------|---------|---------|--------------------|----------------------|)
[//]: # (|      |         |         |                    | CRYTON_              |)

### Hive

#### Debug
Allow debug logs to be saved/displayed.

| type    | default | example | YAML variable path | Environment variable |
|---------|---------|---------|--------------------|----------------------|
| boolean | false   | true    | hive.debug         | CRYTON_HIVE_DEBUG    |

#### Message timeout
Timeout (in seconds) for RabbitMQ requests and messages.

| type  | default | example | YAML variable path   | Environment variable        |
|-------|---------|---------|----------------------|-----------------------------|
| int   | 180     | 300     | hive.message_timeout | CRYTON_HIVE_MESSAGE_TIMEOUT |

!!! warning ""

    If you choose a lower timeout value and the Worker's IP changes during runtime, the messages may timeout. This is because the Worker tries to reconnect to RabbitMQ server after two minutes of silence.

#### Threads per process
Affects the number of message consumers and speed of starting and consuming Rabbit messages.

| type | default | example | YAML variable path       | Environment variable            |
|------|---------|---------|--------------------------|---------------------------------|
| int  | 7       | 5       | hive.threads_per_process | CRYTON_HIVE_THREADS_PER_PROCESS |

#### CPU cores
The number of CPU cores that can be utilized at the same time. This affects the speed of sending and consuming Rabbit messages.

Set the value to `0` to use all cores.

| type | default | example | YAML variable path | Environment variable  |
|------|---------|---------|--------------------|-----------------------|
| int  | 3       | 4       | hive.cpu_cores     | CRYTON_HIVE_CPU_CORES |

#### Rabbit host
RabbitMQ server host.

| type   | default   | example     | YAML variable path | Environment variable    |
|--------|-----------|-------------|--------------------|-------------------------|
| string | 127.0.0.1 | rabbit-host | hive.rabbit.host   | CRYTON_HIVE_RABBIT_HOST |

#### Rabbit port
RabbitMQ server port.

| type | default | example | YAML variable path | Environment variable    |
|------|---------|---------|--------------------|-------------------------|
| int  | 5672    | 15672   | hive.rabbit.port   | CRYTON_HIVE_RABBIT_PORT |

#### Rabbit username
Username for RabbitMQ server login.

| type   | default | example | YAML variable path   | Environment variable        |
|--------|---------|---------|----------------------|-----------------------------|
| string | cryton  | admin   | hive.rabbit.username | CRYTON_HIVE_RABBIT_USERNAME |

#### Rabbit password
Password for RabbitMQ server login.

| type   | default | example | YAML variable path   | Environment variable        |
|--------|---------|---------|----------------------|-----------------------------|
| string | cryton  | admin   | hive.rabbit.password | CRYTON_HIVE_RABBIT_PASSWORD |

#### Rabbit queue - attack_response
Queue name for processing attack responses.

| type   | default                | example                   | YAML variable path                 | Environment variable                      |
|--------|------------------------|---------------------------|------------------------------------|-------------------------------------------|
| string | cryton.attack.response | cryton.attack.response.id | hive.rabbit.queues.attack_response | CRYTON_HIVE_RABBIT_QUEUES_ATTACK_RESPONSE |

#### Rabbit queue - agent_response
Queue name for processing agent responses.

| type   | default               | example                  | YAML variable path                | Environment variable                     |
|--------|-----------------------|--------------------------|-----------------------------------|------------------------------------------|
| string | cryton.agent.response | cryton.agent.response.id | hive.rabbit.queues.agent_response | CRYTON_HIVE_RABBIT_QUEUES_AGENT_RESPONSE |

#### Rabbit queue - event_response
Queue name for processing event responses.

| type   | default               | example                  | YAML variable path                | Environment variable                     |
|--------|-----------------------|--------------------------|-----------------------------------|------------------------------------------|
| string | cryton.event.response | cryton.event.response.id | hive.rabbit.queues.event_response | CRYTON_HIVE_RABBIT_QUEUES_EVENT_RESPONSE |

#### Rabbit queue - control_request
Queue name for processing control requests.

| type   | default                | example                   | YAML variable path                 | Environment variable                      |
|--------|------------------------|---------------------------|------------------------------------|-------------------------------------------|
| string | cryton.control.request | cryton.control.request.id | hive.rabbit.queues.control_request | CRYTON_HIVE_RABBIT_QUEUES_CONTROL_REQUEST |

#### Database host
Postgres server host.

| type   | default   | example       | YAML variable path | Environment variable      |
|--------|-----------|---------------|--------------------|---------------------------|
| string | 127.0.0.1 | database-host | hive.database.host | CRYTON_HIVE_DATABASE_HOST |

#### Database port
Postgres server port.

| type | default | example | YAML variable path | Environment variable      |
|------|---------|---------|--------------------|---------------------------|
| int  | 5432    | 15432   | hive.database.port | CRYTON_HIVE_DATABASE_PORT |

#### Database name
Postgres database name to connect to.

| type   | default | example | YAML variable path | Environment variable      |
|--------|---------|---------|--------------------|---------------------------|
| string | cryton  | custom  | hive.database.name | CRYTON_HIVE_DATABASE_NAME |

#### Database username
Username for Postgres server login.

| type   | default | example | YAML variable path     | Environment variable          |
|--------|---------|---------|------------------------|-------------------------------|
| string | cryton  | admin   | hive.database.username | CRYTON_HIVE_DATABASE_USERNAME |

#### Database password
Password for Postgres server login.

| type   | default | example | YAML variable path     | Environment variable          |
|--------|---------|---------|------------------------|-------------------------------|
| string | cryton  | admin   | hive.database.password | CRYTON_HIVE_DATABASE_PASSWORD |

#### API secret key
Key (64 chars) used by the REST API for cryptographic signing. More information can be found [here](https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-SECRET_KEY){target="_blank"}.

| type   | default | example     | YAML variable path  | Environment variable       |
|--------|---------|-------------|---------------------|----------------------------|
| string | cryton  | XF37...6HB3 | hive.api.secret_key | CRYTON_HIVE_API_SECRET_KEY |

#### API allowed hosts
Domain names that the site can serve. More information can be found [here](https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts){target="_blank"}.

| type                               | default | example     | YAML variable path     | Environment variable          |
|------------------------------------|---------|-------------|------------------------|-------------------------------|
| list of strings separated by space | "*"     | host1 host2 | hive.api.allowed_hosts | CRYTON_HIVE_API_ALLOWED_HOSTS |

### Worker

#### Name
**Unique** name used for Worker identification and communication.

| type   | default | example  | YAML variable path | Environment variable |
|--------|---------|----------|--------------------|----------------------|
| string | worker  | attacker | worker.name        | CRYTON_WORKER_NAME   |

#### Debug
Allow debug logs to be saved/displayed.

| type    | default | example | YAML variable path | Environment variable |
|---------|---------|---------|--------------------|----------------------|
| boolean | false   | true    | worker.debug       | CRYTON_WORKER_DEBUG  |

#### Consumer count
The number of consumers used for Rabbit and internal message processing.

| type | default | example | YAML variable path    | Environment variable         |
|------|---------|---------|-----------------------|------------------------------|
| int  | 7       | 3       | worker.consumer_count | CRYTON_WORKER_CONSUMER_COUNT |

#### Max retries
The number of retries before shuttling down, when the connection to RabbitMQ is lost.

| type | default | example | YAML variable path | Environment variable      |
|------|---------|---------|--------------------|---------------------------|
| int  | 3       | 5       | worker.max_retries | CRYTON_WORKER_MAX_RETRIES |

#### Modules - install requirements
Install `requirements.txt` for each module on startup.

| type    | default | example | YAML variable path                  | Environment variable                       |
|---------|---------|---------|-------------------------------------|--------------------------------------------|
| boolean | true    | false   | worker.modules.install_requirements | CRYTON_WORKER_MODULES_INSTALL_REQUIREMENTS |

#### Rabbit host
RabbitMQ server host.

| type   | default   | example     | YAML variable path | Environment variable      |
|--------|-----------|-------------|--------------------|---------------------------|
| string | 127.0.0.1 | rabbit-host | worker.rabbit.host | CRYTON_WORKER_RABBIT_HOST |

#### Rabbit port
RabbitMQ server port.

| type | default | example | YAML variable path | Environment variable      |
|------|---------|---------|--------------------|---------------------------|
| int  | 5672    | 15672   | worker.rabbit.port | CRYTON_WORKER_RABBIT_PORT |

#### Rabbit username
Username for RabbitMQ server login.

| type   | default | example | YAML variable path     | Environment variable          |
|--------|---------|---------|------------------------|-------------------------------|
| string | cryton  | admin   | worker.rabbit.username | CRYTON_WORKER_RABBIT_USERNAME |

#### Rabbit password
Password for RabbitMQ server login.

| type   | default | example | YAML variable path     | Environment variable          |
|--------|---------|---------|------------------------|-------------------------------|
| string | cryton  | admin   | worker.rabbit.password | CRYTON_WORKER_RABBIT_PASSWORD |

#### Empire host
Empire server host.

| type   | default   | example     | YAML variable path | Environment variable      |
|--------|-----------|-------------|--------------------|---------------------------|
| string | 127.0.0.1 | empire-host | worker.empire.host | CRYTON_WORKER_EMPIRE_HOST |

#### Empire port
Empire server port.

| type | default | example | YAML variable path | Environment variable      |
|------|---------|---------|--------------------|---------------------------|
| int  | 1337    | 11337   | worker.empire.port | CRYTON_WORKER_EMPIRE_PORT |

#### Empire username
Username for Empire server login.

| type   | default | example | YAML variable path     | Environment variable          |
|--------|---------|---------|------------------------|-------------------------------|
| string | cryton  | admin   | worker.empire.username | CRYTON_WORKER_EMPIRE_USERNAME |

#### Empire password
Password for Empire server login.

| type   | default | example | YAML variable path     | Environment variable          |
|--------|---------|---------|------------------------|-------------------------------|
| string | cryton  | admin   | worker.empire.password | CRYTON_WORKER_EMPIRE_PASSWORD |


#### Metasploit host
Metasploit RPC server host.

| type   | default   | example         | YAML variable path     | Environment variable          |
|--------|-----------|-----------------|------------------------|-------------------------------|
| string | 127.0.0.1 | metasploit-host | worker.metasploit.host | CRYTON_WORKER_METASPLOIT_HOST |

#### Metasploit port
Metasploit RPC server port.

| type | default | example | YAML variable path     | Environment variable          |
|------|---------|---------|------------------------|-------------------------------|
| int  | 55553   | 55554   | worker.metasploit.port | CRYTON_WORKER_METASPLOIT_PORT |

#### Metasploit SSL
Use SSL to connect to Metasploit RPC server.

| type    | default | example | YAML variable path    | Environment variable         |
|---------|---------|---------|-----------------------|------------------------------|
| boolean | true    | false   | worker.metasploit.ssl | CRYTON_WORKER_METASPLOIT_SSL |

#### Metasploit username
Username for Metasploit RPC server login.

| type   | default | example | YAML variable path         | Environment variable              |
|--------|---------|---------|----------------------------|-----------------------------------|
| string | cryton  | admin   | worker.metasploit.username | CRYTON_WORKER_METASPLOIT_USERNAME |

#### Metasploit password
Password for Metasploit RPC server login.

| type   | default | example | YAML variable path         | Environment variable              |
|--------|---------|---------|----------------------------|-----------------------------------|
| string | cryton  | admin   | worker.metasploit.password | CRYTON_WORKER_METASPLOIT_PASSWORD |

### CLI

#### Debug
Return raw responses from the REST API.

| type    | default | example | YAML variable path | Environment variable |
|---------|---------|---------|--------------------|----------------------|
| boolean | false   | true    | cli.debug          | CRYTON_CLI_DEBUG     |

#### Timezone
[Timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones){target="_blank"} used for scheduling (for example when scheduling a Run). 

Set the value to `DEFAULT` to use your system timezone.

| type   | default | example       | YAML variable path | Environment variable |
|--------|---------|---------------|--------------------|----------------------|
| string | DEFAULT | Europe/Prague | cli.timezone       | CRYTON_CLI_TIMEZONE  |

#### API host
Cryton Hive's REST API address.

| type   | default   | example     | YAML variable path | Environment variable |
|--------|-----------|-------------|--------------------|----------------------|
| string | 127.0.0.1 | cryton-hive | cli.api.host       | CRYTON_CLI_API_HOST  |

#### API port
Cryton Hive's REST API port.

| type  | default | example | YAML variable path | Environment variable |
|-------|---------|---------|--------------------|----------------------|
| int   | 8000    | 8008    | cli.api.port       | CRYTON_CLI_API_PORT  |

#### API SSL
Use SSL to connect to Cryton Hive's REST API.

| type    | default | example | YAML variable path | Environment variable |
|---------|---------|---------|--------------------|----------------------|
| boolean | false   | true    | cli.api.ssl        | CRYTON_CLI_API_SSL   |
