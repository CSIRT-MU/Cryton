# mod_cmd

Module for running shell commands (depending on the shell used). When specifying "use_session" or "use_named_session", the command will be executed in the respective sessions context.

## System requirements

There are no system requirements.

### For use with sessions only

For this module to function properly, [Metasploit-framework](https://github.com/rapid7/metasploit-framework/wiki/Nightly-Installers) needs to be installed.

After a successful installation of Metasploit-framework, you need to load msgrpc plugin. Easiest way to do this to open your terminal and run `msfrpcd` with `-P toor` to use password and `-S` to turn off SSL (depending on configuration in Worker config file). 

**Optional:**

Another option is to run Metasploit using `msfconsole` and load msgrpc plugin using this command:

````bash
load msgrpc ServerHost=127.0.0.1 ServerPort=55553 User=msf Pass='toor' SSL=true
````

This is just default, feel free to change the parameters to suit your needs, but keep in mind that they must match your worker config file.

After successfully loading the msgrpc plugin, you are all set and ready to use this module.


## Input parameters

Description of input parameters for module.

| Parameter name           | Required | Example value   | Data type | Default value | Parameter description                                                                                                                                                                                                                                                    |
|--------------------------|----------|-----------------|-----------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cmd`                    | Yes      | cat /etc/passwd | string    | -             | The command for execution.                                                                                                                                                                                                                                               |
| `end_checks`             | No       | \[root, admin\] | list      | -             | List of strings that are checked regularly to determine whether the command execution finished. It can also be used, for example, to make sure that the script has run completely, if you put a string at the end of it, which you will then check using this parameter. |
| `session_id`             | No       | 1               | int       | -             | Msf session in which the command should be executed.                                                                                                                                                                                                                     |
| `timeout`                | No       | 60              | int       | -             | Timeout for the command **in seconds**.                                                                                                                                                                                                                                  |
| `minimal_execution_time` | No       | 5               | int       | -             | Time (**in seconds**) to wait for the output before reading from the shell.                                                                                                                                                                                              |
| `serialized_output`      | No       | true            | string    | false         | **!Experimental feature!** If set to `true` the module tries to parse the output of the command into `serialized_output`. **More information [here](#output-serialization).**                                                                                            |

**NOTICE: To utilize existing sessions check out the [session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-documentation/latest/designing-phase/step/#session-management) feature.**

### Example yaml(s)

```yaml
module_arguments:
  cmd: cat /etc/passwd; echo end_check_string
  end_checks: 
  - end_check_string
  session_id: 1
```

## Output

Description of module output.

| Parameter name      | Parameter description                                                            |
|---------------------|----------------------------------------------------------------------------------|
| `return_code`       | 0 - success<br />-1 - fail                                                       |
| `output`            | Raw output from the command or any errors that can occur during module execution |
| `serialized_output` | Serialized script output in JSON that can accessed in other modules as input     |

### Example

```json
{
  "return_code": 0, 
  "output": "contents of passwd file on target",
  "serialized_output": {}
}
```

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
