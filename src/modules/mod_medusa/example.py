from mod import execute, validate

args = {
    "target": "CHANGE_ME",
    "credentials": {
        "username": "vagrant",
        "password": "vagrant",
    }
}

args2 = {
    "command": "medusa -t 4 -u vagrant -p vagrant -h <target_ip> -M ssh"
}


val_output = validate(args)
print(f"validate output: {str(val_output)}")

ex_output = execute(args)
print(f"execute output: {str(ex_output)}")
