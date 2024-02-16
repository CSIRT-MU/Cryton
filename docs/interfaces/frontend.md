Cryton Frontend provides functionality for interacting with Cryton Core more easily and clearly than by using CLI.

By default, the Frontend is served at [http://localhost:8080/](http://localhost:8080/){target="_blank"}.

Use the in-app help pages to learn about usage.

## Features

[//]: # (TODO: make a video, maybe for each feature? or just use timestamps in the video)

### Listing data
You can list all Cryton data by using list pages in the navigation bar. Most important data can be found directly in 
the dashboard. Each data table provides functionality for sorting and filtering data.

### Creating objects
You can create workers, templates, instances, and runs by using create pages in the navigation bar. Every object can be 
also deleted from its list page.

### Template creation
You can create plan templates in the **Plan templates > Create template**. The whole creation process is documented 
in-app with an introduction page and additional help pages for every creation step.

### Run interaction
The front end provides 2 ways to interact with runs. There is a quick interaction menu that you can access in 
**Runs > List runs** by clicking on a run. The interaction menu will expand under the run. Another way is to click 
on the eye icon next to the run which will take you to the run's page. There you can also view the current state of the run 
and its sub-parts, and modify the execution variables for each execution.

#### Execution timeline
You can view timelines of the run's executions by clicking on the clock icon next to a run on the list runs page or by 
clicking on the **show timeline** button on the run's page. The timeline shows the start, pause and finish times of the whole 
execution, stages, and steps. More details can be found in an in-app help page found inside the timeline tab.

### Theming
The front end provides two color themes - light and dark. You can switch between them with a toggle button in the top bar.

## Settings

[//]: # (TODO: settings aren't changeable, needs to be fixed in the docker image)

Cryton Frontend uses environment variables for its settings. Please update them to your needs.

!!! warning "Notice"

    For now, settings can be changed only for the [npm installation](../development/frontend.md#installation).  
    However, it is possible to update the API host and port at runtime at 
    [http://localhost:8080/app/user/settings](http://localhost:8080/app/user/settings){target="_blank"}.

Variables can be found in `src/environments/`. For production modify the _environment.prod.ts_ file, else modify the _environment.ts_ file.

#### crytonRESTApiHost 
Cryton Core's API address.

| value  | default   | example          |
|--------|-----------|------------------|
| string | 127.0.0.1 | cryton-core.host |

#### crytonRESTApiPort
Cryton Core's API port.

| value | default | example |
|-------|---------|---------|
| int   | 8000    | 8008    |

#### refreshDelay
Sets artificial delay in milliseconds for refresh API requests.

??? question "What is this for?"

    Users usually react better if the requests don't happen instantly, but they can see a tiny bit of loading. 
    Initial API request doesn't use delay, this is only for refreshing data

| value | default | example |
|-------|---------|---------|
| int   | 300     | 500     |

#### useHttps
Use SSL to connect to REST API.

| value   | default | example |
|---------|---------|---------|
| boolean | false   | true    |
