After the Run has successfully ended (or not) you can **generate a report** with every Step's output. 
When you have multiple Plan executions in a single Run (when utilizing multiple Workers), you can compare each 
execution and use this insight to e.g. score each team in a *cybersecurity exercise.*

The easiest way to generate a report is to use [CLI](../interfaces/cli.md):
```shell
cryton-cli runs report <ID>
```

Optionally, you can also generate a report for Plan/Stage/Step execution.

You can see an example report here:
```yaml
id: 7
plan_id: 6
plan_name: Basic example
state: FINISHED
schedule_time: null
start_time: '2022-07-21T20:37:27.650142Z'
pause_time: null
finish_time: '2022-07-21T20:37:28.527673Z'
plan_executions:
- id: 7
  plan_name: Basic example
  state: FINISHED
  schedule_time: null
  start_time: '2022-07-21T20:37:27.661100Z'
  finish_time: '2022-07-21T20:37:28.517554Z'
  pause_time: null
  worker_id: 1
  worker_name: e2e-1
  evidence_dir: /tmp/run_7/worker_e2e-1
  stage_executions:
  - id: 7
    stage_name: get-localhost-credentials
    state: FINISHED
    start_time: '2022-07-21T20:37:27.862354Z'
    pause_time: null
    finish_time: '2022-07-21T20:37:28.504804Z'
    schedule_time: '2022-07-21T20:37:27.762581Z'
    step_executions:
    - id: 11
      step_name: check-ssh
      state: FINISHED
      start_time: '2022-07-21T20:37:27.898861Z'
      finish_time: '2022-07-21T20:37:28.276521Z'
      output: ''
      serialized_output:
        stats:
          args: /usr/bin/nmap -oX - -sV -p22 192.168.61.13
          start: '1658386108'
          scanner: nmap
          version: '7.80'
          startstr: Thu Jul 21 06:48:28 2022
          xmloutputversion: '1.04'
        runtime:
          exit: success
          time: '1658386109'
          elapsed: '0.31'
          summary: Nmap done at Thu Jul 21 06:48:29 2022; 1 IP address (1 host up)
            scanned in 0.31 seconds
          timestr: Thu Jul 21 06:48:29 2022
        192.168.61.13:
          ports:
          - cpe:
            - cpe: cpe:/a:openbsd:openssh:8.4p1
            - cpe: cpe:/o:linux:linux_kernel
            state: open
            portid: '22'
            reason: syn-ack
            scripts: []
            service:
              conf: '10'
              name: ssh
              method: probed
              ostype: Linux
              product: OpenSSH
              version: 8.4p1 Debian 5
              extrainfo: protocol 2.0
            protocol: tcp
            reason_ttl: '64'
          state:
            state: up
            reason: arp-response
            reason_ttl: '0'
          osmatch: {}
          hostname:
          - name: 192.168.61.13
            type: PTR
          macaddress:
            addr: 08:00:27:D4:BF:9E
            vendor: Oracle VirtualBox virtual NIC
            addrtype: mac
      evidence_file: 'No evidence '
      valid: false
    - id: 12
      step_name: bruteforce
      state: FINISHED
      start_time: '2022-07-21T20:37:28.343619Z'
      finish_time: '2022-07-21T20:37:28.479002Z'
      output: ''
      serialized_output:
        password: victim
        username: victim
        all_credentials:
        - password: victim
          username: victim
      evidence_file: 'No evidence '
      valid: false

```
