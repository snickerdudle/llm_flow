import unittest
from src.utils.decorators import enforce_type


class TestEnforceTypeDecorator(unittest.TestCase):
    def test_enforce_type_with_valid_args(self):
        @enforce_type({0: int, 1: str})
        def foo(a, b):
            return a, b

        self.assertEqual(foo(1, "hello"), (1, "hello"))

    def test_enforce_type_with_invalid_args(self):
        @enforce_type({0: int, 1: str})
        def foo(a, b):
            return a, b

        with self.assertRaises(TypeError):
            foo("hello", 1)

    def test_enforce_type_with_none_args(self):
        @enforce_type({0: int, 1: str})
        def foo(a, b):
            return a, b

        self.assertEqual(foo(None, "hello"), (None, "hello"))

    def test_enforce_type_with_missing_type(self):
        @enforce_type({0: "NonExistentType"})
        def foo(a):
            return a

        with self.assertRaises(TypeError):
            foo(1)

    def test_enforce_type_with_class_method(self):
        class Foo:
            pass

        a = Foo()
        b = Foo()

        @enforce_type({1: Foo})
        def foo(a, b):
            return a, b

        self.assertEqual(foo(a, b), (a, b))

    def test_enforce_type_with_class_method_fail(self):
        class Foo:
            pass

        class Bar:
            pass

        a = Foo()
        b = Bar()

        @enforce_type({0: Foo, 1: Foo})
        def foo(a, b):
            return a, b

        with self.assertRaises(TypeError):
            foo(a, b)

    def test_enforce_type_with_class_init(self):
        class Foo:
            @enforce_type({1: int, 2: str})
            def __init__(self, a, b):
                self.a = a
                self.b = b

        foo = Foo(1, "hello")
        self.assertEqual(foo.a, 1)
        self.assertEqual(foo.b, "hello")
        self.assertIsInstance(foo, Foo)


if __name__ == "__main__":
    unittest.main()
