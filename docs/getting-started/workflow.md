The current page tries to describe the ideal sequence of steps to use when you are planning a cyber defense exercise and want to use Cryton to automate the attacks.

## Deployment
First, you need to prepare an infrastructure for your cyber defense exercise. Deploying Cryton should be part of it:

1. Deploy and start [Hive](../installation.md)
2. Deploy [CLI](../installation.md) or [Frontend](../installation.md)
3. Deploy and start [Worker(s)](../installation.md)
4. Make sure it works:
    - To ensure your deployment works, try to perform a successful healthcheck on your Worker(s) using CLI, frontend, or possibly REST API
    - Additionally, check the Hive and Worker(s) output if there are any errors

!!! tip "Tips"

    - **CLI** and **Frontend** can be deployed outside the infrastructure and installed on demand
    - Use **one Worker per team** infrastructure

## Attack planning
Every Run can be described by a simple formula:
```
plan template + inventory = Plan instance
Plan instance + Worker = Plan execution
Plan instance + Workers = Run
```

Which results in the following steps:

1. Design a plan template (scenario)
2. Create a Plan instance
3. Register the Worker(s)
4. Create a Run
5. Schedule or execute the Run
6. Get the Run report
