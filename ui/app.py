import customtkinter as ctk
from datetime import date, timedelta
from tkinter import messagebox
from ui.theme import COLORS, UI_FONT
from ui.components import label, SectionCard, MetricCard, PrimaryButton, StatusBadge, Toast, AddEmployeeModal

ctk.set_appearance_mode("light")
PAGES = ("Dashboard", "Employees", "Attendance", "Performance", "Analytics", "Reports", "Settings")


class EmployeeAnalyticsApp(ctk.CTk):
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"

    def __init__(self, service=None):
        super().__init__()
        if service is None:
            from services import WorkforceService
            service = WorkforceService()
        self.service = service; self.title("Employee Attendance & Performance Analytics")
        self.geometry("1440x900"); self.minsize(1200, 700); self.configure(fg_color=COLORS["papaya_whip"])
        self.grid_rowconfigure(1, weight=1); self.grid_columnconfigure(1, weight=1); self.collapsed = False
        self.current_page = None; self.navigation_history = []
        self._sidebar(); self._topbar(); self.content = ctk.CTkFrame(self, fg_color=COLORS["papaya_whip"], corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew"); self.show_page("Dashboard"); self.show_login()

    def show_login(self):
        """Display the local administrator sign-in screen before app access."""
        self.login_overlay = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.login_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        panel = SectionCard(self.login_overlay, width=440, height=490)
        panel.place(relx=.5, rely=.5, anchor="center"); panel.pack_propagate(False)
        ctk.CTkLabel(panel, text="EA", width=56, height=56, corner_radius=14,
                     fg_color=COLORS["active_accent"], text_color="white",
                     font=(UI_FONT, 20, "bold")).pack(pady=(45, 16))
        label(panel, "Welcome back", 26, "bold", role="display").pack()
        label(panel, "Sign in to Employee Analytics", 13, "normal", COLORS["text_secondary"]).pack(pady=(5, 28))
        self.login_user = ctk.CTkEntry(panel, placeholder_text="Administrator username", height=42,
                                       fg_color=COLORS["surface"], border_color=COLORS["line"], text_color=COLORS["text_primary"])
        self.login_user.pack(fill="x", padx=42, pady=(0, 12)); self.login_user.focus_set()
        self.login_password = ctk.CTkEntry(panel, placeholder_text="Password", show="•", height=42,
                                           fg_color=COLORS["surface"], border_color=COLORS["line"], text_color=COLORS["text_primary"])
        self.login_password.pack(fill="x", padx=42)
        self.login_error = label(panel, "", 12, "normal", COLORS["danger"])
        self.login_error.pack(anchor="w", padx=42, pady=(8, 0))
        PrimaryButton(panel, "Sign In", command=self.authenticate, width=356).pack(pady=(16, 10))
        label(panel, "Demo credentials: admin / admin123", 11, "normal", COLORS["text_secondary"]).pack()
        self.login_password.bind("<Return>", lambda _: self.authenticate())

    def authenticate(self):
        if self.login_user.get().strip() == self.ADMIN_USERNAME and self.login_password.get() == self.ADMIN_PASSWORD:
            self.login_overlay.destroy(); Toast(self, "Signed in successfully.", "success")
        else:
            self.login_error.configure(text="Incorrect username or password.")
            self.login_password.delete(0, "end")

    def _sidebar(self):
        self.sidebar=ctk.CTkFrame(self,width=260,fg_color=COLORS["sidebar"],corner_radius=0);self.sidebar.grid(row=0,column=0,rowspan=2,sticky="nsew");self.sidebar.grid_propagate(False)
        brand=ctk.CTkFrame(self.sidebar,fg_color="transparent");brand.pack(fill="x",padx=20,pady=(24,30));ctk.CTkLabel(brand,text="EA",width=42,height=42,corner_radius=11,fg_color=COLORS["active_accent"],text_color="white",font=(UI_FONT,16,"bold")).pack(side="left")
        self.brand=label(brand,"EMPLOYEE\nANALYTICS",17,"bold","white",justify="left");self.brand.pack(side="left",padx=10);self.buttons={};nav=ctk.CTkFrame(self.sidebar,fg_color="transparent");nav.pack(fill="x",padx=12)
        for page in PAGES:
            b=ctk.CTkButton(nav,text="  "+page,anchor="w",height=43,corner_radius=9,fg_color="transparent",hover_color=COLORS["sidebar_hover"],text_color=COLORS["sidebar_text"],font=(UI_FONT,13,"bold"),command=lambda p=page:self.show_page(p));b.pack(fill="x",pady=3);self.buttons[page]=b
        ctk.CTkFrame(self.sidebar,fg_color="transparent").pack(expand=True,fill="both");profile=ctk.CTkFrame(self.sidebar,fg_color=COLORS["sidebar_hover"],corner_radius=12);profile.pack(fill="x",padx=14,pady=14)
        ctk.CTkLabel(profile,text="AU",width=34,height=34,corner_radius=17,fg_color=COLORS["dark_cyan"],text_color="white",font=(UI_FONT,11,"bold")).pack(side="left",padx=10,pady=10);self.admin=label(profile,"Admin User\nSystem Administrator",11,"normal","white",justify="left");self.admin.pack(side="left")

    def _topbar(self):
        bar=ctk.CTkFrame(self,height=68,fg_color="white",corner_radius=0);bar.grid(row=0,column=1,sticky="ew");bar.grid_propagate(False);bar.grid_columnconfigure(1,weight=1)
        ctk.CTkButton(bar,text="=",width=40,height=36,fg_color="transparent",hover_color=COLORS["secondary"],text_color=COLORS["primary"],font=(UI_FONT,19),command=self._collapse).grid(row=0,column=0,padx=18,pady=15);self.context=label(bar,"WORKFORCE OVERVIEW",11,"bold",COLORS["muted"]);self.context.grid(row=0,column=1,sticky="w");label(bar,date.today().strftime("%d %b %Y"),12,"bold",COLORS["primary"],role="data").grid(row=0,column=2,padx=22)
    def _collapse(self):
        self.collapsed=not self.collapsed;self.sidebar.configure(width=76 if self.collapsed else 260);self.brand.configure(text="" if self.collapsed else "EMPLOYEE\nANALYTICS");self.admin.configure(text="" if self.collapsed else "Admin User\nSystem Administrator")
        for page,b in self.buttons.items():b.configure(text="" if self.collapsed else "  "+page,anchor="center" if self.collapsed else "w")
    def _clear(self):
        for c in self.content.winfo_children():c.destroy()
    def show_page(self,page, record_history=True):
        if record_history and self.current_page and self.current_page != page and self.current_page in PAGES:
            self.navigation_history.append(self.current_page)
        self.current_page = page
        self._clear();self.context.configure(text=page.upper())
        for name,b in self.buttons.items():b.configure(fg_color=COLORS["active_nav"] if name==page else "transparent")
        getattr(self,page.lower())()
    def go_back(self):
        if self.navigation_history:
            self.show_page(self.navigation_history.pop(), record_history=False)
        else:
            self.show_page("Dashboard", record_history=False)
    def header(self,title,subtitle,action=None):
        f=ctk.CTkFrame(self.content,fg_color="transparent");f.pack(fill="x",padx=30,pady=(26,18))
        if self.current_page != "Dashboard":
            ctk.CTkButton(f, text="← Back", width=78, height=30, fg_color="transparent", hover_color=COLORS["secondary"],
                          text_color=COLORS["primary"] if self.navigation_history else COLORS["muted"],
                          state="normal" if self.navigation_history else "disabled", command=self.go_back).pack(side="left", pady=5)
        if action:PrimaryButton(f,action[0],command=action[1],width=150).pack(side="right",pady=5)
        heading=ctk.CTkFrame(f,fg_color="transparent");heading.pack(side="left",padx=14)
        label(heading,title,27,"bold",COLORS["text_primary"],role="display").pack(anchor="w");label(heading,subtitle,13,"normal",COLORS["text_secondary"]).pack(anchor="w",pady=(4,0))

    def dashboard(self):
        self.header("Good morning, Admin!", "Here’s what’s happening with your workforce today.");body=ctk.CTkScrollableFrame(self.content,fg_color="transparent");body.pack(fill="both",expand=True,padx=30,pady=(0,18));d=self.service.dashboard();total=max(1,d["total"])
        grid=ctk.CTkFrame(body,fg_color="transparent");grid.pack(fill="x",pady=(0,18));grid.grid_columnconfigure((0,1,2,3),weight=1)
        for i,(title,value,sub,color) in enumerate((("Total Employees",d["total"],"Active workforce",COLORS["dark_teal"]),("Present Today",d["present"],f"{d['present']/total:.1%} of employees",COLORS["dark_cyan"]),("On Leave",d["leave"],f"{d['leave']/total:.1%} of employees",COLORS["pearl_aqua"]),("Absent Today",d["absent"],f"{d['absent']/total:.1%} of employees",COLORS["oxidized_iron"]))):MetricCard(grid,"•",title,str(value),sub,color).grid(row=0,column=i,sticky="ew",padx=7)
        charts=ctk.CTkFrame(body,fg_color="transparent");charts.pack(fill="x",pady=(0,18));charts.grid_columnconfigure((0,1),weight=1)
        self.donut_card(charts,"Today's Attendance",[("Present",d["present"]),("Absent",d["absent"]),("Leave",d["leave"])]).grid(row=0,column=0,sticky="nsew",padx=(0,8))
        self.bars(charts,"Department Performance",[(r["department"],r["score"] or 0) for r in d["departments"]]).grid(row=0,column=1,sticky="nsew",padx=(8,0))
        self.top_performers(body,d["top"])
    def line_card(self,master,title,points):
        card=SectionCard(master,height=235);card.grid_propagate(False);label(card,title,17,"bold").pack(anchor="w",padx=18,pady=15)
        if len(points)<2:label(card,"Not enough data to display this chart.",12,"normal",COLORS["muted"]).pack(expand=True);return card
        c=ctk.CTkCanvas(card,bg="white",highlightthickness=0,height=165);c.pack(fill="both",expand=True,padx=14,pady=(0,12));vals=points[-10:];pts=[(15+i*(550/max(1,len(vals)-1)),120-float(v)) for i,(_,v) in enumerate(vals)]
        for y in (30,65,100):c.create_line(12,y,570,y,fill=COLORS["grid"],dash=(2,3))
        c.create_line(*sum(([x,y] for x,y in pts),[]),fill=COLORS["primary"],width=3,smooth=True)
        for x,y in pts:c.create_oval(x-3,y-3,x+3,y+3,fill=COLORS["primary_hover"],outline="")
        return card
    def bars(self,master,title,rows):
        card=SectionCard(master,height=235);card.grid_propagate(False);label(card,title,17,"bold").pack(anchor="w",padx=18,pady=(15,8))
        if not rows:label(card,"Not enough data to display this chart.",12,"normal",COLORS["muted"]).pack(expand=True)
        for i,(name,score) in enumerate(rows):
            color = (COLORS["primary"], COLORS["primary_hover"], COLORS["regal_navy"])[i % 3]
            r=ctk.CTkFrame(card,fg_color="transparent");r.pack(fill="x",padx=18,pady=4);label(r,name,11,"normal",COLORS["muted"],width=90).pack(side="left");p=ctk.CTkProgressBar(r,height=9,corner_radius=5,progress_color=color,fg_color=COLORS["secondary"]);p.set(float(score)/100);p.pack(side="left",fill="x",expand=True,padx=8);label(r,f"{score:.1f}%",11,"bold",role="data").pack(side="right")
        return card
    def donut_card(self, master, title, rows):
        card=SectionCard(master,height=235);card.grid_propagate(False);label(card,title,17,"bold").pack(anchor="w",padx=18,pady=(15,4))
        total=sum(value for _,value in rows)
        if not total:
            label(card,"No attendance recorded for today.",12,"normal",COLORS["muted"]).pack(expand=True); return card
        canvas=ctk.CTkCanvas(card,bg=COLORS["surface"],highlightthickness=0,height=160);canvas.pack(fill="both",expand=True,padx=16,pady=(0,12))
        colors={"Present":COLORS["primary"],"Absent":COLORS["danger"],"Leave":COLORS["blue_slate"],"Excellent":COLORS["primary"],"Good":COLORS["primary_hover"],"Average":COLORS["blue_slate"],"Needs Improvement":COLORS["danger"]}
        start=90
        for name,value in rows:
            extent=360*value/total
            canvas.create_arc(30,8,170,148,start=start,extent=extent,fill=colors.get(name,COLORS["primary"]),outline=COLORS["surface"],width=2)
            start+=extent
        canvas.create_oval(72,50,128,106,fill=COLORS["surface"],outline="")
        canvas.create_text(100,74,text=str(total),fill=COLORS["text_primary"],font=(UI_FONT,18,"bold"))
        canvas.create_text(100,92,text="TOTAL",fill=COLORS["muted"],font=(UI_FONT,9,"bold"))
        for i,(name,value) in enumerate(rows):
            y=32+i*32; canvas.create_rectangle(210,y,220,y+10,fill=colors.get(name,COLORS["primary"]),outline="")
            canvas.create_text(230,y+5,text=name,anchor="w",fill=COLORS["text_secondary"],font=(UI_FONT,11))
            canvas.create_text(360,y+5,text=str(value),anchor="e",fill=COLORS["text_primary"],font=("JetBrains Mono",11,"bold"))
        return card
    def top_performers(self,master,rows):
        card=SectionCard(master);card.pack(fill="x");label(card,"Top Performers",17,"bold").pack(anchor="w",padx=18,pady=(16,10))
        if not rows:label(card,"No performance reviews available.",12,"normal",COLORS["muted"]).pack(padx=18,pady=20)
        rank_colors=(COLORS["golden_orange"], COLORS["burnt_caramel"], COLORS["rusty_spice"], COLORS["dark_cyan"], COLORS["dark_teal"])
        for i,r in enumerate(rows,1):
            row=ctk.CTkFrame(card,fg_color="transparent");row.pack(fill="x",padx=18,pady=5)
            label(row,f"{i}",13,"bold",rank_colors[min(i-1,4)],role="data",width=28).pack(side="left")
            label(row,r["name"],13,"bold",width=145,anchor="w").pack(side="left");label(row,r["department"],12,"normal",COLORS["text_secondary"],width=170,anchor="w").pack(side="left");label(row,f"{r['overall_score']:.1f}",13,"bold",COLORS["text_primary"],role="data").pack(side="left")

    def employees(self):
        self.header("Employees","Manage your organization’s workforce",("+ Add Employee",lambda:AddEmployeeModal(self)));body=ctk.CTkFrame(self.content,fg_color="transparent");body.pack(fill="both",expand=True,padx=30,pady=(0,24));f=ctk.CTkFrame(body,fg_color="transparent");f.pack(fill="x",pady=(0,15));search=ctk.CTkEntry(f,placeholder_text="Search name or employee ID...",height=39,width=330,corner_radius=9,fg_color="white",border_color=COLORS["line"]);search.pack(side="left");table=SectionCard(body);table.pack(fill="both",expand=True)
        self.dept=ctk.CTkOptionMenu(f,values=["All Departments"]+self.service.departments(),height=38,width=145,command=lambda _:self.employee_rows(table,search.get()),fg_color="white",button_color=COLORS["steel_blue"],text_color=COLORS["ink"]);self.dept.pack(side="left",padx=8);self.status=ctk.CTkOptionMenu(f,values=["All","Active","Inactive","On Leave"],height=38,width=120,command=lambda _:self.employee_rows(table,search.get()),fg_color="white",button_color=COLORS["steel_blue"],text_color=COLORS["ink"]);self.status.set("All");self.status.pack(side="left",padx=8);search.bind("<KeyRelease>",lambda _:self.employee_rows(table,search.get()));self.employee_rows(table,"")
    def employee_rows(self,table,q):
        for x in table.winfo_children():x.destroy()
        headers=("Employee ID","Employee","Department","Designation","Joining Date","Status","Actions");widths=(105,190,125,175,115,100,50);h=ctk.CTkFrame(table,fg_color=COLORS["surface_secondary"],corner_radius=10);h.pack(fill="x",padx=12,pady=(12,5))
        for x,w in zip(headers,widths):label(h,x.upper(),11,"bold",COLORS["text_secondary"],width=w,anchor="w",role="display").pack(side="left",padx=6,pady=11)
        selected_status = "All Status" if self.status.get() == "All" else self.status.get()
        rows=self.service.employees(q,self.dept.get(),selected_status)
        if not rows:label(table,"No employees found\nTry changing your search or filters.",15,"normal",COLORS["muted"],justify="center").pack(expand=True)
        for r in rows:
            row=ctk.CTkFrame(table,fg_color="transparent",height=48);row.pack(fill="x",padx=12,pady=2)
            for key,w in zip(("employee_id","name","department","designation","joining_date"),widths):label(row,r[key],12,"bold" if key=="name" else "normal",width=w,anchor="w").pack(side="left",padx=6,pady=8)
            StatusBadge(row,r["status"],width=100).pack(side="left",padx=6)
            action = "Activate" if r["status"] == "Inactive" else "Deactivate"
            ctk.CTkButton(row,text=action,width=86,height=28,fg_color="transparent",hover_color=COLORS["soft_blue"],text_color=COLORS["primary"] if action=="Activate" else COLORS["danger"],command=lambda e=r["employee_id"], a=action:self._change_employee_status(e,a)).pack(side="left",padx=(0,4))
            ctk.CTkButton(row,text="View",width=45,height=28,fg_color="transparent",hover_color=COLORS["soft_blue"],text_color=COLORS["deep_space_blue"],command=lambda e=r["employee_id"]:self.profile(e)).pack(side="left")
    def _change_employee_status(self, eid, action):
        if action == "Deactivate" and not messagebox.askyesno("Deactivate employee", "Deactivate this employee? Their historical records will be preserved.", parent=self): return
        try:
            (self.service.activate_employee if action == "Activate" else self.service.deactivate_employee)(eid)
            self.show_page("Employees"); Toast(self, f"Employee {action.lower()}d successfully.", "success")
        except Exception as exc: Toast(self, str(exc), "error")
    def profile(self,eid):
        if self.current_page != "Profile":
            if self.current_page: self.navigation_history.append(self.current_page)
            self.current_page = "Profile"
        self._clear();self.context.configure(text="EMPLOYEE PROFILE"); e,a,avg,reviews=self.service.profile(eid);self.header("Employee Profile","Live attendance and performance summary");card=SectionCard(self.content);card.pack(fill="x",padx=30,pady=(0,16));label(card,e["name"],23,"bold").pack(anchor="w",padx=24,pady=(22,3));label(card,f"{e['employee_id']}  •  {e['designation']}  •  {e['department']}",13,"normal",COLORS["muted"]).pack(anchor="w",padx=24);StatusBadge(card,e["status"]).pack(anchor="w",padx=24,pady=(10,10));action="Activate" if e["status"]=="Inactive" else "Deactivate";ctk.CTkButton(card,text=action+" employee",height=32,fg_color=COLORS["primary"] if action=="Activate" else COLORS["danger"],hover_color=COLORS["primary_hover"],command=lambda:self._change_employee_status(eid,action)).pack(anchor="w",padx=24,pady=(0,20));stats=ctk.CTkFrame(self.content,fg_color="transparent");stats.pack(fill="x",padx=30);stats.grid_columnconfigure((0,1,2,3),weight=1)
        for i,(n,v) in enumerate((("Attendance",f"{a['percentage']}%"),("Performance",str(avg)),("Present days",str(a['Present']+a['Late'])),("Avg. working hours",f"{a['avg_hours']:.1f}"))):MetricCard(stats,"•",n,v,"Live database data",COLORS["deep_space_blue"]).grid(row=0,column=i,sticky="ew",padx=6)

    def attendance(self):
        self.attendance_day = getattr(self, "attendance_day", date.today())
        self.header("Attendance", "Edit a daily session, then save all changes together.")
        body=ctk.CTkScrollableFrame(self.content,fg_color="transparent");body.pack(fill="both",expand=True,padx=30,pady=(0,20))
        nav=SectionCard(body);nav.pack(fill="x",pady=(0,14));
        ctk.CTkButton(nav,text="← Previous Day",height=34,fg_color="transparent",hover_color=COLORS["secondary"],text_color=COLORS["primary"],command=lambda:self._move_attendance_day(-1)).pack(side="left",padx=16,pady=12)
        label(nav,self.attendance_day.strftime("%d %b %Y"),18,"bold",role="display").pack(side="left",expand=True)
        ctk.CTkButton(nav,text="Next Day →",height=34,fg_color="transparent",hover_color=COLORS["secondary"],text_color=COLORS["primary"],command=lambda:self._move_attendance_day(1)).pack(side="right",padx=16,pady=12)
        summary=self.service.daily_attendance_summary(self.attendance_day.isoformat());metrics=ctk.CTkFrame(body,fg_color="transparent");metrics.pack(fill="x",pady=(0,14));metrics.grid_columnconfigure((0,1,2,3),weight=1)
        for i,(title,key,color) in enumerate((("Total Employees","total",COLORS["regal_navy"]),("Present","present",COLORS["primary"]),("Absent","absent",COLORS["danger"]),("On Leave","leave",COLORS["blue_slate"]))):
            MetricCard(metrics,"•",title,str(summary[key]),"Database total",color).grid(row=0,column=i,sticky="ew",padx=6)
        controls=SectionCard(body); controls.pack(fill="x",pady=(0,14)); self.show_inactive = getattr(self, "show_inactive", False)
        ctk.CTkCheckBox(controls, text="Show inactive employees", variable=ctk.BooleanVar(value=self.show_inactive), command=self._toggle_inactive, text_color=COLORS["text_secondary"]).pack(side="left", padx=18, pady=12)
        PrimaryButton(controls,"Save Attendance",command=self._save_attendance_session,width=170).pack(side="right",padx=(8,18),pady=10)
        ctk.CTkButton(controls,text="Reset",command=self._reset_attendance_session,width=100,height=38,fg_color="transparent",border_width=1,border_color=COLORS["line"],text_color=COLORS["text_secondary"]).pack(side="right",pady=10)
        table=SectionCard(body);table.pack(fill="x");head=ctk.CTkFrame(table,fg_color=COLORS["surface_secondary"],corner_radius=9);head.pack(fill="x",padx=12,pady=(12,5))
        for text,width in (("EMPLOYEE",210),("ID",100),("DEPARTMENT",130),("STATUS",100),("ATTENDANCE",260),("ENTRY TIME",130),("EXIT TIME",130)): label(head,text,11,"bold",COLORS["text_secondary"],role="display",width=width,anchor="w").pack(side="left",padx=5,pady=11)
        key=self.attendance_day.isoformat()
        if getattr(self,"attendance_pending_day",None) != key:
            self.attendance_pending_day=key
            self.attendance_pending={r["employee_id"]:{"employee_id":r["employee_id"],"status":r["status"] or "Present","check_in":r["check_in"] or "09:00","check_out":r["check_out"] or "17:30"} for r in self.service.attendance_for_date(key, self.show_inactive)}
        for employee in self.service.attendance_for_date(key, self.show_inactive): self._attendance_row(table, employee)
    def _move_attendance_day(self, offset):
        self.attendance_day += timedelta(days=offset); self.attendance_pending_day=None; self.show_page("Attendance")
    def _toggle_inactive(self):
        self.show_inactive=not self.show_inactive; self.attendance_pending_day=None; self.show_page("Attendance")
    def _attendance_row(self, table, employee):
        state=self.attendance_pending[employee["employee_id"]]; row=ctk.CTkFrame(table,fg_color="transparent",height=50);row.pack(fill="x",padx=12,pady=2)
        label(row,employee["name"],13,"bold",width=210,anchor="w").pack(side="left",padx=5,pady=8); label(row,employee["employee_id"],12,"normal",COLORS["text_secondary"],role="data",width=100,anchor="w").pack(side="left",padx=5); label(row,employee["department"],12,"normal",COLORS["text_secondary"],width=130,anchor="w").pack(side="left",padx=5)
        StatusBadge(row,state["status"],width=100).pack(side="left",padx=5)
        actions=ctk.CTkFrame(row,fg_color="transparent");actions.pack(side="left",padx=4)
        for status,color in (("Present",COLORS["primary"]),("Absent",COLORS["danger"]),("Leave",COLORS["blue_slate"])):
            ctk.CTkButton(actions,text=status,width=70,height=30,corner_radius=7,fg_color=color if state["status"]==status else COLORS["surface_secondary"],hover_color=color,text_color="white" if state["status"]==status else color,font=(UI_FONT,10,"bold"),command=lambda e=employee["employee_id"],s=status:self._set_pending_status(e,s)).pack(side="left",padx=2)
        times=["—"]+[f"{(m//60-1)%12+1:02d}:{m%60:02d} {'AM' if m<720 else 'PM'}" for m in range(8*60,21*60+1,30)]
        enabled=state["status"] == "Present"; display=lambda value: self._time_display(value) if value else "—"
        entry=ctk.CTkOptionMenu(row,values=times,variable=ctk.StringVar(value=display(state["check_in"])),width=130,height=32,fg_color=COLORS["primary"] if enabled else COLORS["surface_secondary"],button_color=COLORS["primary_hover"],state="normal" if enabled else "disabled",command=lambda v,e=employee["employee_id"]:self._set_pending_time(e,"check_in",v)); entry.pack(side="left",padx=5)
        exit=ctk.CTkOptionMenu(row,values=times,variable=ctk.StringVar(value=display(state["check_out"])),width=130,height=32,fg_color=COLORS["primary"] if enabled else COLORS["surface_secondary"],button_color=COLORS["primary_hover"],state="normal" if enabled else "disabled",command=lambda v,e=employee["employee_id"]:self._set_pending_time(e,"check_out",v)); exit.pack(side="left",padx=5)
    @staticmethod
    def _time_display(value):
        h,m=map(int,value.split(":")); return f"{(h-1)%12+1:02d}:{m:02d} {'AM' if h<12 else 'PM'}"
    @staticmethod
    def _time_value(value):
        if value == "—": return ""
        clock, suffix=value.split(); h,m=map(int,clock.split(":")); h=(h%12)+(12 if suffix=="PM" else 0); return f"{h:02d}:{m:02d}"
    def _set_pending_status(self,eid,status):
        self.attendance_pending[eid]["status"]=status
        if status in ("Absent","Leave"): self.attendance_pending[eid]["check_in"]=self.attendance_pending[eid]["check_out"]=""
        self.show_page("Attendance")
    def _set_pending_time(self,eid,key,value): self.attendance_pending[eid][key]=self._time_value(value)
    def _reset_attendance_session(self): self.attendance_pending_day=None; self.show_page("Attendance"); Toast(self,"Unsaved attendance changes discarded.","info")
    def _save_attendance_session(self):
        try:
            self.service.save_attendance_batch(self.attendance_day.isoformat(), list(self.attendance_pending.values()))
            self.attendance_pending_day=None; self.show_page("Attendance"); Toast(self,"Attendance saved successfully.","success")
        except Exception as exc: Toast(self,str(exc),"error")
    def performance(self):
        self.header("Performance", "Select an employee, score predefined metrics, and preserve review history.")
        body=ctk.CTkScrollableFrame(self.content,fg_color="transparent");body.pack(fill="both",expand=True,padx=30,pady=(0,20))
        employees=self.service.employees(); choices=[f"{e['name']} — {e['employee_id']}" for e in employees]
        selected=getattr(self,"performance_employee",choices[0] if choices else "")
        selector=SectionCard(body);selector.pack(fill="x",pady=(0,14));label(selector,"SELECT EMPLOYEE",11,"bold",COLORS["text_secondary"],role="display").pack(anchor="w",padx=20,pady=(16,5))
        menu=ctk.CTkOptionMenu(selector,values=choices or ["No employees available"],variable=ctk.StringVar(value=selected),height=40,fg_color=COLORS["primary"],button_color=COLORS["primary_hover"],command=self._select_performance_employee);menu.pack(fill="x",padx=20,pady=(0,16))
        if not choices: return
        eid=selected.rsplit(" — ",1)[-1]; employee=self.service.get_employee(eid)
        summary=SectionCard(body);summary.pack(fill="x",pady=(0,14));label(summary,"Employee Summary",16,"bold").pack(anchor="w",padx=20,pady=(16,5));label(summary,f"{employee['name']}  •  {employee['department']}  •  {employee['designation']}",13,"normal",COLORS["text_secondary"]).pack(anchor="w",padx=20,pady=(0,16))
        card=SectionCard(body);card.pack(fill="x");label(card,"Performance Metrics",17,"bold").pack(anchor="w",padx=20,pady=(18,8));self.performance_values={}; score_values=[str(i) for i in range(10,101,10)]
        for metric in ("Productivity","Quality","Punctuality","Teamwork"):
            row=ctk.CTkFrame(card,fg_color="transparent");row.pack(fill="x",padx=20,pady=5);label(row,metric,13,"bold",width=180,anchor="w").pack(side="left")
            var=ctk.StringVar(value="80"); self.performance_values[metric]=var
            ctk.CTkOptionMenu(row,values=score_values,variable=var,width=145,height=36,fg_color=COLORS["primary"],button_color=COLORS["primary_hover"],command=lambda _:self._update_performance_score()).pack(side="right")
        self.overall_label=label(card,"80",32,"bold",COLORS["primary"],role="data");self.rating_label=label(card,"GOOD",13,"bold",COLORS["primary"],role="display")
        result=ctk.CTkFrame(card,fg_color=COLORS["surface_secondary"],corner_radius=9);result.pack(fill="x",padx=20,pady=16);label(result,"OVERALL SCORE",11,"bold",COLORS["text_secondary"],role="display").pack(side="left",padx=14,pady=12);self.overall_label.pack(side="left");label(result,"RATING",11,"bold",COLORS["text_secondary"],role="display").pack(side="left",padx=(45,10));self.rating_label.pack(side="left")
        PrimaryButton(card,"Save Performance Review",command=lambda:self._save_selected_performance(eid),width=205).pack(anchor="e",padx=20,pady=(0,20))
        history=SectionCard(body);history.pack(fill="x",pady=14);label(history,"Performance History",17,"bold").pack(anchor="w",padx=20,pady=(16,8))
        reviews=self.service.profile(eid)[3]
        if not reviews: label(history,"No previous reviews for this employee.",12,"normal",COLORS["muted"]).pack(anchor="w",padx=20,pady=(0,16))
        for review in reviews:
            row=ctk.CTkFrame(history,fg_color="transparent");row.pack(fill="x",padx=20,pady=4);label(row,review["review_period"],12,"normal",width=200,anchor="w").pack(side="left");label(row,f"{review['overall_score']:.1f}",12,"bold",role="data",width=100,anchor="w").pack(side="left");StatusBadge(row,review["rating"],width=150).pack(side="left")
    def _select_performance_employee(self, value): self.performance_employee=value; self.show_page("Performance")
    def _update_performance_score(self):
        score=sum(int(v.get()) for v in self.performance_values.values())/4; rating=self.service.db.rating(score)
        self.overall_label.configure(text=f"{score:.0f}");self.rating_label.configure(text=rating.upper(),text_color=COLORS["danger"] if rating=="Needs Improvement" else COLORS["primary"] if rating in ("Excellent","Good") else COLORS["blue_slate"])
    def _save_selected_performance(self, eid):
        try:
            score,rating=self.service.save_performance(eid,date.today().strftime("%B %Y"),[v.get() for v in self.performance_values.values()])
            Toast(self,f"Review saved: {score:.1f} ({rating})","success");self.show_page("Performance")
        except Exception as exc: Toast(self,str(exc),"error")
    def form_page(self,title,subtitle,fields,choices,callback,button):
        self.header(title,subtitle);body=ctk.CTkScrollableFrame(self.content,fg_color="transparent");body.pack(fill="both",expand=True,padx=30,pady=(0,20));card=SectionCard(body);card.pack(fill="x");label(card,"Record " + title,18,"bold").pack(anchor="w",padx=20,pady=(18,10));entries={}
        for text,value in fields:label(card,text,12,"bold").pack(anchor="w",padx=20,pady=(5,2));x=ctk.CTkEntry(card,height=35,fg_color="white",border_color=COLORS["line"]);x.insert(0,value);x.pack(fill="x",padx=20);entries[text]=x
        pick=None
        if choices:pick=ctk.CTkOptionMenu(card,values=choices,fg_color=COLORS["deep_space_blue"],button_color=COLORS["steel_blue"]);pick.pack(anchor="w",padx=20,pady=12)
        PrimaryButton(card,button,command=lambda:callback(entries,pick),width=150).pack(anchor="e",padx=20,pady=18)
    def _save_attendance(self,e,p):
        try:self.service.save_attendance(e["Employee ID"].get().upper(),e["Date"].get(),p.get(),e["Check in (HH:MM)"].get(),e["Check out (HH:MM)"].get(),e["Remarks"].get());Toast(self,"Attendance saved successfully.")
        except Exception as x:Toast(self,str(x),"error")
    def _save_performance(self,e,p):
        try:score,rating=self.service.save_performance(e["Employee ID"].get().upper(),e["Review period"].get(),[e[x].get() for x in ("Productivity","Quality","Punctuality","Teamwork")]);Toast(self,f"Review saved: {score} ({rating})")
        except Exception as x:Toast(self,str(x),"error")
    def analytics(self):
        self.header("Analytics","Attendance, workforce and performance insights")
        body=ctk.CTkScrollableFrame(self.content,fg_color="transparent");body.pack(fill="both",expand=True,padx=30,pady=(0,20))
        filters=SectionCard(body);filters.pack(fill="x",pady=(0,14)); label(filters,"DATE RANGE",11,"bold",COLORS["text_secondary"],role="display").pack(side="left",padx=(18,5),pady=12)
        range_var=ctk.StringVar(value=getattr(self,"analytics_range","Today")); department_var=ctk.StringVar(value=getattr(self,"analytics_department","All Departments")); employee_var=ctk.StringVar(value=getattr(self,"analytics_employee","All Employees"))
        ctk.CTkOptionMenu(filters,values=["Today","This Week","This Month","Last Month"],variable=range_var,width=130,fg_color="white",button_color=COLORS["primary"],text_color=COLORS["text_primary"]).pack(side="left",padx=5)
        ctk.CTkOptionMenu(filters,values=["All Departments"]+self.service.departments(),variable=department_var,width=155,fg_color="white",button_color=COLORS["primary"],text_color=COLORS["text_primary"]).pack(side="left",padx=5)
        employees=[f"{e['name']} — {e['employee_id']}" for e in self.service.employees()]
        ctk.CTkOptionMenu(filters,values=["All Employees"]+employees,variable=employee_var,width=190,fg_color="white",button_color=COLORS["primary"],text_color=COLORS["text_primary"]).pack(side="left",padx=5)
        PrimaryButton(filters,"Apply",width=90,command=lambda:self._apply_analytics_filters(range_var.get(),department_var.get(),employee_var.get())).pack(side="right",padx=16,pady=9)
        start,end=self._analytics_dates(range_var.get()); eid="All Employees" if employee_var.get()=="All Employees" else employee_var.get().rsplit(" — ",1)[-1]; d=self.service.analytics(start,end,department_var.get(),eid)
        kpis=ctk.CTkFrame(body,fg_color="transparent");kpis.pack(fill="x",pady=(0,14));kpis.grid_columnconfigure((0,1,2,3),weight=1)
        for i,(title,value) in enumerate((("Total Employees",d["total"]),("Attendance Rate",f"{d['attendance_rate']}%"),("Average Performance",d["average_performance"]),("Average Working Hours",f"{d['average_hours']:.1f} h"))): MetricCard(kpis,"•",title,str(value),"Selected period",(COLORS["regal_navy"],COLORS["primary"],COLORS["sapphire"],COLORS["blue_slate"])[i]).grid(row=0,column=i,sticky="ew",padx=6)
        charts=ctk.CTkFrame(body,fg_color="transparent");charts.pack(fill="x");charts.grid_columnconfigure((0,1),weight=1)
        self.donut_card(charts,"Attendance Distribution",list(d["distribution"].items())).grid(row=0,column=0,sticky="nsew",padx=(0,8),pady=8)
        self.donut_card(charts,"Performance Distribution",list(d["performance_distribution"].items())).grid(row=0,column=1,sticky="nsew",padx=(8,0),pady=8)
        self.bars(charts,"Department Performance",d["department_performance"]).grid(row=1,column=0,sticky="nsew",padx=(0,8),pady=8)
        self.bars(charts,"Department Attendance Rate",d["department_attendance"]).grid(row=1,column=1,sticky="nsew",padx=(8,0),pady=8)
        self.line_card(body,"Attendance Trend",d["trend"]).pack(fill="x",pady=8)
        details=ctk.CTkFrame(body,fg_color="transparent");details.pack(fill="x",pady=8);details.grid_columnconfigure((0,1),weight=1)
        self.bars(details,"Performance Metrics",[(k.title(),v) for k,v in d["metrics"].items()]).grid(row=0,column=0,sticky="nsew",padx=(0,8))
        self._attention_card(details,d["attention"]).grid(row=0,column=1,sticky="nsew",padx=(8,0))
        self.top_performers(body,d["top"])
    def _analytics_dates(self, selected):
        today=date.today()
        if selected=="Today": start=today
        elif selected=="This Week": start=today-timedelta(days=today.weekday())
        elif selected=="Last Month": end=today.replace(day=1)-timedelta(days=1); start=end.replace(day=1); return start.isoformat(),end.isoformat()
        else: start=today.replace(day=1)
        return start.isoformat(),today.isoformat()
    def _apply_analytics_filters(self, period, department, employee):
        self.analytics_range,self.analytics_department,self.analytics_employee=period,department,employee; self.show_page("Analytics")
    def _attention_card(self, master, rows):
        card=SectionCard(master,height=235);card.grid_propagate(False);label(card,"Needs Attention",17,"bold",COLORS["danger"]).pack(anchor="w",padx=18,pady=(15,8))
        if not rows: label(card,"No employees require attention for this period.",12,"normal",COLORS["muted"],wraplength=350).pack(anchor="w",padx=18,pady=14)
        for person in rows[:5]:
            note="Low performance" if person.get("score",100)<60 else "High absence rate"
            row=ctk.CTkFrame(card,fg_color="transparent");row.pack(fill="x",padx=18,pady=4);label(row,person["name"],12,"bold",width=180,anchor="w").pack(side="left");label(row,note,11,"normal",COLORS["danger"]).pack(side="left")
        return card
    def reports(self):
        self.header("Reports","Export live data from the workforce database");card=SectionCard(self.content);card.pack(fill="x",padx=30);label(card,"Employee Directory",18,"bold").pack(anchor="w",padx=20,pady=(20,4));label(card,"Export the current employee directory as CSV or Excel.",13,"normal",COLORS["muted"]).pack(anchor="w",padx=20)
        actions=ctk.CTkFrame(card,fg_color="transparent");actions.pack(anchor="w",padx=20,pady=20);PrimaryButton(actions,"Export CSV",command=lambda:Toast(self,"Report exported: "+self.service.export_employees_csv().name),width=130).pack(side="left",padx=(0,8));PrimaryButton(actions,"Export Excel",command=lambda:Toast(self,"Report exported: "+self.service.export_employees_excel().name),width=130).pack(side="left")
    def settings(self):
        self.header("Settings","Manage organization and workday preferences");card=SectionCard(self.content);card.pack(fill="x",padx=30);entries={};saved=self.service.settings()
        for key,title in (("organization_name","Organization name"),("work_start","Work start (HH:MM)"),("work_end","Work end (HH:MM)"),("grace_minutes","Grace period (minutes)")):
            label(card,title,12,"bold").pack(anchor="w",padx=20,pady=(12,3));e=ctk.CTkEntry(card,height=35,fg_color="white",border_color=COLORS["line"]);e.insert(0,saved.get(key,""));e.pack(fill="x",padx=20);entries[key]=e
        PrimaryButton(card,"Save Settings",command=lambda:(self.service.save_settings({k:e.get() for k,e in entries.items()}),Toast(self,"Settings saved successfully.")),width=140).pack(anchor="e",padx=20,pady=20)
