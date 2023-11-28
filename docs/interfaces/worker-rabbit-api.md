Worker utilizes [RabbitMQ](https://www.rabbitmq.com/){target="_blank"} as it's messaging protocol for asynchronous RPC.

## Rabbit API
Worker is able to process any request sent through RabbitMQ to its Queues (`cryton_worker.WORKER_NAME.attack.request`, 
`cryton_worker.WORKER_NAME.control.request`, `cryton_worker.WORKER_NAME.agent.request`)
defined using *WORKER_NAME* (can be changed using CLI or in the settings).

The response is sent to the queue defined using the `reply_to` parameter in a *message.properties*.

### Attack requests
Requests to execute a command or a module are being processed in the `cryton_worker.WORKER_NAME.attack.request` queue.  
List of supported requests:

#### Execute attack module
To execute an attack module, send a message to `cryton_worker.WORKER_NAME.attack.request` queue in a format 
```json lines
{"ack_queue": "confirmation_queue", "step_type": "worker/execute", "module": module_name, "module_arguments": module_arguments}
```

ACK response format:
```json
{"return_code": 0, "correlation_id": "id"}
```

Response format:
```json
{"return_code": 0, "output": "", "serialized_output": ""}
```

#### Execute command on agent
To execute a command on a deployed agent, send a message to the `cryton_worker.WORKER_NAME.attack.request` queue in a format 
```json
{"step_type": "empire/execute", "arguments": {"shell_command": "whoami", "use_agent": "MyAgent"}}
```

ACK response format:
```json
{"return_code": 0, "correlation_id": "id"}
```

Response format:
```json
{"return_code": 0, "output": "", "serialized_output": ""}
```

#### Execute empire module on agent
To execute an empire module on a deployed agent, send a message to the `cryton_worker.WORKER_NAME.attack.request` queue in a format 
```json
{"step_type": "empire/execute", "arguments": { "empire_module": "python/collection/linux/pillage_user", "use_agent": "MyAgent"}}
```

ACK response format:
```json
{"return_code": 0, "correlation_id": "id"}
```

Response format: 
```json
{"return_code": 0, "output": "", "serialized_output": ""}
```

### Agent requests
Requests to control empire agents are being processed in `cryton_worker.WORKER_NAME.agent.request` queue.  
List of supported requests:

#### Deploy agent
Deploy an agent and send a response containing the result.  
Example: 
```json
{"step_type": "empire/agent-deploy", "arguments": {"stager_type": "multi/bash", "agent_name": "MyAgent", "listener_name": "TestListener", "listener_port": 80, "session_id": "MSF_SESSION_ID"}}
```

Response example: 
```json
{"return_code": 0, "output": "Agent 'MyAgent' deployed on target 192.168.33.12."}
```
### Control requests
To perform a control event send a message to `cryton_worker.WORKER_NAME.control.request` queue in a format 
```json lines
{"event_t": type, "event_v": value}
```

Response format:
```json lines
{"event_t": type, "event_v": value}
```

**List of supported requests:**

#### Validate module
Validate a module and send a response containing the result.  
Example: 
```json lines
{"event_t": "VALIDATE_MODULE", "event_v": {"module": module_name, "module_arguments": module_arguments}}
```

Response example: 
```json
{"event_t": "VALIDATE_MODULE", "event_v": {"return_code": 0, "output": "output"}}
```

#### List modules
List available modules and send a response containing the result.  

Request example: 
```json
{"event_t": "LIST_MODULES", "event_v": {}}
```

Response example: 
```json
{"event_t": "LIST_MODULES", "event_v": {"module_list": ["module_name"]}}
```

#### List sessions
List available Metasploit sessions and send a response containing the result.

Request example:
```json lines
{"event_t": "LIST_SESSIONS", "event_v": {"target_host": target_ip}}
```

Response example: 
```json
{"event_t": "LIST_SESSIONS", "event_v": {"session_list": ["session_id"]}}
```

#### Kill Step execution
Kill running Step (module) and send a response containing the result.  
Example:
```json lines
{"event_t": "KILL_STEP_EXECUTION", "event_v": {"correlation_id": correlation_id}}
```

Response example:
```json
{"event_t": "KILL_STEP_EXECUTION", "event_v": {"return_code": -2, "output": "exception"}}
```

#### Health check
Check if Worker is alive and send a response containing the result.  
Example: 
```json
{"event_t": "HEALTH_CHECK", "event_v": {}}
```

Response example: 
```json
{"event_t": "HEALTH_CHECK", "event_v": {"return_code": 0}}
```

#### Add trigger for HTTPListener
Add trigger with parameters and start listener with `host` and `port` if it doesn't already exists, send a response containing the result afterwards.  

Request example: 
```json lines
{"event_t": "ADD_TRIGGER", "event_v": {"host": host, "port": port, "listener_type": "HTTP", "reply_to": reply_to_queue, 
  "routes": [{"path": path, "method": method, "parameters": [{"name": name, "value": value}]}]}}
```

Response example:
```json
{"event_t": "ADD_TRIGGER", "event_v": {"return_code": 0, "trigger_id": "123"}}
```
#### Remove trigger for HTTPListener
Remove trigger, optionally stop the  HTTPListener if there are no triggers left and send a response containing the result.  

Request example: 
```json
{"event_t": "REMOVE_TRIGGER", "event_v": {"trigger_id": "123"}}
```

#### Add trigger for MSFListener
Add trigger with session identifiers and start MSFListener.

Request example:
```json
{"event_t": "ADD_TRIGGER", "event_v": {"listener_type": "MSF", "reply_to": "cryton_core.control.response", "identifiers": {"via_exploit": "auxiliary/scanner/ssh/ssh_login"}}}
```

Response example: 
```json
{"event_t": "ADD_TRIGGER", "event_v": {"return_code": 0, "trigger_id": "123"}}
```

#### Remove trigger for MSFListener
This will stop the MSFListener because it can't have multiple triggers.

Request example:
```json
{"event_t": "REMOVE_TRIGGER", "event_v": {"trigger_id": "123"}}
```

Response example:
```json
{"event_t": "REMOVE_TRIGGER", "event_v": {"return_code": -2, "output": "exception"}}
```

#### List triggers
List available triggers and send a response containing the result.  

Example:
```json
{"event_t": "LIST_TRIGGERS", "event_v": {}}
```

Response example:
```json lines
{"event_t": "LIST_TRIGGERS", "event_v": {"trigger_list": [{"id": "123", "trigger_param": "trigger_param_value", ...}]}}
```

#### Trigger Stage (Response only)
Sent when a trigger is activated.

Response example:
```json lines
{"event_t": "TRIGGER_STAGE", "event_v": {"stage_execution_id": stage_execution_id}}
```
