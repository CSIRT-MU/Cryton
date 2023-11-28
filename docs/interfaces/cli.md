CLI implements capabilities of the Cryton's REST API and can be automated by using custom scripts.

```
Usage: cryton-cli [OPTIONS] COMMAND [ARGS]...

  A CLI wrapper for Cryton API.

Options:
  -H, --host TEXT     Set Cryton's address (default is localhost).
  -p, --port INTEGER  Set Cryton's address (default is 8000).
  --secure            Set if HTTPS will be used.
  --debug             Show non formatted output.
  --version           Show the version and exit.
  --help              Show this message and exit.

Commands:
  execution-variables  Manage Execution variables from here.
  logs                 Manage Workers from here.
  plan-executions      Manage Plan's executions from here.
  plan-templates       Manage Plan templates from here.
  plans                Manage Plans from here.
  runs                 Manage Runs from here.
  stage-executions     Manage Stage's executions from here.
  stages               Manage Stages from here.
  step-executions      Manage Step's executions from here.
  steps                Manage Steps from here.
  workers              Manage Workers from here.
```

## execution-variables
Manage Execution variables from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Create new execution variable(s) for PLAN\_EXECUTION\_ID from FILE.

PLAN\_EXECUTION\_ID IS ID of the desired PlanExecution.

FILE is path (can be multiple) to file(s) containing execution variables.

**Arguments:**  
- PLAN\_EXECUTION\_ID  
- FILE  

**Options:**  
- help (`--help`) - Show this message and exit.  

### delete
Delete Execution variable with EXECUTION\_VARIABLE\_ID saved in Cryton.

EXECUTION\_VARIABLE\_ID is ID of the Execution\_variable you want to delete.

**Arguments:**  
- EXECUTION\_VARIABLE\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Execution variables in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parent (`-p`, `--parent`) - Filter Execution variables using Plan execution ID.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### show
Show Execution variable with EXECUTION\_VARIABLE\_ID saved in Cryton.

EXECUTION\_VARIABLE\_ID is ID of the Execution variable you want to see.

**Arguments:**  
- EXECUTION\_VARIABLE\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

## generate-docs
Generate Markdown documentation for CLI.

FILE is path/to/your/file where you want to save the generated documentation.

**Arguments:**  
- FILE  

**Options:**  
- layer (`-l`, `--layer`) - Highest header level.  
- help (`--help`) - Show this message and exit.  

## logs
Manage logs from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Logs in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- parameter\_filters (`-f`, `--filter`) - Filter results using substrings (for example `warning`, `2023-08-11T13:26`, etc.).  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

## plan-executions
Manage Plan's executions from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### delete
Delete Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to delete.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### kill
Kill Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to kill.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Plan's executions in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parent (`-p`, `--parent`) - Filter Plan executions using Run ID.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### pause
Pause Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to pause.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### report
Create report for Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to create report for.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the report to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### resume
Resume Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to resume.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### show
Show Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to see.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### validate-modules
Validate modules for Plan's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Plan's execution you want to validate modules for.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

## plan-templates
Manage Plan templates from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Store Plan Template into Cryton.

FILE is path/to/your/file that you want to upload to Cryton.

**Arguments:**  
- FILE  

**Options:**  
- help (`--help`) - Show this message and exit.  

### delete
Delete Template with TEMPLATE\_ID saved in Cryton.

TEMPLATE\_ID is ID of the Template you want to delete.

**Arguments:**  
- TEMPLATE\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### get-template
Get Template with TEMPLATE\_ID saved in Cryton.

TEMPLATE\_ID is ID of the Template you want to get.

**Arguments:**  
- TEMPLATE\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the template to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### list
List existing Plan templates in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### show
Show Template with TEMPLATE\_ID saved in Cryton.

TEMPLATE\_ID is ID of the Template you want to see.

**Arguments:**  
- TEMPLATE\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

## plans
Manage Plans from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Fill template PLAN\_TEMPLATE\_ID with inventory file(s) and save it to Cryton.

