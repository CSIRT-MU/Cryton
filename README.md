![Coverage](https://gitlab.ics.muni.cz/cryton/cryton/badges/master/coverage.svg)

[//]: # (TODO: add badges for python versions, black, pylint, flake8, unit tests, integration tests)

# Cryton
Advanced (attack) orchestrator and scheduler.

Cryton toolset is tested and targeted primarily on **Debian** and **Kali Linux**. Please keep in mind that **only 
the latest version is supported** and issues regarding different OS or distributions may **not** be resolved.

For more information see the [documentation](https://cryton.gitlab-pages.ics.muni.cz/).

## Quick-start
Installation:
```shell
poetry install -E hive -E worker -E cli
```

Run it:
```shell
poetry run cryton-worker start
poetry run cryton-hive start
poetry run cryton-cli
```

## Contributing
Contributions are welcome. Please **contribute to the [project mirror](https://gitlab.com/cryton-toolset/cryton)** on gitlab.com.
For more information see the [contribution page](https://cryton.gitlab-pages.ics.muni.cz/cryton-documentation/latest/contribution-guide/).
