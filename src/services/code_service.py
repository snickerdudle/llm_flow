import base64
import pickle
import tarfile
from io import BytesIO
from typing import Any, List, Optional
from uuid import uuid4

from nameko.extensions import DependencyProvider
from nameko.rpc import rpc

from src.utils.io import deserializePythonObject

import docker


class DockerContainerManager(DependencyProvider):
    """A simple DependencyProvider to manage a Docker container."""

    client = None
    container_name: str = "long_running_python_runner" + uuid4().hex[-8:]
    image_name: str = "python_runner"
    container = None

    def start(self):
        """Called when the service starts."""
        self.client = docker.from_env()

        try:
            self.client.networks.get("no-internet")
        except docker.errors.NotFound:
            self.client.networks.create("no-internet", driver="bridge")

        container = self.client.containers.run(
            image=self.image_name,
            name=self.container_name,
            detach=True,  # Run in the background
            network="no-internet",
            mem_limit="100m",
            command="tail -f /dev/null",  # Keep it running
        )
        print(f"Started container with ID: {self.container_name}")
        self.container = container

        return container

    def stop(self):
        """Called when the service stops."""
        try:
            container = self.client.containers.get(self.container_name)
            try:
                container.stop(timeout=5)  # waits up to 10 seconds
            except docker.errors.Timeout:
                container.kill()
            container.remove()
        except docker.errors.NotFound:
            print(f"Container {self.container_name} not found.")
            return None
        finally:
            self.container = None
            print(f"Stopped container with ID: {self.container_name}")

        return container

    def get_dependency(self, worker_ctx):
        return self


class CodeExecutionService:
    name = "code_execution_service"
    docker_manager = DockerContainerManager()

    def format_code_for_execution(
        self,
        code: str,
        input_vars: Optional[dict[str, Any]] = None,
        output_vars: List[str] = None,
    ) -> str:
        """Format the code for execution.

        The code comes in as a string, and we will execute it in a separate
        docker container for safety reasons. The code will be executed in a
        separate docker container, and the result will be stored in Redis.
        Additionally, the result will be returned to the caller as a dictionary
        of the form:
            INPUT CODE:
                a = 1
                b = a + some_input
                d = b * 4
            INPUT_VARS:
                {"some_input": 2}
            OUTPUT_VARS:
                ["d"]
            RESULT:
                {"d": 12}

        In the above example, the code is executed in a separate docker
        container, and the result is stored in Redis. Before the execution, the
        input variables are pre-run so that the code can use them. The output
        variables are the variables that the caller wants to get the value of
        after the execution. The result is a dictionary of the output variables
        and their values.

        The final execution of the code will look like this:
        code = "
            # First run the input variables
            some_input = 2

            # Then run the code
            a = 1
            b = a + some_input
            d = b * 4

            # Finally assemble the result and pickle it
            import pickle
            result = {"d": d}
            result = pickle.dumps(result)
            result = base64.b64encode(result)
            print(result.decode('utf-8'))
            "

        Args:
            code (str): The code to execute.
            input_vars (Optional[dict[str, Any]]): The input variables to run
                before executing the code.
            output_vars (List[str]): The output variables to return after
                executing the code.
        """
        input_vars = input_vars or {}
        output_vars = output_vars or []

        runnable_code = "# First run the input variables\n"
        for var, val in input_vars.items():
            if type(val) == str:
                runnable_code += f'{var} = "{val}"\n'
            else:
                runnable_code += f"{var} = {val}\n"

        runnable_code += "\n# Then run the code\n"
        runnable_code += code.strip()

        runnable_code += "\n# Finally assemble the result and pickle it\n"
        runnable_code += "import pickle\n"
        runnable_code += "import base64\n"
        runnable_code += "result = {"
        for var in output_vars:
            runnable_code += f'"{var}": {var},'
        runnable_code += "}\n"
        runnable_code += "result = pickle.dumps(result)\n"
        runnable_code += "result = base64.b64encode(result)\n"
        runnable_code += "print(result.decode('utf-8'))\n"

        runnable_code += "# End of code\n\n"
        return runnable_code

    @rpc
    def execute_code(
        self,
        code: str,
        input_vars: Optional[dict[str, Any]] = None,
        output_vars: List[str] = None,
    ):
        """Execute the code.

        Args:
            code (str): The code to execute.
            input_vars (Optional[dict[str, Any]]): The input variables to run
                before executing the code.
            output_vars (List[str]): The output variables to return after
                executing the code.
        """
        runnable_code = self.format_code_for_execution(
            code=code, input_vars=input_vars, output_vars=output_vars
        )

        result = None
        try:
            result = self._run_script_in_docker(runnable_code)
        except:
            print("Something went wrong")
        return result

    def _run_script_in_docker(self, code_string) -> dict[str, Any]:
        # Create an in-memory bytes buffer
        in_memory_file = BytesIO()
        in_memory_file.write(code_string.encode("utf-8"))

        # Create an in-memory tarball
        tar_stream = BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            file_info = tarfile.TarInfo(name="file.py")
            file_info.size = in_memory_file.tell()
            in_memory_file.seek(0)
            tar.addfile(file_info, fileobj=in_memory_file)

        # Transfer the in-memory tarball to Docker
        container_dir = "/tmp/"
        if self.docker_manager is None:
            print("Docker manager is None")
        self.docker_manager.container.put_archive(
            container_dir, tar_stream.getvalue()
        )

        # Execute the script inside the container
        command = ["python", "/tmp/file.py"]
        exit_code, output = self.docker_manager.container.exec_run(cmd=command)

        return deserializePythonObject(output.decode("utf-8").strip())


if __name__ == "__main__":
    # Create a CodeExecutionService instance and run a sample piece of code
    # through for testing purposes
    code_execution_service = CodeExecutionService()
    code_execution_service.execute_code(
        code="""
a = 1
b = a + some_input
c = b * 4
""",
        input_vars={"some_input": 2},
        output_vars=["c"],
    )
