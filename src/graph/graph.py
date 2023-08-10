# Code describing the graph
from inspect import signature
from typing import List, Set, Optional, Union
from queue import Queue
from uuid import uuid4

from src.graph.blocks import BaseBlock
from src.graph.connections import Connection
from src.utils.decorators import autoBlockRetrieve
from functools import wraps

BlockCollectionType = Set[BaseBlock]
ConnectionCollection = Set[Connection]


class Graph:
    def __init__(
        self,
        name: Optional[str] = None,
        blocks: Optional[BlockCollectionType] = None,
    ):
        self._name = name or ""
        self._blocks = blocks or {}
        self._connections: ConnectionCollection = set()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def blocks(self) -> BlockCollectionType:
        return set(self._blocks.values())

    @property
    def connections(self) -> ConnectionCollection:
        return self._connections

    def _checkBlockExists(self, block: Optional[Union[BaseBlock, str]]):
        if block is None:
            return False
        if isinstance(block, BaseBlock):
            block = block.name
        return block in self._blocks

    def tryGetOrCreateNewBlock(
        self, block: Optional[Union[BaseBlock, str]], create: bool = True
    ) -> BaseBlock:
        """
        If the given block is a string, try to get the block with that name.
        If the block does not exist, create a new block with that name.
        If the given block is a BaseBlock, return it.

        Args:
            block (Union[BaseBlock, str]): The block to get or add.

        Returns:
            BaseBlock: The block that was retrieved or created.
        """
        if create:
            if block is None:
                # Create new block name (str)
                cur_num = 0
                while True:
                    block = f"block_{cur_num}"
                    if block not in self._blocks:
                        break
                    cur_num += 1
            if isinstance(block, str):
                # Check to see if we have this block already, or create if we don't
                if block in self._blocks:
                    block = self._blocks[block]
                else:
                    block = BaseBlock(name=block)
        else:
            if block is None:
                raise ValueError("Block cannot be None")
            if isinstance(block, str):
                if block in self._blocks:
                    return self._blocks[block]
                else:
                    raise ValueError(f"Block {block} does not exist")

        return block

    def addBlock(self, block: Optional[Union[BaseBlock, str]] = None) -> None:
        if self._checkBlockExists(block):
            raise ValueError(f"Block {block} already in graph")
        block = self.tryGetOrCreateNewBlock(block)
        self._blocks[block.name] = block

    @autoBlockRetrieve(1)
    def removeBlock(self, block: Union[BaseBlock, str]) -> None:
        if isinstance(block, BaseBlock):
            block_name = block.name
        else:
            block_name = block
        if block_name not in self._blocks:
            raise ValueError(f"Block {block_name} not in graph")
        block = self._blocks[block_name]

        for connection in self.connections:
            if connection.from_block == block or connection.to_block == block:
                self.removeConnection(connection)

        del self._blocks[block_name]

    def addConnection(self, connection: Connection) -> None:
        self.connections.add(connection)

    def removeConnection(self, connection: Connection) -> None:
        connection.removeSelfFromPorts()
        self.connections.remove(connection)

    def __add__(self, other: BaseBlock) -> None:
        self.addBlock(other)

    def __iadd__(self, other: BaseBlock) -> None:
        self.addBlock(other)

    @autoBlockRetrieve(1, 2)
    def connectBlocks(
        self,
        from_block: BaseBlock,
        to_block: BaseBlock,
        from_varname: Optional[str] = None,
        to_varname: Optional[str] = None,
    ) -> None:
        """Connect the given blocks.

        Args:
            from_block (BaseBlock): The block from which the connection
                originates.
            to_block (BaseBlock): The block to which the connection goes.
            from_varname (Optional[str]): The name of the variable from which
                the connection originates.
            to_varname (Optional[str]): The name of the variable to which the
                connection goes.
        """
        new_connection = from_block.connectVariableToVariable(
            block=to_block,
            from_port_var_name=from_varname,
            to_port_var_name=to_varname,
        )
        self.addConnection(new_connection)

    @autoBlockRetrieve(1)
    def getAllBlocksConnectedToBlock(
        self, block: BaseBlock
    ) -> BlockCollectionType:
        """Get all the blocks connected to the given block.

        Args:
            block (BaseBlock): The block whose connected blocks we want to
                retrieve.

        Returns:
            BlockCollectionType: The blocks connected to the given block.
        """
        connected_blocks = {block}
        blocks_queue = Queue()
        blocks_queue.put(block)

        while not blocks_queue.empty():
            cur_block = blocks_queue.get_nowait()
            for neighbor in cur_block.getAllNeighbors():
                if neighbor not in connected_blocks:
                    blocks_queue.put(neighbor)
            connected_blocks.add(cur_block)

        return connected_blocks

    @autoBlockRetrieve(1)
    def getAllBlocksFollowingBlock(
        self, block: BaseBlock
    ) -> BlockCollectionType:
        """Get all the blocks following the given block, inclusive.

        Args:
            block (BaseBlock): The block whose following blocks we want to
                retrieve.

        Returns:
            BlockCollectionType: The blocks following the given block.
        """
        following_blocks = {block}
        blocks_queue = Queue()
        blocks_queue.put(block)

        while not blocks_queue.empty():
            cur_block = blocks_queue.get_nowait()
            for neighbor in cur_block.getOutgoingNeighbors():
                if neighbor not in following_blocks:
                    blocks_queue.put(neighbor)
            following_blocks.add(cur_block)

        return following_blocks

    def getBlockEvaluationOrder(
        self, start_block: Optional[BaseBlock] = None
    ) -> None:
        """Return the order in which the blocks should be evaluated.

        The start block is the block from which the execution should start.
        If no start block is provided, the complete graph is evaluated.

        In the case of the complete graph, the order is determined by the
        connections between the blocks. We start by finding all the blocks that
        have no input connections. These blocks are assigned level 0. Then, we
        find all the blocks that have connections to blocks at level 0. The
        connections emanating from level 0 blocks have level 1. We find the next
        level by finding all the blocks that have connections to blocks at the
        previous level. The blocks at the next level are assigned the highest of
        the levels of the connections that they are connected to. We continue in
        this manner until all blocks have been assigned a level.

        In the case of a start block, the entire graph is evaluated, but if
        there are any blocks that are not connected to the start block, they are
        not evaluated (if we have 2 independent graphs, and we start the
        execution from one of them, the other one is not executed). Only the
        blocks that follow the start block are evaluated.

        Args:
            start_block (Optional[BaseBlock]): The block from which the
                execution should start.

        Returns:
            List[BaseBlock]: The order in which the blocks should be evaluated.
        """
        blocks_to_level = {}
        visited_blocks = set()
        blocks_queue = Queue()

        # Find all the blocks that have no input connections
        for block in self.blocks:
            if not block.getIncomingNeighbors():
                blocks_to_level[block] = 0
                blocks_queue.put(block)

        # Main loop to mark the levels of all the blocks
        while not blocks_queue.empty():
            cur_block = blocks_queue.get_nowait()
            new_block_level = blocks_to_level[cur_block] + 1

            # Find all the blocks that have connections to the current block
            for new_block in cur_block.getOutgoingNeighbors():
                if new_block not in visited_blocks:
                    blocks_queue.put(new_block)
                blocks_to_level[new_block] = max(
                    new_block_level, blocks_to_level.get(new_block, -1)
                )

            visited_blocks.add(cur_block)

        # If a start block is provided, remove all the blocks that are not
        # connected to it
        if start_block is not None:
            all_following = self.getAllBlocksFollowingBlock(start_block)
            blocks_to_level = {
                block: level
                for block, level in blocks_to_level.items()
                if block in all_following
            }

        # First sort the blocks by their name
        blocks_to_level = sorted(
            blocks_to_level.items(), key=lambda x: x[0].name
        )
        # Sort the blocks by their level
        blocks_to_level = sorted(blocks_to_level, key=lambda x: x[1])

        return [block for block, _ in blocks_to_level]

    def runAllBlocks(self) -> None:
        """Run the graph from start to finish."""
        block_evaluation_order = self.getBlockEvaluationOrder()
        for block in block_evaluation_order:
            block.run()

    def runAllAfterBlock(self, block: BaseBlock) -> None:
        """Run the graph after the given block.

        Args:
            block (BaseBlock): The block after which the execution should start.
        """
        block_evaluation_order = self.getBlockEvaluationOrder(block)
        for block in block_evaluation_order:
            block.run()
