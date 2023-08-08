# Code describing the functional blocks of the graph.
from collections import OrderedDict
from enum import Enum
from functools import wraps
from typing import Any, List, Optional, Tuple, Union
from uuid import uuid4


class VariableValue:
    def __init__(self, value: Optional[Any] = None):
        self._value = value
        self._available = self._value is not None
        self._reliable = False

    @property
    def isReliable(self) -> bool:
        return self._reliable

    @property
    def isAvailable(self) -> bool:
        return self._available

    def makeReliable(self) -> None:
        self._reliable = True

    def makeUnreliable(self) -> None:
        self._reliable = False

    def setValue(self, value: Any) -> None:
        self._value = value
        self._available = True

    def getValue(self) -> Tuple[Any, bool]:
        return self._value, self._reliable


class Connection:
    def __init__(
        self,
        from_port: Optional["Port"] = None,
        to_port: Optional["Port"] = None,
    ):
        self._id = uuid4().hex
        if from_port is not None:
            if not isinstance(from_port, Port):
                raise TypeError(
                    f"from_port must be of type Port, not {type(from_port)}."
                )
            from_port.setConnection(self)
        if to_port is not None:
            if not isinstance(to_port, Port):
                raise TypeError(
                    f"to_port must be of type Port, not {type(to_port)}."
                )
            to_port.setConnection(self)
        self.from_port = from_port
        self.to_port = to_port

    @property
    def id(self) -> str:
        return self._id

    @property
    def from_block(self) -> Optional[Any]:
        if self.from_port is None:
            return None
        return self.from_port.parent_block

    @property
    def to_block(self) -> Optional[Any]:
        if self.to_port is None:
            return None
        return self.to_port.parent_block

    def __str__(self) -> str:
        return f"<CX({self.id})>"

    def __repr__(self) -> str:
        return self.__str__()


class Port:
    def __init__(
        self,
        value: Optional[Union[VariableValue, Any]] = None,
        connection: Optional[Connection] = None,
        parent: Optional["ConnectionHub"] = None,
    ):
        if value is not None:
            if not isinstance(value, VariableValue):
                value = VariableValue(value)
        else:
            value = VariableValue()
        self._value = value
        self._parent = parent
        if connection is not None:
            if not isinstance(connection, Connection):
                raise TypeError(
                    f"connection must be of type Connection, not {type(connection)}."
                )
            if self.isInput:
                connection.to_port = self
            else:
                connection.from_port = self
        self._connection = connection

    @property
    def connection(self) -> Optional[Connection]:
        return self._connection

    @property
    def parent_hub(self) -> Optional["ConnectionHub"]:
        return self._parent

    @property
    def parent_block(self) -> Optional[Any]:
        if self.parent_hub is None:
            return None
        return self.parent_hub.parent_block

    @property
    def isInput(self) -> bool:
        if self.parent_hub is None:
            raise ValueError("The parent hub is not set.")
        return self.parent_hub.isInput

    def getValue(self) -> Tuple[Any, bool]:
        return self._value.getValue()

    def setValue(self, value: Any) -> None:
        self._value.setValue(value)

    def setConnection(self, new_connection: Optional[Connection]) -> None:
        if new_connection is not self.connection:
            self._value.makeUnreliable()
            self._connection = new_connection

    def unsetConnection(self) -> None:
        self._connection = None
        self._value.makeUnreliable()


class HubType(Enum):
    INPUT = 1
    OUTPUT = 2
    INTERNAL = 3


class PortVariableNameError(Exception):
    pass


class HubEditError(Exception):
    pass