PLAN\_TEMPLATE\_ID is ID of the template you want to fill.

**Arguments:**  
- TEMPLATE\_ID  

**Options:**  
- inventory\_files (`-i`, `--inventory-file`) - Inventory file used to fill the template. Can be used multiple times.  
- help (`--help`) - Show this message and exit.  

### delete
Delete Plan with PLAN\_ID saved in Cryton.

PLAN\_ID is ID of the Plan you want to delete.

**Arguments:**  
- PLAN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### execute
Execute Plan saved in Cryton with PLAN\_ID on Worker with WORKER\_ID and attach it to Run with RUN\_ID.

PLAN\_ID is ID of the Plan you want to execute.

WORKER\_ID is ID of the Plan you want to execute.

RUN\_ID is ID of the Run you want to attach this execution to.

**Arguments:**  
- PLAN\_ID  
- WORKER\_ID  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### get-plan
Get Plan with PLAN\_ID saved in Cryton.

PLAN\_ID is ID of the Plan you want to get.

**Arguments:**  
- PLAN\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the plan to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### list
List existing Plans in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### show
Show Plan with PLAN\_ID saved in Cryton.

PLAN\_ID is ID of the Plan you want to see.

**Arguments:**  
- PLAN\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### validate
Validate (syntax check) your FILE with Plan.

FILE is path/to/your/file that you want to validate.

**Arguments:**  
- FILE  

**Options:**  
- inventory\_files (`-i`, `--inventory-file`) - Inventory file used to fill the template. Can be used multiple times.  
- help (`--help`) - Show this message and exit.  

## runs
Manage Runs from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Create new Run with PLAN\_ID and WORKER\_IDS.

PLAN\_ID is ID of the Plan you want to create Run for. (for example 1)

WORKER\_IDS is list of IDs you want to use for Run. (1 2 3)

**Arguments:**  
- PLAN\_ID  
- WORKER\_IDS  

**Options:**  
- help (`--help`) - Show this message and exit.  

### delete
Delete Run with RUN\_ID saved in Cryton.

RUN\_ID is ID of the Run you want to delete.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### execute
Execute Run saved in Cryton with RUN\_ID.

RUN\_ID is ID of the Run you want to execute.

**Arguments:**  
- RUN\_ID  

**Options:**  
- skip\_checks (`-S`, `--skip-checks`) - Skip health-checks and modules validation. [:octicons-tag-24: CLI 1.1.0]({{{ releases.cli }}}1.1.0){target="_blank"}  
- help (`--help`) - Show this message and exit.  

!!! info "Changes"

    [:octicons-tag-24: CLI 1.1.0]({{{ releases.cli }}}1.1.0){target="_blank"} [:octicons-tag-24: Core 1.2.0]({{{ releases.core }}}1.2.0){target="_blank"}
    
    Since the CLI release 1.1.0 the command checks if the selected Workers are available and modules are valid. If everything is OK, it executes the Run.

    If you're running Core with a lower version than 1.2.0, use the `-S` option.

### get-plan
Get plan from Run with RUN\_ID saved in Cryton.

RUN\_ID is ID of the Run you want to get plan from.

**Arguments:**  
- RUN\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the plan to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### health-check-workers

[:octicons-tag-24: CLI 1.1.0]({{{ releases.cli }}}1.1.0){target="_blank"}

Check Workers for Run with RUN\_ID saved in Cryton.

RUN\_ID is ID of the Run you want to check Workers for.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### kill
Kill Run saved in Cryton with RUN\_ID.

RUN\_ID is ID of the Run you want to kill.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Runs in Cryton.


**Options:**  
- less (`--less`) - Show 'less' like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### pause
Pause Run saved in Cryton with RUN\_ID.

RUN\_ID is ID of the Run you want to pause.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### postpone
Postpone Run saved in Cryton with RUN\_ID by TIME (hh:mm:ss).

RUN\_ID is ID of the Run you want to postpone.

TIME is time that will be added to the Run's start time (hh:mm:ss).

**Arguments:**  
- RUN\_ID  
- TO\_POSTPONE  

