As the name suggests, a Step is equal to one action. All the possible actions will be described later. 
Every step can have a successor(s) whose execution will follow according to provided conditions.

Example of defining Step using YAML:
```yaml
name: get-credentials
meta:
  description: This is an example description
  ...
step_type: worker/execute
is_init: true
output_prefix: credentials_from_localhost
arguments:
  module: medusa
  module_arguments:
    target: localhost
    credentials:
      username: admin
      password: admin
output:
  replace:
    "^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$": removed-ip
next:
  - type: result
    value: ok
    step: create-sesion
```

To better understand what each argument means and defines, here is a short description (sub-arguments are omitted 
since they will be discussed in more depth in their section):  

- **name** - Sets the name of the Step, which is mainly used to define its purpose (**must be unique** across the Plan).
- **meta** - An undefined dictionary containing metadata. The `description` parameter is just an example, you can define your own.
- **step_type** - Sets what action will the Step perform and what `arguments` will the Step use, more info [below](#step-types).
- **is_init** - Defines if the step is initial (is executed first) and is not a successor.
- **output_prefix** - If you want to use a custom name for sharing Step's results (*serialized_output*) you can define this parameter.
By default, the Step's *name* is used. For more details see [Output prefix](#output-prefix).
- **arguments** - Dictionary of arguments different for each *step_type*. To check out all possible parameters and 
types see [types section](#step-types).
- **next** - Defines Step's successors, more info [below](#conditional-execution).

## Step types
Step types are represented by the mandatory `step_type` parameter which defines what action should be executed in Step.
It tells the Worker component what arguments to expect and what functions to run based on them.

**Currently, there are 3 types:**

| Step type                                                           | Purpose                                                               |
|---------------------------------------------------------------------|-----------------------------------------------------------------------|
| [`worker/execute`](#execute-attack-module-on-worker)                | Execution of attack modules.                                          |
| [`empire/agent-deploy`](#deploy-empire-agent-on-a-target)           | Deployment of Empire agent on target.                                 |
| [`empire/execute`](#execute-shell-script-or-empire-module-on-agent) | Execution of shell commands or Empire modules on active Empire agent. |

### Execute attack module on Worker
This functionality uses `step_type: worker/execute` and enables the execution of an attack module on a worker defined by the following parameters.

| Argument                                                        | Description                                                                                                        |
|-----------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| `module`                                                        | Defines a path (will be added to the path defined in Worker) to the chosen module that will be executed on Worker. |
| `module_arguments`                                              | Python dictionary (JSON) containing arguments that will be passed to the module.                                   |
| `create_named_session`<br>(optional)                            | How to name the session this module will create for later usage.                                                   |
| `use_named_session`<br>(optional)                               | Name of created msf session through Cryton.                                                                        |
| `use_any_session_to_target`<br>(optional)                       | Ip address of target on which has been created MSF session.                                                        |

[Execution variables](#execution-variables) can be used only for the `module_arguments` parameter!

### Deploy Empire agent on a target
This functionality uses `step_type: empire/agent-deploy` and enables to deploy Empire agent on the given target 
(executing Empire generated payload with given parameters on target).

**Usable arguments for this step type are:**

| Argument                                                        | Description                                                                                                                                                                                              |
|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `listener_name`                                                 | Name of listener in Empire for identification. If listener with this name already exists in Empire, it will be used for stager generation.                                                               |
| `listener_port`<br>(optional)                                   | Port on which should be listener communicating with Agents.                                                                                                                                              |
| `listener_options`<br>(optional)                                | Additional adjustable parameters for creating listener. More on [here](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/listeners){target="_blank"}.                                      |
| `listener_type`<br>(optional)                                   | Type of listener (default: http).                                                                                                                                                                        |
| `stager_type`                                                   | Type of stager that should be generated in form of path (example: `multi/bash'). For stager types look [here](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/stagers){target="_blank"}. |
| `stager_options`<br>(optional)                                  | Additional adjustable parameters for generating stager. Parameters can be viewed in individual stager python files or through Empire client.                                                             |
| `agent_name`                                                    | Name for the deployed agent which is going to be used as a reference to this agent later.                                                                                                                |
| `use_named_session`<br>(optional)                               | Name of created msf session through Cryton.                                                                                                                                                              |
| `use_any_session_to_target`<br>(optional)                       | Ip address of target on which has been created msf session                                                                                                                                               |
| `session_id`<br>(optional)                                      | ID of msf session to target.                                                                                                                                                                             |
| [`ssh_connection`](#arguments-for-ssh_connection)<br>(optional) | Arguments for creating ssh connection to target.                                                                                                                                                         |

#### Arguments for `ssh_connection`

| Argument                 | Description                                               |
|--------------------------|-----------------------------------------------------------|
| `target`                 | Ip address for ssh connection.                            |
| `username`<br>(optional) | Username for ssh connection.                              |
| `password`<br>(optional) | Password for ssh connection if `ssh_key` is not supplied. |
| `ssh_key`<br>(optional)  | Ssh key for ssh connection if `password` is not supplied. |
| `port`<br>(optional)     | Port for ssh connection (default: 22).                    |

#### Example
```yaml
- name: deploy-agent
  step_type: empire/agent-deploy
  arguments:
    use_named_session: session_to_target_1 # using named session created in step ssh-session
    listener_name: testing
    listener_port: 80
    stager_type: multi/bash
    agent_name: MyAgent # only lower/upper characters and numbers allowed in name
```

#### Troubleshooting

- Some Metasploit sessions may be unsuitable for deploying Empire agents
- Make sure the Empire host is set correctly in the scenario and is reachable from the target
- Currently, the `multi/launcher` option is the recommended `stager_type` for use with Windows machines
- For Empire stagers to work on newer versions of Windows OS, you need to disable all **firewall** and **antivirus** protection on the target

### Execute shell script or Empire module on agent
This functionality uses `step_type: empire/execute` and allows the execution of shell commands or Empire modules on active Empire agents.

**To execute a Shell command use the following arguments:**

| Argument        | Description                                                                   |
|-----------------|-------------------------------------------------------------------------------|
| `use_agent`     | Name of an active agent that checked on Empire server.                        |
| `shell_command` | Shell command that should be executed on an active agent (example: `whoami`). |

**To execute an Empire module use the following arguments:**

| Argument                         | Description                                                                                                                                                                                                                                     |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_agent`                      | Name of an active agent that checked on Empire server.                                                                                                                                                                                          |
| `module`                         | Name of Empire module in form of a path that should be executed on the active agent (example: `collection/sniffer`). Available Empire modules [here](https://github.com/BC-SECURITY/Empire/tree/master/empire/server/modules){target="_blank"}. |
| `module_arguments`<br>(optional) | Additional arguments for Empire module execution.                                                                                                                                                                                               |


#### Example
```yaml
- name: sniffer-on-agent
  step_type: empire/execute
  arguments:
    use_agent: MyAgent
    module: collection/sniffer
    module_arguments: # Optional
      IpFilter: 192.168.33.12
      PortFilter: 1234
```

```yaml
- name: whoami-on-agent
  step_type: empire/execute
  arguments:
    use_agent: MyAgent
    shell_command: whoami
```

## Conditional execution
To be able to execute an attack scenario according to some execution tree, Steps provide a way to be executed 
according to specified conditions. Multiple types of conditions can be used. To use them in designing a 
Template, a list of dictionaries **containing** params **type**, **value**, and **step** must be provided.

| parameter | Description                                                                                                                    |
|-----------|--------------------------------------------------------------------------------------------------------------------------------|
| **type**  | Defines which value you want to compare, according to the output of the parent Step.                                           |
| **value** | Defines the desired value of the selected type. Can be defined as a string (one value) or a list of strings (multiple values). |
| **step**  | Defines the name(s) of the Step's successor(s). Can be a string (one successor) or a list of strings (multiple successors).    |

The following are types of conditions together with descriptions of possible values.

| Type                | Value                                          | Description                                                                                                                             |
|---------------------|------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `result`            | ok, fail, error                                | Match final `result` of the Step.                                                                                                       |
| `serialized_output` | Regular expression, for example: `^my_regex.*` | Match [regex](https://docs.python.org/3/library/re.html#regular-expression-syntax){target="_blank"} in `serialized_output` of the Step. |
| `output`            | Regular expression, for example: `^my_regex.*` | Match [regex](https://docs.python.org/3/library/re.html#regular-expression-syntax){target="_blank"} in `output` of the Step.            |
| `any`               | Value must be omitted                          | Run successor(s) in any case.                                                                                                           |

### Examples:
```yaml
next:
- type: result
  value: ok
  step: step-to-execute
```

```yaml
next:
- type: serialized_output
  value: 
    - admin
    - root
  step: step-to-execute
```

```yaml
next:
- type: any
  step: 
    - step-to-execute-1
    - step-to-execute-2
```

## Session management
One of the unique features of Cryton is the ability to create and use *sessions* - connections to the target systems. 
When you successfully exploit a running network service on your target machine (victim), you open a connection to it. 
In Cryton, this connection can be given a name and then used during the Plan execution in any Step (which is executed 
on the same Worker node and supports this functionality). Metasploit Framework session management is used for storing 
and interacting with sessions, and therefore must be available and running on the Worker node.

```yaml
- name: step1
  arguments:
    create_named_session: session_to_target_1
    ...
- name: step2
  arguments:
    use_named_session: session_to_target_1
    ...
```

In the example above, the step1 creates a named session *session_to_target_1* (in case it succeeds). 
Its Metasploit ID gets stored in the database and can be used anywhere in the Plan, not only in the following Step 
(as seen in the example). When the Plan creates multiple sessions to the same target, and the attacker does not care which 
he is using, the *use_any_session_to_target* parameter can be used.

```yaml
- name: step1
  arguments:
    use_any_session_to_target: 192.168.56.22
    ...
```

!!! warning "Session types"

    Metasploit Framework supports two types of sessions.
    
    The first is a shell session, you can run any shell commands you want.
    
    The second is called Meterpreter. It allows you to use it's provided commands, such as `ifconfig` or `sysinfo`. 
    To run a command in a shell, you need to use the `execute` command with the `-f`, `-i`, and `-a` options (`execute -f <command> -i -a <arguments>`).
    In some cases, the command execution can fail. Before creating a plan, make sure it works for your target system/exploit.

## Output sharing
Output sharing is used for sharing gained data (*serialized_output*) between multiple steps. To go through the data we use a modified 
version of a dot notation. 

For example, imagine the following dictionary (Python data structure)
```json
{"credentials": [{"username": "admin", "password": "securePassword"}]}
```
If we wanted to access it and get **password** for *admin* user using our version of dot notation, we would use 
`credentials[0].password` which would return *securePassword* string.

This brings in some limitations:

- keys are separated using `.` (More on how to choose a custom separator [here](#custom-separator).
- key can't be in format `[integer]` (regex representation: `^\[[0-9]+]$`) as it represents list (array) index
- list (array) index can be defined multiple times in the same key for example `myKey[1][1]` (it must be defined at its end)
(regex representation: `((\[[0-9]+])+$)`)

There are two techniques for sharing the outputs of modules between steps:

* **output_prefix**
* **output_mapping**

### Output prefix
By default, the prefix string is set to the name of the step. Using its name, any other step can query its output (serialized_output 
of its attack module execution) and use it in its arguments.

Alternatively, this prefix can be set to a custom string. This way, multiple equivalent steps can return the same prefixed 
variable value to be used by a dependent step.
For example:
```yaml
- name: bruteforce
  step_type: worker/execute
  is_init: true
  output_prefix: custom_prefix
  arguments:
    module: medusa
    # Should return username and password in a dictionary
    module_arguments:
      target: localhost
      # Default password list in medusa folder will be used for bruteforce
      credentials:
        username: admin
  next:
  - type: result
    value: ok
    step: ssh
- name: ssh
  step_type: worker/execute
  arguments:
    module: ssh
    module_arguments:
      username: $custom_prefix.username
      password: $custom_prefix.password
```
Also, there is a special prefix named **parent**, which simply takes the output from the parent step execution 
(which executed the current step).

```yaml
- name: stepA
  ...
  next:
  - type: ...
    value: ...
    step: stepB
- name: stepB
  ...
  arguments:
    module_name: module_a
    module_arguments:
      username: $parent.var
```
Output prefix **cannot be the name of other steps or the value "parent"**, otherwise, it can be 
any string **that doesn't contain "$" and "." signs**.

### Custom separator
If for some reason(for example when a key in the module's output is an IPv4 address) you don't want to use `.` as a separator in output-sharing variables, you can use the `settings` parameter in the Plan parameters with a `separator` key for defining custom separator.

Example of a custom separator used on **parent prefix** example above:
```yaml
plan:
  name: my-plan
  owner: my name
  settings:
    separator: "|"
  stages:
    - name: my-stage
      ...
      steps:
      - name: stepA
        ...
        next:
        - type: ...
          value: ...
          step: stepB
      - name: stepB
        ...
        arguments:
          module: module_a
          module_arguments:
            username: $parent|arg
```

### Output mapping
Sometimes you do not care from which module you receive information. Step A and Step B can both return a stolen authentication 
token. For this reason, you can use ```output_prefix```. 
But there is an obvious problem! What if both steps return this value under a different name, e.g. ```token``` and ```auth_token```? 
Prefix would not help you much in this situation. 
For this reason, there is a ```output_mapping``` mechanism. 
```yaml
- name: step_a
  # Returns 'token'
  output_prefix: steal
  output_mapping:
    - name_from: token
      name_to: stolen_token
  step_type: worker/execute
  arguments:
    module: module_a
    module_arguments:
      ...
- name: step_b
  # Returns 'auth_token'
  output_prefix: steal
  output_mapping:
    - name_from: auth_token
      name_to: stolen_token
  step_type: worker/execute
  arguments:
    module: module_b
    module_arguments:
      ...
- name: step_c
  step_type: worker/execute
  arguments:
    module: module_c
    module_arguments:
      token: $steal.stolen_token
```

## Execution variables
To assign different values for each Plan execution in Run, you can use execution variables.  
To define execution variables, use Jinja ([with some tweaks](#limitations)) instead of filling the arguments with 
real values while creating a Plan template.
For example:
```yaml
module_arguments:
  target: '{{ my_jinja_variable }}'
```

**IMPORTANT: Execution variables must be defined as a string using single quotes, otherwise they won't be matched.**

And before you execute Run (and its Plan execution(s)), upload your variable(s). (see [CLI](../interfaces/cli.md#execution-variables)) 

Example of a file with execution variables:
```yaml
variable: localhost
nested:
  variable: value
variable_list:
  - var1
  - var2
```

If a variable cannot be filled, the Step errors out.

### Limitations
* Execution variables must be defined as a string using single quotes.
    ```yaml
    foo: '{{ variable }}'
    ```
* In the case of Step type `worker/execute` you can use these variables only for the `module_arguments` parameter and its sub-parameters. 
For `empire/agent-deploy` or `empire/execute` you can use these variables for the root `arguments` parameter and its sub-parameters.
* Currently, there is support for simple and nested variables only. Examples:
    ```yaml
    foo: '{{ variable }}'
    foo: '{{ nested.variable }}'
    foo: '{{ variable[index] }}'
    foo: '{{ nested.variable[index] }}'
    ```
* If you want to use more Jinja goodies, use the raw block:
    ```yaml
    foo: {% raw %} '{{ variable + 14 }}' {% endraw %}
    ```

## Output serialization

[//]: # (TODO: move this to the design-phase/step.md?)
[//]: # (TODO: needs a bit more information, what is this for, how and where to use it, probably will be solved in the previously created ticket)

Automatic output serialization is an experimental feature.  
It allows you to take the output and use it in other modules in the form of a `serialized_output`. For this to work, the **command output must be a valid JSON** (`"some text"`, `{"a": "b"}`, `["a", "b"]`).

It is in an experimental state primarily due to the randomness of the MSF shells and Windows combination. If you encounter any errors, please submit an issue.

## Output replacing
In case you want to replace some parts of your output, you can define a dictionary of rules (regexes) and strings to replace the matches with.  
Keep in mind, that the rules are applied **in order**.

Here is an example of matching IPv4 and replacing it with `removed-ip`:
```yaml
- name: step
  ...
  output:
    replace:
      "^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$": removed-ip
```
