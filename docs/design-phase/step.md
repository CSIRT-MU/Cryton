Step is equal to one action - module execution. Every step can have a successor(s) whose execution will follow according to the provided conditions.

Example of defining a step using YAML:
```yaml
my-step:
  metadata:
    description: This is an example description
  is_init: true
  module: module-name
  arguments: {}
  output:
    alias: credentials-from-localhost
    replace:
      "^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$": removed-ip
    mapping:
      - from: auth_token
        to: token
  next:
    - type: result
      value: ok
      step: other-steps-name

```

The name of the step is defined by the root element that holds it. In this case it's `my-step` (the name **must be unique** for each stage and step).

To better understand what each argument means and defines, here is a short description (sub-arguments are described in depth in their section):

- **metadata** - An undefined dictionary containing metadata. The `description` parameter is just an example, you can define your own.
- **is_init** - Defines if the step is initial (is executed once the stage has started) and is not a successor.
- **module** - Name of the module to use. See [modules](../modules/index.md) for more information.
- **arguments** - Dictionary containing arguments that will be passed to the module. See [modules](../modules/index.md) for more information.
- **output** - If you want to modify/share the step's output later, you can do so with this parameter. For more details check out the [output sharing](#output-sharing) section.
- **next** - Defines Step's successors, more info [below](#conditional-execution).

## Conditional execution
To execute an attack scenario according to some execution tree, steps provide a way to execute other steps according to the specified conditions.

This can be done with the `next` parameter, which contains an array of objects with the following parameters:

| parameter | type                       | Description                              |
|-----------|----------------------------|------------------------------------------|
| `type`    | string                     | Defines which type of output to compare. |
| `value`   | string or array of strings | Value used for comparison.               |
| `step`    | string or array of strings | Name(s) of the successor(s).             |

The following are types of outputs together with the descriptions of their possible values:

| Type                | Value                              | Description                                                                                                                             |
|---------------------|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `result`            | `ok`, `fail`, `error`              | Match the `result` of the step.                                                                                                         |
| `serialized_output` | Regular expression (`^my_regex.*`) | Match [regex](https://docs.python.org/3/library/re.html#regular-expression-syntax){target="_blank"} in `serialized_output` of the step. |
| `output`            | Regular expression (`^my_regex.*`) | Match [regex](https://docs.python.org/3/library/re.html#regular-expression-syntax){target="_blank"} in `output` of the step.            |
| `any`               | Value must be omitted              | Run successor(s) in any case.                                                                                                           |

### Examples:
```yaml
my-step:
  next:
  - type: result
    value: ok
    step: step-to-execute

```

```yaml
my-step:
  next:
  - type: serialized_output
    value: 
      - admin
      - root
    step: 
      - step-to-execute-1
      - step-to-execute-2

```

```yaml
my-step:
  next:
  - type: any
    step: step-to-execute

```

## Output sharing
Output sharing is a feature that allows sharing of the *serialized_output* between steps. The data can be also shared across stages or even from stages.

### Going through the data
To go through the serialized data we use a modified version of a dot notation with the following rules:

- To access an item inside an object (dictionary) use a [separator](plan.md#separator) - `.` by default
- To access an item inside an array (list) specify an index `[integer]` (regex representation: `^\[[0-9]+]$`)

For example, imagine the following object (dictionary):
```json
{"credentials": [{"username": "admin", "password": "securePassword"}]}
```
If we wanted to access it and get the **password** for the *admin* user, we would use `credentials[0].password` which would return `securePassword`.

### Accessing the data
We use the `$` character to indicate we want to use data from another step. Then we insert the name of the desired step, and finally use the dot notation mentioned [before](#going-through-the-data).

In the template, we would define it like so:
```yaml
get-credentials:  # step with the wanted data
  module: my-module
  arguments: {}

use-password:  # step that needs the data
  module: my-other-module
  arguments:
    password: $get-credentials.credentials[0].password

```

!!! warning ""

    Output sharing is resolved only inside the `arguments` parameter in step.

## Output alias
By default, you can access step's data using its name. Additionally, you can define an alias as an alternative. This can be useful since you can assign the same alias to multiple steps.

??? question "How is the data handled"

    The serialized output from each step is merged into a single object. In case the data exists in multiple steps, the latest data gets used.
    
    Imagine we have two steps with the same alias.
    
    The first one finished with the following output:
    ```json
    {"alpha": "blue", "whiskey": "red"}
    ```
    
    The second step finished a minute later with the following output:
    ```json
    {"whiskey": "green", "charlie": "yellow"}
    ```
    
    The following data would be available to the step accessing the alias:
    ```json
    {"alpha": "blue", "whiskey": "green", "charlie": "yellow"}
    ```

For example:
```yaml
get-credentials:
  module: my-module
  arguments: {}
  output:
    alias: my-super-alias

use-password:
  module: my-other-module
  arguments:
    password: $my-super-alias.credentials[0].password

```

### Parent alias
Furthermore, there is a special alias named **parent**, which is a shortcut for the step (parent) that executed the current step.
```yaml
get-credentials:
  module: my-module
  arguments: {}
  next:
    type: any
    step: use-password

use-password:
  module: my-other-module
  arguments:
    password: $parent.credentials[0].password

```

## Output mapping
Sometimes you do not care from which step you receive information, which is why the *output alias* exists. However, what if the data is saved under a different name (`token` vs. `auth_token`)? For this reason, there is the **output mapping**.
```yaml
step-a: # Returns 'token'
  module: my-module
  arguments: {}
  output:
    alias: steal
    mapping:
      - from: token
        to: stolen_token

step-b: # Returns 'auth_token'
  module: my-other-module
  arguments: {}
  output:
    alias: steal
    mapping:
      - from: auth_token
        to: stolen_token

step-c:
  module: my-other-other-module
  arguments:
    token: $steal.stolen_token

```

## Output replacing
In case you want to replace some parts of your output, you can define a dictionary of rules (regexes) and strings to replace the matches with.  
Keep in mind, that the rules are applied **in order**.

Here is an example of matching IPv4 and replacing it with `removed-ip`:
```yaml
my-step:
  module: my-module
  arguments: {}
  output:
    replace:
      "^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$": removed-ip

```

## Execution variables
To assign different values for each plan execution in a Run, you can use execution variables.

To define an execution variable, use Jinja ([with some tweaks](#limitations)) **wrapped in single quotes**:
```yaml
my-step:
  module: my-module
  arguments:
    target: '{{ my_jinja_variable }}'
```

Before you execute the run, upload the variable(s). See [CLI](../interfaces/cli.md#execution-variables) documentation for more information.

Example of a file with execution variables:
```yaml
variable: localhost
nested:
  variable: value
variables:
  - var1
  - var2
```

### Limitations
* Execution variables must be wrapped in single quotes
    ```yaml
    foo: '{{ variable }}'
    ```
* Execution variables are resolved only for the `arguments` parameter in the step
* Currently, there is support for simple and nested variables only:
    ```yaml
    foo: '{{ variable }}'
    ```
    ```yaml
    foo: '{{ nested.variable }}'
    ```
    ```yaml
    foo: '{{ variable[index] }}'
    ```
    ```yaml
    foo: '{{ nested.variable[index] }}'
    ```
* If you want to use more Jinja goodies, use the raw block:
    ```yaml
    foo: {% raw %} '{{ variable + 14 }}' {% endraw %}
    ```
* If a variable is missing, the step errors out once it's started
