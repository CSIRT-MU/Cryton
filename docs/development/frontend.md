## Installation

!!! danger "Requirements"

    - [npm](https://nodejs.org/en/){target="_blank"}

!!! tip "Recommendations"

    - Override the [settings](../components/frontend.md#settings)

Clone the repository:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-frontend.git
cd cryton-frontend
```

Install the dependencies:
```shell
npm install
```

Serve the app:
=== "Testing"

    ```shell
    ng serve --port 8080
    ```

=== "Production"

    ```shell
    ng serve --prod --port 8080
    ```

!!! warning ""

    Use `ng serve` only for development/testing. In a real production environment use either Docker (compose) installation or a
    production build deployed on a production-ready web server (for example Nginx).

??? info "Build the app"

    You can find the build in the **/dist** folder.
    
    === "Testing"
    
        ```shell
        npm run build
        ```
    
    === "Production"
    
        ```shell
        npm run build-prod
        ```

## Usage
Start a development server:
```shell
npm start
```

The app will refresh itself when the project changes.

!!! note "We use Husky to run pre-commit hooks"

    - Code formatting with Prettier.
    - Linting with ESLint.
    - Running unit tests with Karma.

## Build a Docker image
If you want to build a custom Docker image, clone the repository, and switch to the correct directory:
```shell
git clone https://gitlab.ics.muni.cz/cryton/cryton-frontend.git
cd cryton-frontend
```

Build the image:
```shell
docker build -t custom-frontend-image .
```

Test your docker image:
```shell
docker run -p 127.0.0.1:8080:80 --rm custom-frontend-image
```
