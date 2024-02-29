In this section we will go through our installation options. In case you just want to test Cryton, check the [quick-start](quick-start.md) or [playground](playground.md) pages.

!!! question "Do I need to install all components?"

    Since the version *2.0.0*, Cryton is shipped as a single application with the option to select [extras](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras). Cryton's front-end is treated as a different application.

    
    - Hive and Worker are usually installed on different hosts
    - Installing the front-end is unnecessary if you wish to control Cryton using only the CLI
    - CLI and front-end can be deployed on a different host and installed on demand

## Prerequisites
The following is a list of applications used and required by Cryton (its components).

=== "Hive"

    - [RabbitMQ server](https://www.rabbitmq.com/download.html){target="_blank"}
    - [PostgreSQL database](https://www.postgresql.org/download/){target="_blank"}
    - [PgBouncer](https://www.pgbouncer.org/install.html){target="_blank"}

    ??? tip "Use Docker images for a quick start"
    
        The following commands allow you to quickly deploy the prerequisites without studying them.  
        They use Cryton's default credentials and **shouldn't be used for production**.  
        Be aware that these commands may expose ports to network, **read them first**.
        
        [RabbitMQ](https://hub.docker.com/_/rabbitmq):
        ```shell
        docker run --rm --detach --restart always \
              --publish 5672:5672 \
              --hostname rabbit \
              --name rabbit \
              --env RABBITMQ_DEFAULT_USER=cryton \
              --env RABBITMQ_DEFAULT_PASS=cryton \
              rabbitmq:3.12
        ```
        
        [Postgres](https://hub.docker.com/_/postgres):
        ```shell
        docker run --rm --detach --restart always \
              --hostname postgres \
              --name postgres \
              --volume cryton_db_data:/var/lib/postgresql/data \
              --env POSTGRES_PASSWORD=cryton \
              --env POSTGRES_USER=cryton \
              --env POSTGRES_DB=cryton \
              --env POSTGRES_HOST_AUTH_METHOD=md5 \
              postgres:16
        ```
        
        [PgBouncer](https://hub.docker.com/r/bitnami/pgbouncer):
        ```shell
        docker run --rm --detach --restart always \
              --publish 127.0.0.1:5432:5432 \
              --hostname pgbouncer \
              --name pgbouncer \
              --volume cryton_db_data:/var/lib/postgresql/data \
              --env POSTGRESQL_HOST=postgres \
              --env POSTGRESQL_PASSWORD=cryton \
              --env POSTGRESQL_USERNAME=cryton \
              --env POSTGRESQL_DATABASE=cryton \
              --env PGBOUNCER_DATABASE=cryton \
              --env PGBOUNCER_PORT=5432 \
              --env PGBOUNCER_MAX_CLIENT_CONN=1000 \
              --env PGBOUNCER_MIN_POOL_SIZE=8 \
              --env PGBOUNCER_POOL_MODE=transaction \
              bitnami/pgbouncer:1.22.0
        ```

=== "Worker"

    - [Metasploit Framework](https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html){target="_blank"}
    - [PostgreSQL database](https://www.postgresql.org/download/){target="_blank"} (for Metasploit Framework)
    - [Empire C2](https://bc-security.gitbook.io/empire-wiki/quickstart/installation){target="_blank"}

    ??? tip "Use Docker images for a quick start"
    
        The following commands allow you to quickly deploy the prerequisites without studying them.  
        They use Cryton's default credentials and **shouldn't be used for production**.  
        Be aware that these commands may expose ports to network, **read them first**.
        
        [Metasploit Framework](docker-images.md#metasploit-framework):
        ```shell
        docker run --rm --detach --restart always \
              --tty \
              --network host \
              --name metasploit \
              --env MSF_DB_HOST=127.0.0.1 \
              --env MSF_DB_PORT=5432 \
              --env MSF_DB_NAME=cryton \
              --env MSF_DB_USERNAME=cryton \
              --env MSF_DB_PASSWORD=cryton \
              registry.gitlab.ics.muni.cz:443/cryton/configurations/metasploit-framework:0
        ```
        
        [Postgres](https://hub.docker.com/_/postgres):
        ```shell
        docker run --rm --detach --restart always \
              --publish 127.0.0.1:5432:5432 \
              --hostname postgres \
              --name postgres \
              --volume cryton_db_data:/var/lib/postgresql/data \
              --env POSTGRES_PASSWORD=cryton \
              --env POSTGRES_USER=cryton \
              --env POSTGRES_DB=cryton \
              --env POSTGRES_HOST_AUTH_METHOD=md5 \
              postgres:16
        ```
        
        [Empire](https://hub.docker.com/r/bcsecurity/empire)
        ```shell
        docker run --rm --detach --restart always \
              --interactive \
              --network host \
              --name empire \
              bcsecurity/empire:v4.10.0 \
              server --username cryton --password cryton
        ```

## With pipx
Cryton is available on [PyPI](https://pypi.org/project/cryton/){target="_blank"} and can be installed using ***pipx*** or *pip*.  
It is **highly recommended** to use *pipx*, since it creates and manages an isolated environment.

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [pipx](https://pypa.github.io/pipx/){target="_blank"}

=== "Hive"

    **pipx**
    ```shell
    pipx install cryton[hive]=={{{ release_version }}}.*
    ```
    
    **pip**
    ```shell
    pip install --user cryton[hive]=={{{ release_version }}}.*
    ```

=== "Worker"

    **pipx**
    ```shell
    pipx install cryton[worker]=={{{ release_version }}}.*
    ```
    
    **pip**
    ```shell
    pip install --user cryton[worker]=={{{ release_version }}}.*
    ```

=== "CLI"

    **pipx**
    ```shell
    pipx install cryton[cli]=={{{ release_version }}}.*
    ```
    
    **pip**
    ```shell
    pip install --user cryton[cli]=={{{ release_version }}}.*
    ```

=== "All-in-one"

    **pipx**
    ```shell
    pipx install cryton[all]=={{{ release_version }}}.*
    ```
    
    **pip**
    ```shell
    pip install --user cryton[all]=={{{ release_version }}}.*
    ```

Once you finish the installation, check out the [usage](usage/index.md) page.

## With Docker
Cryton is also shipped in the form of Docker images.

!!! danger "Requirements"

    - [Docker](https://docs.docker.com/engine/install/){target="_blank"}

!!! note

    In the following commands, we are using the `--network host` parameter which tells the container to use host's network interface. You don't have to use it, but make sure the applications and prerequisites can communicate.

    This doesn't apply to the front-end. We will expose only the necessary port.

Once you start the container, and it's healthy, you are all set.

Before starting the containers, make sure to check out the [settings](settings.md) page.  
In case of a misconfiguration the containers can keep restarting (become unhealthy) or Worker and Hive may not communicate. If that happens check the logs from the unhealthy container (`docker logs <container-name>`).

=== "Hive"

    Run the container in the background:
    ```shell
    docker run --network host -d registry.gitlab.ics.muni.cz:443/cryton/cryton/hive:{{{ release_version }}}
    ```

=== "Worker"

    Two versions of Worker are shipped. Both of them contain the modules and their prerequisites. One is based on the Alpine linux and the other on Kali.
    
    Run the *Alpine* linux version container in the background:
    ```shell
    docker run --network host -d registry.gitlab.ics.muni.cz:443/cryton/cryton/worker:{{{ release_version }}}
    ```
    
    Run the *Kali* linux version container in the background:
    ```shell
    docker run --network host -d registry.gitlab.ics.muni.cz:443/cryton/cryton/worker:kali-{{{ release_version }}}
    ```

=== "CLI"

    Run the container and enter an interactive shell:
    ```shell
    docker run --network host -it registry.gitlab.ics.muni.cz:443/cryton/cryton/cli:{{{ release_version }}}
    ```

=== "Frontend"

    Run the container and enter an interactive shell:
    ```shell
    docker run -d -p 127.0.0.1:8080:80 registry.gitlab.ics.muni.cz:443/cryton/cryton-frontend:{{{ release_version }}}
    ```

## Shell completion
Shell completion is available for the *Bash*, *Zsh*, and *Fish* shell and has to be manually enabled (after successful installation).

First, make sure the app directory exists:
```shell
mkdir -p ~/.local/cryton/
```

Generate, save, and load the completion script:

=== "Hive"

    === "Bash"
    
        ```shell
        _CRYTON_HIVE_COMPLETE=bash_source cryton-hive > ~/.local/cryton/cryton-hive-complete.bash
        echo ". ~/.local/cryton/cryton-hive-complete.bash" >> ~/.bashrc
        ```
    
    === "Zsh"
    
        ```shell
        _CRYTON_HIVE_COMPLETE=zsh_source cryton-hive > ~/.local/cryton/cryton-hive-complete.zsh
        echo ". ~/.local/cryton/cryton-hive-complete.zsh" >> ~/.zshrc
        ```
    
    === "Fish"
    
        ```shell
        _CRYTON_HIVE_COMPLETE=fish_source cryton-hive > ~/.config/fish/completions/cryton-hive-complete.fish
        ```

=== "Worker"

    === "Bash"
    
        ```shell
        _CRYTON_WORKER_COMPLETE=bash_source cryton-worker > ~/.local/cryton/cryton-worker-complete.bash
        echo ". ~/.local/cryton/cryton-worker-complete.bash" >> ~/.bashrc
        ```
    
    === "Zsh"
    
        ```shell
        _CRYTON_WORKER_COMPLETE=zsh_source cryton-worker > ~/.local/cryton/cryton-worker-complete.zsh
        echo ". ~/.local/cryton/cryton-worker-complete.zsh" >> ~/.zshrc
        ```
    
    === "Fish"
    
        ```shell
        _CRYTON_WORKER_COMPLETE=fish_source cryton-worker > ~/.config/fish/completions/cryton-worker-complete.fish
        ```

=== "CLI"

    === "Bash"
    
        ```shell
        _CRYTON_CLI_COMPLETE=bash_source cryton-cli > ~/.local/cryton/cryton-cli-complete.bash
        echo ". ~/.local/cryton/cryton-cli-complete.bash" >> ~/.bashrc
        ```
    
    === "Zsh"
    
        ```shell
        _CRYTON_CLI_COMPLETE=zsh_source cryton-cli > ~/.local/cryton/cryton-cli-complete.zsh
        echo ". ~/.local/cryton/cryton-cli-complete.zsh" >> ~/.zshrc
        ```
    
    === "Fish"
    
        ```shell
        _CRYTON_CLI_COMPLETE=fish_source cryton-cli > ~/.config/fish/completions/cryton-cli-complete.fish
        ```

You may need to restart your shell for the changes to take effect.

## Installing additional modules
To install an unofficial module, please check [here](modules/index.md#installing-unofficial-modules).
