## Cryton Core

Get the image:
```
docker pull registry.gitlab.ics.muni.cz:443/cryton/cryton-core:latest
```

### Variables
The image takes the [same variables](components/core.md#available-settings) as its application counterpart with the same version.

### Tags
All tags can be found [here](https://gitlab.ics.muni.cz/cryton/cryton-core/container_registry/5985).

There is also an image with a `proxy-*` tag, which is an Apache proxy for the Core's REST API. It takes no variables.

## Cryton Worker

Get the image:
```
docker pull registry.gitlab.ics.muni.cz:443/cryton/cryton-worker:latest
```

### Variables
The image takes the [same variables](components/core.md#available-settings) as its application counterpart with the same version.

### Tags
All tags can be found [here](https://gitlab.ics.muni.cz/cryton/cryton-worker/container_registry/5987).

There is also an image with a `kali-*` tag, which is based on Kali linux and has all modules and their tools installed.

## Cryton CLI

Get the image:
```
docker pull registry.gitlab.ics.muni.cz:443/cryton/cryton-cli:latest
```

### Variables
The image takes the [same variables](components/cli.md#available-settings) as its application counterpart with the same version.

### Tags
All tags can be found [here](https://gitlab.ics.muni.cz/cryton/cryton-cli/container_registry/5986).

## Cryton Frontend

Get the image:
```
docker pull registry.gitlab.ics.muni.cz:443/cryton/cryton-frontend:latest
```

### Variables
The image has no specific variables or configuration.

### Tags
All tags can be found [here](https://gitlab.ics.muni.cz/cryton/cryton-frontend/container_registry/5984).

## Metasploit Framework

Get the image:
```
docker pull registry.gitlab.ics.muni.cz:443/cryton/configurations/metasploit-framework:latest
```

### Variables

- MSF_RPC_HOST="127.0.0.1"
- MSF_RPC_PORT="55553"
- MSF_RPC_SSL="true"
- MSF_RPC_USERNAME="cryton"
- MSF_RPC_PASSWORD="cryton"
- MSF_DB_HOST="127.0.0.1"
- MSF_DB_PORT="5432"
- MSF_DB_NAME="msf"
- MSF_DB_USERNAME="cryton"
- MSF_DB_PASSWORD="cryton"
- MSF_DB_PREPARED_STATEMENTS="true"
- MSF_DB_ADVISORY_LOCKS="true"

!!! warning

    Set the `MSF_DB_PREPARED_STATEMENTS` and `MSF_DB_ADVISORY_LOCKS` variables to `false` in combination with an external pooler like PgBouncer.

### Configuration
Use the option `tty: true`.

The service must be able to communicate with the Worker.

### Tags
All tags can be found [here](https://gitlab.ics.muni.cz/cryton/configurations/container_registry/6121).

## Empire
Image page can be found [here](https://hub.docker.com/r/bcsecurity/empire).

Get the image:
```
docker pull bcsecurity/empire:v{{{ empire_version }}}
```

### Configuration
Use the option `stdin_open: true`.

Override the default command with: `command: [ "server", "--username", "<username>", "--password", "<password>" ]`.  
The username and password must match the variables `$CRYTON_WORKER_EMPIRE_USERNAME` and `$CRYTON_WORKER_EMPIRE_PASSWORD` from Worker.

The service must be able to communicate with the Worker.

## RabbitMQ
Image page can be found [here](https://hub.docker.com/_/rabbitmq).

Get the image:
```
docker pull rabbitmq
```

### Configuration
The service must be accessible from Core and Worker.

## PostgreSQL
Image page can be found [here](https://hub.docker.com/_/postgres).

Get the image:
```
docker pull postgres
```

## PgBouncer
Image page can be found [here](https://hub.docker.com/r/bitnami/pgbouncer).

Get the image:
```
docker pull bitnami/pgbouncer
```

??? tip "Using with Pycharm"

    To be able to access the DB through the PgBouncer, set the following: 
    
    `PGBOUNCER_IGNORE_STARTUP_PARAMETERS: extra_float_digits`.
