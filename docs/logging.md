Logs are created only for Hive and Worker and stored in **[APP_DIRECTORY](settings.md)/logs**. In case you are running in a Docker, they are displayed in the stdout.

The logs adhere to the following format:
```
{"queue": "cryton_core.control.request", "event": "Queue declared and consuming", "logger": "cryton", "level": "info", "timestamp": "2021-05-18T11:19:20.012152Z"}
{"plan_name": "Example scenario", "plan_id": 129, "event": "plan created", "logger": "cryton", "level": "info", "timestamp": "2021-05-18T06:17:39.753017Z"}
```

## loggers

### Production
Informational logs and higher are logged into a log file. In case you are running in a Docker, the logs are displayed to the console as well.

Step's output is not included in the logs, it can be found in the database/CLI/Frontend.

This is the default logger.

### Debug
All logs are logged into a log file and console. It also logs the Step's output.

To enable the debug logger, update the [Hive](settings.md#debug) or [Worker](settings.md#debug_1) settings.

### Testing
All logs are logged into a console. It also logs the Step's output.

The logger is enabled only for testing.
