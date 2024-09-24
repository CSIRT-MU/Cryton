from datetime import datetime

# Main queue constants
ACTION = "action"
CORRELATION_ID = "correlation_id"
DATA = "data"
RESULT_PIPE = "result_pipe"
QUEUE_NAME = "queue_name"
PROPERTIES = "properties"
HIGH_PRIORITY = 0
MEDIUM_PRIORITY = 1
LOW_PRIORITY = 2

# Processor action types
ACTION_KILL_TASK = "_kill_task"
ACTION_FINISH_TASK = "_finish_task"
ACTION_ADD_TRIGGER = "_add_trigger"
ACTION_REMOVE_TRIGGER = "_remove_trigger"
ACTION_LIST_TRIGGERS = "_list_triggers"
ACTION_SEND_MESSAGE = "_send_message"
ACTION_SHUTDOWN_THREADED_PROCESSOR = "shutdown_threaded_processor"

# Event types
EVENT_VALIDATE_MODULE = "VALIDATE_MODULE"
EVENT_LIST_MODULES = "LIST_MODULES"
EVENT_LIST_SESSIONS = "LIST_SESSIONS"
EVENT_KILL_STEP_EXECUTION = "KILL_STEP_EXECUTION"
EVENT_HEALTH_CHECK = "HEALTH_CHECK"
EVENT_ADD_TRIGGER = "ADD_TRIGGER"
EVENT_REMOVE_TRIGGER = "REMOVE_TRIGGER"
EVENT_TRIGGER_STAGE = "TRIGGER_STAGE"
EVENT_LIST_TRIGGERS = "LIST_TRIGGERS"

# Listener types
HTTP = "HTTP"
MSF = "MSF"

# Listener constants
IDENTIFIERS = "identifiers"
LISTENER_HOST = "host"
LISTENER_PORT = "port"
TRIGGER_TYPE = "trigger_type"
LISTENER_STAGE_EXECUTION_ID = "stage_execution_id"
TRIGGER_PARAMETERS = "parameters"
TRIGGER_ID = "trigger_id"

# RabbitMQ message keywords
EVENT_T = "event_t"
EVENT_V = "event_v"
DEFAULT_MSG_PROPERTIES = {"content_encoding": "utf-8", "timestamp": datetime.now()}
TARGET_IP = "target_ip"
SESSION_LIST = "session_list"
MODULE_LIST = "module_list"
TRIGGER_LIST = "trigger_list"
ACK_QUEUE = "ack_queue"

MODULE = "module"
ARGUMENTS = "arguments"

# Other constants
RESULT = "result"
OUTPUT = "output"
SERIALIZED_OUTPUT = "serialized_output"
CODE_ERROR = "error"
CODE_OK = "ok"
CODE_KILL = "terminated"
FILE = "file"
FILE_CONTENT = "file_content"
FILE_ENCODING = "file_encoding"
BASE64 = "base64"
UTF8 = "utf8"
REPLY_TO = "reply_to"
