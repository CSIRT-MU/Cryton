
## Description
A module that allows local and remote command execution.

The module is used to run a single shell command.  By default, the command is executed locally. If you specify a [session](../../design-phase/step.md#session-management), it will be executed in the respective session's context.

## Prerequisites
In case you want to execute code remotely, Metasploit must be accessible from Worker it will be executed on.

## Input parameters

[//]: # (TODO: instead of passing session_id, pass session? All of its parameters &#40;shell, meterpreter, other&#40;using paramiko&#41;&#41; or gather that from metasploit? Might be better to get information from MSF)

### `command`
Command to execute.

| Name      | Type   | Required | Default value | Example value |
|-----------|--------|----------|---------------|---------------|
| `command` | string | &check;  |               | `whoami`      |

### `end_checks`
Strings to check in the command output to determine whether the execution has finished.

| Name         | Type            | Required | Default value | Example value   |
|--------------|-----------------|----------|---------------|-----------------|
| `end_checks` | array\[string\] | &cross;  |               | `[root, admin]` |

### `timeout`
Timeout for the command (**in seconds**).

| Name      | Type    | Required | Default value | Example value |
|-----------|---------|----------|---------------|---------------|
| `timeout` | integer | &cross;  |               | `60`          |

### `minimal_execution_time`
Time (**in seconds**) to wait for the output before reading from the shell.

| Name                     | Type    | Required | Default value | Example value |
|--------------------------|---------|----------|---------------|---------------|
| `minimal_execution_time` | integer | &cross;  |               | `5`           |

### `session_id`
Metasploit sessions to use.

| Name         | Type    | Required | Default value | Example value |
|--------------|---------|----------|---------------|---------------|
| `session_id` | integer | &cross;  |               | `1`           |

### `serialize_output`
Try to parse the output of the command into `serialized_output`.

| Name               | Type    | Required | Default value | Example value |
|--------------------|---------|----------|---------------|---------------|
| `serialize_output` | boolean | &cross;  | `false`       | `true`        |

## Examples

### Read file on remote system using session

Input:
```yaml
module_arguments:
  cmd: cat /etc/passwd; echo end_flag716282
  end_checks: 
  - end_flag716282
  session_id: 1
```

Output:
```json
{
  "result": "ok",
  "output": "<contents of passwd file on target> end_flag716282",
  "serialized_output": {}
}
```

## Troubleshooting
Known issues, limitations, tips, and workarounds.

## Output serialization
Automatic output serialization is an experimental feature.  
It allows you to take the output and use it in other modules in the form of a `serialized_output`. For this to work, the **command output must be a valid JSON** (`"some text"`, `{"a": "b"}`, `["a", "b"]`).

It is in an experimental state primarily due to the randomness of the MSF shells and Windows combination. If you encounter any errors, please submit an issue.

### Examples
*whoami* on Linux (Debian): `echo \"$(whoami)\"`
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
