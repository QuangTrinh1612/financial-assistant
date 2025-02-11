import importlib.util
from pathlib import Path
import json
import logging
from typing import Optional, Dict, List, Type

logger = logging.getLogger(__name__)

class FunctionsRegistry:
    def __init__(self) -> None:
        self.functions_dir = Path(__file__).parent.parent / 'src' / 'services'
        self.registry: Dict[str, callable] = {}
        self.schema_registry: Dict[str, Dict] = {}
        self.load_functions()

    def load_functions(self) -> None:
        """Dynamically loads functions and class methods from Python files in the functions directory."""
        if not self.functions_dir.exists():
            logger.error(f"Functions directory does not exist: {self.functions_dir}")
            return

        for file in self.functions_dir.glob('*.py'):
            module_name = file.stem
            if module_name.startswith('__'):
                continue  # Skip dunder files

            spec = importlib.util.spec_from_file_location(module_name, file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Register standalone functions
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    if callable(attr) and hasattr(attr, 'schema'):
                        self.registry[attr_name] = attr
                        self.schema_registry[attr_name] = attr.schema

                # Register class methods
                for class_name in dir(module):
                    cls = getattr(module, class_name)
                    if isinstance(cls, type):  # Ensure it's a class
                        for method_name in dir(cls):
                            method = getattr(cls, method_name)
                            if callable(method) and hasattr(method, 'schema'):
                                # Store bound method (class reference included)
                                self.registry[f"{class_name}.{method_name}"] = (cls, method)
                                self.schema_registry[f"{class_name}.{method_name}"] = method.schema

    def resolve_function(self, function_name: str, arguments_json: Optional[str] = None):
        """Resolves and executes a function or class method from the registry."""
        func_entry = self.registry.get(function_name)
        if not func_entry:
            raise ValueError(f"Function {function_name} is not registered.")

        try:
            # Determine if the function is a standalone function or class method
            if isinstance(func_entry, tuple):
                # Class method: (cls, method)
                cls, method = func_entry
                func = method.__get__(cls)  # Bind method to class
            else:
                # Standalone function
                func = func_entry

            # Parse JSON arguments
            if arguments_json is not None:
                arguments_dict = json.loads(arguments_json) if isinstance(arguments_json, str) else arguments_json
                return func(**arguments_dict)
            else:
                return func()
        except json.JSONDecodeError:
            logger.error("Invalid JSON format.")
            return None
        except Exception as e:
            logger.error(f"Error when calling function {function_name}: {e}")
            return None

    def mapped_functions(self) -> List[Dict]:
        """Returns a list of registered functions formatted for OpenAI API function calling."""
        return [{"type": "function", "function": func_schema} for func_schema in self.schema_registry.values()]

    def get_function_callable(self):
        """Returns a dictionary mapping function names to their callable functions."""
        return {func_name: func for func_name, func in self.registry.items()}

    def generate_schema_file(self) -> None:
        """Generates a JSON schema file containing all registered function schemas."""
        schema_path = self.functions_dir / 'function_schemas.json'
        with schema_path.open('w') as f:
            json.dump(list(self.schema_registry.values()), f, indent=2)

    def get_registry_contents(self) -> List[str]:
        """Returns a list of registered function names."""
        return list(self.registry.keys())

    def get_schema_registry(self) -> List[Dict]:
        """Returns the registered function schemas."""
        return list(self.schema_registry.values())