## Installation

!!! danger "Requirements"

    - [npm](https://nodejs.org/en/){target="_blank"}

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

    Use `ng serve` only for development/testing. In a real production environment use either Docker installation or a production build deployed on a production-ready web server (for example Nginx).

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
If you want to build a Docker image, switch to the correct directory:
```shell
cd cryton-frontend
```

Build the image:
```shell
docker build -t <image-name> .
```

Test it:
```shell
docker run -p 127.0.0.1:8080:80 --rm <image-name>
```
