This example will allow you to quickly install the main Cryton tools using **Docker Compose**. 

??? question "Want more deployment options?"

    - [Core](../components/core.md)
    - [Worker](../components/worker.md)
    - [Modules](../components/modules.md)
    - [CLI](../components/cli.md)
    - [Frontend](../components/frontend.md)

!!! info "System requirements"

    Please make sure you are using a system that has at least **2048 MB of RAM** and **2 CPU cores**, otherwise you might experience stability issues.

[//]: # (TODO: make a video)

## Installation

!!! danger "Requirements"

    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}

!!! tip "Recommendations"

    - Docker [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - [Production deployment](../production.md)

First, create a new directory:
```shell
mkdir cryton
cd cryton
```

Create `.env` file and download the settings into it

[//]: # (=== "curl")

[//]: # ()
[//]: # (    ```shell)

[//]: # (    curl -o .env {{{ config.site_url }}}/getting-started/env)

[//]: # (    ```)

[//]: # ()
[//]: # (=== "wget")

[//]: # ()
[//]: # (    ```shell)

[//]: # (    wget -O .env {{{ config.site_url }}}/getting-started/env)

[//]: # (    ```)

??? abstract "Show the .env file"

    ```ini
    {! include "env" !}
    ```

Create `docker-compose.yml` file and download the Compose configuration into it

[//]: # (=== "curl")

[//]: # ()
[//]: # (    ```shell)

[//]: # (    curl -O {{{ config.site_url }}}/getting-started/docker-compose.yml)

[//]: # (    ```)

[//]: # ()
[//]: # (=== "wget")

[//]: # ()
[//]: # (    ```shell)

[//]: # (    wget {{{ config.site_url }}}/getting-started/docker-compose.yml)

[//]: # (    ```)

??? abstract "Show the Compose config"

    ```yaml
    {! include "docker-compose.yml" !}
    ```

Run the Compose configuration:
```shell
docker compose up -d
```

## Test the installation
Now we want to test if the CLI, Worker, and Core are communicating.

Start an interactive shell in the cryton-cli container:
```shell
docker compose exec cryton_cli bash
```

Create (register) the Worker:
```shell
cryton-cli workers create local_worker -d "my local worker for testing"
```

Check if the Worker is reachable (use the **id** from the previous command):
```shell
cryton-cli workers health-check <id>
```

Cryton Core REST API is accessible at http://127.0.0.1:8000 and Cryton Frontend at http://127.0.0.1:8080.
