# Code describing the functional blocks of the graph.
from functools import wraps
from typing import Any, List, Optional
from uuid import uuid4

from src.graph.connections import (
    Connection,
    ConnectionHub,
    HubType,
    Port,
    PortVariableNameError,
)


class BaseBlock:
    """The base class for all blocks in the graph."""

    def __init__(self, name: Optional[str] = None):
        self._id = uuid4().hex
        self._name = name
        self._inputs = self.initilizeInputs()
        self._outputs = self.initilizeOutputs()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name or "NO_NAME"

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def inputs(self) -> ConnectionHub:
        return self._inputs

    @property
    def outputs(self) -> ConnectionHub:
        return self._outputs

    def __str__(self) -> str:
        return f"<BB({self.name})>"

    def __repr__(self) -> str:
        return self.__str__()

    def initilizeInputs(self) -> ConnectionHub:
        """Initialize the inputs object of the block."""
        new_inputs = ConnectionHub(HubType.INPUT, self)
        return new_inputs

    def initilizeOutputs(self) -> ConnectionHub:
        """Initialize the outputs object of the block."""
        new_outputs = ConnectionHub(HubType.OUTPUT, self)
        return new_outputs

    def addInputPort(
        self,
        var_name: Optional[str] = None,
        connection: Optional[Connection] = None,
    ) -> str:
        """Add an input port to the block.

        Args:
            var_name (Optional[str], optional): The name of the variable.
                If not supplied, a name will be generated. Defaults to None.
            connection (Optional[Connection], optional): The connection to add
                to the port. Defaults to None.

        Returns:
            str: The name of the variable.

        Raises:
            PortVariableNameError: Raised if the variable name already exists.
        """
        return self._inputs.addPort(var_name, connection)

    def addOutputPort(
        self,
        var_name: Optional[str] = None,
        connection: Optional[Connection] = None,
    ) -> str:
        """Add an output port to the block.

        Args:
            var_name (Optional[str], optional): The name of the variable.
                If not supplied, a name will be generated. Defaults to None.
            connection (Optional[Connection], optional): The connection to add
                to the port. Defaults to None.

        Returns:
            str: The name of the variable.

        Raises:
            PortVariableNameError: Raised if the variable name already exists.
        """
        return self._outputs.addPort(var_name, connection)

    def projectToPort(self, from_port: Port, to_port: Port) -> None:
        """Create a connection between two ports."""
        cx = Connection(from_port, to_port)

    def connectVariableToVariable(
        self,
        block: "BaseBlock",
        from_port_var_name: str,
        to_port_var_name: str,
        create_if_not_exists: Optional[bool] = True,
    ):
        """Create a connection between two ports of two blocks.

        If the variable name does not exist, create new variables.

        Args:
            block (BaseBlock): The block to connect to.
            from_port_var_name (str): The variable name of the port of the
                current block.
            to_port_var_name (str): The variable name of the port of the
                other block.
            create_if_not_exists (Optional[bool], optional): If True, create

        Raises:
            PortVariableNameError: Raised if the variable name does not exist
                and create_if_not_exists is False.
        """
        from_port = self._outputs.getPort(from_port_var_name)
        if from_port is None:
            if not create_if_not_exists:
                raise PortVariableNameError(
                    f"Variable name '{from_port_var_name}' does not exist in the outputs."
                )
            # No existing port with that name. Create new one
            self.addOutputPort(from_port_var_name)
            from_port = self._outputs.getPort(from_port_var_name)
        to_port = block._inputs.getPort(to_port_var_name)
        if to_port is None:
            if not create_if_not_exists:
                raise PortVariableNameError(
                    f"Variable name '{to_port_var_name}' does not exist in the inputs."
                )
            # No existing port with that name. Create new one
            block.addInputPort(to_port_var_name)
            to_port = block._inputs.getPort(to_port_var_name)
        _ = Connection(from_port, to_port)

    def getAllConnections(self) -> List[Connection]:
        """Get the connections of the block."""
        return self._inputs.getConnections() + self._outputs.getConnections()

    def getAllNeighbors(self) -> List["BaseBlock"]:
        """Get all the neighbors of the block."""
        neighbors = []
        for connection in self.getAllConnections():
            if connection.from_block is not self:
                neighbors.append(connection.from_block)
            else:
                neighbors.append(connection.to_block)
        return neighbors
