# Tests for the graph blocks.

import unittest
from src.graph.blocks import (
    Connection,
    ConnectionHub,
    Port,
    VariableValue,
    BaseBlock,
    HubType,
    PortVariableNameError,
    HubEditError,
)


class TestVariableValue(unittest.TestCase):
    def test_initialization(self):
        vv = VariableValue()
        self.assertIsNone(vv.getValue()[0])
        self.assertFalse(vv.isAvailable)
        self.assertFalse(vv.isReliable)

        vv = VariableValue("Test")
        self.assertEqual(vv.getValue()[0], "Test")
        self.assertTrue(vv.isAvailable)
        self.assertFalse(vv.isReliable)

    def test_reliability(self):
        vv = VariableValue()
        vv.makeReliable()
        self.assertTrue(vv.isReliable)
        vv.makeUnreliable()
        self.assertFalse(vv.isReliable)

    def test_setValue(self):
        vv = VariableValue()
        vv.setValue("ValueSet")
        self.assertEqual(vv.getValue()[0], "ValueSet")
        self.assertTrue(vv.isAvailable)


class TestConnection(unittest.TestCase):
    def test_initialization_1(self):
        cx = Connection()

        hub1 = ConnectionHub(HubType.OUTPUT)
        hub2 = ConnectionHub(HubType.INPUT)

        self.assertIsNone(cx.from_port)
        self.assertIsNone(cx.to_port)

        self.assertRaises(TypeError, Connection, hub1, hub2)

    def test_initialization_2(self):
        cx = Connection()

        self.assertIsNone(cx.from_port)
        self.assertIsNone(cx.to_port)

        hub1 = ConnectionHub(HubType.OUTPUT)
        hub2 = ConnectionHub(HubType.INPUT)

        hub1.addPort(var_name="test", connection=cx)
        hub2.addPort(var_name="test", connection=cx)

        self.assertEqual(cx.from_port, hub1.getPort("test"))
        self.assertEqual(cx.to_port, hub2.getPort("test"))

    def test_initialization_3(self):
        cx = Connection()

        self.assertIsNone(cx.from_port)
        self.assertIsNone(cx.to_port)

        hub1 = ConnectionHub(HubType.OUTPUT)
        hub2 = ConnectionHub(HubType.INPUT)

        p1 = hub1.addPort(var_name="test", connection=cx)
        p2 = hub2.addPort(var_name="test", connection=cx)

        self.assertEqual(p1, "test")
        self.assertEqual(p2, "test")

        self.assertIsNotNone(hub1.getPort(p1).connection)
        self.assertIsNotNone(hub2.getPort(p2).connection)

        self.assertIs(hub1.getPort(p1).connection, cx)
        self.assertIs(hub2.getPort(p2).connection, cx)

    def test_hub_edit_1(self):
        cx = Connection()

        self.assertIsNone(cx.from_port)
        self.assertIsNone(cx.to_port)

        hub1 = ConnectionHub(HubType.OUTPUT)
        hub2 = ConnectionHub(HubType.INPUT)

        p1 = hub1.addPort(connection=cx)
        p2 = hub2.addPort(connection=cx)

        self.assertEqual(cx.from_port, hub1.getPort(p1))
        self.assertEqual(cx.to_port, hub2.getPort(p2))

        hub3 = ConnectionHub(HubType.OUTPUT)

        p3 = hub3.addPort(connection=cx)
        self.assertEqual(cx.from_port, hub3.getPort(p3))
        self.assertEqual(cx.to_port, hub2.getPort(p2))

    def test_hub_edit_2(self):
        cx = Connection()

        self.assertIsNone(cx.from_port)
        self.assertIsNone(cx.to_port)

        hub1 = ConnectionHub(HubType.OUTPUT)
        hub2 = ConnectionHub(HubType.INPUT)

        p1 = hub1.addPort(connection=cx)
        p2 = hub2.addPort(connection=cx)

        self.assertEqual(cx.from_port, hub1.getPort(p1))
        self.assertEqual(cx.to_port, hub2.getPort(p2))

        hub3 = ConnectionHub(HubType.INPUT)

        p3 = hub3.addPort(connection=cx)
        self.assertEqual(cx.from_port, hub1.getPort(p1))
        self.assertEqual(cx.to_port, hub3.getPort(p3))


class TestPort(unittest.TestCase):
    def test_initialization(self):
        port = Port()
        self.assertIsNone(port.getValue()[0])
        self.assertFalse(port.getValue()[1])

        port = Port(value="ValueSet")
        self.assertEqual(port.getValue()[0], "ValueSet")

        cx = Connection()
        port = Port(connection=cx, parent=ConnectionHub(HubType.OUTPUT))
        self.assertEqual(port.connection, cx)
        self.assertEqual(port.connection.from_port, port)

        cx = Connection()
        port = Port(connection=cx, parent=ConnectionHub(HubType.INPUT))
        self.assertEqual(port.connection, cx)
        self.assertEqual(port.connection.to_port, port)


class TestConnectionHub(unittest.TestCase):
    def test_initialization_1(self):
        hub = ConnectionHub(HubType.INPUT)
        self.assertEqual(hub.kind, HubType.INPUT)
        self.assertIsNone(hub.parent_block)

    def test_initialization_2(self):
        hub = ConnectionHub()
        self.assertEqual(hub.kind, HubType.INPUT)
        self.assertIsNone(hub.parent_block)

    def test_add_remove_ports(self):
        hub = ConnectionHub(HubType.INPUT)
        hub.addPort("testVar")
        with self.assertRaises(PortVariableNameError):
            hub.addPort("testVar")
        hub.removePort("testVar")
        with self.assertRaises(PortVariableNameError):
            hub.removePort("testVar")

    def test_rename_ports(self):
        hub = ConnectionHub(HubType.INPUT)
        hub.addPort("testVar")
        hub.renamePort("testVar", "newTestVar")
        with self.assertRaises(PortVariableNameError):
            hub.renamePort("testVar", "newTestVar")
        with self.assertRaises(PortVariableNameError):
            hub.renamePort("newTestVar", "newTestVar")


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
        self.assertIsNotNone(block1.outputs.getPort("output_test").connection)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connection)
        self.assertEqual(
            block1.outputs.getPort("output_test").connection,
            block2.inputs.getPort("input_test").connection,
        )

    def test_connect_blocks_output_does_not_exist(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block2.addInputPort("input_test")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connection)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connection)
        self.assertEqual(
            block1.outputs.getPort("output_test").connection,
            block2.inputs.getPort("input_test").connection,
        )

    def test_connect_blocks_input_does_not_exist(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block1.addOutputPort("output_test")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connection)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connection)
        self.assertEqual(
            block1.outputs.getPort("output_test").connection,
            block2.inputs.getPort("input_test").connection,
        )

    def test_connect_blocks_both_do_not_exist(self):
        block1 = BaseBlock(name="TestBlock1")
        block2 = BaseBlock(name="TestBlock2")
        block1.connectVariableToVariable(block2, "output_test", "input_test")
        self.assertIsNotNone(block1.outputs.getPort("output_test").connection)
        self.assertIsNotNone(block2.inputs.getPort("input_test").connection)
        self.assertEqual(
            block1.outputs.getPort("output_test").connection,
            block2.inputs.getPort("input_test").connection,
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
