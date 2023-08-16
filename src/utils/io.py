import base64
import pickle
from typing import Any
from shortuuid import ShortUUID


def serializePythonObject(obj: Any) -> str:
    """Serialize a Python object to a string.

    Uses Pickle to serialize first, then encodes using base64.

    Args:
        obj: The object to serialize.

    Returns:
        result_str: The serialized object as a string.
    """
    result_str = base64.b64encode(pickle.dumps(obj))
    return result_str.decode("utf-8")


def deserializePythonObject(obj_str: str) -> Any:
    """Deserialize a Python object from a string.

    Uses base64 to decode first, then uses Pickle to deserialize.

    Args:
        obj_str: The string to deserialize.

    Returns:
        result_obj: The deserialized object.
    """
    result_obj = pickle.loads(base64.b64decode(obj_str))
    return result_obj


def randomIdentifier(length: int = 8) -> str:
    """Generate a random identifier."""
    return ShortUUID().random(length=length)


def permissionsToInt(
    read: bool = False,
    write: bool = False,
    execute: bool = False,
    *other_permissions,
):
    """Converts permissions to an integer."""
    permissions = 0
    if read:
        permissions += 1
    if write:
        permissions += 2
    if execute:
        permissions += 4

    cur_level = 8
    for permission in other_permissions:
        if permission:
            permissions += cur_level
        cur_level *= 2

    return permissions
