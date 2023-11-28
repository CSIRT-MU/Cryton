## Description
Cryton Frontend is a graphical interface used to interact with [Cryton Core](core.md) (its API).

[Link to the repository](https://gitlab.ics.muni.cz/cryton/cryton-frontend){target="_blank"}.

## Settings
Cryton Frontend uses environment variables for its settings. Please update them to your needs.

!!! warning "Notice"

    For now, settings can be changed only for the [npm installation](../development/frontend.md#installation).  
    However, it is possible to update the API host and port at runtime at 
    [http://localhost:8080/app/user/settings](http://localhost:8080/app/user/settings){target="_blank"}.

Variables can be found in `src/environments/`. For production modify the _environment.prod.ts_ file, else modify the _environment.ts_ file.

#### crytonRESTApiHost 
Cryton Core's API address.

| value  | default   | example          |
|--------|-----------|------------------|
| string | 127.0.0.1 | cryton-core.host |

#### crytonRESTApiPort
Cryton Core's API port.

| value | default | example |
|-------|---------|---------|
| int   | 8000    | 8008    |

#### refreshDelay
Sets artificial delay in milliseconds for refresh API requests.

??? question "What is this for?"

    Users usually react better if the requests don't happen instantly, but they can see a tiny bit of loading. 
    Initial API request doesn't use delay, this is only for refreshing data

| value | default | example |
|-------|---------|---------|
| int   | 300     | 500     |

#### useHttps
Use SSL to connect to REST API.

| value   | default | example |
|---------|---------|---------|
| boolean | false   | true    |

## Installation

### With Docker
Cryton Frontend is available as a Docker image and can be installed using Docker.

!!! danger "Requirements"

    - [Docker](https://docs.docker.com/engine/install/){target="_blank"}

!!! tip "Recommendations"

    - [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}

[//]: # (    - Override the [settings]&#40;#settings&#41;)

Run the front end in the background:
```shell
docker run -d -p 127.0.0.1:8080:80 registry.gitlab.ics.muni.cz:443/cryton/cryton-frontend:{{{ release_version }}}
```

### With Docker Compose
Example Docker Compose configuration is also available. 

!!! danger "Requirements"

    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}

!!! tip "Recommendations"

    - [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}

[//]: # (    - Override the [settings]&#40;#settings&#41;)

??? tip "Create a new directory"

    ```shell
    mkdir cryton-frontend
    cd cryton-frontend
    ```

Download the configuration using:

=== "curl"

    ```shell
    curl -O https://gitlab.ics.muni.cz/cryton/cryton-frontend/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

=== "wget"

    ```shell
    wget https://gitlab.ics.muni.cz/cryton/cryton-frontend/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

Run the Compose configuration:
```
docker compose up -d
```

## Usage
By default, the Frontend is served at [http://localhost:8080/](http://localhost:8080/){target="_blank"}.

Use the in-app help pages to learn about usage.

[//]: # (TODO: make a video)
