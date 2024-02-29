On this page, we will discuss primarily modules creation. If you want to contribute to the official project repository, make sure you follow the instructions in the [development section](index.md) first.

Modules are [namespace packages](https://packaging.python.org/en/latest/guides/packaging-namespace-packages/) in the `cryton.modules` namespace.

Once Worker receives an execution request, it:

- imports the specified module (in case it exists)
- validates the input using [JSON Schema](https://json-schema.org/) *2020-12* (specified in the `Module.SCHEMA` parameter)
- checks requirements (using the `Module.check_requirements` method)
- runs the module with the supplied arguments (using the `Module.execute` method)
- saves the module output

In order to achieve this, there are some rules:

- module is a namespace package
- the namespace package contains `module.py` file
- the `module.py` file contains class called `Module`
- the `Module` class inherits from `cryton.lib.utility.module.ModuleBase`
- the `Module` class implements all abstract methods from the `ModuleBase`
- the `Module` class overrides the `SCHEMA` class variable (see [JSON Schema](https://json-schema.org/))
- the `Module` class overrides the `ModuleBase.execute` method - it is the entry point for running the module

## Creating a new module

[//]: # (![]&#40;../images/oh-youre-approaching-me.jpg&#41;)

Let's say we want to create a module that just prints and returns `Hello World!`. In case the user specifies a `name` parameter, it will use it instead.

??? question "Want to create your own project with modules?"

    In case you want to keep your modules private, or version the modules yourself, you can create your own repository and install them later as mentioned [here](../modules/index.md#installing-unofficial-modules).
    
    Projects and Python packages should follow the convention of having the `cryton-modules-` prefix.
    
    We will be using [Poetry](https://python-poetry.org/docs/#installation){target="_blank"} for this example.
    
    Create new poetry project for a module called `hello_world` for the `cryton.modules` namespace:
    ```shell
    poetry new --name cryton.modules.hello_world cryton-modules-my-collection
    ```
    
    Go into the project directory:
    ```shell
    cd cryton-modules-my-collection
    ```
    
    Add Cryton (with *worker* extras) as a dependency.
    ```shell
    poetry add "cryton[worker]>=2"
    ```
    
    You're all set. Follow the rest of the guide, but don't forget you already have the module directory (Python package).

In the directory `cryton/modules/` create a new Python package (directory with `__init__.py` file) and give it appropriate name (`hello_world` in our case).
```shell
mkdir cryton/modules/hello_world
touch cryton/modules/hello_world/__init__.py
```

Now create `module.py` file in the new directory.
```shell
touch cryton/modules/hello_world/module.py
```

We should have the following structure:
```
├── cryton
│   ├── modules
│   │   ├── hello_world
│   │   │   ├── __init__.py
│   │   │   ├── module.py
```

Copy the following code into the `cryton/modules/hello_world/module.py` file:
```python
from cryton.lib.utility.module import ModuleBase, ModuleOutput, Result


# Module implementation
class Module(ModuleBase):
    # The SCHEMA variable is used for input arguments validation (it uses JSON Schema)
    SCHEMA = {
        "type": "object",
        "description": "Arguments for the `hello_world` module.",
        "properties": {
            "name": {"type": "string", "minLength": 1, "description": "Name used in the greeting."}
        },
        "additionalProperties": False
    }

    # In case our module has any system requirements, we can check for them here
    def check_requirements(self) -> None:
        pass

    # This is the entrypoint to the module execution. 
    # Write the code you want to run here. Also add parsing and evaluation of results
    def execute(self) -> ModuleOutput:
        # Arguments can be accessed using the `self._arguments` parameter
        name = self._arguments.get("name", "World")

        to_print = f"Hello {name}!"

        self._data.result = Result.OK  # The module finished successfully
        self._data.output = to_print  # Output we want to send
        return self._data

```

You just created a module that checks if the input parameter `name` is a string and has at least one character, in case it is defined. Once the module is executed it returns the greeting.

!!! tip

    - For more information, see the implementation of the `cryton.lib.utility.module.ModuleBase` class
    - Since the modules are installed alongside Cryton, they have access to its features/code (*Metasploit*, *Empire*, ...)
    - Do not forget to add tests
    - Feel free to check other modules for inspiration
