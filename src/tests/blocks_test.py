# Tests for the graph blocks.

import unittest
from graph.blocks import (
    BaseBlock,
)
from src.graph.connections import (
    ConnectionHub,
    HubType,
    PortVariableNameError,
)


class TestBaseBlock(unittest.TestCase):
    def test_initialization(self):
        block = BaseBlock(name="TestBlock")
        self.assertEqual(block.name, "TestBlock")

        self.assertIsInstance(block.inputs, ConnectionHub)
        self.assertIsInstance(block.outputs, ConnectionHub)

    def test_add_input(self):
        block = BaseBlock(name="TestBlock")
        block.addInputPort("testVar")
        with self.assertRaises(PortVariableNameError):
            block.addInputPort("testVar")
        port = block.inputs.getPort("testVar")
        self.assertEqual(port.parent_hub.kind, HubType.INPUT)
        self.assertEqual(port.parent_block, block)

    def test_add_output(self):
        block = BaseBlock(name="TestBlock")
        block.addOutputPort("testVar")
        with self.assertRaises(PortVariableNameError):
            block.addOutputPort("testVar")
        port = block.outputs.getPort("testVar")
        self.assertEqual(port.parent_hub.kind, HubType.OUTPUT)
        self.assertEqual(port.parent_block, block)

    def test_connect_blocks(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block1.addOutputPort("output_test")
        block2.addInputPort("input_test")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connections)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connections)
        self.assertEqual(
            block1.outputs.getPort("output_test").connections,
            block2.inputs.getPort("input_test").connections,
        )

    def test_connect_blocks_output_does_not_exist(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block2.addInputPort("input_test")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connections)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connections)
        self.assertEqual(
            block1.outputs.getPort("output_test").connections,
            block2.inputs.getPort("input_test").connections,
        )

    def test_connect_blocks_input_does_not_exist(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block1.addOutputPort("output_test")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connections)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connections)
        self.assertEqual(
            block1.outputs.getPort("output_test").connections,
            block2.inputs.getPort("input_test").connections,
        )

    def test_connect_blocks_both_do_not_exist(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connections)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connections)
        self.assertEqual(
            block1.outputs.getPort("output_test").connections,
            block2.inputs.getPort("input_test").connections,
        )

    def test_connect_blocks_force_existence_constraint(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        with self.assertRaises(PortVariableNameError):
            block1.connectVariableToVariable(
                block2,
                "output_test",
                "input_test",
                create_if_not_exists=False,
            )
        self.assertIsNone(block1.outputs.getPort("output_test"))
        self.assertIsNone(block2.inputs.getPort("input_test"))


if __name__ == "__main__":
    unittest.main()
