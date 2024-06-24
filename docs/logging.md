The logs adhere to the following format:
```
{"queue": "cryton_core.control.request", "event": "Queue declared and consuming", "logger": "cryton-debug", "level": "info", "timestamp": "2021-05-18T11:19:20.012152Z"}
{"plan_name": "Example scenario", "plan_id": 129, "status": "success", "event": "plan created", "logger": "cryton", "level": "info", "timestamp": "2021-05-18T06:17:39.753017Z"}
```

Logs are stored in the *application directory*, which can be found at `~/.local/cryton/` by default (`/app/` inside Docker).

## Core
Every change of state is logged for later analysis. Every Step the result is also logged, although 
the output is not. It can be found in the database.

You can switch between the debug and the production loggers by changing the [settings](settings.md#debug). 
To run tests, we use a testing logger to avoid saving unwanted logs.

**Production** (`cryton-hive`)

- RotatingFileHandler (*APP_DIRECTORY*/log/cryton-hive.log)

**Debug** (`cryton-hive-debug`)

- RotatingFileHandler (*APP_DIRECTORY*/log/cryton-hive.log)
- Console (std_out)

**Testing** (`cryton-hive-test`)

- Console (std_out)

## Worker
Each request and its processing are logged for later analysis.

You can switch between the debug and the production loggers by changing the [settings](settings.md#debug_1). 
To run tests, we use a testing logger to avoid saving unwanted logs.

**Production** (`cryton-worker`)

- RotatingFileHandler (*APP_DIRECTORY*/log/cryton-worker.log)

**Debug** (`cryton-worker-debug`)

- RotatingFileHandler (*APP_DIRECTORY*/log/cryton-worker.log)
- Console (std_out)

**Testing** (`cryton-worker-test`)

- Console (std_out)
