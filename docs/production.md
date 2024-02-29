There are some rules you should follow when deploying Cryton to a production environment.

## Core
### Settings
Update these settings to not use the default values

- CRYTON_CORE_RABBIT_PASSWORD
- CRYTON_CORE_DB_PASSWORD
- CRYTON_CORE_API_SECRET_KEY

### Proxy
Hide the rest API behind a proxy with restricted access.

!!! tip

    Use the officially supplied docker-compose.yml.

## Worker
### Settings
Update these settings to not use the default values

- CRYTON_WORKER_NAME
- CRYTON_WORKER_MODULES_DIRECTORY
- CRYTON_WORKER_MSF_RPC_PASSWORD
- CRYTON_WORKER_RABBIT_PASSWORD
- CRYTON_WORKER_EMPIRE_PASSWORD


https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
