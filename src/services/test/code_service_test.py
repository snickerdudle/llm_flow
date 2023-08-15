import unittest
from src.services.code_service import CodeExecutionService
from nameko.testing.services import worker_factory
from typing import Optional, List, Any, Dict
from src.utils.io import serializePythonObject, deserializePythonObject


class MockDockerContainer:
    def __init__(self, expected_return_value):
        self.expected_return_value = expected_return_value

    def put_archive(self, *args, **kwargs):
        return

    def exec_run(self, *args, **kwargs):
        # Return exit_code, result
        return 0, serializePythonObject(self.expected_return_value).encode(
            "utf-8"
        )


class MockDockerContainerManager:
    def __init__(self, expected_return_value):
        self.container = MockDockerContainer(expected_return_value)


class TestCodeExecutionService(unittest.TestCase):
    def setUp(self):
        self.service = CodeExecutionService()

    def test_format_code_for_execution_basic(self):
        code = "a = 1\nb = a + 2"
        formatted_code = self.service.format_code_for_execution(code)
        self.assertIn("# First run the input variables", formatted_code)
        self.assertIn("# Then run the code", formatted_code)
        self.assertIn("a = 1", formatted_code)
        self.assertIn("b = a + 2", formatted_code)
        self.assertIn(
            "# Finally assemble the result and pickle it", formatted_code
        )

    def test_format_code_with_input_vars(self):
        code = "c = a + b"
        input_vars = {"a": 5, "b": 7}
        formatted_code = self.service.format_code_for_execution(
            code, input_vars=input_vars
        )
        self.assertIn("a = 5", formatted_code)
        self.assertIn("b = 7", formatted_code)

    def test_format_code_with_string_input_vars(self):
        code = "greeting = 'Hello ' + name"
        input_vars = {"name": "Alice"}
        formatted_code = self.service.format_code_for_execution(
            code, input_vars=input_vars
        )
        self.assertIn('name = "Alice"', formatted_code)

    def test_format_code_with_output_vars(self):
        code = "result = a + b"
        input_vars = {"a": 1, "b": 2}
        output_vars = ["result"]
        formatted_code = self.service.format_code_for_execution(
            code, input_vars=input_vars, output_vars=output_vars
        )
        self.assertIn('"result": result', formatted_code)

    def test_execute_code(self):
        # create worker with mock dependencies
        expected_result = {"result": 3}
        self.service.docker_manager = MockDockerContainerManager(
            expected_result
        )

        code = "result = a + b"
        input_vars = {"a": 1, "b": 2}
        output_vars = ["result"]
        result = self.service.execute_code(
            code, input_vars=input_vars, output_vars=output_vars
        )
        self.assertEqual(result, expected_result)

    def test_execute_code_with_string_output(self):
        # create worker with mock dependencies
        expected_result = {"greeting": "Hello Alice"}
        self.service.docker_manager = MockDockerContainerManager(
            expected_result
        )

        code = "greeting = 'Hello ' + name"
        input_vars = {"name": "Alice"}
        output_vars = ["greeting"]
        result = self.service.execute_code(
            code, input_vars=input_vars, output_vars=output_vars
        )
        self.assertEqual(result, expected_result)

    def test_run_script_in_docker(self):
        expected_result = {"output": 42}
        self.service.docker_manager = MockDockerContainerManager(
            expected_result
        )

        code = """
            import base64
            result = {"output": 42}
            result_encoded = base64.b64encode(pickle.dumps(result))
            print(result_encoded.decode('utf-8'))
        """
        result = self.service._run_script_in_docker(code)
        self.assertEqual(result, {"output": 42})

    # Add more edge cases and special scenarios as needed.


if __name__ == "__main__":
    unittest.main()
