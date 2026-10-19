"""Unit tests for Employee Management System database and service layers."""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import Database
from services import WorkforceService


class TestWorkforceService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.db_path = os.path.join(cls.temp_dir.name, "test_analytics.db")
        cls.db = Database(cls.db_path)
        cls.service = WorkforceService(cls.db)
        cls.service.save_employee({
            "employee_id": "EMP999",
            "name": "Test Engineer",
            "department": "Engineering",
            "designation": "Software Engineer",
            "joining_date": "2026-01-01",
            "status": "Active"
        })

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_database_initialization(self):
        """Verify default seeded tables and departments."""
        departments = self.service.departments()
        self.assertGreaterEqual(len(departments), 5)
        self.assertIn("Engineering", departments)
        self.assertIn("HR", departments)

    def test_employee_crud(self):
        """Verify employee creation and retrieval."""
        emp_id = "EMP888"
        self.service.save_employee({
            "employee_id": emp_id,
            "name": "Jane Developer",
            "department": "Engineering",
            "designation": "Staff Engineer",
            "joining_date": "2026-02-01",
            "status": "Active"
        })

        emp = self.service.get_employee(emp_id)
        self.assertIsNotNone(emp)
        self.assertEqual(emp["name"], "Jane Developer")
        self.assertEqual(emp["department"], "Engineering")

    def test_attendance_recording(self):
        """Verify recording attendance."""
        self.service.save_attendance(
            "EMP999",
            "2026-10-15",
            "Present",
            "09:00",
            "18:00",
            "On time"
        )
        records = self.service.attendance_for_date("2026-10-15")
        emp_records = [r for r in records if r["employee_id"] == "EMP999"]
        self.assertTrue(len(emp_records) > 0)
        self.assertEqual(emp_records[0]["status"], "Present")

    def test_leave_management(self):
        """Verify leave request and approval."""
        self.service.create_leave(
            "EMP999",
            "Casual Leave",
            "2026-11-02",
            "2026-11-03",
            "Personal matters"
        )
        with self.db.session() as con:
            row = con.execute("SELECT leave_id FROM leave_requests WHERE employee_id='EMP999' ORDER BY leave_id DESC LIMIT 1").fetchone()
            self.assertIsNotNone(row)
            leave_id = row["leave_id"]
        self.service.approve_leave(leave_id)

    def test_dashboard_metrics(self):
        """Verify dashboard statistics computation."""
        dash = self.service.dashboard()
        self.assertIn("total", dash)
        self.assertIn("present", dash)
        self.assertIn("leave", dash)
        self.assertIn("absent", dash)
        self.assertGreater(dash["total"], 0)


if __name__ == "__main__":
    unittest.main()
