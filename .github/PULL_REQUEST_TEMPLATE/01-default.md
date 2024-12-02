<!--
Please use a concise and self-explanatory title. Examples:

* Ignore Steps that can't find the required session
* Added real-world pivoting example
* Fix pyyaml not supporting pep 517 builds
-->

### What does this PR do and why?

<!--
Describe in detail what your pull request does and why. Make sure to link the related issues and pull requests.

Please keep this description updated with any discussion.
-->

### Changes

<!--
A list of changes. Please use an ordered list.

In case of UI changes, please provide screenshots.
-->

### How to set up and validate locally

<!--
Please, provide numbered steps on how to set up and validate the changes. It can be similar to the way you've tested the changes. 

In case the changes affect other applications, include them in the example.

Example below:

1. Check out the PR branch and install the application using Poetry (make sure the prerequisites are running)
    ```
    git checkout my-branch
    poetry install
    cryton-core start
    ```
2. Clone CLI, check out to the related PR branch and install the application using Poetry
    ```
    git clone https://gitlab.ics.muni.cz/cryton/cryton-cli.git
    git checkout my-related-branch
    poetry install
    ```
3. Check if the new `runs execute` command makes sure the Workers are up and modules are valid before the execution
    ```
    cryton-cli runs execute 1
    ```
4. You should see the following output
    ```
    Workers are up.
    Modules are valid.
    Run successfully executed!
    ```
-->

### Acceptance checklist

This checklist encourages us to confirm any changes have been analyzed to reduce risks in quality, performance, reliability, security, and maintainability.

* [ ] I have tested the changes work.
* [ ] I have run [End-to-End tests](https://cryton.gitlab-pages.ics.muni.cz/latest/development/#e2e).
* [ ] I have cleaned up my code.
* [ ] I have updated the [tests](https://cryton.gitlab-pages.ics.muni.cz/latest/development/#writing-tests).
* [ ] I have updated the documentation.
* [ ] The changes affect other projects (frontend, ansible roles, etc.).
* [ ] The change is not backwards compatible

<!-- Please, assign a reviewer, labels, and possibly a milestone. -->
