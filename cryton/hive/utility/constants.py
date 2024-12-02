# types
RETURN_VALUE = "return_value"
RESULT = "result"
STATE = "state"
OUTPUT = "output"
SERIALIZED_OUTPUT = "serialized_output"
ANY = "any"

# Types with allowed regex
REGEX_TYPES = [OUTPUT, SERIALIZED_OUTPUT]

# Step main args
ARGUMENTS = "arguments"
MODULE = "module"
NEXT = "next"

# Session system keywords
SESSION_ID = "session_id"

# Stage trigger types
DELTA = "delta"
TIME = "time"
HTTP = "http"
METASPLOIT = "metasploit"

# RabbitMQ message keywords
EVENT_T = "event_t"
EVENT_V = "event_v"
ACK_QUEUE = "ack_queue"
REPLY_TO = "reply_to"

# Other constants
EVENT_ACTION = "action"
TRIGGER_TYPE = "trigger_type"
TRIGGER_ID = "trigger_id"

# Plan settings constants
SEPARATOR = "separator"
SEPARATOR_DEFAULT_VALUE = "."

# Event types
EVENT_VALIDATE_MODULE = "VALIDATE_MODULE"
EVENT_STOP_STEP_EXECUTION = "STOP_STEP_EXECUTION"
EVENT_HEALTH_CHECK = "HEALTH_CHECK"
EVENT_ADD_TRIGGER = "ADD_TRIGGER"
EVENT_REMOVE_TRIGGER = "REMOVE_TRIGGER"
EVENT_TRIGGER_STAGE = "TRIGGER_STAGE"
EVENT_STEP_EXECUTION_ERROR = "STEP_EXECUTION_ERROR"
EVENT_UPDATE_SCHEDULER = "UPDATE_SCHEDULER"

# Scheduler
ADD_REPEATING_JOB = "add_repeating_job"
ADD_JOB = "add_job"
REMOVE_JOB = "remove_job"
RESUME_SCHEDULER = "resume_scheduler"
PAUSE_SCHEDULER = "pause_scheduler"
GET_JOBS = "get_jobs"
RESUME_JOB = "resume_job"
PAUSE_JOB = "pause_job"
RESCHEDULE_JOB = "reschedule_job"

# Datetime formats
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
TIME_FORMAT_DETAILED = "%Y-%m-%dT%H:%M:%S.%fZ"

# Logger types
LOGGER_CRYTON_PRODUCTION = "cryton-hive"
LOGGER_CRYTON_DEBUG = "cryton-hive-debug"
LOGGER_CRYTON_TESTING = "cryton-hive-testing"
VALID_CRYTON_LOGGERS = [LOGGER_CRYTON_TESTING, LOGGER_CRYTON_DEBUG, LOGGER_CRYTON_PRODUCTION]

# Jinja regex values
BLOCK_START_STRING = "'{%"
BLOCK_END_STRING = "%}'"
VARIABLE_START_STRING = "'{{"
VARIABLE_END_STRING = "}}'"
COMMENT_START_STRING = "'{#"
COMMENT_END_STRING = "#}'"