def check_editable(func):
    """Decorator to check if the hub is editable."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.isEditable:
            raise HubEditError("The hub is not editable.")
        return func(self, *args, **kwargs)

    return wrapper


class ConnectionHub:
    def __init__(
        self,
        kind: Optional[HubType] = HubType.INPUT,
        parent: Optional[Any] = None,
        editable: Optional[bool] = True,
    ):
        self._id = uuid4().hex
        self._kind = kind
        self._parent = parent
        self._ports = OrderedDict()
        self._editable = editable

    @property
    def id(self) -> str:
        return self._id

    @property
    def kind(self) -> HubType:
        return self._kind

    @property
    def parent_block(self) -> Any:
        return self._parent

    @property
    def isEditable(self) -> bool:
        return self._editable

    @property
    def isInput(self) -> bool:
        return self.kind == HubType.INPUT

    def __str__(self) -> str:
        return f"<CXH({self.kind})>"

    def __repr__(self) -> str:
        return self.__str__()

    def _setConnectionPort(
        self, connection: Optional[Connection], port: Port
    ) -> None:
        if connection is not None:
            if self.isInput:
                connection.to_port = port
            else:
                connection.from_port = port

    @check_editable
    def addPort(
        self,
        var_name: Optional[str] = None,
        connection: Optional[Connection] = None,
    ) -> str:
        """Add a port to the hub.

        Args:
            var_name (Optional[str], optional): The name of the variable.
                If not supplied, a name will be generated. Defaults to None.
            connection (Optional[Connection], optional): The connection to add
                to the port. Defaults to None.

        Returns:
            str: The name of the variable.

        Raises:
            ConnectionVariableNameError: Raised if the variable name already
                exists.
            HubEditError: Raised if the hub is not editable.
        """
        if var_name is None:
            # Generate a variable name like 'var1', 'var2', etc.
            while True:
                var_name = f"var{len(self._ports) + 1}"
                if var_name not in self._ports:
                    break
        if var_name in self._ports:
            raise PortVariableNameError(
                f"Variable name '{var_name}' already exists. Please use a different name."
            )
        new_port = Port(connection=connection, parent=self)
        self._ports[var_name] = new_port
        return var_name

    @check_editable
    def removePort(self, var_name: str) -> None:
        """Remove a port from the hub."""
        if var_name in self._ports:
            self._ports[var_name].unsetConnection()
            del self._ports[var_name]
        else:
            raise PortVariableNameError(
                f"Variable name '{var_name}' does not exist."
            )

    @check_editable
    def renamePort(self, old_var_name: str, new_var_name: str) -> str:
        """Rename a port in the hub.

        Args:
            old_var_name (str): The old variable name.
            new_var_name (str): The new variable name.

        Returns:
            str: The new variable name.

        Raises:
            ConnectionVariableNameError: Raised if the variable name already
                exists.
        """
        if new_var_name in self._ports:
            raise PortVariableNameError(
                f"Variable name '{new_var_name}' already exists. Please use a different name."
            )
        if old_var_name not in self._ports:
            raise PortVariableNameError(
                f"Variable name '{old_var_name}' does not exist."
            )
        self._ports[new_var_name] = self._ports.pop(old_var_name)
        return new_var_name

    def getPort(self, var_name: str) -> Port:
        """Get the port with the given variable name."""
        return self._ports.get(var_name)

    def getConnections(self) -> List[Connection]:
        """Get the connections of the hub."""
        connections = []
        for port in self._ports.values():
            if port.connection is not None:
                connections.append(port.connection)
        return connections

    def getConnectionsByNode(self, node: Any) -> List[Connection]:
        """Get the connections of the hub that are connected to the given node."""
        connections = []
        for port in self._ports.values():
            connection = port.connection
            if connection is None:
                continue
            if connection.from_block == node or connection.to_block == node:
                connections.append(connection)
        return connections

    def getConnectionsByHub(self, hub: "ConnectionHub") -> List[Connection]:
        """Get the connections of the hub that are connected to the given node."""
        connections = []
        for port in self._ports.values():
            connection = port.connection
            if connection is None:
                continue
            if (
                connection.from_port.parent_hub == hub
                or connection.to_port.parent_hub == hub
            ):
                connections.append(connection)
        return connections
