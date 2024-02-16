To support dynamic security testing. We've added support for creating dynamic plans. They allow the user to 
create an empty Plan/Stage and create their agent to control the execution instead of Cryton's advanced scheduler.

## Features
- Create a Plan/Step/Stage for dynamic execution (an empty list of Stages/Steps can be provided)
- Add Step to Stage execution and execute it
- Add Stage to Plan execution and start it
- Added Steps are automatically set as a successor of the last Step (only if the `is_init` variable is **not** set to *True* and a possible parent Step exists)

## Limitations
- Dynamic plan must have the `dynamic` variable set to *True*
- If you don't want to pass any Stages/Steps you must provide an empty list
- Each Stage and Step must have a unique name in the same Plan (utilize [inventory variables](design-phase/plan-instance.md#inventory-files) to overcome this limitation)
- The Stage/Step you're trying to add must be valid
- Run's Plan must contain the instance (Stage/Step) you are trying to execute
- You cannot create multiple executions for an instance (you can execute an instance only once) under the same Plan execution

## Example using Python
You will probably want to automate these actions rather than using CLI to do them. For this purpose, we will create a simple Python script that will:

1. Create a template
2. Create a Plan
3. Add a Stage
4. Add a Step
5. Create a Run
6. Execute the Run
7. Create a new Step
8. Execute the new Step
9. Get the Run report

!!! danger "Requirements"

    - Cryton Core is running (REST API is accessible at *localhost:8000*)
    - Worker is registered in Core and running
    - mod_cmd is accessible from the Worker

Download the example script:

=== "curl"

    ```shell
    curl -O {{{ config.site_url }}}/execution-phase/dynamic_example.py
    ```

=== "wget"

    ```shell
    wget {{{ config.site_url }}}/execution-phase/dynamic_example.py
    ```

Update the `WORKER_ID` variable, and run the script:
```shell
python3 dynamic_example.py
```

??? abstract "Show the example"

    ```python
    {! include "./dynamic_example.py" !}
    ```

## Example using CLI
For this example we will assume that:

!!! danger "Requirements"

    - Cryton Core is running (REST API is accessible at *localhost:8000*)
    - Worker is registered in Core and running
    - mod_cmd is accessible from the Worker

Files used in this guide can be found in the [Cryton Core repository](https://gitlab.ics.muni.cz/cryton/cryton-core/-/tree/{{{ git_release }}}/examples/dynamic-execution-example){target="_blank"}.

It's best to switch to the example directory, so we will assume that's true.
```shell
cd /path/to/cryton-core/examples/dynamic-execution-example/
```

### Building a base Plan and executing it
First, we create a template
```shell
cryton-cli plan-templates create template.yml
```

Create a Plan (instance)
```shell
cryton-cli plans create <template_id>
```

Add a Stage to the Plan (update the inventory file to your needs)
```shell
cryton-cli stages create <plan_id> stage.yml -i stage-inventory.yml
```

Add an initial Step to the Stage
```shell
cryton-cli steps create <stage_id> step-init.yml
```

Add a reusable Step to the Stage (update the inventory file to your needs)
```shell
cryton-cli steps create <stage_id> step-reusable.yml -i step-reusable-inventory.yml
```

Create a Worker you want to test on
```shell
cryton-cli workers create local
```

Create a Run
```shell
cryton-cli runs create <plan_id> <worker_id>
```

Execute the Run
```shell
cryton-cli runs execute <run_id>
```

### Start a standalone Stage:
Add your Stage to the desired Plan (**Update the inventory file! Stage names must be unique.**)
```shell
cryton-cli stages create <plan_id> stage.yml -i stage-inventory.yml
```

Start your Stage (its trigger) under the desired Plan execution 
```shell
cryton-cli stages start-trigger <stage_id> <plan_execution_id>
```

### Execute a standalone Step:
Add your Step to the desired Stage (**Update the inventory file! Step names must be unique.**)
```shell
cryton-cli steps create <stage_id> step-reusable.yml -i step-reusable-inventory.yml
```

Execute your Step under the desired Stage execution
```shell
cryton-cli steps execute <step_id> <stage_execution_id>
```

### Check the results - works only once the Run is created:
```shell
cryton-cli runs report 1 --less
```
