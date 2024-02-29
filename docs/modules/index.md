# Modules
As mentioned [before](../architecture.md#modules), modules are Python scripts/packages that wrap tools and orchestrate them.

Module execution is done by Workers. All you need to do is to create a [Step](../design-phase/step.md) that will use your desired module.

Each module returns the following:

| Parameter name      | Parameter description                                                                                                                                      |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `result`            | `ok` - execution finished successfully <br /> `fail` - execution finished unsuccessfully <br /> `error` - an error occurred before the module could finish |
| `output`            | Output or errors from the execution                                                                                                                        |
| `serialized_output` | Machine readable output in JSON that can accessed in other modules as input                                                                                |

Modules mentioned in the current section (check the navigation on the left) are bundled in the Worker installation and work out of the box.

## Installing unofficial modules
Installing unofficial module(s) is pretty straight forward.

1. Find the desired module on PyPI or git (look for the `cryton-modules-` prefix)
2. Install the module(s)

=== "pipx"

    ```shell
    pipx inject cryton <package>
    ```
    
    ```shell
    pipx inject cryton git+<git-url>
    ```
    
    Check [here](https://pipx.pypa.io/stable/examples/) for examples.

=== "pip"

    Activate the virtual environment (`source /path/to/venv/bin/activate`) or use its PIP executable (`/path/to/venv/bin/pip`).
    
    ```shell
    pip install <package>
    ```
    
    ```shell
    pip install git+<git-url>
    ```
    
    Check [here](https://packaging.python.org/en/latest/tutorials/installing-packages/) for more information about installing packages and [here](https://pip.pypa.io/en/stable/topics/vcs-support/) for installing packages from VCS.

!!! warning ""

    - Since the version *2.0.0*, installing modules using the *modules* directory is deprecated
    
    - Do not forget to check the instructions of the package you're about to install
