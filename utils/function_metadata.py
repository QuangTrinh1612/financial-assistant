from inspect import signature, Parameter
import functools
import re
from typing import Callable, Dict, List

def parse_docstring(func: Callable) -> Dict[str, str]:
    """
    Parses the docstring of a function and returns a dict with parameter descriptions.
    """
    doc = func.__doc__
    if not doc:
        return {}

    param_re = re.compile(r':param\s+(\w+):\s*(.*)')
    param_descriptions = {}

    for line in doc.split('\n'):
        match = param_re.match(line.strip())
        if match:
            param_name, param_desc = match.groups()
            param_descriptions[param_name] = param_desc

    return param_descriptions

def python_type_to_json_type(py_type):
    """Maps Python types to JSON schema types."""
    type_mapping = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    return type_mapping.get(py_type, "string")  # Default to string if unknown

def function_schema(name: str, description: str, required_params: List[str]):
    def decorator_function(func: Callable) -> Callable:

        sig = signature(func)

        if not all(param in sig.parameters for param in required_params):
            raise ValueError(f"Missing required parameters in {func.__name__}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        param_descriptions = parse_docstring(func)

        serialized_params = {
            param_name: {
                "type": python_type_to_json_type(param.annotation),
                "description": param_descriptions.get(param_name, "No description")
            }
            for param_name, param in sig.parameters.items() if param_name in required_params
        }

        wrapper.schema = {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": serialized_params,
                "required": required_params
            }
        }
        return wrapper
    return decorator_function