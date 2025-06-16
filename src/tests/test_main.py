import unittest
from unittest import TestCase
from unittest.mock import MagicMock
import src.main as main


class TestMain(TestCase):
    """Test for main module."""

    def test_register_employee(self):
        size_before = len(main.employees)
        main.register_employee("Wale")
        size_after = len(main.employees)
        self.assertGreater(size_after, size_before)
        self.assertEqual(main.employees[-1]["name"], "Wale")


if __name__ == "__main__":
    unittest.main()
