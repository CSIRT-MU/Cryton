# Usage

Before starting the applications, make sure to check out the [settings](../settings.md) page.  
In case of a misconfiguration the application may not start or Worker and Hive may not communicate. If that happens check the command output or [logs](../logging.md).

## Hive
Use the following to invoke the application:
```shell
cryton-hive
```

You should see a help page:
```
Usage: cryton-hive [OPTIONS] COMMAND [ARGS]...

  Cryton Hive.

Options:
  ...
```

To learn about each command's options use:
```shell
cryton-hive <your command> --help
```

To migrate the database and start the application use:
```shell
cryton-hive start --migrate-database
```

REST API is by default running at [http://0.0.0.0:8000](http://0.0.0.0:8000){target="_blank"} (interactive documentation at [http://0.0.0.0:8000/doc](http://0.0.0.0:8000/doc){target="_blank"}).

To serve the REST API on a different host/port, use the `--bind` option:
```shell
cryton-hive start --bind <address>:<port>
```

??? tip "Run it in the background"

    Use the `nohup` command:
    ```shell
    nohup cryton-hive start > /tmp/hive_std_out 2>&1 &
    ```

    To **stop** it, find its processes and kill them:
    ```shell
    ps -aux | grep cryton-hive
    kill <PID> <PID>
    ```

## Worker
Use the following to invoke the application:
```shell
cryton-worker
```

You should see a help page:
```
Usage: cryton-worker [OPTIONS] COMMAND [ARGS]...

  Cryton Worker.

Options:
  ...
```

To learn about each command's options use:
```shell
cryton-worker <your command> --help
```

To start the Worker use:
```shell
cryton-worker start
```

??? tip "Run it in the background"

    Use the `nohup` command:
    ```shell
    nohup cryton-worker start > /tmp/worker_std_out 2>&1 &
    ```

    To **stop** it, find its processes and kill them:
    ```shell
    ps -aux | grep cryton-worker
    kill <PID> <PID>
    ```

## CLI
Use the following command to invoke the application:
```shell
cryton-cli
```

You should see a help page:
```
Usage: cryton-cli [OPTIONS] COMMAND [ARGS]...

  Wrapper for Hive's REST API.

Options:
  ...
```

To learn about each command's options use:
```shell
cryton-cli <your command> --help
```
