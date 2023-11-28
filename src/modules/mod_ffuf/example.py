from mod import execute, validate

args = {
    "target": "https:198.51.100.1/FUZZ",
    "serialized_output": True,
    "wordlist" : "/usr/share/wordlists/dirb/small.txt",
    "options": ""
}

val_output = validate(default_args)
print(f"validate output: {val_output}")

ex_output = execute(default_args)
print(f"execute output: {ex_output}")
