def inject(original: dict | list) -> dict | list:
    """
    Allow definition of output sharing variables alongside the original schema property.
    :param original: The original schema property
    :return: Original property that also allows to define output sharing variables
    """
    pattern_output_sharing = {"type": "string", "pattern": r"^\$.+$"}
    pattern_execution_variables = {"type": "string", "pattern": r"^\{\{.*\}\}$"}

    if isinstance(original, dict):
        return {"anyOf": [original, pattern_output_sharing, pattern_execution_variables]}
    return original + [pattern_output_sharing, pattern_execution_variables]


def inject_schema(schema: dict, ignore_sub_schema_keywords: bool = False, wrap: bool = True):
    """
    Allow definition of output sharing variables alongside the original schema.
    :param schema: Schema to inject with output sharing variables
    :param ignore_sub_schema_keywords: Do not resolve sub schema keys (anyOf, allOf, oneOf, then, else)
    :param wrap: Whether to inject the schema or just its sub schemas
    :return: Original schema that also allows to define output sharing variables
    """
    if not ignore_sub_schema_keywords:
        if (sub_schema := schema.get("anyOf")) is not None and isinstance(sub_schema, list):
            schema["anyOf"] = inject([inject_schema(s, wrap=False) for s in sub_schema])
        if (sub_schema := schema.get("allOf")) is not None and isinstance(sub_schema, list):
            schema["allOf"] = [inject_schema(s, wrap=False) for s in sub_schema]
        if (sub_schema := schema.get("oneOf")) is not None and isinstance(sub_schema, list):
            schema["oneOf"] = inject([inject_schema(s, wrap=False) for s in sub_schema])
        if sub_schema := schema.get("then"):
            schema["then"] = inject_schema(sub_schema, wrap=False)
        if sub_schema := schema.get("else"):
            schema["else"] = inject_schema(sub_schema, wrap=False)

    schema_type = schema.get("type", "")
    if schema_type == "object" or not ignore_sub_schema_keywords:
        if props := schema.get("properties", {}):
            for key, prop in props.items():
                props[key] = inject_schema(prop, True)
    elif schema_type == "array":
        if items := schema.get("items"):
            schema["items"] = inject_schema(items)

    return inject(schema) if wrap else schema
