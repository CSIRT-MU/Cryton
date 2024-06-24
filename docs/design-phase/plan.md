Plan is the basic unit of an attack scenario. It contains the name and owner of the Plan and a list of [Stages](stage.md).

![](../images/design-plan.png)

Example of defining a Plan using YAML:
```yaml
plan:
  name: my-plan
  owner: my name
  meta:
    description: This is an example description
    ...
  settings:
    separator: |
  dynamic: false
  stages:
    ...

```

To better understand what each argument means and defines, here is a short description:

- **name** - Sets the name of the Plan.
- **meta** - An undefined dictionary containing metadata. The `description` parameter is just an example, you can define your own.
- **owner** - Name of the person who created the Plan.
- **stages** - List of [Stages](stage.md) that will be executed during the Plan's execution.
- **settings** - Parameters for customization of specific functionalities (only `separator` for now, more about `separator` [here](step.md#custom-separator))
- **dynamic** - Whether the Plan will be static or the user can temper with it afterward. More information can be found [here](../execution-phase/dynamic-execution.md).
