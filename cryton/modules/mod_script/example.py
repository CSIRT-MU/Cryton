from mod import execute, validate

args = {
    "script_path": "/tmp/test.py",
    "executable": "python3",
    "serialized_output": True,
    "timeout": 30,
}

val_output = validate(args)
print(f"validate output: {str(val_output)}")

ex_output = execute(args)
print(f"execute output: {str(ex_output)}")
