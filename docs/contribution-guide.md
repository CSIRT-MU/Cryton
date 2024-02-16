## Fixing and reporting bugs
Any identified bugs should be posted as an issue in the respective [gitlab repository](https://gitlab.com/cryton-toolset){target="_blank"}. 
Please, include as much detail as possible for the developers, to be able to reproduce the erroneous behavior.

!!! warning ""

    Before you create an issue, make sure it doesn't exist yet.

!!! warning ""

    If the issue exists in the [official Gitlab repository](https://gitlab.ics.muni.cz/cryton){target="_blank"}, please mention it in your issue.

## Contributing code
To support project development check out the development instructions:

- [Core](development/core.md)
- [Worker](development/worker.md)
- [Modules](development/modules.md)
- [CLI](development/cli.md)
- [Frontend](development/frontend.md)

## Contribution guidelines

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
- Each class should be patched to use the test logger if possible ([Core](logging.md#core); [worker](logging.md#worker))
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

## Documentation

### CLI documentation generation
Install Cryton CLI and run `cryton-cli generate-docs doc.md`

### Marking changes/new features
Use the following to mark a new feature:
```markdown
[:octicons-tag-24: 2.1.0]({{{ releases.cryton }}}2.1.0){target="_blank"}
```

### Core REST API documentation generation

- Install the [swagger-markdown tool](https://www.npmjs.com/package/swagger-markdown){target="_blank"}
- Download the schema from [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/){target="_blank"}
- Run `swagger-markdown -i path/to/swagger-schema.yml`.

### Useful links

- [MkDocs Wiki](https://github.com/mkdocs/mkdocs/wiki){target="_blank"} (Third-party themes, recipes, plugins and more)
- [Best-of-MkDocs](https://github.com/pawamoy/best-of-mkdocs){target="_blank"} (Curated list of themes, plugins and more)

### Known issues
Using the variable `config.site_url` on localhost will provide a complete and correct path. However, we are using mike for versioning and
the variable on the production deployment will miss a slash (`/`) at the end.