# mod_script

Module for running custom scripts.

## System requirements

There are no system requirements.

## Input parameters

Description of input parameters for module.

| Parameter name      | Required | Example value  | Data type | Default value | Parameter description                                                                                                                                                                                                             |
|---------------------|----------|----------------|-----------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `script_path`       | Yes      | /tmp/script.py | string    | -             | Full path to the script.                                                                                                                                                                                                          |
| `script_arguments`  | No       | -arg1 example  | string    | -             | Optional arguments for script.                                                                                                                                                                                                    |
| `executable`        | Yes      | python3        | string    | -             | What should be used to execute the script                                                                                                                                                                                         |
| `serialized_output` | No       | true           | string    | false         | **!Experimental feature!** If set to `true` the module tries to parse the output of the script into `serialized_output`. For this to work, the **script output must be a valid JSON** (`"some text"`, `{"a": "b"}`, `["a", "b"]`) |
| `timeout`           | No       | 60             | int       | -             | For how long - in seconds - the script should run (overrides args), if not set, module waits until the script finishes.                                                                                                           |

### Example yaml(s)

```yaml
module_arguments:
  script_path: /tmp/example.py
  script_arguments: -t 10.10.10.5
  executable: python3
  timeout: 30
```

## Output

Description of output.

| Parameter name      | Parameter description                                                           |
|---------------------|---------------------------------------------------------------------------------|
| `return_code`       | 0 - success<br />-1 - fail                                                      |
| `output`            | Raw output from the script or any errors that can occur during module execution |
| `serialized_output` | Serialized script output in JSON that can accessed in other modules as input    |

### Example

```json
{
  "serialized_output": {},
  "output": "script output",
  "return_code": 0
}
```