A stage is a unit defined by a target and its trigger (for example time of start). It holds attack [steps](step.md) that are related to each other.

![](../images/design-stage.png)

Example of defining a stage using YAML:
```yaml
my-stage:
  metadata:
    description: This is an example description
  type: delta
  arguments:
    minutes: 5
  depends_on:
    - previous-stage
  steps: {}

```

The name of the stage is defined by the root element that holds it. In this case it's `my-stage` (the name **must be unique** for each stage and step).

To better understand what each argument means and defines, here is a short description (sub-arguments are described in depth in their section):

- **metadata** - An undefined dictionary containing metadata. The `description` parameter is just an example, you can define your own.
- **type** - Which trigger is used to determine when to start the stage. For more details see the [triggers](#triggers) section.
- **arguments** - Arguments specific for each type of trigger. For more details see the [triggers](#triggers) section.
- **depends_on** - If the stage depends on other stages, we can tell it to wait until the other stages are finished. For more details see the [dependencies](#dependencies) section.
- **steps** - [Steps](step.md) that will be executed during the stage's execution.

## Triggers

### Immediate
Run the stage immediately. No arguments are supported.
```yaml
my-stage:
  type: immediate
  steps: {}

```

If no type is defined, it is used as the default option.
```yaml
my-stage:
  steps: {}

```

### Delta
Once the plan is started, wait for the specified time before starting the stage.
```yaml
my-stage:
  type: delta
  arguments:
    hours: 1
  steps: {}

```

**Arguments:**

| Argument | Default | Description         |
|----------|---------|---------------------|
| days     | 0       | Wait for n days.    |
| hours    | 0       | Wait for n hours.   |
| minutes  | 0       | Wait for n minutes. |
| seconds  | 0       | Wait for n seconds. |

!!! note ""

    At least one argument is required.

### Time
Schedule execution for a specific date and time.
```yaml
# This stage would be executed on the day the plan was executed at 08:00:00 in Europe/Prague timezone
type: time
arguments:
  timezone: Europe/Prague
  hour: 8

```

**Arguments:**

| Argument | Default       | Description                                                                                       |
|----------|---------------|---------------------------------------------------------------------------------------------------|
| timezone | UTC           | [Timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones){target="_blank"} to use. |
| year     | Current year  | Year in which stage should be executed.                                                           |
| month    | Current month | Month in which stage should be executed.                                                          |
| day      | Current day   | Day in which stage should be executed.                                                            |
| hour     | 0             | Hour in which stage should be executed.                                                           |
| minute   | 0             | Minute in which stage should be executed.                                                         |
| second   | 0             | Second in which stage should be executed.                                                         |

!!! note ""

    At least one argument is required (excluding the timezone).

### HTTP
The stage will be executed once the specific data are received in the HTTP request (GET/POST) on the listener.
```yaml
type: http
arguments:
  host: localhost
  port: 8082
  routes:
    - path: /index
      method: GET
      parameters:
        - name: parameter
          value: value
  steps: {}

```

**Arguments:**

| Argument | Default | Description                                               |
|----------|---------|-----------------------------------------------------------|
| host     | 0.0.0.0 | Address used to serve the listener on the Worker machine. |
| port     |         | Port used to serve the listener on the Worker machine.    |
| routes   |         | List of routes the listener will check for requests.      |

**Arguments for the routes parameter:**

| Argument   | Default | Description                    |
|------------|---------|--------------------------------|
| path       |         | Request's path.                |
| method     |         | Request's allowed method.      |
| parameters |         | Request's required parameters. |


**Arguments for the parameters parameter:**

| Argument | Default | Description        |
|----------|---------|--------------------|
| name     |         | Parameter's name.  |
| value    |         | Parameter's value. |

### Metasploit
Metasploit trigger runs an exploit the same as the Metasploit module.
The stage will be executed once the metasploit module has finished successfully. More information can be found [here](../modules/list/metasploit.md).
```yaml
type: metasploit
arguments:
  module_name: scanner/ssh/ssh_login
  datastore:
    RHOSTS: 127.0.0.1
    USERNAME: vagrant
    PASSWORD: vagrant
  steps: {}

```

## Dependencies
Creating time-based triggers can be limiting, since the stage itself can take more time than expected. To ensure that the stages will execute in the correct order, you can check if a stage has already finished. This way you can ensure that the output from other stages is available.

```yaml
my-stage:
  depends_on:
    - other-stage
  steps: {}

```
