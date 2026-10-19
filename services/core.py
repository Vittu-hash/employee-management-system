"""Business rules and query API used by the CustomTkinter UI."""
from datetime import date, datetime, timedelta
from pathlib import Path
import csv
from database.database import Database


class ValidationError(ValueError): pass


class WorkforceService:
    def __init__(self, database=None): self.db = database or Database()
    def _query(self, sql, args=()):
        with self.db.session() as con: return con.execute(sql, args).fetchall()
    def departments(self): return [r["name"] for r in self._query("SELECT name FROM departments ORDER BY name")]
    def employees(self, search="", department="All Departments", status="All Status"):
        where, args = ["1=1"], []
        if search: where.append("(employee_id LIKE ? OR name LIKE ?)"); args += [f"%{search}%", f"%{search}%"]
        if department != "All Departments": where.append("department=?"); args.append(department)
        if status != "All Status": where.append("status=?"); args.append(status)
        return self._query("SELECT * FROM employees WHERE " + " AND ".join(where) + " ORDER BY name", args)
    def get_employee(self, employee_id):
        rows=self._query("SELECT * FROM employees WHERE employee_id=?",(employee_id,)); return rows[0] if rows else None
    def save_employee(self, values, existing_id=None):
        eid=values.get("employee_id", "").strip().upper(); name=" ".join(values.get("name", "").split()); dept=values.get("department", ""); desig=" ".join(values.get("designation", "").split()); joined=values.get("joining_date", ""); status=values.get("status", "Active")
        if not all((eid,name,dept,desig,joined)): raise ValidationError("Please complete all employee fields.")
        try: datetime.strptime(joined,"%Y-%m-%d")
        except ValueError: raise ValidationError("Joining date must use YYYY-MM-DD.")
        if datetime.strptime(joined,"%Y-%m-%d").date() > date.today(): raise ValidationError("Joining date cannot be in the future.")
        if dept not in self.departments(): raise ValidationError("Select a valid department.")
        try:
            with self.db.session() as con:
                if existing_id:
                    con.execute("UPDATE employees SET name=?,department=?,designation=?,joining_date=?,status=?,updated_at=CURRENT_TIMESTAMP WHERE employee_id=?",(name,dept,desig,joined,status,existing_id))
                else: con.execute("INSERT INTO employees(employee_id,name,department,designation,joining_date,status) VALUES (?,?,?,?,?,?)",(eid,name,dept,desig,joined,status))
        except Exception as exc:
            if "UNIQUE" in str(exc): raise ValidationError("Employee ID already exists.")
            raise ValidationError("Unable to save employee.")
    def deactivate_employee(self,eid):
        with self.db.session() as con: con.execute("UPDATE employees SET status='Inactive',updated_at=CURRENT_TIMESTAMP WHERE employee_id=?",(eid,))
    def activate_employee(self,eid):
        """Reactivate the existing employee record without changing its ID or history."""
        with self.db.session() as con:
            if con.execute("UPDATE employees SET status='Active',updated_at=CURRENT_TIMESTAMP WHERE employee_id=?", (eid,)).rowcount != 1:
                raise ValidationError("Employee not found.")
    def attendance_summary(self, eid=None, start=None, end=None):
        start=start or (date.today()-timedelta(days=30)).isoformat(); end=end or date.today().isoformat(); args=[start,end]; clause="date BETWEEN ? AND ?"
        if eid: clause+=" AND employee_id=?";args.append(eid)
        rows=self._query(f"SELECT status,COUNT(*) count,COALESCE(AVG(working_hours),0) avg_hours,COALESCE(SUM(overtime_hours),0) overtime FROM attendance WHERE {clause} GROUP BY status",args); out={"Present":0,"Absent":0,"Leave":0,"Late":0,"Half Day":0,"Work From Home":0,"avg_hours":0,"overtime":0}
        for r in rows: out[r["status"]]=r["count"];out["avg_hours"] = max(out["avg_hours"],r["avg_hours"]);out["overtime"] += r["overtime"]
        total=sum(out[s] for s in ("Present","Absent","Late","Half Day","Work From Home")); equivalent=out["Present"]+out["Late"]+out["Work From Home"]+.5*out["Half Day"];out["percentage"]=round(100*equivalent/total,1) if total else 0;return out
    def attendance_for_date(self, day, include_inactive=False):
        """Return the editable daily attendance state; normal sessions show active staff only."""
        return self._query("""SELECT e.employee_id,e.name,e.department,a.status
                                   ,a.check_in,a.check_out
                            FROM employees e LEFT JOIN attendance a
                              ON a.employee_id=e.employee_id AND a.date=?
                            WHERE (? OR e.status!='Inactive') ORDER BY e.name""", (day, int(include_inactive)))
    def daily_attendance_summary(self, day):
        rows = self._query("SELECT status, COUNT(*) n FROM attendance WHERE date=? GROUP BY status", (day,))
        counts = {r["status"]: r["n"] for r in rows}
        total = self._query("SELECT COUNT(*) n FROM employees WHERE status!='Inactive'")[0]["n"]
        return {"total": total, "present": counts.get("Present", 0) + counts.get("Late", 0) + counts.get("Work From Home", 0),
                "absent": counts.get("Absent", 0), "leave": counts.get("Leave", 0)}
    def department_attendance(self, day):
        return self._query("""SELECT e.department,
                       ROUND(100.0 * SUM(CASE WHEN a.status IN ('Present','Late','Work From Home') THEN 1 ELSE 0 END)
                       / NULLIF(COUNT(e.employee_id), 0), 1) rate
                       FROM employees e LEFT JOIN attendance a ON a.employee_id=e.employee_id AND a.date=?
                       WHERE e.status!='Inactive' GROUP BY e.department ORDER BY e.department""", (day,))
    def save_attendance(self,eid,day,status,check_in="",check_out="",remarks=""):
        try: datetime.strptime(day,"%Y-%m-%d")
        except ValueError: raise ValidationError("Date must use YYYY-MM-DD.")
        if not self.get_employee(eid): raise ValidationError("Choose an employee.")
        if status not in ("Present", "Absent", "Leave", "Late", "Half Day", "Work From Home"): raise ValidationError("Choose a valid attendance status.")
        hours=late=overtime=0
        if status in ("Present","Late","Work From Home","Half Day"):
            if not check_in and not check_out:
                check_in = check_out = ""
            elif not check_in:
                raise ValidationError("Present attendance requires an entry time.")
            if not check_in and not check_out:
                # Daily status marking intentionally does not require time entry.
                pass
            else:
                try:
                    ci=datetime.strptime(check_in,"%H:%M")
                    if check_out:
                        co=datetime.strptime(check_out,"%H:%M")
                        if co <= ci: raise ValidationError("Exit time must be after entry time.")
                        hours=round((co-ci).seconds/3600,2); overtime=round(max(0,hours-8),2)
                    late=max(0,(ci.hour*60+ci.minute)-(9*60+10))
                except ValidationError:
                    raise
                except ValueError:
                    raise ValidationError("Times must use 24-hour HH:MM format.")
        try:
            with self.db.session() as con: con.execute("INSERT INTO attendance(employee_id,date,status,check_in,check_out,working_hours,late_minutes,overtime_hours,remarks) VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(employee_id,date) DO UPDATE SET status=excluded.status,check_in=excluded.check_in,check_out=excluded.check_out,working_hours=excluded.working_hours,late_minutes=excluded.late_minutes,overtime_hours=excluded.overtime_hours,remarks=excluded.remarks",(eid,day,status,check_in or None,check_out or None,hours,late,overtime,remarks))
        except Exception as exc: raise ValidationError("Unable to save attendance.")
    def save_attendance_batch(self, day, records):
        """Persist one daily editing session atomically, using attendance's unique employee/date key."""
        for record in records:
            self.save_attendance(record["employee_id"], day, record["status"], record.get("check_in", ""), record.get("check_out", ""))

    def analytics(self, start, end, department="All Departments", employee_id="All Employees"):
        """Cohesive analytics dataset scoped by date, department and optional employee."""
        clauses, args = ["a.date BETWEEN ? AND ?"], [start, end]
        if department != "All Departments": clauses.append("e.department=?"); args.append(department)
        if employee_id != "All Employees": clauses.append("e.employee_id=?"); args.append(employee_id)
        where = " AND ".join(clauses)
        attendance = self._query(f"SELECT a.*,e.department,e.name FROM attendance a JOIN employees e ON e.employee_id=a.employee_id WHERE {where}", args)
        perf_clauses, perf_args = ["1=1"], []
        if department != "All Departments": perf_clauses.append("e.department=?"); perf_args.append(department)
        if employee_id != "All Employees": perf_clauses.append("e.employee_id=?"); perf_args.append(employee_id)
        perf_where = " AND ".join(perf_clauses)
        performance = self._query(f"SELECT p.*,e.department,e.name FROM performance p JOIN employees e ON e.employee_id=p.employee_id WHERE {perf_where}", perf_args)
        active_clause = "status!='Inactive'" + (" AND department=?" if department != "All Departments" else "") + (" AND employee_id=?" if employee_id != "All Employees" else "")
        active_args = ([department] if department != "All Departments" else []) + ([employee_id] if employee_id != "All Employees" else [])
        total = self._query(f"SELECT COUNT(*) n FROM employees WHERE {active_clause}", active_args)[0]["n"]
        present = [r for r in attendance if r["status"] in ("Present", "Late", "Work From Home")]
        valid_hours = [r["working_hours"] for r in present if r["check_in"] and r["check_out"]]
        dist = {k: sum(r["status"] == k for r in attendance) for k in ("Present", "Absent", "Leave")}
        trend = {}
        for r in attendance:
            trend.setdefault(r["date"], []).append(r["status"] in ("Present", "Late", "Work From Home"))
        departments = {}
        for r in attendance: departments.setdefault(r["department"], []).append(r["status"] in ("Present", "Late", "Work From Home"))
        perf_by_dept = {}
        for r in performance: perf_by_dept.setdefault(r["department"], []).append(r["overall_score"])
        metrics = {m: round(sum(r[m] for r in performance)/len(performance), 1) if performance else 0 for m in ("productivity","quality","punctuality","teamwork")}
        ratings = {k: sum(r["rating"] == k for r in performance) for k in ("Excellent","Good","Average","Needs Improvement")}
        ranked = sorted(performance, key=lambda r:r["overall_score"], reverse=True)[:5]
        # Existing, tangible signals only: low review score and recorded absence rate.
        people = {}
        for r in attendance: people.setdefault(r["employee_id"], {"name":r["name"], "total":0, "absent":0}); people[r["employee_id"]]["total"] += 1; people[r["employee_id"]]["absent"] += r["status"] == "Absent"
        for r in performance: people.setdefault(r["employee_id"], {"name":r["name"], "total":0, "absent":0})["score"] = r["overall_score"]
        attention = [v for v in people.values() if v.get("score",100) < 60 or (v["total"] and v["absent"]/v["total"] >= .2)]
        return {"total": total, "attendance_rate": round(100*len(present)/len(attendance),1) if attendance else 0,
                "average_performance": round(sum(r["overall_score"] for r in performance)/len(performance),1) if performance else 0,
                "average_hours": round(sum(valid_hours)/len(valid_hours),2) if valid_hours else 0,
                "distribution":dist, "trend":[(k,round(100*sum(v)/len(v),1)) for k,v in sorted(trend.items())],
                "department_attendance":[(k,round(100*sum(v)/len(v),1)) for k,v in sorted(departments.items())],
                "department_performance":[(k,round(sum(v)/len(v),1)) for k,v in sorted(perf_by_dept.items())],
                "performance_distribution":ratings, "metrics":metrics, "top":ranked, "attention":attention}
    def save_performance(self,eid,period,metrics,remarks=""):
        if not eid or not period: raise ValidationError("Employee and review period are required.")
        try: vals=[float(x) for x in metrics]
        except ValueError: raise ValidationError("Performance scores must be numeric.")
        if any(x<0 or x>100 for x in vals): raise ValidationError("Scores must be between 0 and 100.")
        if any(x not in range(10, 101, 10) for x in vals): raise ValidationError("Choose scores in increments of 10.")
        overall=round(sum(vals)/4,1); rating=self.db.rating(overall)
        with self.db.session() as con: con.execute("INSERT INTO performance(employee_id,review_period,productivity,quality,punctuality,teamwork,overall_score,rating,remarks,reviewed_by,review_date) VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(employee_id,review_period) DO UPDATE SET productivity=excluded.productivity,quality=excluded.quality,punctuality=excluded.punctuality,teamwork=excluded.teamwork,overall_score=excluded.overall_score,rating=excluded.rating,remarks=excluded.remarks,review_date=excluded.review_date",(eid,period,*vals,overall,rating,remarks,"Admin User",date.today().isoformat()))
        return overall,rating
    def dashboard(self):
        today=date.today().isoformat(); total=self._query("SELECT COUNT(*) n FROM employees WHERE status!='Inactive'")[0]["n"]
        status={r["status"]:r["n"] for r in self._query("SELECT status,COUNT(*) n FROM attendance WHERE date=? GROUP BY status",(today,))}
        top=self._query("SELECT e.name,e.department,p.overall_score FROM performance p JOIN employees e ON e.employee_id=p.employee_id ORDER BY p.overall_score DESC LIMIT 5")
        dept=self._query("SELECT e.department,ROUND(AVG(p.overall_score),1) score FROM employees e LEFT JOIN performance p ON p.employee_id=e.employee_id WHERE e.status!='Inactive' GROUP BY e.department ORDER BY score DESC")
        trend=self._query("SELECT date,ROUND(100.0*SUM(CASE WHEN status IN ('Present','Late','Work From Home') THEN 1 WHEN status='Half Day' THEN .5 ELSE 0 END)/COUNT(*),1) rate FROM attendance WHERE date>=? GROUP BY date ORDER BY date",((date.today()-timedelta(days=30)).isoformat(),))
        return {"total":total,"present":status.get("Present",0)+status.get("Late",0)+status.get("Work From Home",0),"leave":status.get("Leave",0),"absent":status.get("Absent",0),"top":top,"departments":dept,"trend":trend}
    def performance_distribution(self):
        rows = self._query("SELECT rating, COUNT(*) n FROM performance GROUP BY rating")
        return {r["rating"]: r["n"] for r in rows}
    def profile(self,eid):
        emp=self.get_employee(eid); attendance=self.attendance_summary(eid, "2000-01-01", date.today().isoformat()); perf=self._query("SELECT * FROM performance WHERE employee_id=? ORDER BY review_date DESC",(eid,)); avg=round(sum(r["overall_score"] for r in perf)/len(perf),1) if perf else 0;return emp,attendance,avg,perf
    def export_employees_csv(self):
        folder=Path(__file__).resolve().parent.parent/"exports";folder.mkdir(exist_ok=True); target=folder/f"employees_{date.today():%Y_%m_%d}.csv"; index=1
        while target.exists(): target=folder/f"employees_{date.today():%Y_%m_%d}_{index}.csv";index+=1
        rows=self.employees()
        with target.open("w",newline="",encoding="utf-8") as f:
            w=csv.writer(f);w.writerow(["Employee ID","Name","Department","Designation","Joining Date","Status"]);w.writerows([[r[k] for k in ("employee_id","name","department","designation","joining_date","status")] for r in rows])
        return target
    def _export_path(self, stem, suffix):
        folder=Path(__file__).resolve().parent.parent/"exports";folder.mkdir(exist_ok=True);target=folder/f"{stem}_{date.today():%Y_%m_%d}{suffix}";n=1
        while target.exists(): target=folder/f"{stem}_{date.today():%Y_%m_%d}_{n}{suffix}";n+=1
        return target
    def export_employees_excel(self):
        try:
            import pandas as pd
            target=self._export_path("employees", ".xlsx")
            pd.DataFrame([dict(r) for r in self.employees()]).to_excel(target,index=False)
            return target
        except ImportError as exc: raise ValidationError("Excel export requires pandas and openpyxl.") from exc
    def export_employee_pdf(self, employee_id):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen.canvas import Canvas
            emp,attendance,average,reviews=self.profile(employee_id)
            if not emp: raise ValidationError("Employee not found.")
            target=self._export_path(f"employee_{employee_id}", ".pdf");pdf=Canvas(str(target),pagesize=A4);pdf.setTitle("Employee report")
            y=790;pdf.setFont("Helvetica-Bold",18);pdf.drawString(48,y,"Employee Report");y-=38;pdf.setFont("Helvetica",11)
            for line in (f"Name: {emp['name']}",f"Employee ID: {emp['employee_id']}",f"Department: {emp['department']}",f"Designation: {emp['designation']}",f"Attendance: {attendance['percentage']}%",f"Average Performance: {average}"):
                pdf.drawString(48,y,line);y-=22
            pdf.save();return target
        except ImportError as exc: raise ValidationError("PDF export requires reportlab.") from exc
    def create_leave(self, employee_id, leave_type, start_date, end_date, reason):
        try: start=datetime.strptime(start_date,"%Y-%m-%d").date();end=datetime.strptime(end_date,"%Y-%m-%d").date()
        except ValueError: raise ValidationError("Leave dates must use YYYY-MM-DD.")
        if not self.get_employee(employee_id): raise ValidationError("Choose a valid employee.")
        if end < start: raise ValidationError("Leave end date must be after start date.")
        if leave_type not in ("Casual Leave","Sick Leave","Earned Leave","Unpaid Leave","Emergency Leave"): raise ValidationError("Choose a valid leave type.")
        days=sum(1 for i in range((end-start).days+1) if (start+timedelta(days=i)).weekday()<5)
        with self.db.session() as con: con.execute("INSERT INTO leave_requests(employee_id,leave_type,start_date,end_date,days,reason,status) VALUES (?,?,?,?,?,?,?)",(employee_id,leave_type,start.isoformat(),end.isoformat(),days,reason,"Pending"))
    def approve_leave(self, leave_id):
        with self.db.session() as con:
            leave=con.execute("SELECT * FROM leave_requests WHERE leave_id=?",(leave_id,)).fetchone()
            if not leave: raise ValidationError("Leave request not found.")
            con.execute("UPDATE leave_requests SET status='Approved' WHERE leave_id=?",(leave_id,))
            start=datetime.strptime(leave["start_date"],"%Y-%m-%d").date();end=datetime.strptime(leave["end_date"],"%Y-%m-%d").date()
            for i in range((end-start).days+1):
                day=start+timedelta(days=i)
                if day.weekday()<5: con.execute("INSERT INTO attendance(employee_id,date,status) VALUES (?,?,'Leave') ON CONFLICT(employee_id,date) DO UPDATE SET status='Leave'",(leave["employee_id"],day.isoformat()))
    def settings(self): return {r["key"]:r["value"] for r in self._query("SELECT key,value FROM settings")}
    def save_settings(self, values):
        with self.db.session() as con:
            for k,v in values.items(): con.execute("INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(k,str(v)))
