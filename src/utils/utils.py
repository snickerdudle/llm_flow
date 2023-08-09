import functools
from inspect import signature


class PortVariableNameError(Exception):
    pass


class HubEditError(Exception):
    pass


def enforce_type(type_mapping):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            parameters = list(sig.parameters)

            # Map passed args and kwargs to their parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Check types
            for position, type_name in type_mapping.items():
                param_name = parameters[position]
                actual_arg = bound_args.arguments[param_name]
                if actual_arg is None:
                    continue

                if isinstance(type_name, str):
                    if actual_arg.__class__.__name__ != type_name:
                        raise TypeError(
                            f"Argument {param_name} expected to be of type {type_name}, but got {type(actual_arg).__name__}."
                        )
                else:
                    if not isinstance(actual_arg, type_name):
                        raise TypeError(
                            f"Argument {param_name} expected to be of type {type_name}, but got {type(actual_arg).__name__}."
                        )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def check_editable(func):
    """Decorator to check if the hub is editable."""

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.isEditable:
            raise HubEditError("The hub is not editable.")
        return func(self, *args, **kwargs)

    return wrapper
