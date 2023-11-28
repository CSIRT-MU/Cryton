## Description
Cryton CLI is a command line interface used to interact with [Cryton Core](core.md) (its API).

[Link to the repository](https://gitlab.ics.muni.cz/cryton/cryton-cli){target="_blank"}.

## Settings
Cryton CLI uses environment variables for its settings. Please update them to your needs.

### Overriding settings
To override the settings, use the `export` command:
```shell
export CRYTON_CLI_API_HOST=127.0.0.1
```

!!! note ""

    Use `unset` to remove a variable.

!!! tip ""

    Some settings can be overridden using the CLI. Try using:
    ```
    cryton-cli --help
    ```

??? tip "Overriding settings permanently"

    <div id="settings-permanent"></div>

    First, make sure the app directory exists:
    ```shell
    mkdir -p ~/.local/cryton-cli/
    ```
    
    Download the default settings into the app directory:
    
    === "curl"
    
        ```shell
        curl -o ~/.local/cryton-cli/.env https://gitlab.ics.muni.cz/cryton/cryton-cli/-/raw/{{{ git_release }}}/.env
        ```
    
    === "wget"
    
        ```shell
        wget -O ~/.local/cryton-cli/.env https://gitlab.ics.muni.cz/cryton/cryton-cli/-/raw/{{{ git_release }}}/.env
        ```

    Open the file and update it to your needs.

??? tip "Overriding settings with Docker"

    <div id="settings-docker"></div>

    To override a variable use the `-e` or the `--env-file` option:
    ```
    docker run -e CRYTON_CLI_API_HOST=127.0.0.1 --env-file relative/path/to/.env ...
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
          - relative/path/to/.env
    ```

    More information can be found [here](https://docs.docker.com/compose/environment-variables/set-environment-variables/#use-the-environment-attribute){target="_blank"}.

### Available settings

#### CRYTON_CLI_TIME_ZONE
[Timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones){target="_blank"} used for scheduling (for example when 
scheduling a Run). Use the `AUTO` value to use your system timezone.

| value  | default | example       |
|--------|---------|---------------|
| string | AUTO    | Europe/Prague |

#### CRYTON_CLI_API_HOST
Cryton Core's API address.

| value  | default   | example          |
|--------|-----------|------------------|
| string | 127.0.0.1 | cryton-core.host |

#### CRYTON_CLI_API_PORT
Cryton Core's API port.

| value | default | example |
|-------|---------|---------|
| int   | 8000    | 8008    |

#### CRYTON_CLI_API_SSL
Use SSL to connect to REST API.

| value    | default | example |
|----------|---------|---------|
| boolean  | false   | true    |

#### CRYTON_CLI_API_ROOT
REST API URL. **(do not change, if you don't know what you're doing)**

| value  | default | example   |
|--------|---------|-----------|
| string | api/    | api/path/ |

#### CRYTON_CLI_APP_DIRECTORY
Path to the Cryton CLI directory. **(do not change, if you don't know what you're doing)**

| value  | default              | example       |
|--------|----------------------|---------------|
| string | ~/.local/cryton-cli/ | /path/to/app/ |

!!! info ""

    The default value in Docker is set to `/app`.

## Installation

### With pipx
Cryton CLI is available in the [PyPI](https://pypi.org/project/cryton-cli/){target="_blank"} and can be installed using *pip*. 
However, we **highly recommend** installing the app in an isolated environment using [pipx](https://pypa.github.io/pipx/){target="_blank"}.

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [pipx](https://pypa.github.io/pipx/){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](#settings)
    - Enable [shell completion](#shell-completion)

Install the app:

=== "pipx"

    ```shell
    pipx install cryton-cli=={{{ release_version }}}.*
    ```

=== "pip"

    ```shell
    pip install --user cryton-cli=={{{ release_version }}}.*
    ```

### With Docker
Cryton CLI is available as a Docker image and can be installed using Docker.

!!! danger "Requirements"

    - [Docker](https://docs.docker.com/engine/install/){target="_blank"}

!!! tip "Recommendations"

    - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - Override the [settings](#settings)
    - If you're using persistent settings, switch to the [app directory](#cryton_cli_app_directory) and [pass the settings](#settings-docker)

Run the container and enter an interactive shell:
```shell
docker run -it --network host registry.gitlab.ics.muni.cz:443/cryton/cryton-cli:{{{ release_version }}}
```

### With Docker Compose
Example Docker Compose configuration is also available. 

!!! danger "Requirements"

    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}

!!! tip "Recommendations"

    - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}
    - Override the [settings](#settings)
    - If you're using persistent settings, switch to the [app directory](#cryton_cli_app_directory) and [pass the settings](#settings-compose)

??? tip "Switch to the app directory"

    ```shell
    mkdir -p ~/.local/cryton-cli/
    cd ~/.local/cryton-cli/
    ```

Download the configuration using:

=== "curl"

    ```shell
    curl -O https://gitlab.ics.muni.cz/cryton/cryton-cli/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

=== "wget"

    ```shell
    wget https://gitlab.ics.muni.cz/cryton/cryton-cli/-/raw/{{{ git_release }}}/docker-compose.yml
    ```

Run the container and enter an interactive shell:
```
docker compose run cryton_cli
```

## Usage
Use the following to invoke the app:
```shell
cryton-cli
```

You should see a help page:
```
Usage: cryton-cli [OPTIONS] COMMAND [ARGS]...

  A CLI wrapper for Cryton API.

Options:
  ...
```

To learn about each command's options use:
```shell
cryton-cli <your command> --help
```

??? question "How to change the default API host/port?"
    
    To change the default API host/port use *-H* and *-p* options.
    ```shell
    cryton-cli -H 127.0.0.1 -p 8000 <your command>
    ```

## Shell completion
Shell completion is available for the *Bash*, *Zsh*, and *Fish* shell and has to be manually enabled.

!!! info ""

    - To enable the shell completion, the tool must be present
    - The shell completion is enabled in Docker by default

First, make sure the app directory exists:

=== "Bash"

    ```shell
    mkdir -p ~/.local/cryton-cli/
    ```

=== "Zsh"

    ```shell
    mkdir -p ~/.local/cryton-cli/
    ```

Generate, save, and load the completion script:

=== "Bash"

    ```shell
    _CRYTON_CLI_COMPLETE=bash_source cryton-cli > ~/.local/cryton-cli/cryton-cli-complete.bash
    echo ". ~/.local/cryton-cli/cryton-cli-complete.bash" >> ~/.bashrc
    ```

=== "Zsh"

    ```shell
    _CRYTON_CLI_COMPLETE=zsh_source cryton-cli > ~/.local/cryton-cli/cryton-cli-complete.zsh
    echo ". ~/.local/cryton-cli/cryton-cli-complete.zsh" >> ~/.zshrc
    ```

=== "Fish"

    ```shell
    _CRYTON_CLI_COMPLETE=fish_source cryton-cli > ~/.config/fish/completions/cryton-cli-complete.fish
    ```

You may need to restart your shell for the changes to take effect.
