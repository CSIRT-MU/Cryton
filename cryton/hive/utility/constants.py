# types
RETURN_VALUE = 'return_value'
RESULT = 'result'
OUTPUT = 'output'
SERIALIZED_OUTPUT = 'serialized_output'
ANY = 'any'

# Types with allowed regex
REGEX_TYPES = [OUTPUT, SERIALIZED_OUTPUT]

# Step main args
ARGUMENTS = 'arguments'
STEP_TYPE = 'step_type'
NEXT = "next"

# Arguments for step type worker/execute and empire/execute module
MODULE = 'module'
MODULE_ARGUMENTS = 'module_arguments'

# Arguments for step type deploy-agent
LISTENER_NAME = 'listener_name'
LISTENER_PORT = 'listener_port'
LISTENER_OPTIONS = 'listener_options'
LISTENER_TYPE = 'listener_type'
STAGER_TYPE = 'stager_type'
STAGER_OPTIONS = 'stager_options'
AGENT_NAME = 'agent_name'

# Arguments for step type empire/execute
USE_AGENT = 'use_agent'
SHELL_COMMAND = 'shell_command'

# Session system keywords
SESSION_ID = 'session_id'
CREATE_NAMED_SESSION = 'create_named_session'
USE_NAMED_SESSION = 'use_named_session'
USE_ANY_SESSION_TO_TARGET = 'use_any_session_to_target'
SSH_CONNECTION = 'ssh_connection'

# Step types
STEP_TYPE_WORKER_EXECUTE = 'worker/execute'
STEP_TYPE_DEPLOY_AGENT = 'empire/agent-deploy'
STEP_TYPE_EMPIRE_EXECUTE = 'empire/execute'
STEP_TYPES_LIST = [STEP_TYPE_WORKER_EXECUTE, STEP_TYPE_DEPLOY_AGENT, STEP_TYPE_EMPIRE_EXECUTE]

# Stage trigger types
DELTA = 'delta'
DATETIME = 'datetime'
HTTP_LISTENER = 'HTTPListener'
MSF_LISTENER = 'MSFListener'

# Successor related
VALID_SUCCESSOR_TYPES = [RESULT, ANY, SERIALIZED_OUTPUT, OUTPUT]
SUCCESSOR_TYPES_WITHOUT_ANY = [RESULT, SERIALIZED_OUTPUT, OUTPUT]

# RabbitMQ message keywords
EVENT_T = "event_t"
EVENT_V = "event_v"
ACK_QUEUE = "ack_queue"
REPLY_TO = "reply_to"

# Other constants
EVENT_ACTION = 'action'
TRIGGER_TYPE = "trigger_type"
TRIGGER_ID = "trigger_id"

# Plan settings constatnts
SEPARATOR = 'separator'
SEPARATOR_DEFAULT_VALUE = '.'

# Event types
EVENT_VALIDATE_MODULE = "VALIDATE_MODULE"
EVENT_LIST_MODULES = "LIST_MODULES"
EVENT_LIST_SESSIONS = "LIST_SESSIONS"
EVENT_KILL_STEP_EXECUTION = "KILL_STEP_EXECUTION"
EVENT_HEALTH_CHECK = "HEALTH_CHECK"
EVENT_ADD_TRIGGER = "ADD_TRIGGER"
EVENT_REMOVE_TRIGGER = "REMOVE_TRIGGER"
EVENT_TRIGGER_STAGE = "TRIGGER_STAGE"
EVENT_STEP_EXECUTION_ERROR = "STEP_EXECUTION_ERROR"
EVENT_UPDATE_SCHEDULER = 'UPDATE_SCHEDULER'

# Scheduler
ADD_REPEATING_JOB = 'add_repeating_job'
ADD_JOB = 'add_job'
REMOVE_JOB = 'remove_job'
RESUME_SCHEDULER = 'resume_scheduler'
PAUSE_SCHEDULER = 'pause_scheduler'
GET_JOBS = 'get_jobs'
RESUME_JOB = 'resume_job'
PAUSE_JOB = 'pause_job'
RESCHEDULE_JOB = 'reschedule_job'

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
