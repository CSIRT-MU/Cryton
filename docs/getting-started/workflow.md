The following is the ideal sequence of steps to use when you are planning an attack and using Cryton to automate it.

## Deployment
First, you need to prepare an infrastructure for your cyber defense exercise. Deploying the Cryton toolset should be part of it:

1. Install and set up [Core](../components/core.md)
2. Install [CLI](../components/cli.md) and [Frontend](../components/frontend.md)
3. Install and set up your [Worker(s)](../components/worker.md)
4. Make sure it works:
    - Core is up and running
    - CLI/Frontend can access Core's REST API
    - Worker(s) are up and running
    - Worker(s) are connected to the RabbitMQ server

Once the Cryton tools are deployed, you can start planning your attack.

!!! tip "Tips"

    - CLI and Frontend can be deployed outside the infrastructure since other components don't need access to them
    - Use one worker per team infrastructure

!!! note ""

    This section can be represented by the [quick-start](quick-start.md) guide.

## Attack planning
Every Run can be described by a simple formula:
```
plan template + inventory = Plan instance
Plan instance + Worker = Plan execution
Plan instance + Workers = Run
```

Which results in the following steps:

1. Choose or design a plan template
2. Create a Plan instance
3. Register the Worker(s)
4. Create a Run
5. Schedule or execute the Run
6. Get the Run Report

!!! note ""

    More information about this section can be found in the [execution example](execution-example.md).
