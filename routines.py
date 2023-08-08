# Routines-related functions and classes
from typing import Optional, Any, List, Union
from collections import UserList


RoutineListType = Union[List["Routine"], "RoutineCollection"]
OneOrMoreRoutinesType = Union["Routine", RoutineListType]


class Routine:
    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        subroutines: Optional[OneOrMoreRoutinesType] = None,
    ):
        self._name = name
        self._description = description or ""
        self.subroutines = subroutines or RoutineCollection()

    @property
    def name(self) -> str:
        return self._name or ""

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        self._description = new_description

    def __str__(self) -> str:
        return f"<R({self.name}): {self.description}>"

    def __repr__(self) -> str:
        return self.__str__()


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
