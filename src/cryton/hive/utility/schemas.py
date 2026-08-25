from importlib import import_module

from cryton.lib.utility.schemas import inject_schema


def import_module_schema(name: str):
    try:
        return inject_schema(import_module(f"cryton.modules.{name}.module").Module.get_schema())
    except ImportError:
        return {"type": "object"}


NAME_PATTERN = "^[a-zA-Z0-9_-]+$"

PLAN = {
    "definitions": {
        "metadata": {
            "type": "object",
            "properties": {"description": {"type": "string", "description": "Description."}},
            "additionalProperties": True,
            "description": "Additional information. Won't affect the scenario.",
        },
        "step": {
            "type": "object",
            "properties": {
                "metadata": {"$ref": "#/definitions/metadata"},
                "is_init": {"type": "boolean", "description": "Mark the step as initial."},
                "module": {"type": "string", "description": "Module to run."},
                "arguments": {"type": "object", "description": "Arguments passed to the module."},
                "output": {
                    "type": "object",
                    "properties": {
                        "alias": {
                            "type": "string",
                            "pattern": NAME_PATTERN,
                            "description": "Alias used in output sharing.",
                        },
                        "mapping": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from": {"type": "string", "description": "Original path."},
                                    "to": {"type": "string", "description": "New path."},
                                },
                                "additionalProperties": False,
                            },
                            "description": "Mapping of the module output.",
                        },
                        "replace": {
                            "type": "object",
                            "patternProperties": {"^.*$": {"type": "string"}},
                            "additionalProperties": False,
                            "description": "Replace with regex parts of module output.",
                        },
                    },
                    "additionalProperties": False,
                    "description": "Settings for output sharing.",
                },
                "next": {
                    "description": "Settings for conditional execution.",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["state", "serialized_output", "output", "any"],
                                "description": "Which type of output to compare.",
                            },
                            "step": {
                                "anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "string"}],
                                "description": "Step(s) to execute in case of matched conditions.",
                            },
                        },
                        "required": ["type", "step"],
                        "allOf": [
                            {
                                "if": {"properties": {"type": {"const": "state"}}, "required": ["type"]},
                                "then": {
                                    "properties": {
                                        "value": {
                                            "description": "Value that will trigger the the successor(s).",
                                            "type": "string",
                                            "enum": ["finished", "failed", "error"],
                                        },
                                    },
                                    "required": ["value"],
                                },
                            },
                            {
                                "if": {"properties": {"type": {"const": "serialized_output"}}, "required": ["type"]},
                                "then": {
                                    "properties": {
                                        "value": {
                                            "description": "Value that will trigger the the successor(s).",
                                            "type": "string",
                                        },
                                    },
                                    "required": ["value"],
                                },
                            },
                            {
                                "if": {"properties": {"type": {"const": "output"}}, "required": ["type"]},
                                "then": {
                                    "properties": {
                                        "value": {
                                            "description": "Value that will trigger the the successor(s).",
                                            "type": "string",
                                        },
                                    },
                                    "required": ["value"],
                                },
                            },
                            {
                                "if": {"properties": {"type": {"const": "any"}}, "required": ["type"]},
                                "then": {"maxProperties": 2},
                            },
                        ],
                    },
                },
            },
            "allOf": [
                {
                    "if": {"properties": {"module": {"const": "atomic_red_team"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("atomic_red_team")}},
                },
                {
                    "if": {"properties": {"module": {"const": "command"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("command")}},
                },
                {
                    "if": {"properties": {"module": {"const": "empire"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("empire")}},
                },
                {
                    "if": {"properties": {"module": {"const": "ffuf"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("ffuf")}},
                },
                {
                    "if": {"properties": {"module": {"const": "medusa"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("medusa")}},
                },
                {
                    "if": {"properties": {"module": {"const": "metasploit"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("metasploit")}},
                },
                {
                    "if": {"properties": {"module": {"const": "nmap"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("nmap")}},
                },
                {
                    "if": {"properties": {"module": {"const": "script"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("script")}},
                },
                {
                    "if": {"properties": {"module": {"const": "wpscan"}}, "required": ["module"]},
                    "then": {"properties": {"arguments": import_module_schema("wpscan")}},
                },
            ],
            "required": ["module"],
            "additionalProperties": False,
        },
        "stage": {
            "type": "object",
            "description": "",
            "properties": {
                "metadata": {"$ref": "#/definitions/metadata"},
                "type": {
                    "type": "string",
                    "enum": ["immediate", "delta", "time", "http", "metasploit"],
                    "description": "How and when to start the stage.",
                },
                "depends_on": {
                    "type": "array",
                    "items": {"type": "string", "pattern": NAME_PATTERN},
                    "description": "Which stages must be finished before execution.",
                },
                "arguments": {"type": "object", "description": "Define arguments for triggering the stage."},
                "steps": {
                    "type": "object",
                    "patternProperties": {NAME_PATTERN: {"$ref": "#/definitions/step"}},
                    "description": "Stage's steps.",
                },
            },
            "additionalProperties": False,
            "required": ["steps"],
            "allOf": [
                {
                    "if": {"properties": {"type": {"const": "delta"}}, "required": ["type"]},
                    "then": {
                        "properties": {
                            "arguments": {
                                "type": "object",
                                "properties": {
                                    "days": {"type": "integer", "description": "Wait for n days."},
                                    "hours": {"type": "integer", "description": "Wait for n hours."},
                                    "minutes": {"type": "integer", "description": "Wait for n minutes."},
                                    "seconds": {"type": "integer", "description": "Wait for n seconds."},
                                },
                                "minProperties": 1,
                                "additionalProperties": False,
                            },
                        },
                        "required": ["arguments"],
                    },
                },
                {
                    "if": {"properties": {"type": {"const": "time"}}, "required": ["type"]},
                    "then": {
                        "properties": {
                            "arguments": {
                                "type": "object",
                                "properties": {
                                    "timezone": {
                                        "type": "string",
                                        "description": "Timezone when to start the execution.",
                                    },
                                    "year": {"type": "integer", "description": "Year when to start the execution."},
                                    "month": {"type": "integer", "description": "Month when to start the execution."},
                                    "day": {"type": "integer", "description": "Day when to start the execution."},
                                    "hour": {"type": "integer", "description": "Hour when to start the execution."},
                                    "minute": {"type": "integer", "description": "Minute when to start the execution."},
                                    "second": {"type": "integer", "description": "second when to start the execution."},
                                },
                                "if": {"properties": {"timezone": {"pattern": "^.*$"}}, "required": ["timezone"]},
                                "then": {
                                    "minProperties": 2,
                                    # "additionalProperties": False,
                                },
                                "else": {
                                    "minProperties": 1,
                                    # "additionalProperties": False,
                                },
                            },
                        },
                        "required": ["arguments"],
                    },
                },
                {
                    "if": {"properties": {"type": {"const": "http"}}, "required": ["type"]},
                    "then": {
                        "properties": {
                            "arguments": {
                                "type": "object",
                                "properties": {
                                    "host": {
                                        "type": "string",
                                        "description": "Address used to serve the listener on the Worker machine.",
                                    },
                                    "port": {
                                        "type": "integer",
                                        "description": "Port used to serve the listener on the Worker machine.",
                                    },
                                    "routes": {
                                        "description": "List of routes the listener will check for requests.",
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "path": {"type": "string", "description": "Request's path."},
                                                "method": {
                                                    "type": "string",
                                                    "description": "Request's allowed method.",
                                                },
                                                "parameters": {
                                                    "description": "Request's required parameters.",
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "name": {
                                                                "type": "string",
                                                                "description": "Parameter's name.",
                                                            },
                                                            "value": {
                                                                "type": "string",
                                                                "description": "Parameter's value.",
                                                            },
                                                        },
                                                        "required": ["name", "value"],
                                                        "additionalProperties": False,
                                                    },
                                                    "minItems": 1,
                                                },
                                            },
                                            "required": ["path", "method", "parameters"],
                                            "additionalProperties": False,
                                        },
                                        "minItems": 1,
                                    },
                                },
                                "required": ["port", "routes"],
                                "additionalProperties": False,
                            },
                        },
                        "required": ["arguments"],
                    },
                },
                {
                    "if": {"properties": {"type": {"const": "metasploit"}}, "required": ["type"]},
                    "then": {
                        "properties": {
                            "arguments": import_module_schema("metasploit"),
                        },
                        "required": ["arguments"],
                    },
                },
            ],
        },
    },
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.com/cryton.schema.json",
    "title": "Cryton template",
    "type": "object",
    "description": "Cryton template schema",
    "properties": {
        "name": {"type": "string", "description": "Name of the scenario."},
        "dynamic": {"type": "boolean", "description": "Whether the plan can be changed during runtime or not."},
        "settings": {
            "type": "object",
            "properties": {"separator": {"type": "string", "description": "Separator used in output sharing."}},
            "description": "Scenario specific settings.",
        },
        "metadata": {"$ref": "#/definitions/metadata"},
        "stages": {
            "type": "object",
            "patternProperties": {NAME_PATTERN: {"$ref": "#/definitions/stage"}},
            "description": "Scenario's stages.",
        },
    },
    "required": ["name", "stages"],
    "additionalProperties": False,
}
