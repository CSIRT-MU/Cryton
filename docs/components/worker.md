## Description
Cryton Worker is used for executing [attack modules](modules.md) remotely. It consumes messages from [Cryton Core](core.md) through the
[RabbitMQ](https://www.rabbitmq.com/){target="_blank"}.

[Link to the repository](https://gitlab.ics.muni.cz/cryton/cryton-worker){target="_blank"}.

## Settings
Cryton Worker uses environment variables for its settings. Please update them to your needs.

### Overriding settings
To override the settings, use the `export` command:
```shell
export CRYTON_WORKER_NAME=name
```

!!! note ""

    Use `unset` to remove a variable.

!!! tip ""

    Some settings can be overridden using the CLI. Try using:
    ```
    cryton-worker start --help
    ```

??? tip "Overriding settings permanently"

    <div id="settings-permanent"></div>

    First, make sure the app directory exists:
    ```shell
    mkdir -p ~/.local/cryton-worker/
    ```
    
    Download the default settings into the app directory:
    
    === "curl"
    
        ```shell
        curl -o ~/.local/cryton-worker/.env https://gitlab.ics.muni.cz/cryton/cryton-worker/-/raw/{{{ git_release }}}/.env
        ```
    
    === "wget"
    
        ```shell
        wget -O ~/.local/cryton-worker/.env https://gitlab.ics.muni.cz/cryton/cryton-worker/-/raw/{{{ git_release }}}/.env
        ```

    Open the file and update it to your needs.

??? tip "Overriding settings with Docker"

    <div id="settings-docker"></div>

    To override a variable use the `-e` or the `--env-file` option:
    ```
    docker run -e CRYTON_WORKER_NAME=name --env-file relative/path/to/.env ...
    ```

    More information can be found [here](https://docs.docker.com/engine/reference/commandline/run/#env){target="_blank"}.

??? tip "Overriding settings with Docker compose"

    <div id="settings-compose"></div>

    Override variables in the `environment` or the `env_file` attribute:
    ```
    services
      service:
        environment:
          - CRYTON_WORKER_NAME=name
        env_file:
          - relative/path/to/.env
    ```

    More information can be found [here](https://docs.docker.com/compose/environment-variables/set-environment-variables/#use-the-environment-attribute){target="_blank"}.

### Available settings

#### CRYTON_WORKER_NAME
Unique name used to identify the Worker.

| value  | default | example   |
|--------|---------|-----------|
| string | worker  | my_worker |

!!! warning

    Worker's name is used as an identifier. Make sure it matches once you use it in Cryton Core.

#### CRYTON_WORKER_MODULES_DIRECTORY
Path to the directory containing the modules.

| value  | default               | example                      |
|--------|-----------------------|------------------------------|
| string | APP_DIRECTORY/modules | /opt/cryton-modules/modules/ |

#### CRYTON_WORKER_DEBUG
Make Worker run in debug mode.

| value   | default | example |
|---------|---------|---------|
| boolean | false   | true    |

#### CRYTON_WORKER_INSTALL_REQUIREMENTS
Install requirements.txt for each module on startup.

| value   | default | example |
|---------|---------|---------|
| boolean | true    | false   |

#### CRYTON_WORKER_CONSUMER_COUNT
The number of consumers used for Rabbit communication (more equals faster request processing and heavier processor usage).

| value | default | example |
|-------|---------|---------|
| int   | 7       | 3       |

#### CRYTON_WORKER_PROCESSOR_COUNT
The number of processors used for internal requests (more equals faster internal requests processing, but heavier processor usage).

| value | default | example |
|-------|---------|---------|
| int   | 7       | 3       |

#### CRYTON_WORKER_MAX_RETRIES
How many times to try to re-connect to RabbitMQ when the connection is lost.

| value | default | example |
|-------|---------|---------|
| int   | 3       | 5       |

#### CRYTON_WORKER_MSF_RPC_HOST
Metasploit Framework RPC host.

| value | default   | example     |
|-------|-----------|-------------|
| str   | 127.0.0.1 | msfrpc.host |

#### CRYTON_WORKER_MSF_RPC_PORT
Metasploit Framework RPC port.

| value | default | example |
|-------|---------|---------|
| int   | 55553   | 55554   |

#### CRYTON_WORKER_MSF_RPC_SSL
Use SSL to connect to Metasploit Framework RPC.

| value   | default | example |
|---------|---------|---------|
| boolean | true    | false   |

#### CRYTON_WORKER_MSF_RPC_USERNAME
Username for Metasploit Framework RPC login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | msf     |

#### CRYTON_WORKER_MSF_RPC_PASSWORD
Password for Metasploit Framework RPC login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | toor    |

#### CRYTON_WORKER_RABBIT_HOST
RabbitMQ server host.

| value  | default   | example     |
|--------|-----------|-------------|
| string | 127.0.0.1 | rabbit.host |

#### CRYTON_WORKER_RABBIT_PORT
RabbitMQ server port.

| value | default | example |
|-------|---------|---------|
| int   | 5672    | 15672   |

#### CRYTON_WORKER_RABBIT_USERNAME
Username for RabbitMQ server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | admin   |

#### CRYTON_WORKER_RABBIT_PASSWORD
Password for RabbitMQ server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | mypass  |

#### CRYTON_WORKER_EMPIRE_HOST
Empire server host.

| value  | default   | example     |
|--------|-----------|-------------|
| string | 127.0.0.1 | empire.host |

#### CRYTON_WORKER_EMPIRE_PORT
Empire server port.

| value | default | example |
|-------|---------|---------|
| int   | 1337    | 11337   |

#### CRYTON_WORKER_EMPIRE_USERNAME
Username for Empire server login.

| value  | default | example     |
|--------|---------|-------------|
| string | cryton  | empireadmin |

#### CRYTON_WORKER_EMPIRE_PASSWORD
Password for Empire server login.

| value  | default | example     |
|--------|---------|-------------|
| string | cryton  | password123 |

#### CRYTON_WORKER_MSF_DB_HOST
[:octicons-tag-24: Worker 1.1.0]({{{ releases.worker }}}1.1.0){target="_blank"}
Postgres server host.

| value  | default   | example       |
|--------|-----------|---------------|
| string | 127.0.0.1 | cryton-msf-db |

#### CRYTON_WORKER_MSF_DB_PORT
[:octicons-tag-24: Worker 1.1.0]({{{ releases.worker }}}1.1.0){target="_blank"}
Postgres server port.

| value | default | example |
|-------|---------|---------|
| int   | 5432    | 15432   |

#### CRYTON_WORKER_MSF_DB_NAME
[:octicons-tag-24: Worker 1.1.0]({{{ releases.worker }}}1.1.0){target="_blank"}
Used Postgres database name.

| value  | default | example |
|--------|---------|---------|
| string | msf     | cryton  |

#### CRYTON_WORKER_MSF_DB_USERNAME
[:octicons-tag-24: Worker 1.1.0]({{{ releases.worker }}}1.1.0){target="_blank"}
Username for Postgres server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | user    |

#### CRYTON_WORKER_MSF_DB_PASSWORD
[:octicons-tag-24: Worker 1.1.0]({{{ releases.worker }}}1.1.0){target="_blank"}
Password for Postgres server login.

| value  | default | example |
|--------|---------|---------|
| string | cryton  | passwd  |

#### CRYTON_WORKER_APP_DIRECTORY
Path to the Cryton Worker directory. **(do not change, if you don't know what you're doing)**

| value  | default                 | example       |
|--------|-------------------------|---------------|
| string | ~/.local/cryton-worker/ | /path/to/app/ |

!!! info ""

    The default value in Docker is set to `/app`.

## Prerequisites
Cryton Worker requires the following technologies to run properly:

- [Metasploit Framework](https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html){target="_blank"}
- [Empire C2](https://bc-security.gitbook.io/empire-wiki/quickstart/installation){target="_blank"}
- [PostgreSQL database](https://www.postgresql.org/download/){target="_blank"} (required by Metasploit Framework)

To make the installation process smoother the prerequisites are bundled within the [Docker Compose](#with-docker-compose) installation.

??? question "Want to use pipx or Docker, but don't want to install and set up the prerequisites on your own?"

    !!! danger "Requirements"
    
        - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
        - Create [permanent settings](#settings-permanent)
    
    !!! tip "Recommendations"
    
        - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}

    Switch to the app directory:
    ```shell
    cd ~/.local/cryton-worker/
    ```
    
    Download the Compose configuration:
    
    === "curl"
    
        ```shell
        curl -O https://gitlab.ics.muni.cz/cryton/cryton-worker/-/raw/{{{ git_release }}}/docker-compose.prerequisites.yml
        ```
    
    === "wget"
    
        ```shell
        wget https://gitlab.ics.muni.cz/cryton/cryton-worker/-/raw/{{{ git_release }}}/docker-compose.prerequisites.yml
        ```
    
    Run the Compose configuration:
    ```
    docker compose -f docker-compose.prerequisites.yml up -d
    ```

??? question "Have an already running Postgres (database) instance?"

    In case you have a running Postgres instance, you can reuse it. Just make sure it's accessible from the *msfconsole* and update the `CRYTON_WORKER_MSF_DB_*` variables to your needs.  
    You also have to **update the Compose configuration** you're using, so it won't launch a new database instance.
    
    More information about the MSF Docker image can be found [here](../docker-settings.md#metasploit-framework).

## Installation

### With Docker Compose
The easiest way to install Cryton Worker, modules, and its prerequisites is to use the example Docker Compose configuration.

!!! danger "Requirements"

    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
    - Create [permanent settings](#settings-permanent)

!!! tip "Recommendations"

    - Docker [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - Override the [settings](#settings)

First, switch to the app directory:
```shell
cd ~/.local/cryton-worker/
```

!!! warning

    Make sure that the `CRYTON_WORKER_MODULES_DIRECTORY` setting contains the default value.

Download the configuration using:

=== "curl"

    ```shell
    curl -O https://gitlab.ics.muni.cz/cryton/cryton-worker/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

=== "wget"

    ```shell
    wget https://gitlab.ics.muni.cz/cryton/cryton-worker/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

Run the Compose configuration:
```
docker compose up -d
```

??? question "What should the output look like?"

    ```
    [+] Running 6/6
     ✔ Network cryton-worker_default              Created      0.1s 
     ✔ Volume "cryton-worker_cryton_msf_db_data"  Created      0.0s 
     ✔ Container cryton-empire                    Started      0.0s 
     ✔ Container cryton-msf-db                    Healthy      0.0s 
     ✔ Container cryton-msf                       Started      0.0s 
     ✔ Container cryton-worker                    Started      0.0s
    ```

Everything should be set. Check if the installation was successful and the Worker is running:
```shell
docker compose cryton_worker logs
```
You should see `[*] Waiting for messages.` in the output.

### With pipx
Cryton Worker is available in the [PyPI](https://pypi.org/project/cryton-worker/){target="_blank"} and can be installed using *pip*. 
However, we **highly recommend** installing the app in an isolated environment using [pipx](https://pypa.github.io/pipx/){target="_blank"}.

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [pipx](https://pypa.github.io/pipx/){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)
    - Enable [shell completion](#shell-completion)

Install the [modules](modules.md#installation) into the app directory.

!!! warning

    Make sure that the `CRYTON_WORKER_MODULES_DIRECTORY` setting contains the default value.

Install the app:

=== "pipx"

    ```shell
    pipx install cryton-worker=={{{ release_version }}}.*
    ```

=== "pip"

    ```shell
    pip install --user cryton-worker=={{{ release_version }}}.*
    ```

### With Docker
Cryton Worker is available as a Docker image and can be installed using Docker.

!!! danger "Requirements"

    - [Docker](https://docs.docker.com/engine/install/){target="_blank"}

!!! tip "Recommendations"

    - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - Override the [settings](#settings)
    - If you're using persistent settings, switch to the [app directory](#cryton_worker_app_directory) and [pass the settings](#settings-docker)

Two versions of Worker image are shipped. 

The bare version only contains Worker and should be used on a Kali OS.  
The Kali version takes care of the modules and their system requirements. However, the drawback is its large size.

=== "bare version"

    Install the [modules](modules.md#installation) into the app directory and export the path:
    ```shell
    export CRYTON_WORKER_MODULES_DIRECTORY=~/.local/cryton-worker/modules/
    ```
    
    !!! warning "Make sure that the persistent settings match"
    
        Check the real value of the variable using:
        ```shell
        export | grep CRYTON_WORKER_MODULES_DIRECTORY
        ```

    The following command ensures effortless deployment. It mounts the modules and shares the host's networking namespace.
    ```
    docker run --network host -v ${CRYTON_WORKER_MODULES_DIRECTORY}:/app/modules -d registry.gitlab.ics.muni.cz:443/cryton/cryton-worker:{{{ release_version }}}
    ```

    !!! warning "Limitations"
    
        - The easiest way to make the container accessible from the outside and to allow the container to access the prerequisites is to use the `--network host` option
        - Since the image doesn't contain the tools, Metasploit Framework, or Empire C2 server, you need to set up and mount them on your own using [volumes](https://docs.docker.com/storage/volumes/)

=== "kali version"

    !!! warning

        Make sure that the `CRYTON_WORKER_MODULES_DIRECTORY` setting contains the default value.

    The following command will start the Worker container. It shares the host's networking namespace.
    ```
    docker run --network host -d registry.gitlab.ics.muni.cz:443/cryton/cryton-worker:kali-{{{ release_version }}}
    ```

    !!! warning "Limitations"
    
        - The easiest way to make the container accessible from the outside and to allow the container to access the prerequisites is to use the `--network host` option
        - Since the image doesn't contain the Metasploit Framework, or Empire C2 server, you need to set up on your own

## Usage
!!! info ""

    If you're using Docker (Compose) to install the app, you can ignore this section.

Use the following to invoke the app:
```shell
cryton-worker
```

You should see a help page:
```
Usage: cryton-worker [OPTIONS] COMMAND [ARGS]...

  Cryton Worker CLI.

Options:
  ...
```

To learn about each command's options use:
```shell
cryton-worker <your command> --help
```

To start Worker use `cryton-worker start` and you should see something like:
```
Starting Worker worker..
To exit press CTRL+C
Connection does not exist. Retrying..
Connection to RabbitMQ server established.
[*] Waiting for messages.
```

??? question "Want to run the Worker in the background?"

    Use the `nohup` command:
    ```shell
    nohup cryton-worker start > /tmp/worker_std_out 2>&1 &
    ```

    To **stop** the Worker, find their processes and kill them:
    ```shell
    ps -aux | grep cryton-worker
    kill <PID> <PID>
    ```

## Shell completion
Shell completion is available for the *Bash*, *Zsh*, and *Fish* shell and has to be manually enabled.

!!! info ""

    - To enable the shell completion, the tool must be present
    - The shell completion is enabled in Docker by default

First, make sure the app directory exists:

=== "Bash"

    ```shell
    mkdir -p ~/.local/cryton-worker/
    ```

=== "Zsh"

    ```shell
    mkdir -p ~/.local/cryton-worker/
    ```

Generate, save, and load the completion script:

=== "Bash"

    ```shell
    _CRYTON_WORKER_COMPLETE=bash_source cryton-worker > ~/.local/cryton-worker/cryton-worker-complete.bash
    echo ". ~/.local/cryton-worker/cryton-worker-complete.bash" >> ~/.bashrc
    ```

=== "Zsh"

    ```shell
    _CRYTON_WORKER_COMPLETE=zsh_source cryton-worker > ~/.local/cryton-worker/cryton-worker-complete.zsh
    echo ". ~/.local/cryton-worker/cryton-worker-complete.zsh" >> ~/.zshrc
    ```

=== "Fish"

    ```shell
    _CRYTON_WORKER_COMPLETE=fish_source cryton-worker > ~/.config/fish/completions/cryton-worker-complete.fish
    ```

You may need to restart your shell for the changes to take effect.
