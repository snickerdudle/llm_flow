from multiprocessing import Process
import subprocess
import time
from typing import Any, List, Optional
from src.graph.blocks.block import BaseBlock


class GraphRun:
    """A class that represents a run of a graph."""

    def __init__(self, graph: Any):
        self.graph = graph

    def executeGraphOperations(
        self, custom_block_order: Optional[List[BaseBlock]] = None
    ):
        """Executes the graph operations.

        First, get the order of operations from the Graph structure. Then, for
        each operation, execute it in a new process. Finally, wait for all
        processes to finish.

        Args:
            custom_block_order: A custom block order to use instead of the
                default one.
        """
        if custom_block_order is not None:
            block_order = custom_block_order
        else:
            block_order = self.graph.getBlocksOrder()

        processes = []
        block_id_to_status = {}

        for block in block_order:
            process = Process(target=block.run)
            process.start()
            processes.append(process)
        for process in processes:
            process.join()


class GraphExecutionEnvironment:
    """A class that represents a graph execution environment."""

    def __init__(self, graph: Any):
        self.graph = graph

        # Create Code Worker Job
        self.code_worker = self.startCodeWorkerJob()

    def startCodeWorkerJob(self):
        """Starts the code execution server and the worker jobs."""
        pass


if __name__ == "__main__":
    g = GraphExecutionEnvironment(None)
