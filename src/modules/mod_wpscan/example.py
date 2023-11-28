from mod import execute, validate

default_args = {
    "target": "CHANGE_ME",
    # "serialized_output": False,
    # "api_token": "TOKEN",
    "options": "--max-threads 7"
}

custom_command_args = {
    "custom_command": "wpscan --url CHANGE_ME -f json"
}


val_output = validate(default_args)
print(f"validate output: {str(val_output)}")

ex_output = execute(default_args)
print(f"execute output: {str(ex_output)}")
