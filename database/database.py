"""SQLite persistence and seeded demo data for the desktop application."""
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path


class Database:
    def __init__(self, path=None):
        root = Path(__file__).resolve().parent.parent
        self.path = Path(path or root / "data" / "employee_analytics.db")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        return con

    @contextmanager
    def session(self):
        """Commit successful work and always release SQLite's file handle."""
        con = self.connect()
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def initialize(self):
        with self.session() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS departments (department_id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, description TEXT);
            CREATE TABLE IF NOT EXISTS employees (employee_id TEXT PRIMARY KEY, name TEXT NOT NULL, department TEXT NOT NULL REFERENCES departments(name), designation TEXT NOT NULL, joining_date TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('Active','Inactive','On Leave')), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS attendance (attendance_id INTEGER PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES employees(employee_id), date TEXT NOT NULL, status TEXT NOT NULL, check_in TEXT, check_out TEXT, working_hours REAL DEFAULT 0, late_minutes INTEGER DEFAULT 0, overtime_hours REAL DEFAULT 0, remarks TEXT, UNIQUE(employee_id,date));
            CREATE TABLE IF NOT EXISTS performance (performance_id INTEGER PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES employees(employee_id), review_period TEXT NOT NULL, productivity REAL NOT NULL CHECK(productivity BETWEEN 0 AND 100), quality REAL NOT NULL CHECK(quality BETWEEN 0 AND 100), punctuality REAL NOT NULL CHECK(punctuality BETWEEN 0 AND 100), teamwork REAL NOT NULL CHECK(teamwork BETWEEN 0 AND 100), overall_score REAL NOT NULL, rating TEXT NOT NULL, remarks TEXT, reviewed_by TEXT, review_date TEXT NOT NULL, UNIQUE(employee_id,review_period));
            CREATE TABLE IF NOT EXISTS leave_requests (leave_id INTEGER PRIMARY KEY, employee_id TEXT NOT NULL REFERENCES employees(employee_id), leave_type TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, days INTEGER NOT NULL, reason TEXT, status TEXT NOT NULL DEFAULT 'Pending', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS holidays (holiday_id INTEGER PRIMARY KEY, date TEXT UNIQUE NOT NULL, name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
            CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance(employee_id);
            CREATE INDEX IF NOT EXISTS idx_performance_employee ON performance(employee_id);
            """)
            for name in ("Engineering", "Finance", "HR", "Marketing", "Sales"):
                con.execute("INSERT OR IGNORE INTO departments(name,description) VALUES (?,?)", (name, f"{name} department"))
            defaults = {"organization_name":"Acme Workforce Pvt. Ltd.", "work_start":"09:00", "work_end":"18:00", "grace_minutes":"10", "theme":"Light"}
            for key, value in defaults.items(): con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES (?,?)", (key,value))
            if con.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0: self._seed(con)

    def _seed(self, con):
        from mock_data.data import EMPLOYEES
        for eid, name, dept, desig, joined, status, _ in EMPLOYEES:
            joined_iso = datetime.strptime(joined, "%d %b %Y").date().isoformat()
            con.execute("INSERT INTO employees(employee_id,name,department,designation,joining_date,status) VALUES (?,?,?,?,?,?)", (eid,name,dept,desig,joined_iso,status))
        today = date.today()
        for d_offset in range(1, 61):
            day = today - timedelta(days=d_offset)
            if day.weekday() >= 5: continue
            for pos, emp in enumerate(EMPLOYEES):
                eid = emp[0]; state = "Present" if (pos + d_offset) % 13 else "Late" if (pos+d_offset)%7 else "Absent"
                ci, co = ("09:20", "18:10") if state == "Late" else ("09:02", "18:06")
                hours = 8.0 if state != "Absent" else 0
                con.execute("INSERT OR IGNORE INTO attendance(employee_id,date,status,check_in,check_out,working_hours,late_minutes,overtime_hours) VALUES (?,?,?,?,?,?,?,?)", (eid,day.isoformat(),state,ci if state != "Absent" else None,co if state != "Absent" else None,hours,20 if state=="Late" else 0,0.1 if state=="Present" else 0))
        for i, emp in enumerate(EMPLOYEES):
            score = emp[-1]; metrics = (score+2, score-1, score, score-1)
            rating = self.rating(score)
            con.execute("INSERT OR IGNORE INTO performance(employee_id,review_period,productivity,quality,punctuality,teamwork,overall_score,rating,reviewed_by,review_date) VALUES (?,?,?,?,?,?,?,?,?,?)", (emp[0], "August " + str(today.year), *metrics, score, rating, "Admin User", today.isoformat()))

    @staticmethod
    def rating(score):
        return "Excellent" if score >= 90 else "Good" if score >= 75 else "Average" if score >= 60 else "Needs Improvement"
