It is possible to install Cryton using ansible. We will only cover basics and installation on a single machine.

All roles with more information can be found [here](https://gitlab.ics.muni.cz/cryton/ansible){target="_blank"}.

## Quick-start
First, we have to create `inventory.yml` file:

??? abstract "Show the inventory.yml file"

    ```yaml
    {! include "./inventory.yml" !}
    ```

Now, create `playbook.yml` file and copy one of the following examples:

??? abstract "Show the playbook.yml example (preferred installation is using pip)"

    ```yaml
    {! include "./playbook-pip.yml" !}
    ```

??? abstract "Show the playbook.yml example (preferred installation is using Docker)"

    ```yaml
    {! include "./playbook-docker.yml" !}
    ```

Once we have created `playbook.yml` and `inventory.yml`, we can install the [requirements](https://galaxy.ansible.com/docs/using/installing.html){target="_blank"} and run the playbook.
