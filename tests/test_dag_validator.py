import unittest
from scripts.orchestration.dag_validator import DAG_VALIDATOR

class TestDAGValidator(unittest.TestCase):
    def setUp(self):
        self.validator = DAG_VALIDATOR()

    def test_chain_length(self):
        self.assertTrue(self.validator.validate_workflow(["a", "b", "c"]))
        self.assertFalse(self.validator.validate_workflow(["a", "b", "c", "d", "e", "f"]))

    def test_cycles(self):
        self.assertFalse(self.validator.validate_workflow(["agent-1", "agent-2", "agent-1"]))
        self.assertTrue(self.validator.validate_workflow(["agent-1", "agent-2", "agent-3"]))

    def test_recursion_depth(self):
        self.assertTrue(self.validator.is_recursion_safe(0))
        self.assertTrue(self.validator.is_recursion_safe(1))
        self.assertFalse(self.validator.is_recursion_safe(2))

if __name__ == "__main__":
    unittest.main()
