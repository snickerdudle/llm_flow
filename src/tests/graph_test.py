import unittest
from unittest.mock import MagicMock
from queue import Queue
from src.graph.graph import Graph
from src.graph.blocks import BaseBlock


class TestGraph(unittest.TestCase):
    def test_getAllBlocksConnectedToBlock_singleBlock(self):
        graph = Graph()
        block = BaseBlock("A")
        graph.addBlock(block)
        self.assertEqual(graph.getAllBlocksConnectedToBlock(block), {block})

    def test_getAllBlocksConnectedToBlock_singleBlock_string(self):
        graph = Graph()
        block = BaseBlock("A")
        graph.addBlock(block)
        self.assertEqual(graph.getAllBlocksConnectedToBlock("A"), {block})

    def test_getAllBlocksConnectedToBlock_singleBlock_string_noadd(self):
        graph = Graph()
        block = BaseBlock("A")
        self.assertRaises(ValueError, graph.getAllBlocksConnectedToBlock, "A")

    def test_getAllBlocksConnectedToBlock_multipleBlocks(self):
        graph = Graph()
        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        blockA.connectVariableToVariable(blockB)
        self.assertEqual(
            graph.getAllBlocksConnectedToBlock(blockA), {blockA, blockB}
        )

    def test_getBlockEvaluationOrder_noStartBlock(self):
        graph = Graph()
        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        graph.addBlock(blockA)
        graph.addBlock(blockB)
        blockA.connectVariableToVariable(blockB)

        self.assertEqual(graph.getBlockEvaluationOrder(), [blockA, blockB])

    def test_getBlockEvaluationOrder_withStartBlock(self):
        graph = Graph()
        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        blockC = BaseBlock("C")
        graph.addBlock(blockA)
        graph.addBlock(blockB)
        graph.addBlock(blockC)

        blockA.connectVariableToVariable(blockB)

        self.assertEqual(
            graph.getBlockEvaluationOrder(blockA), [blockA, blockB]
        )
        self.assertEqual(graph.getBlockEvaluationOrder(blockB), [blockB])
        self.assertEqual(graph.getBlockEvaluationOrder(blockC), [blockC])

    # Add more tests for other scenarios, including more complex graph structures.
    def test_getBlockEvaluationOrder_noStartBlock_complexGraph(self):
        """
             A
            / \
            B  C
            |  | \
            D  E  F
            \ / \ /
               G
        """
        graph = Graph()
        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        blockC = BaseBlock("C")
        blockD = BaseBlock("D")
        blockE = BaseBlock("E")
        blockF = BaseBlock("F")
        blockG = BaseBlock("G")
        graph.addBlock(blockA)
        graph.addBlock(blockB)
        graph.addBlock(blockC)
        graph.addBlock(blockD)
        graph.addBlock(blockE)
        graph.addBlock(blockF)
        graph.addBlock(blockG)

        blockA.connectVariableToVariable(blockB)
        blockA.connectVariableToVariable(blockC)
        blockB.connectVariableToVariable(blockD)
        blockB.connectVariableToVariable(blockE)
        blockC.connectVariableToVariable(blockE)
        blockC.connectVariableToVariable(blockF)
        blockD.connectVariableToVariable(blockG)
        blockE.connectVariableToVariable(blockG)
        blockF.connectVariableToVariable(blockG)

        self.assertEqual(
            graph.getBlockEvaluationOrder(),
            [blockA, blockB, blockC, blockD, blockE, blockF, blockG],
        )

    def test_getBlockEvaluationOrder_complexGraph(self):
        """
             A
             |
             B
            / \
            D  C
            |  |
            F  E
        """
        graph = Graph()

        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        blockC = BaseBlock("C")
        blockD = BaseBlock("D")
        blockE = BaseBlock("E")
        blockF = BaseBlock("F")

        # Create graph connections
        blockA.connectVariableToVariable(blockB)
        blockB.connectVariableToVariable(blockD)
        blockB.connectVariableToVariable(blockC)
        blockC.connectVariableToVariable(blockE)
        blockD.connectVariableToVariable(blockE)
        blockD.connectVariableToVariable(blockF)

        graph.addBlock(blockA)
        graph.addBlock(blockB)
        graph.addBlock(blockC)
        graph.addBlock(blockD)
        graph.addBlock(blockE)
        graph.addBlock(blockF)

        # No start block implies the entire graph is evaluated
        # We expect: A, B and C (all level 0), then D (level 1), then E (level 2), then F (level 3)
        self.assertEqual(
            graph.getBlockEvaluationOrder(),
            [blockA, blockB, blockC, blockD, blockE, blockF],
        )
        self.assertEqual(
            graph.getBlockEvaluationOrder(blockC),
            [blockC, blockE],
        )

    def test_add_block_no_name(self):
        graph = Graph()
        graph.addBlock()
        graph.addBlock()
        graph.addBlock()

        self.assertEqual(len(graph.blocks), 3)
        self.assertSetEqual(
            set([block.name for block in graph.blocks]),
            {"block_0", "block_1", "block_2"},
        )

    def test_add_block_name_collision(self):
        graph = Graph()
        graph.addBlock("A")
        self.assertRaises(ValueError, graph.addBlock, "A")
        graph.addBlock(BaseBlock("B"))
        graph.addBlock(BaseBlock())

        self.assertEqual(len(graph.blocks), 3)
        self.assertSetEqual(
            set([block.name for block in graph.blocks]), {"A", "B", "NO_NAME"}
        )

    def test_remove_block(self):
        graph = Graph()
        block = BaseBlock("A")
        graph.addBlock(block)
        self.assertEqual(len(graph.blocks), 1)
        graph.removeBlock(block)
        self.assertEqual(len(graph.blocks), 0)

        graph.addBlock("B")
        graph.addBlock("C")
        graph.removeBlock("B")
        self.assertEqual(len(graph.blocks), 1)

    def test_remove_block_not_in_graph(self):
        graph = Graph()
        block = BaseBlock("A")
        graph.addBlock("B")

        self.assertRaises(ValueError, graph.removeBlock, block)
        self.assertRaises(ValueError, graph.removeBlock, "A")

    def test_connect_blocks(self):
        graph = Graph()
        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        graph.addBlock(blockA)
        graph.addBlock(blockB)

        graph.connectBlocks(blockA, blockB)
        self.assertEqual(len(blockA.getOutgoingNeighbors()), 1)
        self.assertEqual(len(blockA.getOutgoingConnections()), 1)
        self.assertEqual(len(blockB.getIncomingNeighbors()), 1)
        self.assertEqual(len(blockB.getIncomingConnections()), 1)
        self.assertEqual(
            blockA.getOutgoingConnections(), blockB.getIncomingConnections()
        )
        self.assertEqual(len(graph.connections), 1)

    def test_connect_blocks_string_name(self):
        graph = Graph()
        blockA = BaseBlock("A")
        blockB = BaseBlock("B")
        graph.addBlock(blockA)
        graph.addBlock(blockB)

        graph.connectBlocks("A", "B")
        self.assertEqual(len(blockA.getOutgoingNeighbors()), 1)
        self.assertEqual(len(blockA.getOutgoingConnections()), 1)
        self.assertEqual(len(blockB.getIncomingNeighbors()), 1)
        self.assertEqual(len(blockB.getIncomingConnections()), 1)
        self.assertEqual(
            blockA.getOutgoingConnections(), blockB.getIncomingConnections()
        )
        self.assertEqual(len(graph.connections), 1)


if __name__ == "__main__":
    unittest.main()
