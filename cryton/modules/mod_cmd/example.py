from mod import execute, validate

args = {
    "cmd": "cat /etc/passwd",
    # "timeout": 10,
    # "end_checks": ["vagrant"],
    # "session_id": 2  # needs active session
}

val_output = validate(args)
print(f"validate output: {str(val_output)}")

ex_output = execute(args)
print(f"execute output: {str(ex_output)}")
