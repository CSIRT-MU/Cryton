
## Description
A module for executing scripts (Python, sh, bash, ...).

## Prerequisites
There are no specific prerequisites.

## Input parameters

### `script_path`
Full path to the script.

| Name          | Type   | Required | Default value | Example value    |
|---------------|--------|----------|---------------|------------------|
| `script_path` | string | &check;  |               | `/tmp/script.py` |

### `script_arguments`
Optional arguments for the script.

| Name               | Type   | Required | Default value | Example value   |
|--------------------|--------|----------|---------------|-----------------|
| `script_arguments` | string | &cross;  |               | `-arg1 example` |

### `executable`
What should be used to execute the script.

| Name         | Type   | Required | Default value | Example value      |
|--------------|--------|----------|---------------|--------------------|
| `executable` | string | &check;  |               | `/usr/bin/python3` |

### `serialize_output`
Try to parse the output of the script into `serialized_output`.

| Name               | Type    | Required | Default value | Example value |
|--------------------|---------|----------|---------------|---------------|
| `serialize_output` | boolean | &cross;  | `false`       | `true`        |

### `timeout`
Timeout for the command (**in seconds**).

| Name      | Type    | Required | Default value | Example value |
|-----------|---------|----------|---------------|---------------|
| `timeout` | integer | &cross;  | `60`          | `30`          |

## Examples

### Run Python script
Input:
```yaml
module_arguments:
  script_path: /tmp/example.py
  script_arguments: -t 10.10.10.5
  executable: python3
  timeout: 30
```

Output:
```json
{
  "serialized_output": {},
  "output": "script output",
  "result": "ok"
}
```

## Troubleshooting
So far so good.

## Output serialization
Automatic output serialization is an experimental feature.  
It allows you to take the output and use it in other modules in the form of a `serialized_output`. For this to work, the **command output must be a valid JSON** (`"some text"`, `{"a": "b"}`, `["a", "b"]`).
