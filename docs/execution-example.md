Now, we will walk through a simple attack scenario execution.

In case you need a testing environment or an advanced example, feel free to use the [playground](playground.md).

!!! warning "Prerequisites"

    It is assumed that you've followed the [quick-start](quick-start.md) guide.

## Create a plan template
The first step to run an automated attack is to create its description - [template](design-phase/index.md).

We will be using [this example](https://gitlab.ics.muni.cz/cryton/cryton/-/tree/{{{ git_release }}}/examples/basic-example/template.yml){target="_blank"}.  
It describes an attack scenario with 2 steps (actions). First, it scans the target host and checks if SSH (port 22) is open. If it's open, it checks if the provided credentials are correct.

??? note "Download the template"

    === "curl"
    
        ```shell
        curl -O https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/examples/basic-example/template.yml
        ```
    
    === "wget"
    
        ```shell
        wget https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/examples/basic-example/template.yml
        ```

---

??? tip "Validate the template first"

    Before we upload the template, we should validate it. However, for our template to be validated correctly, we have to provide an inventory file, which is described [here](#create-a-plan-instance). Once we have it, we can simply run:
    ```shell
    cryton-cli plans validate template.yml -i inventory.yml
    ```
    
    ??? example "Example"
        
        ```shell
        cryton-cli plans validate template.yml -i inventory.yml
        ```
    
        Expected output:
        ```
        Plan successfully validated! (<response>)
        ```

If we are satisfied with our template, we can upload it using CLI:
```shell
cryton-cli plan-templates create path/to/template.yml
```

??? example "Example"

    ```shell
    cryton-cli plan-templates create template.yml
    ```

    Expected output:
    ```
    Template successfully created! ({'id': 1})
    ```

## Create a Plan instance
Now we need to create a Plan instance we will use for the attack. Create it using a combination of the previously uploaded template and an [inventory file](design-phase/plan-instance.md#inventory-files) which is used to fill the missing variables in our template.  
The inventory file can be found [here](https://gitlab.ics.muni.cz/cryton/cryton-core/-/blob/{{{ git_release }}}/examples/basic-example/inventory.yml){target="_blank"}.

??? note "Download the inventory file"

    === "curl"
    
        ```shell
        curl -O https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/examples/basic-example/inventory.yml
        ```
    
    === "wget"
    
        ```shell
        wget https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/examples/basic-example/inventory.yml
        ```

To create a new Plan instance use:
```shell
cryton-cli plans create <TEMPLATE_ID> -i path/to/my/inventory.yml
```

??? example "Example"
    
    ```shell
    cryton-cli plans create 1 -i inventory.yml
    ```

    Expected output:
    ```
    Plan Instance successfully created! ({'id': 1})
    ```

## Register the Worker
To be able to run the scenario, we need to register an existing Worker. Keep in mind that **WORKER_NAME** must match the Worker’s `CRYTON_WORKER_NAME` setting:
```shell
cryton-cli workers create <WORKER_NAME> -d <WORKER_DESCRIPTION>
```

??? example "Example"

    ```shell
    cryton-cli workers create local_worker -d "my worker on localhost"
    ```

    Expected output:
    ```
    Worker successfully created! ({'id': 1})
    ```

To check if the Worker is running, run a health check:
```shell
cryton-cli workers health-check <WORKER_ID>
```

??? example "Example"
    
    ```shell
    cryton-cli workers health-check 1
    ```

    Expected output:
    ```
    The Worker successfully checked! (<response>)
    ```

## Create a Run
Finally, we create a new [Run](execution-phase/index.md) using the previously created Plan instance and Worker:
```shell
cryton-cli runs create <PLAN_INSTANCE_ID> <WORKER_ID>
```

??? example "Example"

    ```shell
    cryton-cli runs create 1 1
    ```

    Expected output:
    ```
    Run successfully created! ({'id': 1})
    ```

## Execute the Run

!!! warning "It works... but at what cost?"

    Before you proceed, make sure that you are allowed to scan and brute-force the selected target. Otherwise, there may be consequences.

Now that everything is prepared, we can execute our Run immediately or schedule it for later.

=== "immediately"

    To execute the Run immediately:

    ```shell
    cryton-cli runs execute <RUN_ID>
    ```

    ??? example "Example"
    
        ```shell
        cryton-cli runs execute 1
        ```

        Expected output:
        ```
        Run successfully executed! (Run 1 was executed.)
        ```

=== "schedule it for later"

    Run executions can be scheduled to a specific date and time. By default, the system timezone will be used. To use the UTC timezone, use the `--utc-timezone` flag.
    ```shell
    cryton-cli runs schedule <RUN_ID> <DATE> <TIME>
    ```
    
    ??? example "Example"
    
        ```shell
        cryton-cli runs schedule 1 2020-06-08 10:00:00
        ```

        Expected output:
        ```
        Run successfully scheduled! (Run 1 is scheduled for 2020-06-08 10:00:00.)
        ```

## Show Run information
Check Run's state and other useful information:
```shell
cryton-cli runs show <RUN_ID>
```

??? example "Example"
    
    ```shell
    cryton-cli runs show 1
    ```

    Expected output:
    ```
    id: 1, schedule_time: None, start_time: 2021-05-24T00:08:45.200025, pause_time: None, finish_time: 2021-05-24T00:09:18.397199, state: RUNNING
    ```

## Get a report
Get a report of your Run and its results anytime during its execution:
```shell
cryton-cli runs report <RUN_ID>
```

??? example "Example"
    
    ```shell
    cryton-cli runs report 1
    ```

    Expected output:
    ```
    Successfully created Run's report! (file saved at: /tmp/report_run_1_2020-06-08-10-15-00-257994_xdQeV)
    ```

??? tip "Read the report directly"

    Reports can be viewed directly in cryton-cli (**to quit, press Q**):
    ```shell
    cryton-cli runs report <RUN_ID> --less
    ```
    
    ??? example "Example"
        
        ```shell
        cryton-cli runs report 1 --less
        ```
