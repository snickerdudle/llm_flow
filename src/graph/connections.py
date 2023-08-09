# Code describing the functional blocks of the graph.
from collections import OrderedDict
from enum import Enum
from typing import Any, List, Optional, Set, Tuple, Union
from uuid import uuid4

from src.utils.utils import PortVariableNameError, check_editable, enforce_type


class VariableValue:
    def __init__(self, value: Optional[Any] = None):
        self._id = uuid4().hex
        self._value = value
        self._available = self._value is not None
        self._reliable = False

    @property
    def id(self) -> str:
        return self._id

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
    @enforce_type({1: "Port", 2: "Port"})
    def __init__(
        self,
        from_port: Optional["Port"] = None,
        to_port: Optional["Port"] = None,
    ):
        self._id = uuid4().hex
        if from_port is not None:
            from_port.addConnection(self)
        if to_port is not None:
            to_port.addConnection(self)
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

    @property
    def from_hub(self) -> Optional[Any]:
        if self.from_port is None:
            return None
        return self.from_port.parent_hub

    @property
    def to_hub(self) -> Optional[Any]:
        if self.to_port is None:
            return None
        return self.to_port.parent_hub

    def __str__(self) -> str:
        return f"<CX({self.id})>"

    def __repr__(self) -> str:
        return self.__str__()

    def removeSelfFromPorts(self) -> None:
        if self.from_port is not None:
            self.from_port.removeConnection(self)
        if self.to_port is not None:
            self.to_port.removeConnection(self)


class Port:
    @enforce_type({2: "Connection", 3: "ConnectionHub"})
    def __init__(
        self,
        value: Optional[Union[VariableValue, Any]] = None,
        connection: Optional[Connection] = None,
        parent: Optional["ConnectionHub"] = None,
    ):
        self._id = uuid4().hex
        if value is not None:
            if not isinstance(value, VariableValue):
                value = VariableValue(value)
        else:
            value = VariableValue()
        self._value = value
        self._parent = parent
        self._connections = set()
        if connection is not None:
            if self.isInput:
                connection.to_port = self
            else:
                connection.from_port = self
            self._connections.add(connection)

    @property
    def id(self) -> str:
        return self._id

    @property
    def connections(self) -> Set[Connection]:
        return self._connections

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

    def addConnection(self, new_connection: Optional[Connection]) -> None:
        if self.isInput:
            self._value.makeUnreliable()
        self._connections.add(new_connection)

    def removeConnection(self, connection: Optional[Connection]) -> None:
        self._connections.discard(connection)
        if self.isInput:
            self._value.makeUnreliable()

    def removeAllConnections(self) -> None:
        for connection in self._connections:
            connection.removeSelfFromPsorts()
        self._connections.clear()
        if self.isInput:
            self._value.makeUnreliable()


class HubType(Enum):
    INPUT = 1
    OUTPUT = 2
    INTERNAL = 3


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

    @property
    def portDict(self) -> OrderedDict[Port]:
        return self._ports

    @property
    def portList(self) -> List[Port]:
        return list(self.portDict.values())

    @property
    def portNames(self) -> List[str]:
        return list(self.portDict.keys())

    @property
    def numPorts(self) -> int:
        return len(self.portDict)

    def isEmpty(self) -> bool:
        """Return True if the hub is empty."""
        return len(self.getConnections()) == 0

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
    @enforce_type({1: str, 2: "Connection"})
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
                var_name = f"var{self.numPorts + 1}"
                if var_name not in self.portDict:
                    break
        if var_name in self.portDict:
            raise PortVariableNameError(
                f"Variable name '{var_name}' already exists. Please use a different name."
            )
        new_port = Port(connection=connection, parent=self)
        self.portDict[var_name] = new_port
        return var_name

    @check_editable
    def removePort(self, var_name: str) -> None:
        """Remove a port from the hub."""
        if var_name in self.portDict:
            self.portDict[var_name].removeAllConnections()
            del self.portDict[var_name]
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
        if new_var_name in self.portDict:
            raise PortVariableNameError(
                f"Variable name '{new_var_name}' already exists. Please use a different name."
            )
        if old_var_name not in self.portDict:
            raise PortVariableNameError(
                f"Variable name '{old_var_name}' does not exist."
            )
        self.portDict[new_var_name] = self.portDict.pop(old_var_name)
        return new_var_name

    @enforce_type({1: str})
    def getPort(self, var_name: str) -> Port:
        """Get the port with the given variable name."""
        return self.portDict.get(var_name)

    def getConnections(self) -> Set[Connection]:
        """Get the connections of the hub."""
        connections = set()
        for port in self.portList:
            # Expand the set by the connections of the port
            connections = connections.union(port.connections)
        return connections

    def getConnectionsByBlock(self, block: Any) -> Set[Connection]:
        """Get the connections of the hub that are connected to the given block."""
        connections = set()
        for port in self.portList:
            for connection in port.connections:
                if (
                    connection.from_block == block
                    or connection.to_block == block
                ):
                    connections.add(connection)
        return connections

    @enforce_type({1: "ConnectionHub"})
    def getConnectionsByHub(self, hub: "ConnectionHub") -> List[Connection]:
        """Get the connections of the hub that are connected to the given node."""
        connections = set()
        for port in self.portList:
            for connection in port.connections:
                if connection.from_hub == hub or connection.to_hub == hub:
                    connections.add(connection)
        return connections
