Modules are hot-swappable, which means the modules don't have to be present at startup. 
This is especially useful for development but **not recommended for production**.

## Development environment
Since the modules will be used and installed in the Worker environment, it is best to develop inside it.

1. [Install Worker using Poetry](worker.md#installation)
2. Enter the Worker's environment (make sure you are in the correct directory)
    ```shell
    poetry shell
    ```
3. Switch to the directory containing your module
    ```shell
    cd /path/to/cryton-modules/modules/my_module
    ```
4. Install the module requirements
    ```shell
    pip install -r requirements.txt
    ```

## How to create attack modules
In this section, we will discuss best practices and some rules that each module must follow.

To be able to execute a module using the Worker, it must have the following structure and IO arguments.

- Each module must have its directory with its name.
- The main module script must be called `mod.py`.
- Module must contain an `execute` function that takes a dictionary and returns a dictionary. It's an entry point for executing it.
- Module should contain a `validate` function that takes a dictionary, validates it, and returns 0 if it's okay, else raises an exception.

Path example:  
`/CRYTON_WORKER_MODULES_DIRECTORY/my-module-name/mod.py`

Where:

- **CRYTON_WORKER_MODULES_DIRECTORY** has to be the same path as is defined in the *CRYTON_WORKER_MODULES_DIRECTORY* variable.
- **my-module-name** is the directory containing your module.
- **mod.py** is the module file.

Here's an example of a typical module directory:
```
my_module_name/
├── mod.py
├── test_mod.py
├── README.md
├── requirements.txt
└── example.py
```

### mod.py
The most important file is the module itself (**must be called `mod.py`**). It consists of two main methods:
- `execute` (is used as an entry point for module execution; takes and returns **dictionary**)
- `validate` (is used to validate input parameters for the `execute` method; takes **dictionary** and returns 0 if it's okay, else raises an exception)

You can also use [prebuilt functionality](#prebuilt-functionality) from Worker.

#### I/O parameters
Every module has its unique input parameters. These are given by the Worker as a dictionary to the 
module `execute` (when executing the module) or `validate` (when validating the module parameters) function. 

Once the *execute* method has finished it must return a dictionary to the Worker with the following keys:

| Parameter name      | Parameter meaning                                                                                                                                                                                                              |
|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `return_code`       | Numeric representation of result (0, -1, -2). <br />0 (OK) means the module finished successfully.<br />-1 (FAIL) means the module finished unsuccessfully.<br />-2 (ERROR) means the module finished with an unhandled error. |
| `serialized_output` | Parsed output of the module. Eg. for a brute force module, this might be a list of found usernames and passwords.                                                                                                              |                                                                                                                                                                           |
| `output`            | Raw output of the module                                                                                                                                                                                                       |

#### Examples
Here's a minimal example:
```python
def validate(arguments: dict) -> int:
    if arguments != {}:
        return 0  # If arguments are valid.
    raise Exception("No arguments")  # If arguments aren't valid.

def execute(arguments: dict) -> dict:
    # Do stuff.
    return {"return_code": 0, "serialized_output": ["x", "y"]}

```

And also a bit more complex example:
```python
from schema import Schema
from cryton_worker.lib.util.module_util import File


def validate(arguments: dict) -> int:
    """
    Validate input arguments for the execute function.
    :param arguments: Arguments for module execution
    :raises: schema.SchemaError
    :return: 0 If arguments are valid
    """
    conf_schema = Schema({
        'path': File(str),
    })

    conf_schema.validate(arguments)
    return 0


def execute(arguments: dict) -> dict:
    """
    This attack module can read a local file.
    Detailed information should be in README.md.
    :param arguments: Arguments for module execution
    :return: Generally supported output parameters (for more information check Cryton Worker README.md)
    """
    # Set default return values
    ret_vals = {
        "return_code": -1,
        "serialized_output": {},
        "output": ""
    }

    # Parse arguments
    path_to_file = arguments.get("path")

    try:  # Try to get the file's content
        with open(path_to_file) as f:
            my_file = f.read()
    except IOError as ex:  # In case of fatal error (expected) update output
        ret_vals.update({'output': str(ex)})
        return ret_vals

    # In case of success update return_code to 0 (OK) and send the file content to the worker
    ret_vals.update({"return_code": 0})
    ret_vals.update({'output': my_file})

    return ret_vals

```

### test_mod.py
Contains a set of tests to check if the code is correct.

Here's a simple example:
```python
from mod import execute


class TestMyModuleName:
    def test_mod_execute(self):
        arguments = {'cmd': "test"}

        result = execute(arguments)

        assert result == {"return_code": 0}

```

Run the tests ([set up the environment first](#development-environment)):

```shell
pytest test_mod.py --cov=. --cov-report html
```

### README.md
README file should describe what the module is for, its IO parameters, and give the user some examples.

It should also say what system requirements are necessary (with version).

### requirements.txt
Here are the specified Python packages that are required to run the module. These requirements must be compliant with the
Python requirements in Cryton Worker.

For example, if the module wants to use the `schema` package with version *2.0.0*, but the Worker requires version *2.1.1*, it won't work.

### example.py
Is a set of predefined parameters that should allow the user to test if the module works as intended.

Example:

```python
from mod import execute, validate

args = {
    "argument1": "value1",
    "argument2": "value2"
}

validate_output = validate(args)
print(f"validate output: {validate_output}")

execute_output = execute(args)
print(f"execute output: {execute_output}")


```

Run the example ([set up the environment first](#development-environment)):

```shell
python example.py
```

## Prebuilt functionality
The worker provides prebuilt functionality to make building modules easier. Import it using:
```python
from cryton_worker.lib.util import module_util
```

It gives you access to:
### Metasploit
Wrapper for *MsfRpcClient* from *[pymetasploit3](https://github.com/DanMcInerney/pymetasploit3)*.
Examples:
```python
# Check if the connection to the MSF RPC server is OK before doing anything.
from cryton_worker.lib.util.module_util import Metasploit
msf = Metasploit()
if msf.is_connected():
    msf.do_stuff()
```

---

```python
from cryton_worker.lib.util.module_util import Metasploit
search_criteria = {"via_exploit": "my/exploit"}
found_sessions = Metasploit().get_sessions(**search_criteria)
```

---

```python
from cryton_worker.lib.util.module_util import Metasploit
output = Metasploit().execute_in_session("my_command", "session_id")
```

??? note "Changes"

    [:octicons-tag-24: Worker 1.1.0]({{{ releases.worker }}}1.1.0){target="_blank"} Added `minimal_execution_time` parameter

---

```python
from cryton_worker.lib.util.module_util import Metasploit

options = {"exploit_arguments": {}, "payload_arguments": {}}
Metasploit().execute_exploit("my_exploit", "my_payload", **options)
```

---

```python
from cryton_worker.lib.util.module_util import Metasploit
token = Metasploit().client.add_perm_token()
```

---

```python
from cryton_worker.lib.util.module_util import Metasploit
output = Metasploit().get_parameter_from_session("session_id", "my_param")
```

### get_file_binary
Function to get a file as binary.  
Example:
```python
from cryton_worker.lib.util.module_util import get_file_binary
my_file_content = get_file_binary("/path/to/my/file")
```

### File
Class used with *[schema](https://pypi.org/project/schema/)* for validation if the file exists.  
Example:
```python
from schema import Schema
from cryton_worker.lib.util.module_util import File
schema = Schema(File(str))
schema.validate("/path/to/file")
```

### Dir
Class used with *[schema](https://pypi.org/project/schema/)* for validation if the directory exists.  
Example:
```python
from schema import Schema
from cryton_worker.lib.util.module_util import Dir
schema = Schema(Dir(str))
schema.validate("/path/to/directory")
```