**Options:**  
- help (`--help`) - Show this message and exit.  

### report
Create report for Run with RUN\_ID saved in Cryton.

RUN\_ID is ID of the Run you want to create report for.

**Arguments:**  
- RUN\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the report to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### reschedule
Reschedule Run saved in Cryton with RUN\_ID to specified DATE and TIME.

RUN\_ID is ID of the Run you want to reschedule.

DATE in format year-month-day (Y-m-d).

TIME in format hours:minutes:seconds (H:M:S).

**Arguments:**  
- RUN\_ID  
- TO\_DATE  
- TO\_TIME  

**Options:**  
- utc\_timezone (`--utc-timezone`) - Input time in UTC timezone.  
- help (`--help`) - Show this message and exit.  

### resume
Resume Run saved in Cryton with RUN\_ID.

RUN\_ID is ID of the Run you want to resume.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### schedule
Schedule Run saved in Cryton with RUN\_ID to specified DATE and TIME.

RUN\_ID is ID of the Run you want to schedule.

DATE in format year-month-day (Y-m-d).

TIME in format hours:minutes:seconds (H:M:S).

**Arguments:**  
- RUN\_ID  
- TO\_DATE  
- TO\_TIME  

**Options:**  
- utc\_timezone (`--utc-timezone`) - Input time in UTC timezone.  
- help (`--help`) - Show this message and exit.  

### show
Show Run with RUN\_ID saved in Cryton.

RUN\_ID is ID of the Run you want to see.

**Arguments:**  
- RUN\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### unschedule
Unschedule Run saved in Cryton with RUN\_ID.

RUN\_ID is ID of the Run you want to unschedule.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### validate-modules
Validate modules for Run with RUN\_ID saved in Cryton.

RUN\_ID is ID of the Run you want to validate modules for.

**Arguments:**  
- RUN\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

## stage-executions
Manage Stage's executions from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### delete
Delete Stage's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Stage's execution you want to delete.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### kill
Kill Stage's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Stage's execution you want to kill.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Stage's executions in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parent (`-p`, `--parent`) - Filter Stage executions using Plan execution ID.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### re-execute
Re-execute Stage's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Stage's execution you want to kill.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- immediately (`--immediately`) - Re-execute StageExecution immediately without starting its Trigger.  
- help (`--help`) - Show this message and exit.  

### report
Create report for Stage's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Stage's execution you want to create report for.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the report to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### show
Show Stage's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Stage's execution you want to see.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

## stages
Manage Stages from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Create Stage from FILE and add it to Plan with PLAN\_ID.

PLAN\_ID is an ID of the Plan you want to add the Stage to.

FILE is a path to the file containing the Stage template.

**Arguments:**  
- PLAN\_ID  
- FILE  

**Options:**  
- inventory\_files (`-i`, `--inventory-file`) - Inventory file used to fill the template. Can be used multiple times.  
- help (`--help`) - Show this message and exit.  

### delete
Delete Stage with STAGE\_ID saved in Cryton.

STAGE\_ID is ID of the Stage you want to delete.

**Arguments:**  
- STAGE\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Stages in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parent (`-p`, `--parent`) - Filter Stages using Plan ID.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### show
Show Stage with STAGE\_ID saved in Cryton.

STAGE\_ID is ID of the Stage you want to see.

**Arguments:**  
- STAGE\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### start-trigger
Start Stage's trigger with STAGE\_ID under Plan execution with PLAN\_EXECUTION\_ID.

STAGE\_ID is an ID of the Stage you want to start.

PLAN\_EXECUTION\_ID is an ID of the Plan execution you want to set as a parent of the Stage execution.

**Arguments:**  
- STAGE\_ID  
- PLAN\_EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### validate
Validate (syntax check) your FILE with Stage.

FILE is path/to/your/file that you want to validate.

**Arguments:**  
- FILE  

**Options:**  
- inventory\_files (`-i`, `--inventory-file`) - Inventory file used to fill the template. Can be used multiple times.  
- dynamic (`-D`, `--dynamic`) - If Stage will be used with a dynamic Plan.  
- help (`--help`) - Show this message and exit.  

