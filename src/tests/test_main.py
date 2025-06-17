import unittest
from unittest import TestCase

# from unittest.mock import MagicMock
import src.main as main
from datetime import datetime, timedelta


class TestMain(TestCase):
    """Test for main module."""

    def setUp(self):
        """Setup resources."""
        main.employees = [{"id": "0001", "name": "Wale", "balance": 20}]
        main.leave_histories = []

    def test_register_employee(self):
        size_before = len(main.employees)
        main.register_employee("Wale")
        size_after = len(main.employees)
        self.assertGreater(size_after, size_before)
        self.assertEqual(main.employees[-1]["name"], "Wale")

    def test_apply_for_leave(self):
        size_before = len(main.leave_histories)
        leave_balance_before = main.employees[0]["balance"]

        # Add 3 future days
        current_date = datetime.now()
        day_1 = (current_date + timedelta(days=2)).strftime("%Y-%m-%d")
        day_2 = (current_date + timedelta(days=3)).strftime("%Y-%m-%d")
        day_3 = (current_date + timedelta(days=4)).strftime("%Y-%m-%d")
        leave_dates = [day_1, day_2, day_3]

        # Apply for leave
        results = main.apply_for_leave(
            employee_id="0001",
            leave_dates=leave_dates,
            purpose=main.LeaveType.SICK.value,
        )

        size_after = len(main.leave_histories)
        leave_balance_after = main.employees[0]["balance"]

        self.assertGreater(size_after, size_before)
        self.assertEqual(size_before + 3, size_after)
        self.assertEqual(main.leave_histories[-1]["employee_id"], "0001")
        self.assertEqual(main.leave_histories[-3]["leave_date"], day_1)
        self.assertEqual(main.leave_histories[-2]["leave_date"], day_2)
        self.assertEqual(main.leave_histories[-1]["leave_date"], day_3)
        self.assertEqual(
            main.leave_histories[-1]["purpose"], main.LeaveType.SICK.value
        )  # no-qa
        self.assertEqual(
            leave_balance_after, (leave_balance_before - len(leave_dates))
        )  # no-qa
        self.assertIn("success", results.lower())

    def test_apply_for_leave_invalid_date_returns_failure(self):
        """Tests that invalid date returns failure message."""
        # invalid leave dates in the past
        current_date = datetime.now()
        day_1 = (current_date - timedelta(days=2)).strftime("%Y-%m-%d")
        day_2 = (current_date - timedelta(days=3)).strftime("%Y-%m-%d")

        history_size_before = len(main.leave_histories)

        leave_dates = [day_1, day_2]

        result = main.apply_for_leave(
            employee_id="0001",
            leave_dates=leave_dates,
            purpose=main.LeaveType.SICK.value,
        )

        history_size_after = len(main.leave_histories)

        self.assertIn("Error: Invalid leave dates", result)
        self.assertEqual(history_size_before, history_size_after)

    def test_apply_for_leave_invalid_employee_id_returns_not_found(self):
        """Tests that invalid employee_id returns failure message."""
        # invalid employee ID
        invalid_emp_id = "0400"

        current_date = datetime.now()
        day_1 = (current_date + timedelta(days=2)).strftime("%Y-%m-%d")
        day_2 = (current_date + timedelta(days=3)).strftime("%Y-%m-%d")

        history_size_before = len(main.leave_histories)

        leave_dates = [day_1, day_2]

        result = main.apply_for_leave(
            employee_id=invalid_emp_id,
            leave_dates=leave_dates,
            purpose=main.LeaveType.SICK.value,
        )

        history_size_after = len(main.leave_histories)

        self.assertIn("not found", result.lower())
        self.assertEqual(history_size_before, history_size_after)

    def test_apply_for_leave_invalid_purpose_defaults_others(self):
        """Tests that purpose out of context defaults to failure."""
        other_purpose = "my personal reason"
        current_date = datetime.now()
        day_1 = (current_date + timedelta(days=2)).strftime("%Y-%m-%d")
        day_2 = (current_date + timedelta(days=3)).strftime("%Y-%m-%d")
        leave_dates = [day_1, day_2]

        main.apply_for_leave(
            employee_id="0001",
            leave_dates=leave_dates,
            purpose=other_purpose,
        )
        self.assertEqual(main.leave_histories[-1]["purpose"], "others")

    def test_add_leave_to_history(self):
        """Test leave can be added to history."""
        mock_date = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        mock_leave = {
            "employee_id": "0001",
            "purpose": "vacation",
            "leave_date": mock_date,
        }

        size_before = len(main.leave_histories)
        main.add_leave_to_history(**mock_leave)
        size_after = len(main.leave_histories)

        self.assertEqual(size_after, size_before + 1)

    def test_add_leave_to_history_works_for_any_valid_date(self):
        """Tests all valid leave date string is formated
        and can be added to history."""
        # mock_date = "20/06/2025, 10:30:25 AM"
        mock_date = "January 26, 2030, 10:30:25 AM"
        mock_leave = {
            "employee_id": "0001",
            "purpose": "vacation",
            "leave_date": mock_date,
        }

        size_before = len(main.leave_histories)
        main.add_leave_to_history(**mock_leave)
        size_after = len(main.leave_histories)

        self.assertEqual(size_after, size_before + 1)
        self.assertEqual(main.leave_histories[-1]["leave_date"], "2030-01-26")

    def test_cancel_leaves_valid_input(self):
        """Tests that cancel_leaves works for valid input."""
        current_date = datetime.now()
        day_1 = (current_date + timedelta(days=2)).strftime("%Y-%m-%d")
        day_2 = (current_date + timedelta(days=3)).strftime("%Y-%m-%d")
        mock_emp_id = "0001"
        mock_leave_dates = [day_1, day_2]

        size_before = len(main.leave_histories)

        # apply for leaves
        main.apply_for_leave(
            employee_id=mock_emp_id,
            leave_dates=mock_leave_dates,
            purpose="sick",
        )
        # cancel leaves
        main.cancel_leaves(mock_emp_id, mock_leave_dates)

        size_after = len(main.leave_histories)

        self.assertEqual(size_after, size_before)


if __name__ == "__main__":
    unittest.main()
