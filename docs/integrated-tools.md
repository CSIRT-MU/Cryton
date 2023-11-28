This page holds the information about the integrated tools.

## Metasploit Framework
Metasploit's [homepage](https://github.com/rapid7/metasploit-framework){target="_blank"} and [documentation](https://docs.metasploit.com/){target="_blank"}.

Latest tested and supported version is **{{{ metasploit_version }}}**.

### Configuration
Metasploit's RPC server must be running and accessible by Worker ([Worker MSF settings](components/worker.md#available-settings)).

??? tip "Start the server manually in the background"
    
    To start the server manually use:
    ```shell
    msfrpcd -U cryton -P cryton
    ```

??? tip "Start the server manually from the msfconsole"

    Start the MSF console and run the following to start the RPC server:
    ```
    load msgrpc ServerHost=127.0.0.1 ServerPort=55553 User=cryton Pass='cryton' SSL=true
    ```

### Features

- [Session management](design-phase/step.md#session-management)
- [MSF listener](design-phase/stage.md#msf-listener)
- [Module execution](modules.md#modmsf)

## Empire
Empire's [homepage](https://github.com/BC-SECURITY/Empire){target="_blank"} and [documentation](https://bc-security.gitbook.io/empire-wiki/){target="_blank"}.

Latest tested and supported version is **{{{ empire_version }}}**.

### Configuration
Empire's server must be running and accessible by Worker ([Worker Empire settings](components/worker.md#available-settings)).

### Features

- [Deploy agent](design-phase/step.md#deploy-empire-agent-on-a-target)
- [Use agent](design-phase/step.md#execute-shell-script-or-empire-module-on-agent)

### Troubleshooting

#### Empire Agent cannot connect to the Empire server
1. If you are using metasploit session for agent deployment, check that the session is functioning correctly
2. Check that the Listener Host option is set to an IP address of the machine that the Empire server is running on and that the target you are deploying an Empire agent on has access to that IP address

#### Deploy Empire agent on Windows
Currently, the `multi/launcher` option is the recommended `stager_type` for use with Windows machines.

!!! warning

    For Empire stagers to work on newer versions of Windows OS, you need to disable all **firewall** and **antivirus** protection on the targeted Windows machine.
