"""
app.py — Main GUI for Smart BMI Tracker & Analyzer
Run:  python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database as db
import bmi_engine as engine
import charts
import export_utils
from ui_theme import *


# ══════════════════════════════════════════════════════════════════════════════
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart BMI Tracker & Analyzer")
        self.geometry("1200x760")
        self.minsize(1000, 680)
        self.configure(bg=BG_DARK)
        self._setup_styles()

        self.current_user: dict | None = None
        self._build_ui()
        self._refresh_user_list()

    # ── Styles ────────────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",       background=BG_DARK)
        s.configure("Card.TFrame",  background=BG_CARD)
        s.configure("Surface.TFrame", background=BG_SURFACE)
        s.configure("TLabel",       background=BG_DARK,   foreground=TEXT_PRI, font=FONT_BODY)
        s.configure("Card.TLabel",  background=BG_CARD,   foreground=TEXT_PRI, font=FONT_BODY)
        s.configure("Dim.TLabel",   background=BG_CARD,   foreground=TEXT_DIM, font=FONT_SMALL)
        s.configure("TEntry",       fieldbackground=BG_INPUT, foreground=TEXT_PRI,
                    insertcolor=TEXT_PRI, borderwidth=1, relief="flat")
        s.configure("TButton",      background=ACCENT,    foreground=TEXT_PRI,
                    font=FONT_SUBHEAD, borderwidth=0, focusthickness=0, padding=(12,8))
        s.map("TButton",
              background=[("active", ACCENT_LIGHT), ("pressed", "#5C2FFF")],
              foreground=[("active", TEXT_PRI)])
        s.configure("Danger.TButton", background=DANGER, foreground=TEXT_PRI,
                    font=FONT_SMALL, padding=(8,4))
        s.map("Danger.TButton", background=[("active","#C62828")])
        s.configure("Success.TButton", background=SUCCESS, foreground=BG_DARK,
                    font=FONT_SMALL, padding=(8,4))
        s.map("Success.TButton", background=[("active","#4CAF50")])
        s.configure("Treeview", background=BG_CARD, foreground=TEXT_PRI,
                    fieldbackground=BG_CARD, rowheight=28, font=FONT_BODY)
        s.configure("Treeview.Heading", background=BG_SURFACE, foreground=ACCENT_LIGHT,
                    font=FONT_SUBHEAD)
        s.map("Treeview", background=[("selected", ACCENT)])
        s.configure("TNotebook", background=BG_DARK, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_SURFACE, foreground=TEXT_SEC,
                    font=FONT_SUBHEAD, padding=(16,8))
        s.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", ACCENT_LIGHT)])
        s.configure("TScrollbar", background=BORDER, troughcolor=BG_SURFACE,
                    borderwidth=0, arrowcolor=TEXT_DIM)
        s.configure("TCombobox", fieldbackground=BG_INPUT, foreground=TEXT_PRI,
                    background=BG_INPUT, selectbackground=ACCENT)

    # ── Root layout ───────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_SURFACE, height=64)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⚖  Smart BMI Tracker & Analyzer",
                 font=FONT_TITLE, bg=BG_SURFACE, fg=ACCENT_LIGHT).pack(side="left", padx=PAD)
        tk.Label(hdr, text="Health Monitoring Dashboard",
                 font=FONT_SMALL, bg=BG_SURFACE, fg=TEXT_DIM).pack(side="left", padx=4)
        self._clock_lbl = tk.Label(hdr, text="", font=FONT_SMALL, bg=BG_SURFACE, fg=TEXT_DIM)
        self._clock_lbl.pack(side="right", padx=PAD)
        self._tick_clock()

        # Left sidebar
        sidebar = tk.Frame(self, bg=BG_SURFACE, width=240)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Main notebook
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True, padx=PAD_SM, pady=PAD_SM)
        self._build_calculator_tab()
        self._build_history_tab()
        self._build_charts_tab()

    # ── Sidebar (User Management) ─────────────────────────────────────────────
    def _build_sidebar(self, parent):
        tk.Label(parent, text="USER PROFILES", font=FONT_SMALL,
                 bg=BG_SURFACE, fg=ACCENT_LIGHT).pack(pady=(PAD, PAD_SM), padx=PAD, anchor="w")

        # Current user display
        self._user_badge = tk.Label(parent, text="No user selected",
                                    font=FONT_SUBHEAD, bg=BG_SURFACE, fg=TEXT_DIM,
                                    wraplength=200, justify="center")
        self._user_badge.pack(padx=PAD, pady=PAD_SM)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=PAD, pady=PAD_SM)

        # User listbox
        tk.Label(parent, text="Select User:", font=FONT_SMALL, bg=BG_SURFACE, fg=TEXT_SEC).pack(anchor="w", padx=PAD)
        lb_frame = tk.Frame(parent, bg=BG_SURFACE)
        lb_frame.pack(fill="both", expand=True, padx=PAD, pady=(4, 0))
        self._user_lb = tk.Listbox(lb_frame, bg=BG_CARD, fg=TEXT_PRI,
                                   selectbackground=ACCENT, font=FONT_BODY,
                                   borderwidth=0, relief="flat", activestyle="none")
        lb_scroll = ttk.Scrollbar(lb_frame, orient="vertical", command=self._user_lb.yview)
        self._user_lb.configure(yscrollcommand=lb_scroll.set)
        lb_scroll.pack(side="right", fill="y")
        self._user_lb.pack(fill="both", expand=True)
        self._user_lb.bind("<<ListboxSelect>>", self._on_user_select)

        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=PAD, pady=PAD_SM)

        # Add new user
        tk.Label(parent, text="Add New User:", font=FONT_SMALL, bg=BG_SURFACE, fg=TEXT_SEC).pack(anchor="w", padx=PAD)
        self._new_user_var = tk.StringVar()
        new_entry = tk.Entry(parent, textvariable=self._new_user_var, bg=BG_INPUT,
                             fg=TEXT_PRI, insertbackground=TEXT_PRI,
                             relief="flat", font=FONT_BODY)
        new_entry.pack(fill="x", padx=PAD, pady=4)
        new_entry.bind("<Return>", lambda e: self._add_user())
        ttk.Button(parent, text="➕  Add User", command=self._add_user).pack(fill="x", padx=PAD, pady=2)
        ttk.Button(parent, text="🗑  Delete User", style="Danger.TButton",
                   command=self._delete_user).pack(fill="x", padx=PAD, pady=2)

    # ── Calculator Tab ────────────────────────────────────────────────────────
    def _build_calculator_tab(self):
        tab = ttk.Frame(self._nb)
        self._nb.add(tab, text="  🧮  Calculator  ")

        wrapper = tk.Frame(tab, bg=BG_DARK)
        wrapper.pack(fill="both", expand=True, padx=PAD, pady=PAD)

        # Left: input card
        left = tk.Frame(wrapper, bg=BG_CARD, bd=0)
        left.pack(side="left", fill="y", padx=(0, PAD_SM))

        tk.Label(left, text="Calculate BMI", font=FONT_HEAD,
                 bg=BG_CARD, fg=ACCENT_LIGHT).pack(padx=PAD, pady=(PAD, PAD_SM), anchor="w")
        tk.Label(left, text="Enter measurements below", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXT_DIM).pack(padx=PAD, anchor="w")

        ttk.Separator(left, orient="horizontal").pack(fill="x", padx=PAD, pady=PAD_SM)

        def labeled_entry(parent, label, unit):
            tk.Label(parent, text=label, font=FONT_SUBHEAD,
                     bg=BG_CARD, fg=TEXT_SEC).pack(padx=PAD, pady=(PAD_SM, 2), anchor="w")
            row = tk.Frame(parent, bg=BG_CARD)
            row.pack(fill="x", padx=PAD, pady=(0, PAD_SM))
            var = tk.StringVar()
            e = tk.Entry(row, textvariable=var, bg=BG_INPUT, fg=TEXT_PRI,
                         insertbackground=TEXT_PRI, relief="flat",
                         font=("Segoe UI", 13), width=14)
            e.pack(side="left")
            tk.Label(row, text=unit, font=FONT_BODY, bg=BG_CARD, fg=TEXT_DIM).pack(side="left", padx=6)
            return var, e

        self._weight_var, self._weight_entry = labeled_entry(left, "Weight", "kg")
        self._height_var, self._height_entry = labeled_entry(left, "Height", "cm")

        tk.Label(left, text="Valid: Weight 10–500 kg  |  Height 50–300 cm",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM).pack(padx=PAD, pady=(0, PAD_SM))

        ttk.Button(left, text="  Calculate BMI  ",
                   command=self._calculate).pack(padx=PAD, pady=PAD_SM, fill="x")
        ttk.Button(left, text="  Clear  ",
                   command=self._clear_inputs).pack(padx=PAD, pady=(0, PAD), fill="x")

        # Right: result card
        right = tk.Frame(wrapper, bg=BG_CARD, bd=0)
        right.pack(side="left", fill="both", expand=True)

        tk.Label(right, text="Result", font=FONT_HEAD,
                 bg=BG_CARD, fg=ACCENT_LIGHT).pack(padx=PAD, pady=(PAD, PAD_SM), anchor="w")
        ttk.Separator(right, orient="horizontal").pack(fill="x", padx=PAD, pady=PAD_SM)

        # BMI gauge canvas
        self._gauge_canvas = tk.Canvas(right, bg=BG_CARD, height=180,
                                       highlightthickness=0)
        self._gauge_canvas.pack(fill="x", padx=PAD, pady=PAD_SM)
        self._draw_gauge(None)

        # BMI number
        self._bmi_lbl = tk.Label(right, text="---", font=FONT_NUM,
                                 bg=BG_CARD, fg=ACCENT_LIGHT)
        self._bmi_lbl.pack()

        self._cat_lbl = tk.Label(right, text="Enter values and press Calculate",
                                 font=FONT_BIG, bg=BG_CARD, fg=TEXT_DIM)
        self._cat_lbl.pack(pady=(4, 0))

        self._msg_lbl = tk.Label(right, text="", font=FONT_BODY,
                                 bg=BG_CARD, fg=TEXT_SEC, wraplength=480, justify="center")
        self._msg_lbl.pack(padx=PAD, pady=PAD_SM)

        # Save button
        self._save_btn = ttk.Button(right, text="💾  Save Record",
                                    command=self._save_record, state="disabled")
        self._save_btn.pack(padx=PAD, pady=(0, PAD))

        self._last_result: engine.BMIResult | None = None

    # ── History Tab ───────────────────────────────────────────────────────────
    def _build_history_tab(self):
        tab = ttk.Frame(self._nb)
        self._nb.add(tab, text="  📋  History  ")

        # Toolbar
        bar = tk.Frame(tab, bg=BG_SURFACE)
        bar.pack(fill="x", padx=PAD, pady=PAD_SM)
        ttk.Button(bar, text="🔄 Refresh", command=self._refresh_history).pack(side="left", padx=2)
        ttk.Button(bar, text="📤 Export CSV", style="Success.TButton",
                   command=self._export_csv).pack(side="left", padx=2)
        ttk.Button(bar, text="🗑 Delete Selected", style="Danger.TButton",
                   command=self._delete_record).pack(side="left", padx=2)

        # Stats bar
        self._stats_frame = tk.Frame(tab, bg=BG_SURFACE)
        self._stats_frame.pack(fill="x", padx=PAD, pady=(0, PAD_SM))
        self._stats_labels = {}
        for key in ("Total", "Average", "Lowest", "Highest"):
            f = tk.Frame(self._stats_frame, bg=BG_CARD, padx=12, pady=8)
            f.pack(side="left", padx=4)
            tk.Label(f, text=key, font=FONT_SMALL, bg=BG_CARD, fg=TEXT_DIM).pack()
            lbl = tk.Label(f, text="—", font=FONT_SUBHEAD, bg=BG_CARD, fg=ACCENT_LIGHT)
            lbl.pack()
            self._stats_labels[key] = lbl

        # Treeview
        cols = ("Date & Time", "Weight (kg)", "Height (cm)", "BMI", "Category")
        tree_frame = tk.Frame(tab, bg=BG_DARK)
        tree_frame.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))
        self._tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                   selectmode="browse")
        widths = [160, 100, 100, 80, 120]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center")
        vs = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        # Tag colours
        for cat, col in CAT_COLORS.items():
            self._tree.tag_configure(cat, foreground=col)

    # ── Charts Tab ────────────────────────────────────────────────────────────
    def _build_charts_tab(self):
        tab = ttk.Frame(self._nb)
        self._nb.add(tab, text="  📈  Charts  ")

        bar = tk.Frame(tab, bg=BG_SURFACE)
        bar.pack(fill="x", padx=PAD, pady=PAD_SM)
        ttk.Button(bar, text="🔄 Refresh Charts", command=self._refresh_charts).pack(side="left", padx=2)
        ttk.Button(bar, text="💾 Save Graph", style="Success.TButton",
                   command=self._save_graph).pack(side="left", padx=2)

        self._chart_frame = tk.Frame(tab, bg=BG_DARK)
        self._chart_frame.pack(fill="both", expand=True, padx=PAD, pady=(0, PAD))
        self._current_fig = None

        # Placeholder
        tk.Label(self._chart_frame,
                 text="Select a user and add records to view charts.",
                 font=FONT_SUBHEAD, bg=BG_DARK, fg=TEXT_DIM).pack(expand=True)

    # ══════════════════════════════════════════════════════════════════════════
    # User actions
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh_user_list(self):
        self._user_lb.delete(0, "end")
        for u in db.get_all_users():
            self._user_lb.insert("end", u["name"])

    def _on_user_select(self, _evt=None):
        sel = self._user_lb.curselection()
        if not sel:
            return
        name = self._user_lb.get(sel[0])
        user = db.get_user_by_name(name)
        if user:
            self.current_user = user
            self._user_badge.config(text=f"👤 {user['name']}", fg=ACCENT_LIGHT)
            self._refresh_history()
            self._refresh_charts()
            self._nb.select(0)

    def _add_user(self):
        name = self._new_user_var.get().strip()
        if not name:
            messagebox.showwarning("Input Required", "Please enter a user name.")
            return
        if db.get_user_by_name(name):
            messagebox.showwarning("Duplicate", f"User '{name}' already exists.")
            return
        if len(name) > 50:
            messagebox.showwarning("Too Long", "Name must be 50 characters or fewer.")
            return
        db.add_user(name)
        self._new_user_var.set("")
        self._refresh_user_list()

    def _delete_user(self):
        if not self.current_user:
            messagebox.showwarning("No User", "Please select a user first.")
            return
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete user '{self.current_user['name']}' and ALL records?"):
            return
        db.delete_user(self.current_user["id"])
        self.current_user = None
        self._user_badge.config(text="No user selected", fg=TEXT_DIM)
        self._refresh_user_list()
        self._tree.delete(*self._tree.get_children())
        for lbl in self._stats_labels.values():
            lbl.config(text="—")

    # ══════════════════════════════════════════════════════════════════════════
    # BMI calculation
    # ══════════════════════════════════════════════════════════════════════════

    def _calculate(self):
        if not self.current_user:
            messagebox.showwarning("No User", "Please select or create a user first.")
            return
        try:
            w, h = engine.validate_inputs(self._weight_var.get(), self._height_var.get())
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        result = engine.calculate_bmi(w, h)
        self._last_result = result
        self._bmi_lbl.config(text=f"{result.bmi:.1f}", fg=CAT_COLORS.get(result.category, ACCENT_LIGHT))
        self._cat_lbl.config(text=result.category, fg=CAT_COLORS.get(result.category, TEXT_PRI))
        self._msg_lbl.config(text=result.message, fg=TEXT_SEC)
        self._save_btn.config(state="normal")
        self._draw_gauge(result.bmi)

    def _clear_inputs(self):
        self._weight_var.set("")
        self._height_var.set("")
        self._bmi_lbl.config(text="---", fg=ACCENT_LIGHT)
        self._cat_lbl.config(text="Enter values and press Calculate", fg=TEXT_DIM)
        self._msg_lbl.config(text="")
        self._save_btn.config(state="disabled")
        self._last_result = None
        self._draw_gauge(None)

    def _save_record(self):
        if not self._last_result or not self.current_user:
            return
        r = self._last_result
        db.add_bmi_record(self.current_user["id"], r.weight_kg, r.height_cm,
                          r.bmi, r.category)
        messagebox.showinfo("Saved", f"BMI {r.bmi:.1f} ({r.category}) saved!")
        self._save_btn.config(state="disabled")
        self._refresh_history()
        self._refresh_charts()

    # ══════════════════════════════════════════════════════════════════════════
    # Gauge drawing
    # ══════════════════════════════════════════════════════════════════════════

    def _draw_gauge(self, bmi: float | None):
        c = self._gauge_canvas
        c.delete("all")
        W = c.winfo_width() or 500
        H = 180
        cx, cy, r = W // 2, H - 20, 130

        # Background arc zones (semi-circle)
        import math
        zones = [
            (180, 207, INFO),       # Underweight
            (207, 234, SUCCESS),    # Normal
            (234, 261, WARNING),    # Overweight
            (261, 300, DANGER),     # Obese
        ]
        for start, end, col in zones:
            c.create_arc(cx - r, cy - r, cx + r, cy + r,
                         start=start - 180, extent=end - start,
                         style="arc", outline=col, width=18)

        # Needle
        if bmi is not None:
            frac = engine.bmi_meter_fraction(bmi)
            angle_deg = 180 + frac * 180          # 180° = left, 360° = right
            angle_rad = math.radians(angle_deg)
            nx = cx + (r - 20) * math.cos(angle_rad)
            ny = cy - (r - 20) * math.sin(angle_rad)
            c.create_line(cx, cy, nx, ny, fill=TEXT_PRI, width=3, capstyle="round")

        # Center dot
        c.create_oval(cx - 8, cy - 8, cx + 8, cy + 8,
                      fill=ACCENT, outline=TEXT_PRI, width=2)

        # Labels
        for lbl, x_off in [("10", -r - 10), ("25", 0), ("40+", r + 10)]:
            c.create_text(cx + x_off, cy + 20, text=lbl,
                          fill=TEXT_DIM, font=FONT_SMALL)

        c.create_text(cx, cy + 40, text="BMI Scale (10 – 40+)",
                      fill=TEXT_DIM, font=FONT_SMALL)

    # ══════════════════════════════════════════════════════════════════════════
    # History helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh_history(self):
        if not self.current_user:
            return
        records = db.get_records_for_user(self.current_user["id"])
        self._tree.delete(*self._tree.get_children())
        for r in records:
            self._tree.insert("", "end",
                               iid=str(r["id"]),
                               values=(r["recorded_at"], r["weight_kg"],
                                       r["height_cm"], f"{r['bmi']:.2f}", r["category"]),
                               tags=(r["category"],))
        stats = db.get_stats_for_user(self.current_user["id"])
        if stats and stats.get("total", 0) > 0:
            self._stats_labels["Total"].config(text=str(stats["total"]))
            self._stats_labels["Average"].config(text=f"{stats['avg_bmi']:.1f}" if stats['avg_bmi'] is not None else "—")
            self._stats_labels["Lowest"].config(text=f"{stats['min_bmi']:.1f}" if stats['min_bmi'] is not None else "—")
            self._stats_labels["Highest"].config(text=f"{stats['max_bmi']:.1f}" if stats['max_bmi'] is not None else "—")
        else:
            for lbl in self._stats_labels.values():
                lbl.config(text="—")

    def _delete_record(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a record to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this BMI record?"):
            return
        db.delete_record(int(sel[0]))
        self._refresh_history()
        self._refresh_charts()

    def _export_csv(self):
        if not self.current_user:
            messagebox.showwarning("No User", "Select a user first.")
            return
        records = db.get_records_for_user(self.current_user["id"])
        export_utils.export_to_csv(records, self.current_user["name"])

    # ══════════════════════════════════════════════════════════════════════════
    # Charts helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh_charts(self):
        for w in self._chart_frame.winfo_children():
            w.destroy()
        self._current_fig = None

        if not self.current_user:
            tk.Label(self._chart_frame, text="Select a user to view charts.",
                     font=FONT_SUBHEAD, bg=BG_DARK, fg=TEXT_DIM).pack(expand=True)
            return

        records = db.get_records_for_user(self.current_user["id"])
        stats   = db.get_stats_for_user(self.current_user["id"])

        # Top row: trend chart (wide)
        top = tk.Frame(self._chart_frame, bg=BG_DARK)
        top.pack(fill="both", expand=True)

        fig_trend, _ = charts.build_trend_chart(records)
        self._current_fig = fig_trend
        canvas1 = FigureCanvasTkAgg(fig_trend, master=top)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="left", fill="both", expand=True)

        # Bottom row: pie + stats
        bot = tk.Frame(self._chart_frame, bg=BG_DARK)
        bot.pack(fill="x")

        fig_pie, _ = charts.build_category_pie(records)
        cv2 = FigureCanvasTkAgg(fig_pie, master=bot)
        cv2.draw()
        cv2.get_tk_widget().pack(side="left", fill="both", expand=True)

        fig_bar, _ = charts.build_stats_bar(stats)
        cv3 = FigureCanvasTkAgg(fig_bar, master=bot)
        cv3.draw()
        cv3.get_tk_widget().pack(side="left", fill="both", expand=True)

    def _save_graph(self):
        if self._current_fig is None:
            messagebox.showwarning("No Chart", "Refresh charts first.")
            return
        export_utils.export_graph_image(self._current_fig)

    # ══════════════════════════════════════════════════════════════════════════
    # Clock
    # ══════════════════════════════════════════════════════════════════════════

    def _tick_clock(self):
        now = datetime.now().strftime("%a, %d %b %Y   %H:%M:%S")
        self._clock_lbl.config(text=now)
        self.after(1000, self._tick_clock)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()
