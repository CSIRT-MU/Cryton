Now, we will walk through a simple scenario execution.

In case you need a testing environment or an advanced example, feel free to use the [playground](playground.md).

!!! warning "Prerequisites"

    It is assumed that you've followed the [quick-start](quick-start.md) guide.

## Create a plan template
The first step to run an automated scenario is to create its description - [template](design-phase/index.md).

We will be using [this example](https://gitlab.ics.muni.cz/cryton/cryton/-/tree/{{{ git_release }}}/examples/functionality/basic/template.yml){target="_blank"}.  
It describes a scenario with one stage and a single step (action).

??? note "Download the template"

    === "curl"
    
        ```shell
        curl -O https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/examples/functionality/basic/template.yml
        ```
    
    === "wget"
    
        ```shell
        wget https://gitlab.ics.muni.cz/cryton/cryton/-/raw/{{{ git_release }}}/examples/functionality/basic/template.yml
        ```

Before we upload the template to Cryton, we should validate it. This can be done with:
```shell
cryton-cli plans validate template.yml
```

??? example "Example"
    
    ```shell
    cryton-cli plans validate template.yml
    ```

    Expected output:
    ```
    Plan successfully validated! (<response>)
    ```

If we are satisfied with our template, we can upload it using CLI:
```shell
cryton-cli plan-templates create template.yml
```

??? example "Example"

    ```shell
    cryton-cli plan-templates create template.yml
    ```

    Expected output:
    ```
    Template successfully created! ({'id': 1})
    ```

## Create a plan instance
Now we need to create a plan instance we will use for our attack/run. Since our template has no [inventory variables](design-phase/index.md#inventory-files), we will be only using the template (its ID we got from the previous step) to create it.

To create a new Plan instance use:
```shell
cryton-cli plans create <TEMPLATE_ID>
```

??? example "Example"
    
    ```shell
    cryton-cli plans create 1 -i inventory.yml
    ```

    Expected output:
    ```
    Plan Instance successfully created! ({'id': 1})
    ```

## Register a Worker
To be able to run the scenario, we need to register a new Worker. Keep in mind that **WORKER_NAME** must match the Worker’s `CRYTON_WORKER_NAME` setting:
```shell
cryton-cli workers create <WORKER_NAME> -d <WORKER_DESCRIPTION>
```

??? example "Example"

    ```shell
    cryton-cli workers create worker -d "my worker on localhost"
    ```

    Expected output:
    ```
    Worker successfully created! ({'id': 1})
    ```

To check if the Worker is responding, run a health check:
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

## Create a run
Finally, we create a new [Run](execution-phase/index.md) using the previously created plan instance and Worker:
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

## Execute the run

!!! warning "It works... but at what cost?"

    Before you proceed with running any scenario, make sure you are allowed to do so. Otherwise, there may be consequences.

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

## Show run information
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
