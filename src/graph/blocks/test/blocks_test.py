# Tests for the graph blocks.

import unittest
from src.graph.blocks.block import BaseBlock, Variable
from src.graph.connections import (
    ConnectionHub,
    HubType,
    PortVariableNameError,
)


class TestBaseBlock(unittest.TestCase):
    def setUp(self):
        self.block1 = BaseBlock(1)
        self.block2 = BaseBlock(2)
        self.block3 = BaseBlock(3)

        self.block1.connectVariableToVariable(self.block2, "output", "input")
        self.block2.connectVariableToVariable(self.block3, "output", "input")
        self.block1.connectVariableToVariable(self.block3, "output", "input")

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

    def test_getIncomingConnections(self):
        self.assertEqual(len(self.block1.getIncomingConnections()), 0)
        self.assertEqual(len(self.block2.getIncomingConnections()), 1)
        self.assertEqual(len(self.block3.getIncomingConnections()), 2)

    def test_getOutgoingConnections(self):
        self.assertEqual(len(self.block1.getOutgoingConnections()), 2)
        self.assertEqual(len(self.block2.getOutgoingConnections()), 1)
        self.assertEqual(len(self.block3.getOutgoingConnections()), 0)

    def test_getAllConnections(self):
        self.assertEqual(len(self.block1.getAllConnections()), 2)
        self.assertEqual(len(self.block2.getAllConnections()), 2)
        self.assertEqual(len(self.block3.getAllConnections()), 2)

    def test_getIncomingNeighbors(self):
        self.assertSetEqual(self.block1.getIncomingNeighbors(), set())
        self.assertSetEqual(self.block2.getIncomingNeighbors(), {self.block1})
        self.assertSetEqual(
            self.block3.getIncomingNeighbors(), {self.block1, self.block2}
        )

    def test_getOutgoingNeighbors(self):
        self.assertSetEqual(
            self.block1.getOutgoingNeighbors(), {self.block2, self.block3}
        )
        self.assertSetEqual(self.block2.getOutgoingNeighbors(), {self.block3})
        self.assertSetEqual(self.block3.getOutgoingNeighbors(), set())

    def test_getAllNeighbors(self):
        self.assertSetEqual(
            self.block1.getAllNeighbors(), {self.block2, self.block3}
        )
        self.assertSetEqual(
            self.block2.getAllNeighbors(), {self.block1, self.block3}
        )
        self.assertSetEqual(
            self.block3.getAllNeighbors(), {self.block1, self.block2}
        )

    def test_serialize(self):
        block = BaseBlock(name="TestBlock", id="A")
        serialized = block.serialize()
        print(serialized)

        expected_serialized = {
            "id": "A",
            "name": "TestBlock",
            "description": "NO_DESCRIPTION",
            "inputs": {},
            "outputs": {},
            "type": "BaseBlock",
        }

        self.assertDictEqual(serialized, expected_serialized)


class TestVariable(unittest.TestCase):
    def test_serialize(self):
        block = Variable(name="TestBlock", id="A")
        serialized = block.serialize()

        expected_serialized = {
            "id": "A",
            "name": "TestBlock",
            "description": "NO_DESCRIPTION",
            "inputs": {},
            "outputs": {
                "id": "fb812a057a7f49b68d590f78638455f6",
                "kind": "OUTPUT",
                "ports": {
                    "var1": {
                        "id": "5ef4505ee4484ca8adf5f027f44db342",
                        "value": 0,
                        "connections": [],
                    }
                },
            },
            "type": "Variable",
        }

        self.assertIn("id", serialized["outputs"])
        serialized["outputs"].pop(
            "id"
        )  # Remove the id, since it is randomly generated
        expected_serialized["outputs"].pop(
            "id"
        )  # Remove the id, since it is randomly generated

        self.assertIn("id", serialized["outputs"]["ports"]["var1"])
        serialized["outputs"]["ports"]["var1"].pop("id")
        expected_serialized["outputs"]["ports"]["var1"].pop("id")

        self.assertDictEqual(serialized, expected_serialized)


if __name__ == "__main__":
    unittest.main()
