# mod_medusa

This module implements attacking capabilities of Medusa bruteforce tool.

## System requirements

System requirements (those not listed in requirements.txt for python).

For this module to function properly, [Medusa](https://www.kali.org/tools/medusa/) needs to be installed.

## Input parameters

Description of input parameters for module.

### Parameters with predefined inputs

| Parameter name | Required | Example value | Data type | Default value | Parameter description                                          |
|----------------|----------|---------------|-----------|---------------|----------------------------------------------------------------|
| `target`       | Yes      | 127.0.0.1     | string    | -             | Bruteforce target.                                             |
| `mod`          | No       | ftp           | string    | ssh           | Specified mod(service) you want to use to attack.              |
| `raw_output`   | No       | false         | bool      | true          | Flag whether you want to return raw output from Medusa.        |
| `credentials`  | No       | false         | dict      | -             | Parameters that can be used under this key are in table below. |
| `tasks`        | No       | false         | int       | 4             | Total number of login pairs to be tested concurrently.         |


Parameters that can be used under `credentials`.

| Parameter name  | Parameter description                                                                                                                                                                                            |
|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `username`      | Username to use for bruteforce                                                                                                                                                                                   |
| `password`      | Password to use for bruteforce                                                                                                                                                                                   |
| `username_file` | Absolute path to file with usernames (default is username wordlist in mod folder)                                                                                                                                |
| `password_file` | Absolute path to file with passwords (default is password wordlist in mod folder)                                                                                                                                |
| `combo_file`    | Absolute path to file with login pairs - user:password (official format can be found in http://foofus.net/goons/jmk/medusa/medusa.html). **Cannot be combined with other input parameters under `credentials`!** |

### Parameters with custom Medusa command

| Parameter name | Parameter description                                                                               |
|----------------|-----------------------------------------------------------------------------------------------------|
| `command`      | Medusa command with syntax as in command line. **Cannot be combined with other input parameters!**  |

## Example yaml(s)

### Example with predefined inputs
```yaml
module_arguments:
  target: CHANGE ME
  raw_output: true
  credentials:
    username: vagrant
    password: vagrant
  tasks: 4
```

```yaml
module_arguments:
  target: CHANGE ME
  credentials:
    combo_file: /absolute/path/to/file
  tasks: 4
```

### Example with custom command
```yaml
module_arguments:
  command: medusa -t 4 -u vagrant -p vagrant -h <target> -M ssh
```

## Output

Description of module output.

| Parameter name      | Parameter description                                                         |
|---------------------|-------------------------------------------------------------------------------|
| `return_code`       | 0 - success<br />-1 - fail                                                    |
| `output`            | Raw output from Medusa or any errors that can occur during module execution.  |
| `serialized_output` | Serialized Medusa output to JSON that can accessed in other modules as input. |

### serialized_output

Description of `serialized_output` output parameter

| Parameter name    | Parameter description                                                    |
|-------------------|--------------------------------------------------------------------------|
| `username`        | First username found during bruteforce.                                  |
| `password`        | First password found during bruteforce.                                  |
| `all_credentials` | List of dictionaries containing all the credentials found in bruteforce. |

### Example

```json lines
{
  'return_code': 0, 
  'output': 'Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>\n\nACCOUNT CHECK: [ssh] Host: 192.168.56.3 (1 of 1, 0 complete) User: vagrant (1 of 1, 0 complete) Password: vagrant (1 of 1 complete)\nACCOUNT FOUND: [ssh] Host: 192.168.56.3 User: vagrant Password: vagrant [SUCCESS]\n', 
  'serialized_output': {'username': 'vagrant', 'password': 'vagrant', 'all_credentials': [{'username': 'vagrant', 'password': 'vagrant'}]}
}
```