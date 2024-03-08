In this guide, we will use **Docker Compose** to deploy Cryton, its prerequisites, and frontend.

!!! question "Want more deployment options?"

    - [Installation guide](installation.md) (pip/pipx/Docker)
    - [Playground](playground.md) (prebuilt Docker infrastructure)

[//]: # (TODO: make a video)

!!! danger "Requirements"

    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
    - `curl` / `wget`
    - System with **2048 MB of RAM** and **2 CPU cores**

Download the Compose config file

=== "curl"

    ```shell
    curl -O https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

=== "wget"

    ```shell
    wget https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

and run it:
```shell
docker compose up -d
```

!!! note ""

    Cryton's REST API should be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000) and frontend at [http://127.0.0.1:8080](http://127.0.0.1:8080).

    If that's not the case, make sure the ports aren't occupied by a different application.

## Test the deployment
Now we want to test if the CLI, Worker, and Hive are communicating.

Start an interactive shell in the cryton-cli container:
```shell
docker compose exec cryton_cli bash
```

Register the Worker:
```shell
cryton-cli workers create worker -d "my local worker for testing"
```

Check if the Worker is reachable (use the **id** from the previous command):
```shell
cryton-cli workers health-check <id>
```
