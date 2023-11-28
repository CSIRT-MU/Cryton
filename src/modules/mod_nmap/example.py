from mod import execute, validate

args = {
    "target": "CHANGE_ME",
    "ports": [22, 80],
    "options": "-T2",
    "timeout": 50,
    "port_parameters": [
        {"portid": "22", "state": "open", "service": {"ostype": "Linux", "product": "OpenSSH"}}
    ]
}

args_with_command = {
    "command": "nmap -T4 <target_ip>",
    "timeout": 50,
    "port_parameters": [
        {"portid": "22", "state": "open", "service": {"ostype": "Linux", "product": "OpenSSH"}}
    ]
}

val_output = validate(args)
print(f"validate output: {str(val_output)}")

ex_output = execute(args)
print(f"execute output: {str(ex_output)}")
