import unittest
from src.graph.routines.routines import Routine, RoutineCollection


class TestRoutine(unittest.TestCase):
    def setUp(self):
        self.routine = Routine(
            name="Test Routine", description="A test routine"
        )

    def test_routine_creation(self):
        self.assertEqual(self.routine.name, "Test Routine")
        self.assertEqual(self.routine.description, "A test routine")

    def test_routine_str_representation(self):
        self.assertEqual(
            str(self.routine), "<R(Test Routine): A test routine>"
        )

    def test_routine_collection_creation(self):
        routine_collection = RoutineCollection(name="Test Routine Collection")
        self.assertEqual(routine_collection.name, "Test Routine Collection")

    def test_routine_collection_str_representation(self):
        routine_collection = RoutineCollection(name="Test Routine Collection")
        self.assertEqual(
            str(routine_collection), "<RC(Test Routine Collection): []>"
        )

    def test_routine_collection_from_one_or_more_routines(self):
        routine = Routine(name="Test Routine", description="A test routine")
        routine_collection = RoutineCollection.fromOneOrMoreRoutines(routine)
        self.assertEqual(len(routine_collection), 1)
        self.assertEqual(routine_collection[0], routine)

        routine_list = [routine, routine]
        routine_collection = RoutineCollection.fromOneOrMoreRoutines(
            routine_list
        )
        self.assertEqual(len(routine_collection), 2)
        self.assertEqual(routine_collection[0], routine)
        self.assertEqual(routine_collection[1], routine)

    def test_routine_collection_add(self):
        routine = Routine(name="Test Routine", description="A test routine")
        routine_collection = RoutineCollection(name="Test Routine Collection")
        routine_collection += routine
        self.assertEqual(len(routine_collection), 1)
        self.assertEqual(routine_collection[0], routine)

        routine_list = [routine, routine]
        routine_collection = RoutineCollection(name="Test Routine Collection")
        routine_collection += routine_list
        self.assertEqual(len(routine_collection), 2)
        self.assertEqual(routine_collection[0], routine)
        self.assertEqual(routine_collection[1], routine)

        routine_collection = RoutineCollection(name="Test Routine Collection")
        routine_collection += routine
        routine_collection += routine_list
        self.assertEqual(len(routine_collection), 3)
        self.assertEqual(routine_collection[0], routine)
        self.assertEqual(routine_collection[1], routine)
        self.assertEqual(routine_collection[2], routine)

    def test_routine_collection_nested(self):
        routine = Routine(name="Test Routine", description="A test routine")
        routine_collection = RoutineCollection(name="Test Routine Collection")
        routine_collection += routine
        routine_collection += routine_collection
        self.assertEqual(len(routine_collection), 2)
        self.assertEqual(routine_collection[0], routine)
        self.assertEqual(routine_collection[1], routine)

        routine_list = [routine, routine]
        routine_collection = RoutineCollection(name="Test Routine Collection")
        routine_collection += routine_list
        routine_collection += routine_collection
        self.assertEqual(len(routine_collection), 4)
        self.assertEqual(routine_collection[0], routine)
        self.assertEqual(routine_collection[1], routine)
        self.assertEqual(routine_collection[2], routine)
        self.assertEqual(routine_collection[3], routine)


if __name__ == "__main__":
    unittest.main()
