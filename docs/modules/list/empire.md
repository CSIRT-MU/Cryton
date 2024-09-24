## Description

Module orchestrates [Empire](https://github.com/BC-SECURITY/Empire). It allows you to deploy and use its agents.

## Prerequisites

Empire C2 server must be accessible from Worker it will be executed on.

## Input parameters

### `agent_name`

Name of the deployed agent.

| Name         | Type   | Required | Default value | Example value |
|--------------|--------|----------|---------------|---------------|
| `agent_name` | string | &check;  |               | `myAgent`     |

### `action`

Which type of action you want to perform.

Current options are:

* `deploy` - deploy a new agent
* `execute-command` - execute a command on an existing agent
* `execute-module` - execute an Empire module on an existing agent

| Name     | Type   | Required | Default value | Example value |
|----------|--------|----------|---------------|---------------|
| `action` | string | &check;  |               | `deploy`      |

=== "Deploy agent"

    ### `session_id`
    
    Metasploit session to use.
    
    | Name         | Type    | Required | Default value | Example value |
    |--------------|---------|----------|---------------|---------------|
    | `session_id` | integer | &check;  |               | `1`           |
    
    ### `listener`
    
    Arguments used for listener creation.
    
    | Name       | Type   | Required | Default value | Example value         |
    |------------|--------|----------|---------------|-----------------------|
    | `listener` | object | &check;  |               | `{"name": "my-name"}` |
    
    #### `name`
    
    Name of listener in Empire for identification. If listener with this name already exists in Empire, it will be used for
    stager generation.
    
    | Name   | Type   | Required | Default value | Example value |
    |--------|--------|----------|---------------|---------------|
    | `name` | string | &check;  |               | `myName`      |
    
    #### `port`
    
    Port on which should be listener communicating with Agents.
    
    | Name   | Type    | Required | Default value | Example value |
    |--------|---------|----------|---------------|---------------|
    | `port` | integer | &cross;  | `80`          | `8080`        |
    
    #### `type`
    
    Type of the listener.
    
    | Name   | Type   | Required | Default value | Example value |
    |--------|--------|----------|---------------|---------------|
    | `type` | string | &cross;  | `http`        | `smb`         |
    
    #### `options`
    
    Additional adjustable parameters for creating listener. More
    on [here](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/listeners){target="_blank"}.
    
    | Name      | Type   | Required | Default value | Example value           |
    |-----------|--------|----------|---------------|-------------------------|
    | `options` | object | &cross;  |               | `{"BindIP": "0.0.0.0"}` |
    
    ### `stager`
    
    Arguments used for stager creation.
    
    | Name     | Type   | Required | Default value | Example value            |
    |----------|--------|----------|---------------|--------------------------|
    | `stager` | object | &check;  |               | `{"type": "multi/bash"}` |
    
    #### `type`
    
    Type of stager that should be generated in form of path. For stager types
    look [here](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/stagers){target="_blank"}.
    
    | Name   | Type   | Required | Default value | Example value |
    |--------|--------|----------|---------------|---------------|
    | `type` | string | &check;  |               | `multi/bash`  |
    
    #### `options`
    
    Additional adjustable parameters for generating stager. Parameters can be viewed in individual stager python files or
    through Empire client.
    
    | Name      | Type   | Required | Default value | Example value            |
    |-----------|--------|----------|---------------|--------------------------|
    | `options` | object | &cross;  |               | `{"Language": "python"}` |

=== "Execute command"

    ### `command`
    
    Command to execute on the agent.
    
    | Name      | Type   | Required | Default value | Example value |
    |-----------|--------|----------|---------------|---------------|
    | `command` | string | &check;  |               | `whoami`      |

=== "Execute module"

    ### `module`
    
    Arguments used for Empire module execution.
    
    | Name     | Type   | Required | Default value | Example value                    |
    |----------|--------|----------|---------------|----------------------------------|
    | `module` | object | &check;  |               | `{"name": "collection/sniffer"}` |
    
    #### `name`
    
    Name of the Empire module in form of a path. Available Empire
    modules [here](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/modules){target="_blank"}.
    
    | Name   | Type   | Required | Default value | Example value        |
    |--------|--------|----------|---------------|----------------------|
    | `name` | string | &check;  |               | `collection/sniffer` |
    
    #### `arguments`
    
    Additional arguments for the Empire module.
    
    | Name        | Type   | Required | Default value | Example value               |
    |-------------|--------|----------|---------------|-----------------------------|
    | `arguments` | object | &cross;  |               | `{"IpFilter": "127.0.0.1"}` |

## Examples

### Deploy agent

Input:

```yaml
my-step:
  module: empire
  arguments:
    action: deploy
    agent_name: MyAgent
    session_id: 1
    listener:
      name: testing
    stager:
      type: multi/bash

```

Output:

```json
{
  "result": "ok",
  "output": "Agent 'MyAgent' deployed on target 192.168.61.12.",
  "serialized_output": {}
}
```

### Execute command on agent

Input:

```yaml
my-step:
  module: empire
  arguments:
    action: execute-command
    agent_name: MyAgent
    command: whoami

```

Output:

```json
{
  "result": "ok",
  "output": "{'agent': 'E5XSKQ4F', 'command': 'whoami', 'results': 'victim', 'taskID': 2, 'user_id': 1, 'username': 'empireadmin'}",
  "serialized_output": {}
}
```

### Execute module on agent

Input:

```yaml
my-step:
  module: empire
  arguments:
    action: execute-module
    agent_name: MyAgent
    module:
      name: collection/sniffer
      arguments:
        IpFilter: 192.168.33.12
        PortFilter: 1234

```

Output:

```json
{
  "result": "ok",
  "output": "<output from the module execution>",
  "serialized_output": {}
}
```

## Troubleshooting

Only the 4.10.0 version is supported.

* Some Metasploit sessions may be unsuitable for deploying Empire agents
* Make sure the Empire host is set correctly in the scenario and is reachable from the target
* Currently, the `multi/launcher` option is the recommended stager for use with Windows machines
* For Empire stagers to work on newer versions of Windows OS, you need to disable all **firewall** and **antivirus**
  protection on the target

## Output serialization

The output is not serialized.
