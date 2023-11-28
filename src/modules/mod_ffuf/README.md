# mod_ffuf

This module runs ffuf on given target and returns a file with found directories.

## System requirements

For this module to function properly, [ffuf](https://github.com/ffuf/ffuf) needs to be installed.

## Input parameters

Description of input parameters for module.

### Parameters with predefined inputs

| Parameter name      | Required | Example value                   | Data type | Default value | Parameter description |
|---------------------|----------|---------------------------------|-----------|---------------|---------------------------|
| `target`            | Yes      | http://127.0.0.1:8000/FUZZ      | string    | -             | Scan target.                                                                                                                                                                       |
| `wordlist`          | Yes      | /usr/share/wordlists/dirb/small.txt | string| -             | The wordlist for fuzzing the webserver                                                                                                                                         |
| `options`           | No       | -X POST                         | string    | -             | Additional ffuf parameters.                                                                                                                                                      |
| `serialized_output` | No       | False                           | bool      | True          | Flag for returning json serialized result in `serialized_output`, so that it could be used as input in other modules. **NOTICE: uses `-of json -o tmp_file-{timestamp}` as a parameter in ffuf command.** |





## Output parameters

Description of module output.

| Parameter name      | Parameter description                                                         |
|---------------------|-------------------------------------------------------------------------------|
| `return_code`       | 0 - success<br />-1 - fail                                                    |
| `output`            | Raw output of ffuf or any errors that can occur during module execution.      |
| `serialized_output` | Serialized ffuf output in JSON that can accessed in other modules as input. |


## Example yaml(s) with module results

### Example with serialized output
```yaml
module_arguments:
  target: CHANGE_ME
  wordlist: "/usr/share/wordlists/dirb/small.txt"
  options: -X POST
  
```

```json lines
{"time":"2023-05-16T12:04:36+02:00","config":{"sni":"","url":"http://172.16.169.128/FUZZ","json":false,"rate":0,"delay":{"value":"0.00"},"fmode":"or","http2":false,"mmode":"or","quiet":false,"colors":false,"method":"POST","cmdline":"ffuf -w /usr/share/wordlists/dirb/small.txt -u http://172.16.169.128/FUZZ -of json -o /tmp/cryton-ffuf-1684231474.215272.tmp -X POST","headers":{},"maxtime":0,"threads":40,"timeout":10,"verbose":false,"debuglog":"","matchers":{"Mutex":{},"Filters":{},"Matchers":{"status":{"value":"200,204,301,302,307,401,403,405,500"}},"IsCalibrated":false,"PerDomainFilters":{}},"postdata":"","proxyurl":"","scrapers":"all","stop_403":false,"stop_all":false,"inputmode":"clusterbomb","recursion":false,"wordlists":["/usr/share/wordlists/dirb/small.txt"],"configfile":"","extensions":[],"ignorebody":false,"inputshell":"","outputfile":"/tmp/cryton-ffuf-1684231474.215272.tmp","maxtime_job":0,"requestfile":"","scraperfile":"","stop_errors":false,"cmd_inputnum":100,"outputformat":"json","requestproto":"https","inputproviders":[{"name":"wordlist","value":"/usr/share/wordlists/dirb/small.txt","keyword":"FUZZ","template":""}],"noninteractive":false,"replayproxyurl":"","autocalibration":false,"outputdirectory":"","recursion_depth":0,"follow_redirects":false,"recursion_strategy":"default","OutputSkipEmptyFile":false,"autocalibration_keyword":"FUZZ","autocalibration_perhost":false,"autocalibration_strings":[],"dirsearch_compatibility":false,"autocalibration_strategy":"basic","ignore_wordlist_comments":false},"results":[],"commandline":"ffuf -w /usr/share/wordlists/dirb/small.txt -u http://172.16.169.128/FUZZ -of json -o /tmp/cryton-ffuf-1684231474.215272.tmp -X POST"}
```

### Example with text output
```yaml
module_arguments:
  target: CHANGE_ME
  options: --max-threads 7
  serialized_output: False
```

```
/'___\ /'___\ /'___\ /\ \__/ /\ \__/ __ __ /\ \__/ \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\ \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/ \ \_\ \ \_\ \ \____/ \ \_\ \/_/ \/_/ \/___/ \/_/ v2.0.0-dev ________________________________________________ :: Method : POST :: URL : http://172.16.169.128/FUZZ :: Wordlist : FUZZ: /usr/share/wordlists/dirb/small.txt :: Output file : /tmp/cryton-ffuf-1684231474.215272.tmp :: File format : json :: Follow redirects : false :: Calibration : false :: Timeout : 10 :: Threads : 40 :: Matcher : Response status: 200,204,301,302,307,401,403,405,500 ________________________________________________ [2K:: Progress: [40/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [492/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [959/959] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 :: [2K:: Progress: [959/959] :: Job [1/1] :: 121 req/sec :: Duration: [0:00:01] :: Errors: 0 ::
```
