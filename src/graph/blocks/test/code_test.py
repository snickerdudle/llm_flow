import unittest
from src.graph.blocks.block import BaseBlock
from src.graph.blocks.code import Code


class TestCode(unittest.TestCase):
    def setUp(self):
        self.code = Code()

    def test_id(self):
        self.assertIsNotNone(self.code.id)

    def test_name(self):
        self.assertEqual(self.code.name, "NO_NAME")
        self.code.name = "Test Code"
        self.assertEqual(self.code.name, "Test Code")

    def test_qualname(self):
        self.assertEqual(self.code.qualname, "Code(NO_NAME)")
        self.code.name = "Test Code"
        self.assertEqual(self.code.qualname, "Code(Test Code)")

    def test_description(self):
        self.assertEqual(self.code.description, "NO_DESCRIPTION")
        self.code.description = "Test Description"
        self.assertEqual(self.code.description, "Test Description")

    def test_inputs(self):
        self.assertEqual(len(self.code.inputs), 0)

    def test_outputs(self):
        self.assertEqual(len(self.code.outputs), 1)
        self.assertListEqual(["code"], self.code.outputs.portNames)

    def test_changes_affect_reliability(self):
        self.assertTrue(self.code.changes_affect_reliability)

    def test_str(self):
        self.assertEqual(str(self.code), "<C(NO_NAME)>")

    def test_repr(self):
        self.assertEqual(repr(self.code), "<C(NO_NAME)>")

    def test_inherited_functionality(self):
        self.assertTrue(issubclass(Code, BaseBlock))


if __name__ == "__main__":
    unittest.main()
