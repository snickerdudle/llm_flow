from typing import Optional
from src.graph.blocks.block import Variable


class Code(Variable):
    """A block that contains code."""

    def __init__(self, *args, code: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self._code = code or "print('Hello World!')"
        self.changes_affect_reliability = True

        self.clearAllVariables()
        self.createNewVariable("code")

    @property
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, new_code: str) -> None:
        self._code = new_code

    def __str__(self) -> str:
        return f"<C({self.name})>"

    def run(self) -> None:
        """Run the code."""
        super(Code, self).run()
        code = self.code
        exec_environment = self.graph.getCodeExecEnvironment()
        return_values = exec_environment.execute(code)
        self.editVariableValue("code", return_values)
