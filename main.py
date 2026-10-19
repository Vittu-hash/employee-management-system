"""Launch the Employee Attendance & Performance Analytics desktop UI."""

import sys
from pathlib import Path

# Keep local package imports reliable even when launched from another folder.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database import Database
from services import WorkforceService
from ui.app import EmployeeAnalyticsApp


if __name__ == "__main__":
    app = EmployeeAnalyticsApp(WorkforceService(Database()))
    app.mainloop()
