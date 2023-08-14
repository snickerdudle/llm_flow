from functools import wraps
from inspect import signature
from typing import List
from src.utils.logger import Logger


class HubEditError(Exception):
    pass


def autoBlockRetrieve(*idxs: List[int]):
    """Decorator to automatically retrieve blocks from the graph."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            parameters = list(sig.parameters)
            graph = args[0]

            # Map passed args and kwargs to their parameter names
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Check types
            for idx in idxs:
                param_name = parameters[idx]
                actual_arg = bound_args.arguments[param_name]
                if actual_arg is None:
                    continue

                if isinstance(actual_arg, str):
                    # Convert to block
                    block = graph.tryGetOrCreateNewBlock(
                        actual_arg, create=False
                    )
                    bound_args.arguments[param_name] = block

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper

    return decorator


def enforce_type(type_mapping):
    def decorator(func):
        @wraps(func)
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

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.isEditable:
            raise HubEditError("The hub is not editable.")
        return func(self, *args, **kwargs)

    return wrapper


def log_operation(save_to_file: bool = False):
    """Decorator to log operations on the block."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logger = Logger()
            logger.log(f"<--- {self.qualname}", func)

            results = None
            try:
                results = func(self, *args, **kwargs)
            except Exception as e:
                logger.log(
                    f"Operation on block {self.qualname} failed with error: {e.__class__.__name__}",
                    func,
                )

            if save_to_file:
                logger.writeBufferToFile()

            return results

        return wrapper

    return decorator
