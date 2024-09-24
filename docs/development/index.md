# Development

## Environment setup
First, we have to set up the development environment. This is done using Poetry.

!!! danger "Requirements"

    - [Python](https://www.python.org/about/gettingstarted/){target="_blank"} >={{{ python.min }}},<{{{ python.max }}}
    - [Poetry](https://python-poetry.org/docs/#installation){target="_blank"}
    - [Docker Compose](https://docs.docker.com/compose/install/){target="_blank"}

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton.git
```

Go to the correct directory:
```shell
cd cryton
```

Start the prerequisites:
```shell
docker compose -f docker-compose.prerequisites.yml up -d
```

??? tip "Clean up and rebuild the prerequisites"

    !!! warning

        The following commands removes all images and volumes. Make sure you know what you're doing!

    ```
    docker compose -f docker-compose.prerequisites.yml down -t 0 && docker system prune --all --force && docker volume prune --all --force && docker compose -f docker-compose.prerequisites.yml up -d 
    ```

??? tip "Unable to access the database with Pycharm"

    To be able to access the DB through the PgBouncer, add the following variable to the service definition in the Compose configuration: 
    
    `PGBOUNCER_IGNORE_STARTUP_PARAMETERS: extra_float_digits`.

Install Cryton:
```shell
poetry install --all-extras --with docs
```

To spawn a shell use:
```shell
poetry shell
```

## Usage
Run Hive:
```shell
poetry run cryton-hive start --migrate-database
```

Run Worker:
```shell
poetry run cryton-worker start
```

Run CLI:
```shell
poetry run cryton-cli
```

[Link to the usage](../usage/index.md).

## Testing

### Pytest
```shell
pytest --cov=cryton tests/unit/ --cov-config=.coveragerc-unit --cov-report html
```

```shell
pytest --cov=cryton tests/integration/ --cov-config=.coveragerc-integration --cov-report html
```

???+ "Run specific test" 

    ```shell
    pytest my_test_file.py::MyTestClass::my_test
    ```

### tox
Use in combination with [pyenv](https://github.com/pyenv/pyenv){target="_blank"}.

```shell
tox -- tests/unit/ --cov=cryton --cov-config=.coveragerc-unit
```

```shell
tox -- tests/integration/ --cov=cryton --cov-config=.coveragerc-integration
```

Use the provided [`ci-python` image](#ci-python) to get an isolated environment.

### E2E
E2E tests will test Hive, Worker, and CLI together.

Build playground with E2E tests ready:
```shell
docker compose -f docker-compose.yml -f docker-compose.playground.yml -f docker-compose.dev.yml -f docker-compose.e2e.yml up -d --build
```

Enter the CLI container:
```shell
docker exec -it cryton-cli bash
```

Run the tests:
```shell
/app/.venv/bin/python /app/tests_e2e/cli.py run-tests
```

??? note "Possible tests"

    - `basic`
    - `advanced`
    - `control`
    - `empire`
    - `http_trigger`
    - `msf_trigger`
    - `datetime_trigger`
    - `all`

## Django related

## Custom script setup with Django
```python
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cryton.hive.settings")
import django
django.setup()
```

### Apply migrations
```
cryton-hive migrate
```

### Generate migrations
```
cryton-hive makemigrations cryton_app
```

## Build a Docker image
If you want to build a custom Docker image, clone the repository, and go into it:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton.git
cd cryton
```

Build the image:
```shell
docker build --tag <image-tag> --target production --file <dockerfile> .
```

## Documentation
Serve the documentation locally:
```shell
mkdocs serve -a localhost:8002
```

### Generate CLI documentation
Install Cryton CLI and run `cryton-cli generate-docs doc.md`.

### Generate template JSON schema
Install Cryton Hive and run `cryton-hive generate-schema`.

### Marking changes/new features
Use the following to mark a new feature:
```markdown
[:octicons-tag-24: 2.1.0]({{{ releases.cryton }}}2.1.0){target="_blank"}
```

### REST API documentation generation

* Install the [swagger-markdown tool](https://www.npmjs.com/package/swagger-markdown){target="_blank"}
* Download the schema from [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/){target="_blank"}
* Run `swagger-markdown -i path/to/swagger-schema.yml`.

### Useful links

- [MkDocs Wiki](https://github.com/mkdocs/mkdocs/wiki){target="_blank"} (Third-party themes, recipes, plugins and more)
- [Best-of-MkDocs](https://github.com/pawamoy/best-of-mkdocs){target="_blank"} (Curated list of themes, plugins and more)

### Known issues
Using the variable `config.site_url` on localhost will provide a complete and correct path. However, we are using mike for versioning and the variable on the production deployment will miss a slash (`/`) at the end.

## Guidelines

[//]: # (TODO: update)

### Used technology versions
Make sure the tools' versions we use are supported:

- https://www.postgresql.org/support/versioning/
- https://devguide.python.org/versions/

### Writing tests
This guide simplifies and pinpoints the most important points.

For in-app testing, we are using unit/integration tests written using the *Pytest* library.

Unit tests are meant to test a specific method/function in an isolated environment (using mocking) while 
the integration tests check if a unit (method/function) can run even without being isolated. End-to-end tests are 
testing if all the functionality works across the whole Cryton toolset.

- Settings for Pytest can be found in a *pyproject.toml* file
- Tests (that test the same code part/class) are grouped using classes
- Each class that works with the Django DB has to be marked with `@pytest.mark.django_db`
- Each class should be patched to use the test logger if possible ([Core](../logging.md#core); [worker](../logging.md#worker))
- Unit tests shouldn't interact with the DB. 
- Use the `model_bakery` library instead of mocking the DB interactions for the integration tests
- For easier mocking, each test class should have a `path` class variable. If we are testing a class 
in `path/to/module.py`, then the *path* variable will be `path = "path.to.module"`. To mock we simply use 
`mocker.patch(self.path + ".<method_to_mock>")`.
- We are using the *mocker* library instead of the *unittest.mock.Mock*.
- Each test method starts with the `test_` prefix.
- Each fixture method starts with the `f_` prefix.
- When using parametrize, the created parameters must have the `p_` prefix.

A test should follow the following structure.
```python
import pytest

class TestUnitName:
    path = "path.to.patch.MyClass"

    @pytest.fixture
    def f_to_patch(self, mocker):
        return mocker.patch(f"{self.path}.to_patch")

    @pytest.mark.parametrize(
        "p_to_parametrize",
        [
        ]
    )
    def test_to_test(self, f_to_patch, p_to_parametrize):
        # Arrange - set everything needed for the test

        # Mock - mock everything needed to isolate your test

        # Act - trigger your code unit

        # Assert - assert the outcome is exactly as expected to avoid any unpleasant surprises later
        pass
```

## Docker images

### production-base
Image used for building Python applications.

Build it:
```shell
docker build --tag registry.gitlab.ics.muni.cz:443/cryton/cryton/production-base:$(git rev-parse HEAD) --tag registry.gitlab.ics.muni.cz:443/cryton/cryton/production-base:latest docker/production-base/
```

Push it:
```shell
docker push --all-tags registry.gitlab.ics.muni.cz:443/cryton/cryton/production-base
```

### ci-python
To get the same environment as in the CI/CD pipeline, use the provided `ci-python` image.

Build it:
```shell
docker build --tag registry.gitlab.ics.muni.cz:443/cryton/cryton/ci-python:$(git rev-parse HEAD) --tag registry.gitlab.ics.muni.cz:443/cryton/cryton/ci-python:latest docker/ci-python/
```

Push it:
```shell
docker push --all-tags registry.gitlab.ics.muni.cz:443/cryton/cryton/ci-python
```
