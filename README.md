# Employee Attendance & Performance Analytics

A modern desktop application built with Python and **CustomTkinter** for managing workforce records, tracking daily attendance, evaluating quarterly performance, handling leave workflows, and generating analytics reports.

---

## Features

- **Employee Directory**: Search and filter workforce records by department, status, or keyword. Add, update, activate, and deactivate employee profiles.
- **Attendance Management**: Record daily attendance states (`Present`, `Late`, `Half Day`, `Work From Home`, `Absent`, `Leave`), log check-in/out times, and automatically calculate working hours, late minutes, and overtime.
- **Performance Evaluation**: Evaluate staff on productivity, quality, punctuality, and teamwork with automatic score and rating aggregation (`Outstanding`, `Exceeds Expectations`, `Meets Expectations`, etc.).
- **Leave Request Workflow**: Submit and approve leave requests with automatic attendance status updates across working days.
- **Analytics & Visualizations**: Interactive charts powered by Matplotlib showing department attendance rates, attendance trends, score distributions, and top performers.
- **Data Exporting**: Export directory rosters to Excel (`.xlsx`) or CSV, and export formatted single-employee profiles to PDF via ReportLab.
- **Theming & Preferences**: Modern interface with configurable organization settings, work schedules, grace periods, and theme modes.

---

## Tech Stack

- **GUI Framework**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Database**: SQLite3 (centralized session context and foreign key enforcement)
- **Data Processing**: Pandas, OpenPyXL
- **Plotting & Visuals**: Matplotlib
- **Document Generation**: ReportLab
- **Language**: Python 3.10+

---

## Project Structure

```
Employee Management System/
├── main.py                 # Application entry point
├── requirements.txt         # Python package dependencies
├── data/                   # SQLite database directory (auto-created)
│   └── .gitkeep
├── database/               # Database management and schema initialization
│   ├── __init__.py
│   └── database.py
├── mock_data/              # Initial seed data definitions
│   ├── __init__.py
│   └── data.py
├── services/               # Core business logic and query APIs
│   ├── __init__.py
│   └── core.py
├── ui/                     # CustomTkinter interface components and screens
│   ├── __init__.py
│   ├── app.py
│   ├── components.py
│   └── theme.py
└── tests/                  # Automated unit test suite
    └── test_services.py
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Vittu-hash/employee-management-system.git
   cd employee-management-system
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Launch the desktop UI with:
```bash
python main.py
```

On first launch, the application automatically initializes the SQLite schema in `data/employee_analytics.db` and populates realistic mock data for departments and team members.

---

## Running Tests

Execute the unit test suite:
```bash
python -m unittest discover -s tests -v
```

---

## License

This project is licensed under the MIT License.
