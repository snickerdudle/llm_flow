# Routines-related functions and classes
from typing import Optional, Any, List, Union
from collections import UserList
from src.graph.blocks import BaseBlock


RoutineListType = Union[List["Routine"], "RoutineCollection"]
OneOrMoreRoutinesType = Union["Routine", RoutineListType]


class Routine(BaseBlock):
    def __init__(
        self,
        subroutines: Optional[OneOrMoreRoutinesType] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.subroutines = subroutines or RoutineCollection()

    def __str__(self) -> str:
        return f"<R({self.name}): {self.description}>"


class RoutineCollection(UserList):
    def __init__(
        self,
        data: Optional[OneOrMoreRoutinesType] = None,
        name: Optional[str] = None,
    ):
        self.data = data or []
        self._name = name or ""

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    def __str__(self) -> str:
        return f"<RC({self.name}): {self.data}>"

    @classmethod
    def fromOneOrMoreRoutines(
        cls, routine_set: OneOrMoreRoutinesType
    ) -> "RoutineCollection":
        if isinstance(routine_set, Routine):
            return cls([routine_set])
        return cls(routine_set)

    def __add__(self, other: OneOrMoreRoutinesType) -> "RoutineCollection":
        if not isinstance(other, RoutineCollection):
            other = RoutineCollection.fromOneOrMoreRoutines(other)
        self.data.extend(other.data)
        return self

    def __iadd__(self, other: OneOrMoreRoutinesType) -> "RoutineCollection":
        return self.__add__(other)
