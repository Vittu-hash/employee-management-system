import customtkinter as ctk
from ui.theme import COLORS, DISPLAY_FONT, UI_FONT, DATA_FONT


def label(master, text, size=14, weight="normal", color=None, role="ui", **kwargs):
    family = {"display": DISPLAY_FONT, "data": DATA_FONT}.get(role, UI_FONT)
    return ctk.CTkLabel(master, text=text, font=(family, size, weight), text_color=color or COLORS["text_primary"], **kwargs)


class SectionCard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["surface"], corner_radius=14, border_width=1,
                         border_color=COLORS["line"], **kwargs)


class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(master, text=text, command=command, height=38, corner_radius=9,
                         fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                         font=(UI_FONT, 13, "bold"), **kwargs)


class StatusBadge(ctk.CTkLabel):
    styles = {"Active": (COLORS["soft_success"], COLORS["success"]), "On Leave": (COLORS["soft_warning"], COLORS["blue_slate"]),
              "Inactive": (COLORS["soft_warning"], COLORS["blue_slate"]), "Present": (COLORS["soft_success"], COLORS["success"]),
              "Late": (COLORS["soft_warning"], COLORS["warning"]), "Absent": (COLORS["soft_danger"], COLORS["danger"]), "Leave": (COLORS["soft_warning"], COLORS["blue_slate"])}
    def __init__(self, master, status, **kwargs):
        bg, fg = self.styles.get(status, (COLORS["soft_blue"], COLORS["deep_space_blue"]))
        super().__init__(master, text=status, fg_color=bg, text_color=fg, corner_radius=8, padx=10, pady=3,
                         font=(UI_FONT, 11, "bold"), **kwargs)


class MetricCard(SectionCard):
    def __init__(self, master, icon, title, value, subtext, accent=COLORS["deep_space_blue"]):
        super().__init__(master)
        icon_box = ctk.CTkLabel(self, text=icon, width=38, height=38, corner_radius=10, fg_color=accent, text_color="white", font=(UI_FONT, 18, "bold"))
        icon_box.pack(anchor="w", padx=18, pady=(16, 10))
        label(self, title.upper(), 11, "bold", COLORS["text_secondary"], role="display").pack(anchor="w", padx=18)
        label(self, value, 30, "bold", role="data").pack(anchor="w", padx=18, pady=(1, 2))
        label(self, subtext, 11, "normal", COLORS["success"] if "↑" in subtext else COLORS["muted"]).pack(anchor="w", padx=18, pady=(0, 16))


class Toast(ctk.CTkFrame):
    def __init__(self, master, text, kind="info"):
        color = {"info": COLORS["primary"], "success": COLORS["dark_cyan"],
                 "warning": COLORS["golden_orange"], "error": COLORS["brown_red"]}.get(kind, COLORS["primary"])
        super().__init__(master, fg_color=color, corner_radius=10)
        label(self, text, 12, "bold", "white").pack(padx=18, pady=11)
        self.place(relx=.97, rely=.08, anchor="ne")
        self.after(3200, self.destroy)


class AddEmployeeModal(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(app); self.app = app
        self.title("Add Employee"); self.geometry("650x430"); self.resizable(False, False); self.configure(fg_color=COLORS["background"])
        self.transient(app); self.grab_set()
        label(self, "Add New Employee", 23, "bold", role="display").pack(anchor="w", padx=32, pady=(28, 4))
        label(self, "Add an employee profile to your organization.", 13, "normal", COLORS["muted"]).pack(anchor="w", padx=32, pady=(0, 22))
        form = ctk.CTkFrame(self, fg_color="transparent"); form.pack(fill="both", expand=True, padx=32)
        fields = [("Employee ID", "EMP013"), ("Full Name", "Enter full name"), ("Department", "Select department"), ("Designation", "Enter designation"), ("Date of Joining", "YYYY-MM-DD")]
        self.entries = {}
        for i, (name, hint) in enumerate(fields):
            r, c = divmod(i, 2); box = ctk.CTkFrame(form, fg_color="transparent"); box.grid(row=r, column=c, sticky="ew", padx=(0, 14) if c == 0 else (14, 0), pady=7)
            label(box, name, 12, "bold").pack(anchor="w", pady=(0, 5))
            if name == "Department":
                ent = ctk.CTkOptionMenu(box, values=self.app.service.departments(), height=38, corner_radius=8, fg_color="white", button_color=COLORS["steel_blue"], text_color=COLORS["ink"])
            else: ent = ctk.CTkEntry(box, placeholder_text=hint, height=38, corner_radius=8, border_color=COLORS["line"], fg_color="white")
            ent.pack(fill="x"); self.entries[name] = ent
        form.grid_columnconfigure((0, 1), weight=1)
        self.error = label(self, "", 12, "normal", COLORS["brick_red"]); self.error.pack(anchor="w", padx=32)
        actions = ctk.CTkFrame(self, fg_color="transparent"); actions.pack(fill="x", padx=32, pady=20)
        ctk.CTkButton(actions, text="Cancel", width=110, height=38, fg_color="white", text_color=COLORS["ink"], border_width=1, border_color=COLORS["line"], command=self.destroy).pack(side="right", padx=(10, 0))
        PrimaryButton(actions, "Add Employee", width=135, command=self.save).pack(side="right")
    def save(self):
        value = lambda key: self.entries[key].get()
        try:
            self.app.service.save_employee({"employee_id":value("Employee ID"), "name":value("Full Name"), "department":value("Department"), "designation":value("Designation"), "joining_date":value("Date of Joining")})
        except Exception as exc:
            self.error.configure(text=str(exc)); return
        self.destroy(); self.app.show_page("Employees"); Toast(self.app, "Employee added successfully.")
