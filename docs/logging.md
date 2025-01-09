Logs are created only for Hive and Worker and stored in **[APP_DIRECTORY](settings.md)/logs**. In case you are running in a Docker, they are displayed in the stdout.

The logs adhere to the following format:
```
{"channel_consumer_count": 7, "event": "Starting channel consumers", "logger": "cryton-worker", "level": "debug", "timestamp": "2025-01-07T11:18:53.922221Z"}
{"event": "Opening a new Channel", "level": "debug", "logger": "amqpstorm.connection", "timestamp": "2025-01-07 11:18:53"}
```

## loggers

### Production
Informational Cryton logs and higher are logged into a log file. In case you are running in a Docker, the logs are displayed to the console as well.

Step's output is not included in the logs, it can be found in the database/CLI/Frontend.

This is the default logger.

### Debug
All logs (even from other loggers) are logged into a log file and console. It also logs the Step's output.

To enable the debug logger, update the [Hive](settings.md#debug) or [Worker](settings.md#debug_1) settings.
