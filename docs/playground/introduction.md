The Cryton playground is an isolated environment where you can test the capabilities of the Cryton toolset on your local machine.

The main reasons you might want to try it:

- With a single command you can build the whole infrastructure
- With a single command you can run a predefined attack plan
- It takes minutes and is easy to reset
- It allows you to quickly run E2E tests

???+ note "Limitations"

    - Docker doesn't allow custom gateways/routers which results in creating overlying networks that simulate separated networks

## Setup

!!! danger "Requirements"

    - [Git](https://git-scm.com/)
    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
    - Make sure you have at least 4 cores and 8GB of RAM

!!! tip "Recommendations"

    - Docker [Post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/){target="_blank"}

First, we clone the repository and switch into it:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-playground.git
cd cryton-playground
```

Now, we build the infrastructure:
```shell
docker compose up -d
```

Once we are done, Cryton toolset and vulnerable targets should be up and running.

## Usage
Once we have the infrastructure running, we have multiple options.

### Run the example scenario
We have prepared an example attack scenario that uses multiple Cryton features ([session management](../design-phase/step.md#session-management),
[output sharing](../design-phase/step.md#output-sharing), [conditional execution](../design-phase/step.md#conditional-execution), and more ...).

You can run it using:
```shell
docker compose exec cryton_cli /opt/resources/run_scenario_1.sh
```

More information can be found [here](example-scenario.md).

### Create your own scenario
If you know what you're doing, you can try to come up with your own attack plan.

Feel free to access the Worker container and try to find vulnerabilities and attack vectors that you could utilize in your
final scenario. If the provided infrastructure is not ideal for your needs, you can also add more containers.

??? question "How do I access a container?"

    Generally you want to start an interactive session inside the container using:
    ```shell
    docker compose exec -it <container_name> bash
    ```
    
    To access the Worker container use:
    ```shell
    docker compose exec -it cryton_worker bash
    ```

### E2E testing
If you're trying to develop a new feature for the Cryton toolset, you might want to run some tests. That can be troublesome
if you need to test many components or run multiple tests multiple times.

First, we need to link all necessary components to the **cryton-playground** directory (**make sure you are in the correct directory** `cd cryton-playground`):
```shell
ln -s /path/to/cryton-cli cryton-cli
ln -s /path/to/cryton-core cryton-core
ln -s /path/to/cryton-worker cryton-worker
ln -s /path/to/cryton-frontend cryton-frontend
ln -s /path/to/cryton-modules cryton-modules
ln -s /path/to/cryton-e2e cryton-e2e
```

???+ question "Do I need to link all components?"

    If you've updated only one component, there is no need to download and link other components. However, you need to
    remove the service(s) that you haven't changed (linked) from the `docker-compose.e2e.yml` file.

Rebuild the infrastructure:
```shell
docker compose down -t 0 && docker compose -f docker-compose.yml -f docker-compose.e2e.yml up -d --build
```

Run e2e tests:
```shell
docker compose exec cryton_cli cryton-e2e run-tests
```

More information can be found [here](../development/e2e-testing.md).

---

## Troubleshooting

### Unable to build the infrastructure
Make sure the address pools this playground uses are available.

### Services are not running correctly
If you're having problems with the services (they keep restarting for example):

1. Shut down the running infrastructure with no timeout:
    ```shell
    docker compose down -t 0
    ```

2. Remove all unused data, volumes, and images:
    ```shell
    docker system prune --volumes --all
    ```

3. Build the Infrastructure again:
    ```shell
    docker compose up -d
    ```

### Proxy settings
If you're using a proxy, paste the following settings into `~/.docker/config.json` on your host:
```
{
 "proxies":
 {
   "default":
   {
     "httpProxy": "<proxy-address>",
     "httpsProxy": "<proxy-address>",
     "noProxy": "localhost,.cryton"
   }
 }
}
```

---

## Infrastructure

### core.cryton
Contains Cryton Core, Apache proxy, CLI (optionally cryton-e2e).

IP addresses:

- 192.168.90.10

### worker.cryton
Contains Cryton Worker, MSF, Empire C2.

IP addresses:

- 192.168.90.11
- 192.168.91.11

### cryton_frontend
Contains Cryton Frontend.

IP addresses:

- 192.168.90.12

### db.cryton
Contains DB server.

IP addresses:

- 192.168.90.13

### pgbouncer.cryton
Contains PgBouncer server.

IP addresses:

- 192.168.90.14

### rabbit.cryton
Contains RabbitMQ server.

IP addresses:

- 192.168.90.15

### wordpress_db
DB server for WordPress.

IP addresses:

- 192.168.93.11

### wordpress_app
WordPress application with known credentials.

IP addresses:

- 192.168.91.10
- 192.168.92.10
- 192.168.93.10
- 192.168.94.10

### vulnerable_ftp
FTP server with a known exploit.

IP addresses:

- 192.168.92.20

### vulnerable_db
Postgres DB server.

IP addresses:

- 192.168.92.21
- 192.168.94.21

### vulnerable_user_machine
Contains Ubuntu image with a running SSH service and weak credentials.

IP addresses:

- 192.168.94.20
