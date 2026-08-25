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
ACTION_STOP_TASK = "_stop_task"
ACTION_FINISH_TASK = "_finish_task"
ACTION_ADD_TRIGGER = "_add_trigger"
ACTION_REMOVE_TRIGGER = "_remove_trigger"
ACTION_SEND_MESSAGE = "_send_message"
ACTION_SHUTDOWN_THREADED_PROCESSOR = "shutdown_threaded_processor"

# Event types
EVENT_TRIGGER_STAGE = "TRIGGER_STAGE"

# Listener constants
IDENTIFIERS = "identifiers"
LISTENER_HOST = "host"
LISTENER_PORT = "port"
TRIGGER_TYPE = "trigger_type"
TRIGGER_PARAMETERS = "parameters"
TRIGGER_ID = "trigger_id"

# RabbitMQ message keywords
EVENT_T = "event_t"
EVENT_V = "event_v"
DEFAULT_MSG_PROPERTIES = {"content_encoding": "utf-8", "timestamp": datetime.now()}
ACK_QUEUE = "ack_queue"

MODULE = "module"
ARGUMENTS = "arguments"

# Other constants
RESULT = "result"
OUTPUT = "output"
CODE_ERROR = "error"
CODE_OK = "ok"
REPLY_TO = "reply_to"
