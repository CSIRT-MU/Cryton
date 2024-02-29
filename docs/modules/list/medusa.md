
## Description
This module implements attacking capabilities of the [Medusa](https://github.com/jmk-foofus/medusa) bruteforce tool.

## Prerequisites
[Medusa](https://www.kali.org/tools/medusa/) must be installed.

## Input parameters

=== "Simple"

    ### `target`
    Bruteforce target.
    
    | Name     | Type   | Required | Default value | Example value |
    |----------|--------|----------|---------------|---------------|
    | `target` | string | &check;  |               | `127.0.0.1`   |
    
    ### `mod`
    mod (service) to attack.
    
    | Name  | Type   | Required | Default value | Example value |
    |-------|--------|----------|---------------|---------------|
    | `mod` | string | &cross;  | `ssh`         | `ftp`         |
    
    ### `tasks`
    Number of login pairs tested concurrently.
    
    | Name    | Type    | Required | Default value | Example value |
    |---------|---------|----------|---------------|---------------|
    | `tasks` | integer | &cross;  | `4`           | `8`           |
    
    ### `options`
    Additional Medusa parameters.
    
    | Name      | Type   | Required | Default value | Example value |
    |-----------|--------|----------|---------------|---------------|
    | `options` | string | &cross;  |               | `-t 3`        |
    
    ### `credentials`
    Group for credentials input.
    
    | Name          | Type   | Required | Default value | Example value                     |
    |---------------|--------|----------|---------------|-----------------------------------|
    | `credentials` | object | &check;  |               | `{"combo_file": "/path/to/file"}` |
    
    Specify either `combo_file` or one of each username (`username`/`username_file`) and password (`password`/`password_file`) parameters:
    
    #### `username`
    Username to bruteforce.
    
    | Name       | Type   | Required | Default value | Example value |
    |------------|--------|----------|---------------|---------------|
    | `username` | string | &cross;  |               | `username`    |
    
    #### `username_file`
    Absolute path to file with usernames to bruteforce.
    
    | Name            | Type   | Required | Default value | Example value   |
    |-----------------|--------|----------|---------------|-----------------|
    | `username_file` | string | &cross;  |               | `/path/to/file` |
    
    #### `password`
    Password to bruteforce.
    
    | Name       | Type   | Required | Default value | Example value |
    |------------|--------|----------|---------------|---------------|
    | `password` | string | &cross;  |               | `password`    |
    
    #### `password_file`
    Absolute path to file with passwords to bruteforce.
    
    | Name            | Type   | Required | Default value | Example value   |
    |-----------------|--------|----------|---------------|-----------------|
    | `password_file` | string | &cross;  |               | `/path/to/file` |
    
    #### `combo_file`
    Absolute path to file with login pairs to bruteforce. The file should be in format `username:password`. More information can be found [here](http://foofus.net/goons/jmk/medusa/medusa.html).
    
    | Name         | Type   | Required | Default value | Example value   |
    |--------------|--------|----------|---------------|-----------------|
    | `combo_file` | string | &cross;  |               | `/path/to/file` |

=== "Custom"

    ### `command`
    Medusa command to run with syntax as in command line (with executable).
    
    | Name      | Type   | Required | Default value | Example value                               |
    |-----------|--------|----------|---------------|---------------------------------------------|
    | `command` | string | &check;  |               | `medusa -u user -p pass -h <target> -M ssh` |

## Examples

### SSH bruteforce
Input:
```yaml
module_arguments:
  target: CHANGE_ME
  raw_output: true
  credentials:
    username: vagrant
    password: vagrant
  tasks: 4
```

Output:
```json
{
  "result": "ok", 
  "output": "Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>\n\nACCOUNT CHECK: [ssh] Host: 192.168.56.3 (1 of 1, 0 complete) User: vagrant (1 of 1, 0 complete) Password: vagrant (1 of 1 complete)\nACCOUNT FOUND: [ssh] Host: 192.168.56.3 User: vagrant Password: vagrant [SUCCESS]\n", 
  "serialized_output": {"username": "vagrant", "password": "vagrant", "all_credentials": [{"username": "vagrant", "password": "vagrant"}]}
}
```

### Custom command
Input:
```yaml
module_arguments:
  command: medusa -t 4 -u vagrant -p vagrant -h <target> -M ssh
```

Output:
```json
{
  "result": "ok", 
  "output": "Medusa v2.2 [http://www.foofus.net] (C) JoMo-Kun / Foofus Networks <jmk@foofus.net>\n\nACCOUNT CHECK: [ssh] Host: 192.168.56.3 (1 of 1, 0 complete) User: vagrant (1 of 1, 0 complete) Password: vagrant (1 of 1 complete)\nACCOUNT FOUND: [ssh] Host: 192.168.56.3 User: vagrant Password: vagrant [SUCCESS]\n", 
  "serialized_output": {"username": "vagrant", "password": "vagrant", "all_credentials": [{"username": "vagrant", "password": "vagrant"}]}
}
```

## Troubleshooting
So far so good.

## Output serialization
Only the credentials are serialized. They're parsed from the output.

`serialized_output` contains:

| Parameter name    | Parameter description                                                    |
|-------------------|--------------------------------------------------------------------------|
| `username`        | First username found during bruteforce.                                  |
| `password`        | First password found during bruteforce.                                  |
| `all_credentials` | List of dictionaries containing all the credentials found in bruteforce. |
