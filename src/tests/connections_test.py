# Tests for the graph blocks.

import unittest
from src.graph.connections import (
    Connection,
    ConnectionHub,
    Port,
    VariableValue,
    HubType,
    PortVariableNameError,
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
