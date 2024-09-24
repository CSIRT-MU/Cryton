
## Description
A module that allows local and remote command execution.

The module is used to run a single shell command.  By default, the command is executed locally. If you specify a session, it will be executed in the respective session's context.

## Prerequisites
In case you want to execute code remotely, Metasploit must be accessible from Worker it will be executed on.

## Input parameters

### `command`
Command to execute.

| Name      | Type   | Required | Default value | Example value |
|-----------|--------|----------|---------------|---------------|
| `command` | string | &check;  |               | `whoami`      |

### `timeout`
Timeout for the command (**in seconds**).

| Name      | Type    | Required | Default value | Example value |
|-----------|---------|----------|---------------|---------------|
| `timeout` | integer | &cross;  |               | `60`          |

### `session_id`
Metasploit session to use.

| Name         | Type    | Required | Default value | Example value |
|--------------|---------|----------|---------------|---------------|
| `session_id` | integer | &cross;  |               | `1`           |

### `serialize_output`
Try to parse the output of the command into `serialized_output`.

| Name               | Type    | Required | Default value | Example value |
|--------------------|---------|----------|---------------|---------------|
| `serialize_output` | boolean | &cross;  | `false`       | `true`        |

### `force_shell`
Run the command in shell even in a Meterpreter session. To run the command in the Meterpreter shell, set this to `false`.

| Name          | Type    | Required | Default value | Example value |
|---------------|---------|----------|---------------|---------------|
| `force_shell` | boolean | &cross;  | `true`        | `false`       |

## Examples

### Read file on remote system using session

Input:
```yaml
my-step:
  module: command
  arguments:
    command: cat /etc/passwd
    session_id: 1

```

Output:
```json
{
  "result": "ok",
  "output": "<contents of passwd file on target>",
  "serialized_output": {}
}
```

## Troubleshooting
So far so good.

## Output serialization
Automatic output serialization is an experimental feature.  
It allows you to take the output and use it in other modules in the form of a `serialized_output`. For this to work, the **command output must be a valid JSON** (`"some text"`, `{"a": "b"}`, `["a", "b"]`).

It is in an experimental state primarily due to the randomness of the MSF shells and Windows combination. If you encounter any errors, please submit an issue.

### Examples
*whoami* on Linux (Debian): `echo \\"$(whoami)\\"`
```json
{
  "output": "\"username\"",
  "serialized_output": {"auto_serialized": "username"}
}
```

*whoami* on Windows 10: `Powershell -C "whoami | ConvertTo-Json"`
```json
{
  "output": "\"username\"",
  "serialized_output": {"auto_serialized": "username"}
}
```