## step-executions
Manage Step's executions from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### delete
Delete Step's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Step's execution you want to delete.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### kill
Kill Step's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Step's execution you want to kill.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Step's executions in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parent (`-p`, `--parent`) - Filter Step executions using Stage execution ID.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### re-execute
Re-execute Step's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Step's execution you want to kill.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### report
Create report for Step's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Step's execution you want to create report for.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- file (`-f`, `--file`) - File to save the report to (default is /tmp).  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### show
Show Step's execution with EXECUTION\_ID saved in Cryton.

EXECUTION\_ID is ID of the Step's execution you want to see.

**Arguments:**  
- EXECUTION\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

## steps
Manage Steps from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Create Step from FILE and add it to Stage with STAGE\_ID.

STAGE\_ID is an ID of the Stage you want to add the Stage to.

FILE is a path to the file containing the Step template.

**Arguments:**  
- STAGE\_ID  
- FILE  

**Options:**  
- inventory\_files (`-i`, `--inventory-file`) - Inventory file used to fill the template. Can be used multiple times.  
- help (`--help`) - Show this message and exit.  

### delete
Delete Step with STEP\_ID saved in Cryton.

STEP\_ID is ID of the Step you want to delete.

**Arguments:**  
- STEP\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### execute
Execute Step with STEP\_ID under Stage execution with STAGE\_EXECUTION\_ID.

STEP\_ID is ID of the Step you want to execute.

STAGE\_EXECUTION\_ID is an ID of the Stage execution you want to set as a parent of the Step execution.

**Arguments:**  
- STEP\_ID  
- STAGE\_EXECUTION\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Steps in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parent (`-p`, `--parent`) - Filter Steps using Stage ID.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### show
Show Step with STEP\_ID saved in Cryton.

STEP\_ID is ID of the Step you want to see.

**Arguments:**  
- STEP\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  

### validate
Validate (syntax check) your FILE with Step.

FILE is path/to/your/file that you want to validate.

**Arguments:**  
- FILE  

**Options:**  
- inventory\_files (`-i`, `--inventory-file`) - Inventory file used to fill the template. Can be used multiple times.  
- help (`--help`) - Show this message and exit.  

## workers
Manage Workers from here.


**Options:**  
- help (`--help`) - Show this message and exit.  

### create
Create new Worker with NAME and save it into Cryton.

NAME of your Worker (will be used to match your Worker). For example: "MyCustomName".

**Arguments:**  
- NAME  

**Options:**  
- description (`-d`, `--description`) - Description of your Worker (wrap in "").  
- force (`-f`, `--force`) - Ignore, if Worker with the same parameter 'name' exists.  
- help (`--help`) - Show this message and exit.  

### delete
Delete Worker with WORKER\_ID saved in Cryton.

WORKER\_ID is ID of the Worker you want to delete.

**Arguments:**  
- WORKER\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### health-check
Check if Worker with WORKER\_ID saved in Cryton is online.

WORKER\_ID is ID of the Worker you want to check.

**Arguments:**  
- WORKER\_ID  

**Options:**  
- help (`--help`) - Show this message and exit.  

### list
List existing Workers in Cryton.


**Options:**  
- less (`--less`) - Show less like output.  
- offset (`-o`, `--offset`) - The initial index from which to return the results.  
- limit (`-l`, `--limit`) - Number of results to return per page.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- parameter\_filters (`-f`, `--filter`) - Filter results using returned parameters (for example `id=1`, `name=test`, etc.).  
- help (`--help`) - Show this message and exit.  

### show
Show Worker with WORKER\_ID saved in Cryton.

WORKER\_ID is ID of the Worker you want to see.

**Arguments:**  
- WORKER\_ID  

**Options:**  
- less (`--less`) - Show less like output.  
- localize (`--localize`) - Convert UTC datetime to local timezone.  
- help (`--help`) - Show this message and exit.  
