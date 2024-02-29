
## Description
A module for web fuzzing using the [FFUF](https://github.com/ffuf/ffuf) tool.

This module runs FFUF on given target and returns a file with found directories.


## Prerequisites
[FFUF](https://github.com/ffuf/ffuf) must be installed.

## Input parameters

=== "Simple"

    ### `target`
    Scan target.
    
    | Name     | Type   | Required | Default value | Example value                |
    |----------|--------|----------|---------------|------------------------------|
    | `target` | string | &check;  |               | `http://127.0.0.1:8000/FUZZ` |
    
    ### `wordlist`
    The wordlist for fuzzing the webserver.
    
    | Name       | Type   | Required | Default value | Example value                         |
    |------------|--------|----------|---------------|---------------------------------------|
    | `wordlist` | string | &check;  |               | `/usr/share/wordlists/dirb/small.txt` |
    
    ### `options`
    Additional FFUF parameters.
    
    | Name      | Type   | Required | Default value | Example value |
    |-----------|--------|----------|---------------|---------------|
    | `options` | string | &cross;  |               | `-X POST`     |
    
    ### `serialize_output`
    Use FFUF's serialization (`-of json -o file`).
    
    | Name               | Type    | Required | Default value | Example value |
    |--------------------|---------|----------|---------------|---------------|
    | `serialize_output` | boolean | &cross;  | `true`        | `false`       |

=== "Custom"

    ### `command`
    FFUF command to run with syntax as in command line (with executable).
    
    | Name      | Type   | Required | Default value | Example value                   |
    |-----------|--------|----------|---------------|---------------------------------|
    | `command` | string | &check;  |               | `ffuf -u http://CHANGE_ME/FUZZ` |

## Examples

[//]: # (TODO: update the examples)

### Example with serialized output
Input:
```yaml
module_arguments:
  target: CHANGE_ME
  wordlist: "/usr/share/wordlists/dirb/small.txt"
  options: -X POST
  
```

Output:
```json
{"time":"2023-05-16T12:04:36+02:00","config":{"sni":"","url":"http://172.16.169.128/FUZZ","json":false,"rate":0,"delay":{"value":"0.00"},"fmode":"or","http2":false,"mmode":"or","quiet":false,"colors":false,"method":"POST","cmdline":"ffuf -w /usr/share/wordlists/dirb/small.txt -u http://172.16.169.128/FUZZ -of json -o /tmp/cryton-ffuf-1684231474.215272.tmp -X POST","headers":{},"maxtime":0,"threads":40,"timeout":10,"verbose":false,"debuglog":"","matchers":{"Mutex":{},"Filters":{},"Matchers":{"status":{"value":"200,204,301,302,307,401,403,405,500"}},"IsCalibrated":false,"PerDomainFilters":{}},"postdata":"","proxyurl":"","scrapers":"all","stop_403":false,"stop_all":false,"inputmode":"clusterbomb","recursion":false,"wordlists":["/usr/share/wordlists/dirb/small.txt"],"configfile":"","extensions":[],"ignorebody":false,"inputshell":"","outputfile":"/tmp/cryton-ffuf-1684231474.215272.tmp","maxtime_job":0,"requestfile":"","scraperfile":"","stop_errors":false,"cmd_inputnum":100,"outputformat":"json","requestproto":"https","inputproviders":[{"name":"wordlist","value":"/usr/share/wordlists/dirb/small.txt","keyword":"FUZZ","template":""}],"noninteractive":false,"replayproxyurl":"","autocalibration":false,"outputdirectory":"","recursion_depth":0,"follow_redirects":false,"recursion_strategy":"default","OutputSkipEmptyFile":false,"autocalibration_keyword":"FUZZ","autocalibration_perhost":false,"autocalibration_strings":[],"dirsearch_compatibility":false,"autocalibration_strategy":"basic","ignore_wordlist_comments":false},"results":[],"commandline":"ffuf -w /usr/share/wordlists/dirb/small.txt -u http://172.16.169.128/FUZZ -of json -o /tmp/cryton-ffuf-1684231474.215272.tmp -X POST"}
```

### Example with text output
Input:
```yaml
module_arguments:
  target: CHANGE_ME
  options: --max-threads 7
  serialize_output: False
```

Output:
```text
/'___\ /'___\ /'___\ /\ \__/ /\ \__/ __ __ /\ \__/ \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\ \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/ \ \_\ \ \_\ \ \____/ \ \_\ \/_/ \/_/ \/___/ \/_/ v2.0.0-dev ________________________________________________ :: Method : POST :: URL : http://172.16.169.128/FUZZ :: Wordlist : FUZZ: /usr/share/wordlists/dirb/small.txt :: Output file : /tmp/cryton-ffuf-1684231474.215272.tmp :: File format : json :: Follow redirects : false :: Calibration : false :: Timeout : 10 :: Threads : 40 :: Matcher : Response status: 200,204,301,302,307,401,403,405,500 ________________________________________________ [2K:: Progress: [40/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [492/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [959/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [959/959] :: Job [1/1] :: 121 req/sec :: Duration: [0:00:01] :: Errors: 0 ::
```

## Troubleshooting
So far so good.

## Output serialization
Output is serialized by FFUF itself.
