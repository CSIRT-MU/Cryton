# mod_nmap

This module implements scanning capabilities of Nmap.

It is scanning target's ports. By default, it scans the most common ports and returns a list with all ports and their parameters.

## System requirements

For this module to function properly, [Nmap](https://www.kali.org/tools/nmap/) needs to be installed.

## Input parameters

Description of input parameters for module.

### Parameters with predefined inputs

| Parameter name    | Required | Example value                                            | Data type | Default value                                | Parameter description                                                                                                                                        |
|-------------------|----------|----------------------------------------------------------|-----------|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `target`          | Yes      | 127.0.0.1                                                | string    | -                                            | Scan target.                                                                                                                                                 |
| `ports`           | No       | [1-300, 443]                                             | array     | scans top 100 common ports (--top-ports 100) | List of individual ports or range of ports to be scanned.                                                                                                    |
| `port_parameters` | No       | all the possible parameters are [here](#port-parameters) | dict      | -                                            | Check if found ports match your desired parameters. If the port with desired parameters is not found, the module will result in failure (`return_code: -1`). |
| `options`         | No       | -T4 -sV                                                  | string    | -                                            | Additional Nmap parameters.                                                                                                                                  |
| `raw_output`      | No       | false                                                    | bool      | true                                         | Flag whether you want to return raw output from Nmap scan.                                                                                                   |    
| `timeout`         | No       | 30                                                       | int       | 60                                           | Timeout for nmap scan                                                                                                                                        |    


### Parameters with custom nmap command

| Parameter name      | Required | Example value                                            | Data type | Default value | Parameter description                                                                                                                                        |
|---------------------|----------|----------------------------------------------------------|-----------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `command`           | Yes      | nmap -T4 127.0.0.1                                       | string    | -             | Custom nmap command like in command line.                                                                                                                    |
| `serialized_output` | No       | false                                                    | bool      | true          | Option to serialize raw output to JSON, this option will add `-oX -` parameter to the command(if not already there) for xml output needed for serialization. |
| `port_parameters`   | No       | all the possible parameters are [here](#port-parameters) | dict      | -             | Check if found ports match your desired parameters. If the port with desired parameters is not found, the module will result in failure (`return_code: -1`). |
| `raw_output`        | No       | false                                                    | bool      | true          | Flag whether you want to return raw output from Nmap scan.                                                                                                   |    
| `timeout`           | No       | 30                                                       | int       | 60            | Timeout for nmap scan                                                                                                                                        |    


### Port parameters
Example of all possible options for `port_parameters`.
```yaml
---
protocol: tcp
portid: '22'
state: open
reason: syn-ack
reason_ttl: '0'
service:
  name: ssh
  product: OpenSSH
  version: 6.6.1p1 Ubuntu 2ubuntu2.13
  extrainfo: Ubuntu Linux; protocol 2.0
  ostype: Linux
  method: probed
  conf: '10'
cpe:
- cpe:/a:openbsd:openssh:6.6.1p1
- cpe:/o:linux:linux_kernel
scripts: []
```
All options try to find string in the nmap serialized output, and they are non-case sensitive. For example if the `cpe` in the nmap output would be cpe:/o:linux:linux_kernel, `cpe: -linux` in `port_parameters` would match it successfully.

## Output parameters

Description of module output.

| Parameter name      | Parameter description                                                         |
|---------------------|-------------------------------------------------------------------------------|
| `return_code`       | 0 - success<br />-1 - fail                                                    |
| `output`            | Raw output of Nmap scan or any errors that can occur during module execution. |
| `serialized_output` | Serialized Nmap output in JSON that can accessed in other modules as input.   |

## Example yaml(s) with module results

### Example with predefined inputs
```yaml
module_arguments:
  target: CHANGE ME
  ports:
    - 1-30
    - 80
  port_parameters:
    - protocol: tcp
      portid: '80'
      state: open
      reason: syn-ack
      reason_ttl: '0'
      service:
        name: http
        product: Apache httpd
        version: 2.4.7
        method: probed
        conf: '10'
      cpe: 
        - apache
  options: -T4 -sV
```

```json lines
{
  'return_code': 0, 
  'serialized_output': {'192.168.56.3': {'osmatch': {}, 'ports': [{'protocol': 'tcp', 'portid': '21', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'ftp', 'product': 'ProFTPD', 'version': '1.3.5', 'ostype': 'Unix', 'method': 'probed', 'conf': '10'}, 'cpe': [{'cpe': 'cpe:/a:proftpd:proftpd:1.3.5'}], 'scripts': []}, {'protocol': 'tcp', 'portid': '22', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'ssh', 'product': 'OpenSSH', 'version': '6.6.1p1 Ubuntu 2ubuntu2.13', 'extrainfo': 'Ubuntu Linux; protocol 2.0', 'ostype': 'Linux', 'method': 'probed', 'conf': '10'}, 'cpe': [{'cpe': 'cpe:/a:openbsd:openssh:6.6.1p1'}, {'cpe': 'cpe:/o:linux:linux_kernel'}], 'scripts': []}, {'protocol': 'tcp', 'portid': '80', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'http', 'product': 'Apache httpd', 'version': '2.4.7', 'hostname': '127.0.2.1', 'method': 'probed', 'conf': '10'}, 'cpe': [{'cpe': 'cpe:/a:apache:http_server:2.4.7'}], 'scripts': []}], 'hostname': [], 'macaddress': None, 'state': {'state': 'up', 'reason': 'syn-ack', 'reason_ttl': '0'}}, 'stats': {'scanner': 'nmap', 'args': '/usr/bin/nmap -oX - -T4 -sV -p-29,80 192.168.56.3', 'start': '1660830754', 'startstr': 'Thu Aug 18 15:52:34 2022', 'version': '7.92', 'xmloutputversion': '1.05'}, 'runtime': {'time': '1660830775', 'timestr': 'Thu Aug 18 15:52:55 2022', 'summary': 'Nmap done at Thu Aug 18 15:52:55 2022; 1 IP address (1 host up) scanned in 21.05 seconds', 'elapsed': '21.05', 'exit': 'success'}}, 
  'output': '<nmaprun scanner="nmap" args="/usr/bin/nmap -oX - -T4 -sV -p-29,80 192.168.56.3" start="1660830754" startstr="Thu Aug 18 15:52:34 2022" version="7.92" xmloutputversion="1.05">\n<scaninfo type="connect" protocol="tcp" numservices="30" services="1-29,80" />\n<verbose level="0" />\n<debugging level="0" />\n<hosthint><status state="up" reason="unknown-response" reason_ttl="0" />\n<address addr="192.168.56.3" addrtype="ipv4" />\n<hostnames>\n</hostnames>\n</hosthint>\n<host starttime="1660830767" endtime="1660830775"><status state="up" reason="syn-ack" reason_ttl="0" />\n<address addr="192.168.56.3" addrtype="ipv4" />\n<hostnames>\n</hostnames>\n<ports><extraports state="filtered" count="27">\n<extrareasons reason="no-response" count="27" proto="tcp" ports="1-20,23-29" />\n</extraports>\n<port protocol="tcp" portid="21"><state state="open" reason="syn-ack" reason_ttl="0" /><service name="ftp" product="ProFTPD" version="1.3.5" ostype="Unix" method="probed" conf="10"><cpe>cpe:/a:proftpd:proftpd:1.3.5</cpe></service></port>\n<port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="0" /><service name="ssh" product="OpenSSH" version="6.6.1p1 Ubuntu 2ubuntu2.13" extrainfo="Ubuntu Linux; protocol 2.0" ostype="Linux" method="probed" conf="10"><cpe>cpe:/a:openbsd:openssh:6.6.1p1</cpe><cpe>cpe:/o:linux:linux_kernel</cpe></service></port>\n<port protocol="tcp" portid="80"><state state="open" reason="syn-ack" reason_ttl="0" /><service name="http" product="Apache httpd" version="2.4.7" hostname="127.0.2.1" method="probed" conf="10"><cpe>cpe:/a:apache:http_server:2.4.7</cpe></service></port>\n</ports>\n<times srtt="464" rttvar="1667" to="100000" />\n</host>\n<runstats><finished time="1660830775" timestr="Thu Aug 18 15:52:55 2022" summary="Nmap done at Thu Aug 18 15:52:55 2022; 1 IP address (1 host up) scanned in 21.05 seconds" elapsed="21.05" exit="success" /><hosts up="1" down="0" total="1" />\n</runstats>\n</nmaprun>'
}
```

### Example with custom command
```yaml
module_arguments:
  command: nmap -A -T4 --top-ports 100 <target>
  timeout: 20
```

```json lines
{
    'return_code': 0, 
    'serialized_output': {'192.168.56.51': {'osmatch': {}, 'ports': [{'protocol': 'tcp', 'portid': '22', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'ssh', 'product': 'OpenSSH', 'version': '6.6.1p1 Ubuntu 2ubuntu2.13', 'extrainfo': 'Ubuntu Linux; protocol 2.0', 'ostype': 'Linux', 'method': 'probed', 'conf': '10'}, 'cpe': [{'cpe': 'cpe:/a:openbsd:openssh:6.6.1p1'}, {'cpe': 'cpe:/o:linux:linux_kernel'}], 'scripts': [{'name': 'ssh-hostkey', 'raw': '\n  1024 c7:23:04:56:47:12:29:44:cd:b5:47:f7:5a:cb:ad:6b (DSA)\n  2048 ab:d9:26:30:04:cd:99:ee:2c:f2:33:82:cd:2d:28:67 (RSA)\n  256 80:e7:ff:d4:4d:83:fb:e8:9f:69:27:68:bd:05:d4:2b (ECDSA)\n  256 61:36:ed:35:89:45:08:e0:85:da:45:05:9f:70:ed:15 (ED25519)', 'data': {'children': [{'fingerprint': 'c723045647122944cdb547f75acbad6b', 'type': 'ssh-dss', 'key': 'AAAAB3NzaC1kc3MAAACBAO9HtEJnY/fqKHmaAw+ycL4gHrICR7T/1JL5lpm0drDcrZtWI/mDhDiICba8yZlQrELAhnsP9yQf0AtRDiAA8zOqFw/55RdejvvUzWWUTI+5shisefPHbSRzHrJsO9khVR9gbDkirdGnOvjzi4qIHsqOPW6ji6/WhBWmjAKOWjr1AAAAFQDeFPBoAJqvJf+dPA1d3v+pH/VVpQAAAIEA3XepPB0Uo4M6J4UYCsX+Lu8SWujQ0AOSm9jQqmVQpD9sjnBWnAUP7ScUoSX1om7GadlZLMWT4GM3ljq3fQ+tNh/hejenJioTfnYY1BLlwpiqpNq9kU4JyF5vq1ZXdOPPKwJar52IDQf+p6M9fMtHrRgLVqXt5eHUWFDCiyxRi6kAAACBAL8lNl2BPKTyk66pGaKyUOBKw030K+2KPCdsupfzKS6oa5ZUWLSv2xToq0mKCLa+AcIr3yCS+q/v0oS85GawG56s5aQ9qNAlQbqDXqM/5TJx7xv57uDsZH5dNzyAEIM/+FjoiT6acQHFQ+DHRMrWwTuU3nHi5BF5k31/DflS8h+J', 'bits': '1024'}, {'fingerprint': 'abd9263004cd99ee2cf23382cd2d2867', 'type': 'ssh-rsa', 'key': 'AAAAB3NzaC1yc2EAAAADAQABAAABAQDjroBPHxLTl8UXL2r6HHW9Hcj+p2J4uUJh3k7ULVR8/aTRnJxyUfCPDway/lyoa2tY5qtiAF8k4tI53o7cCNnzL/aRW+w3PHIWGaYyI8VmNQxKKvQqcorML5UUaif9H3nTIN6+MIK+bxWMOnjq9vMnz4lzDYp6JX5Ra1LzflhmYHhnVVHA1JUuERp2MzN5OC3QJ+YaOCYYkbuY+GIn/SV+tcTbVXvpj6Dk3IQAQx1plQLbjcLda3wJjB+Umb+Xr/YkrKGvlWJTjc75I1+qIT4IJ1bKeecERHnT/IPpg8w7CDv3mHTlhW3fA9I3D3YElh21C/RFzwaGbOFP5q5pdunP', 'bits': '2048'}, {'fingerprint': '80e7ffd44d83fbe89f692768bd05d42b', 'type': 'ecdsa-sha2-nistp256', 'key': 'AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPkR0kyR7nNOBkue6qsy995GPdpnlnrsbDMkm/8lrx8dTkg+xg5exjZcQeATsNgMbzvwAcm4NXEMg3RNiLAJ4Zo=', 'bits': '256'}, {'fingerprint': '6136ed35894508e085da45059f70ed15', 'type': 'ssh-ed25519', 'key': 'AAAAC3NzaC1lZDI1NTE5AAAAIJIkt1AlQN1PvvvgH6AgQjroOF2iIYTC0QFqP0Kfx9bC', 'bits': '256'}]}}]}, {'protocol': 'tcp', 'portid': '111', 'state': 'open', 'reason': 'syn-ack', 'reason_ttl': '0', 'service': {'name': 'rpcbind', 'version': '2-4', 'extrainfo': 'RPC #100000', 'method': 'probed', 'conf': '10'}, 'cpe': [], 'scripts': [{'name': 'rpcinfo', 'raw': '\n  program version    port/proto  service\n  100000  2,3,4        111/tcp   rpcbind\n  100000  2,3,4        111/udp   rpcbind\n  100000  3,4          111/tcp6  rpcbind\n  100000  3,4          111/udp6  rpcbind\n  100024  1          34829/tcp   status\n  100024  1          35465/udp   status\n  100024  1          38358/udp6  status\n  100024  1          41647/tcp6  status\n', 'data': {'100024': {'tcp6': {'version': {'children': [{0: '1'}]}, 'children': [{'port': '41647', 'owner': '107', 'addr': '::'}]}, 'udp': {'version': {'children': [{0: '1'}]}, 'children': [{'port': '35465', 'owner': '107', 'addr': '0.0.0.0'}]}, 'udp6': {'version': {'children': [{0: '1'}]}, 'children': [{'port': '38358', 'owner': '107', 'addr': '::'}]}, 'tcp': {'version': {'children': [{0: '1'}]}, 'children': [{'port': '34829', 'owner': '107', 'addr': '0.0.0.0'}]}}, '100000': {'udp': {'version': {'children': [{0: '2', 1: '3', 2: '4'}]}, 'children': [{'port': '111', 'owner': 'superuser', 'addr': '0.0.0.0'}]}, 'local': {'version': {'children': [{0: '3', 1: '4'}]}, 'children': [{'addr': '/run/rpcbind.sock', 'owner': 'superuser'}]}, 'tcp6': {'version': {'children': [{0: '3', 1: '4'}]}, 'children': [{'port': '111', 'owner': 'superuser', 'addr': '::'}]}, 'udp6': {'version': {'children': [{0: '3', 1: '4'}]}, 'children': [{'port': '111', 'owner': 'superuser', 'addr': '::'}]}, 'tcp': {'version': {'children': [{0: '2', 1: '3', 2: '4'}]}, 'children': [{'port': '111', 'owner': 'superuser', 'addr': '0.0.0.0'}]}}}}]}], 'hostname': [], 'macaddress': None, 'state': {'state': 'up', 'reason': 'conn-refused', 'reason_ttl': '0'}}, 'stats': {'scanner': 'nmap', 'args': 'nmap -oX - -A -T4 --top-ports 100 192.168.56.51', 'start': '1660741353', 'startstr': 'Wed Aug 17 15:02:33 2022', 'version': '7.92', 'xmloutputversion': '1.05'}, 'runtime': {'time': '1660741360', 'timestr': 'Wed Aug 17 15:02:40 2022', 'summary': 'Nmap done at Wed Aug 17 15:02:40 2022; 1 IP address (1 host up) scanned in 7.65 seconds', 'elapsed': '7.65', 'exit': 'success'}}, 
    'output': '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE nmaprun>\n<?xml-stylesheet href="file:///usr/bin/../share/nmap/nmap.xsl" type="text/xsl"?>\n<!-- Nmap 7.92 scan initiated Wed Aug 17 15:02:33 2022 as: nmap -oX - -A -T4 -&#45;top-ports 100 192.168.56.51 -->\n<nmaprun scanner="nmap" args="nmap -oX - -A -T4 -&#45;top-ports 100 192.168.56.51" start="1660741353" startstr="Wed Aug 17 15:02:33 2022" version="7.92" xmloutputversion="1.05">\n<scaninfo type="connect" protocol="tcp" numservices="100" services="7,9,13,21-23,25-26,37,53,79-81,88,106,110-111,113,119,135,139,143-144,179,199,389,427,443-445,465,513-515,543-544,548,554,587,631,646,873,990,993,995,1025-1029,1110,1433,1720,1723,1755,1900,2000-2001,2049,2121,2717,3000,3128,3306,3389,3986,4899,5000,5009,5051,5060,5101,5190,5357,5432,5631,5666,5800,5900,6000-6001,6646,7070,8000,8008-8009,8080-8081,8443,8888,9100,9999-10000,32768,49152-49157"/>\n<verbose level="0"/>\n<debugging level="0"/>\n<hosthint><status state="up" reason="unknown-response" reason_ttl="0"/>\n<address addr="192.168.56.51" addrtype="ipv4"/>\n<hostnames>\n</hostnames>\n</hosthint>\n<host starttime="1660741353" endtime="1660741360"><status state="up" reason="conn-refused" reason_ttl="0"/>\n<address addr="192.168.56.51" addrtype="ipv4"/>\n<hostnames>\n</hostnames>\n<ports><extraports state="closed" count="98">\n<extrareasons reason="conn-refused" count="98" proto="tcp" ports="7,9,13,21,23,25-26,37,53,79-81,88,106,110,113,119,135,139,143-144,179,199,389,427,443-445,465,513-515,543-544,548,554,587,631,646,873,990,993,995,1025-1029,1110,1433,1720,1723,1755,1900,2000-2001,2049,2121,2717,3000,3128,3306,3389,3986,4899,5000,5009,5051,5060,5101,5190,5357,5432,5631,5666,5800,5900,6000-6001,6646,7070,8000,8008-8009,8080-8081,8443,8888,9100,9999-10000,32768,49152-49157"/>\n</extraports>\n<port protocol="tcp" portid="22"><state state="open" reason="syn-ack" reason_ttl="0"/><service name="ssh" product="OpenSSH" version="6.6.1p1 Ubuntu 2ubuntu2.13" extrainfo="Ubuntu Linux; protocol 2.0" ostype="Linux" method="probed" conf="10"><cpe>cpe:/a:openbsd:openssh:6.6.1p1</cpe><cpe>cpe:/o:linux:linux_kernel</cpe></service><script id="ssh-hostkey" output="&#xa;  1024 c7:23:04:56:47:12:29:44:cd:b5:47:f7:5a:cb:ad:6b (DSA)&#xa;  2048 ab:d9:26:30:04:cd:99:ee:2c:f2:33:82:cd:2d:28:67 (RSA)&#xa;  256 80:e7:ff:d4:4d:83:fb:e8:9f:69:27:68:bd:05:d4:2b (ECDSA)&#xa;  256 61:36:ed:35:89:45:08:e0:85:da:45:05:9f:70:ed:15 (ED25519)"><table>\n<elem key="fingerprint">c723045647122944cdb547f75acbad6b</elem>\n<elem key="type">ssh-dss</elem>\n<elem key="key">AAAAB3NzaC1kc3MAAACBAO9HtEJnY/fqKHmaAw+ycL4gHrICR7T/1JL5lpm0drDcrZtWI/mDhDiICba8yZlQrELAhnsP9yQf0AtRDiAA8zOqFw/55RdejvvUzWWUTI+5shisefPHbSRzHrJsO9khVR9gbDkirdGnOvjzi4qIHsqOPW6ji6/WhBWmjAKOWjr1AAAAFQDeFPBoAJqvJf+dPA1d3v+pH/VVpQAAAIEA3XepPB0Uo4M6J4UYCsX+Lu8SWujQ0AOSm9jQqmVQpD9sjnBWnAUP7ScUoSX1om7GadlZLMWT4GM3ljq3fQ+tNh/hejenJioTfnYY1BLlwpiqpNq9kU4JyF5vq1ZXdOPPKwJar52IDQf+p6M9fMtHrRgLVqXt5eHUWFDCiyxRi6kAAACBAL8lNl2BPKTyk66pGaKyUOBKw030K+2KPCdsupfzKS6oa5ZUWLSv2xToq0mKCLa+AcIr3yCS+q/v0oS85GawG56s5aQ9qNAlQbqDXqM/5TJx7xv57uDsZH5dNzyAEIM/+FjoiT6acQHFQ+DHRMrWwTuU3nHi5BF5k31/DflS8h+J</elem>\n<elem key="bits">1024</elem>\n</table>\n<table>\n<elem key="fingerprint">abd9263004cd99ee2cf23382cd2d2867</elem>\n<elem key="type">ssh-rsa</elem>\n<elem key="key">AAAAB3NzaC1yc2EAAAADAQABAAABAQDjroBPHxLTl8UXL2r6HHW9Hcj+p2J4uUJh3k7ULVR8/aTRnJxyUfCPDway/lyoa2tY5qtiAF8k4tI53o7cCNnzL/aRW+w3PHIWGaYyI8VmNQxKKvQqcorML5UUaif9H3nTIN6+MIK+bxWMOnjq9vMnz4lzDYp6JX5Ra1LzflhmYHhnVVHA1JUuERp2MzN5OC3QJ+YaOCYYkbuY+GIn/SV+tcTbVXvpj6Dk3IQAQx1plQLbjcLda3wJjB+Umb+Xr/YkrKGvlWJTjc75I1+qIT4IJ1bKeecERHnT/IPpg8w7CDv3mHTlhW3fA9I3D3YElh21C/RFzwaGbOFP5q5pdunP</elem>\n<elem key="bits">2048</elem>\n</table>\n<table>\n<elem key="fingerprint">80e7ffd44d83fbe89f692768bd05d42b</elem>\n<elem key="type">ecdsa-sha2-nistp256</elem>\n<elem key="key">AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBPkR0kyR7nNOBkue6qsy995GPdpnlnrsbDMkm/8lrx8dTkg+xg5exjZcQeATsNgMbzvwAcm4NXEMg3RNiLAJ4Zo=</elem>\n<elem key="bits">256</elem>\n</table>\n<table>\n<elem key="fingerprint">6136ed35894508e085da45059f70ed15</elem>\n<elem key="type">ssh-ed25519</elem>\n<elem key="key">AAAAC3NzaC1lZDI1NTE5AAAAIJIkt1AlQN1PvvvgH6AgQjroOF2iIYTC0QFqP0Kfx9bC</elem>\n<elem key="bits">256</elem>\n</table>\n</script></port>\n<port protocol="tcp" portid="111"><state state="open" reason="syn-ack" reason_ttl="0"/><service name="rpcbind" version="2-4" extrainfo="RPC #100000" method="probed" conf="10"/><script id="rpcinfo" output="&#xa;  program version    port/proto  service&#xa;  100000  2,3,4        111/tcp   rpcbind&#xa;  100000  2,3,4        111/udp   rpcbind&#xa;  100000  3,4          111/tcp6  rpcbind&#xa;  100000  3,4          111/udp6  rpcbind&#xa;  100024  1          34829/tcp   status&#xa;  100024  1          35465/udp   status&#xa;  100024  1          38358/udp6  status&#xa;  100024  1          41647/tcp6  status&#xa;"><table key="100024">\n<table key="tcp6">\n<table key="version">\n<elem>1</elem>\n</table>\n<elem key="port">41647</elem>\n<elem key="owner">107</elem>\n<elem key="addr">::</elem>\n</table>\n<table key="udp">\n<table key="version">\n<elem>1</elem>\n</table>\n<elem key="port">35465</elem>\n<elem key="owner">107</elem>\n<elem key="addr">0.0.0.0</elem>\n</table>\n<table key="udp6">\n<table key="version">\n<elem>1</elem>\n</table>\n<elem key="port">38358</elem>\n<elem key="owner">107</elem>\n<elem key="addr">::</elem>\n</table>\n<table key="tcp">\n<table key="version">\n<elem>1</elem>\n</table>\n<elem key="port">34829</elem>\n<elem key="owner">107</elem>\n<elem key="addr">0.0.0.0</elem>\n</table>\n</table>\n<table key="100000">\n<table key="udp">\n<table key="version">\n<elem>2</elem>\n<elem>3</elem>\n<elem>4</elem>\n</table>\n<elem key="port">111</elem>\n<elem key="owner">superuser</elem>\n<elem key="addr">0.0.0.0</elem>\n</table>\n<table key="local">\n<table key="version">\n<elem>3</elem>\n<elem>4</elem>\n</table>\n<elem key="addr">/run/rpcbind.sock</elem>\n<elem key="owner">superuser</elem>\n</table>\n<table key="tcp6">\n<table key="version">\n<elem>3</elem>\n<elem>4</elem>\n</table>\n<elem key="port">111</elem>\n<elem key="owner">superuser</elem>\n<elem key="addr">::</elem>\n</table>\n<table key="udp6">\n<table key="version">\n<elem>3</elem>\n<elem>4</elem>\n</table>\n<elem key="port">111</elem>\n<elem key="owner">superuser</elem>\n<elem key="addr">::</elem>\n</table>\n<table key="tcp">\n<table key="version">\n<elem>2</elem>\n<elem>3</elem>\n<elem>4</elem>\n</table>\n<elem key="port">111</elem>\n<elem key="owner">superuser</elem>\n<elem key="addr">0.0.0.0</elem>\n</table>\n</table>\n</script></port>\n</ports>\n<times srtt="484" rttvar="383" to="100000"/>\n</host>\n<runstats><finished time="1660741360" timestr="Wed Aug 17 15:02:40 2022" summary="Nmap done at Wed Aug 17 15:02:40 2022; 1 IP address (1 host up) scanned in 7.65 seconds" elapsed="7.65" exit="success"/><hosts up="1" down="0" total="1"/>\n</runstats>\n</nmaprun>'
}
```