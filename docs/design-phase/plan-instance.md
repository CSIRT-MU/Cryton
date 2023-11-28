The second stage is creating a Plan instance. While Template contains unfilled variables (therefore the name "template"), 
Plan instance fills these things in by combining the template with an **inventory file**. This file contains all 
information that needs to be filled in the template. After instantiation, everything is ready to create a **Run**.

!!! warning

    After creating the Plan instance only the [Execution variables](step.md#execution-variables) can be left unfilled and must be explicitly defined as a string.

## Inventory files
When you create a template, you don't always have all the information you need for directly executing it. Or you 
simply want to make it reusable for other people in their environment. To provide variability in 
templates we support **inventory files**. These inventory files can be used to provide variable values to templates 
using **Jinja** language.

A valid Plan file is written in YAML format with variables in the Jinja format, which have to be replaced during the 
instantiation process.

Inventory file example:
```yaml
names:
  stage1_target: 192.168.56.102
```

Template example:
```yaml
  # Stage two: target is web server
  - target: {{names.stage1_target}}
```
