Please use a concise and self-explanatory title. Examples:

* Steps that can't find the required session are ignored
* Added real-world pivoting examples
* Fix pyyaml not supporting pep 517 builds

### What does this MR do and why?

Describe in detail what your merge request does and why.

Please keep this description updated with any discussion that takes place so
that reviewers can understand your intent. Keeping the description updated is
especially important if they haven't participated in the discussion.

%{first_multiline_commit}

Make sure to link the related issues and merge requests.

### Changes

A list of changes. Please use an ordered list.

In case of UI changes, please provide screenshots.

If the changes affect **other components**, use the `changes-incompatible` label (**remove otherwise**):

/label changes-incompatible

If the changes break **backward compatibility** (API for example), use the `changes-breaking` label (**remove otherwise**):

/label changes-breaking

### How to set up and validate locally

Please, provide numbered steps on how to set up and validate the changes. It can be similar to the way you've tested the changes. 

In case the changes affect other applications, include them in the example.

Example below:

1. Check out the MR branch and install the application using Poetry (make sure the prerequisites are running)
    ```
    git checkout my-branch
    poetry install
    cryton-core start
    ```
2. Clone CLI, check out to the related MR branch and install the application using Poetry
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

### MR acceptance checklist

This checklist encourages us to confirm any changes have been analyzed to reduce risks in quality, performance, reliability, security, and maintainability.

* [ ] I have tested the changes work.
* [ ] I have cleaned up my code.
* [ ] I have added/updated the [application tests](https://cryton.gitlab-pages.ics.muni.cz/cryton-documentation/latest/contribution-guide/#writing-tests).
* [ ] I have updated the documentation (opened an MR in the documentation project).
* [ ] If the changes affect other projects, I have created additional MR in the affected projects.
* [ ] I have run End-to-End tests.

Please, assign a reviewer, labels, and possibly a milestone.

/assign me
