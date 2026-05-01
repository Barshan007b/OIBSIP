"""
Secure Password Generator Pro
A feature-rich password generator with modern GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import secrets
import string
import math
import json
import csv
import os
import datetime
import pyperclip

# ── Colour palette ──────────────────────────────────────────────────
BG_DARK       = "#0d1117"
BG_CARD       = "#161b22"
BG_INPUT      = "#21262d"
ACCENT        = "#58a6ff"
ACCENT2       = "#3fb950"
ACCENT3       = "#f78166"
ACCENT4       = "#d2a8ff"
TEXT_PRIMARY  = "#e6edf3"
TEXT_MUTED    = "#8b949e"
BORDER        = "#30363d"
WEAK_COL      = "#f85149"
FAIR_COL      = "#e3b341"
GOOD_COL      = "#3fb950"
STRONG_COL    = "#58a6ff"

FONT_TITLE    = ("Segoe UI", 18, "bold")
FONT_HEADING  = ("Segoe UI", 12, "bold")
FONT_BODY     = ("Segoe UI", 10)
FONT_SMALL    = ("Segoe UI", 9)
FONT_MONO     = ("Cascadia Code", 13, "bold")

HISTORY_FILE  = os.path.join(os.path.dirname(__file__), "history.json")


# ── Utility helpers ──────────────────────────────────────────────────
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_history(hist):
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(hist, f, indent=2)
    except Exception:
        pass


def calc_entropy(password, pool_size):
    if pool_size == 0 or len(password) == 0:
        return 0
    return len(password) * math.log2(pool_size)


def strength_label(entropy):
    if entropy < 28:
        return "Weak", WEAK_COL, 1
    elif entropy < 50:
        return "Moderate", FAIR_COL, 2
    elif entropy < 80:
        return "Strong", GOOD_COL, 3
    else:
        return "Very Strong", STRONG_COL, 4


# ── Main Application ─────────────────────────────────────────────────
class PasswordGeneratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Password Generator Pro")
        self.geometry("900x750")
        self.minsize(820, 680)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # State variables
        self.use_upper   = tk.BooleanVar(value=True)
        self.use_lower   = tk.BooleanVar(value=True)
        self.use_digits  = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.avoid_ambig = tk.BooleanVar(value=False)
        self.avoid_repeat= tk.BooleanVar(value=False)
        self.length_var  = tk.IntVar(value=16)
        self.password_var= tk.StringVar(value="")
        self.exclude_var = tk.StringVar(value="")
        self.history     = load_history()

        self._build_ui()
        self._on_generate()   # generate one on startup

    # ── UI Construction ───────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG_DARK)
        hdr.pack(fill="x", padx=24, pady=(20, 8))
        tk.Label(hdr, text="🔐", font=("Segoe UI Emoji", 26),
                 bg=BG_DARK, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="  Secure Password Generator Pro",
                 font=FONT_TITLE, bg=BG_DARK, fg=TEXT_PRIMARY).pack(side="left")
        tk.Label(hdr,
                 text="Powered by cryptographically secure randomness",
                 font=FONT_SMALL, bg=BG_DARK, fg=TEXT_MUTED).pack(side="right", pady=6)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=24, pady=(0, 12))

        # Two-column layout
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill="both", expand=True, padx=24, pady=0)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        left  = tk.Frame(body, bg=BG_DARK)
        right = tk.Frame(body, bg=BG_DARK)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    # ── Left Panel ────────────────────────────────────────────────────
    def _build_left(self, parent):
        # Password display card
        card1 = self._card(parent, "Generated Password")
        card1.pack(fill="x", pady=(0, 12))

        pw_frame = tk.Frame(card1, bg=BG_INPUT, bd=0, relief="flat",
                            highlightthickness=1, highlightbackground=BORDER)
        pw_frame.pack(fill="x", padx=12, pady=(0, 10))

        self.pw_display = tk.Entry(
            pw_frame, textvariable=self.password_var,
            font=FONT_MONO, bg=BG_INPUT, fg=ACCENT,
            bd=0, relief="flat", state="readonly",
            readonlybackground=BG_INPUT, cursor="arrow",
            justify="center", width=30
        )
        self.pw_display.pack(fill="x", padx=12, pady=12)

        btn_row = tk.Frame(card1, bg=BG_CARD)
        btn_row.pack(fill="x", padx=12, pady=(0, 12))

        self._btn(btn_row, "⚡ Generate", self._on_generate, ACCENT, side="left")
        self._btn(btn_row, "📋 Copy", self._on_copy, ACCENT2, side="left", padx=8)
        self._btn(btn_row, "🔄 Refresh", self._on_generate, ACCENT4, side="right")

        # Strength meter card
        card2 = self._card(parent, "Password Strength")
        card2.pack(fill="x", pady=(0, 12))

        self.strength_label_var = tk.StringVar(value="—")
        self.entropy_label_var  = tk.StringVar(value="Entropy: —")

        row_s = tk.Frame(card2, bg=BG_CARD)
        row_s.pack(fill="x", padx=12, pady=(0, 6))

        self.strength_lbl = tk.Label(row_s, textvariable=self.strength_label_var,
                                     font=("Segoe UI", 14, "bold"),
                                     bg=BG_CARD, fg=GOOD_COL)
        self.strength_lbl.pack(side="left")
        tk.Label(row_s, textvariable=self.entropy_label_var,
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED).pack(side="right")

        self.meter_canvas = tk.Canvas(card2, height=12, bg=BG_INPUT,
                                      bd=0, highlightthickness=0)
        self.meter_canvas.pack(fill="x", padx=12, pady=(0, 8))

        self.strength_tips = tk.Label(card2, text="", font=FONT_SMALL,
                                      bg=BG_CARD, fg=TEXT_MUTED,
                                      wraplength=400, justify="left")
        self.strength_tips.pack(padx=12, pady=(0, 10), anchor="w")

        # Length card
        card3 = self._card(parent, "Password Length")
        card3.pack(fill="x", pady=(0, 12))

        len_row = tk.Frame(card3, bg=BG_CARD)
        len_row.pack(fill="x", padx=12, pady=(0, 10))

        self.len_slider = ttk.Scale(
            len_row, from_=4, to=128, orient="horizontal",
            variable=self.length_var, command=self._on_length_change
        )
        self._style_scale()
        self.len_slider.pack(side="left", fill="x", expand=True, padx=(0, 12))

        self.len_spinbox = ttk.Spinbox(
            len_row, from_=4, to=128, textvariable=self.length_var,
            width=5, font=FONT_BODY, command=self._on_generate
        )
        self.len_spinbox.pack(side="right")
        self.len_spinbox.bind("<Return>", lambda e: self._on_generate())

        # Character types card
        card4 = self._card(parent, "Character Types")
        card4.pack(fill="x", pady=(0, 12))

        checks = [
            ("Uppercase  A-Z", self.use_upper,   ACCENT),
            ("Lowercase  a-z", self.use_lower,   ACCENT2),
            ("Numbers   0-9",  self.use_digits,  FAIR_COL),
            ("Symbols  !@#$%", self.use_symbols, ACCENT3),
        ]
        for i, (label, var, col) in enumerate(checks):
            self._checkbox(card4, label, var, col)

        # Export row
        exp_row = tk.Frame(parent, bg=BG_DARK)
        exp_row.pack(fill="x", pady=(4, 0))
        self._btn(exp_row, "💾 Export TXT", self._export_txt, TEXT_MUTED, side="left", small=True)
        self._btn(exp_row, "📊 Export CSV", self._export_csv, TEXT_MUTED, side="left", padx=8, small=True)

    # ── Right Panel ───────────────────────────────────────────────────
    def _build_right(self, parent):
        # Advanced settings card
        card5 = self._card(parent, "Advanced Settings")
        card5.pack(fill="x", pady=(0, 12))

        self._checkbox(card5, "Avoid ambiguous chars  (O,0,l,I,1)", self.avoid_ambig, ACCENT4)
        self._checkbox(card5, "Avoid repeated characters",            self.avoid_repeat, ACCENT4)

        excl_lbl = tk.Label(card5, text="Exclude custom characters:",
                            font=FONT_SMALL, bg=BG_CARD, fg=TEXT_MUTED)
        excl_lbl.pack(anchor="w", padx=12, pady=(6, 2))

        excl_entry = tk.Entry(card5, textvariable=self.exclude_var,
                              font=FONT_BODY, bg=BG_INPUT, fg=TEXT_PRIMARY,
                              bd=0, relief="flat", insertbackground=ACCENT,
                              highlightthickness=1, highlightbackground=BORDER)
        excl_entry.pack(fill="x", padx=12, pady=(0, 10))
        excl_entry.bind("<KeyRelease>", lambda e: self._on_generate())

        # Quick presets card
        card6 = self._card(parent, "Quick Presets")
        card6.pack(fill="x", pady=(0, 12))

        presets = [
            ("PIN (4-digit)",      4,  False, False, True,  False),
            ("Simple (8-char)",    8,  True,  True,  True,  False),
            ("Standard (12-char)", 12, True,  True,  True,  True),
            ("Strong (20-char)",   20, True,  True,  True,  True),
            ("Max Security (32)",  32, True,  True,  True,  True),
        ]
        for name, ln, up, lo, di, sy in presets:
            btn = tk.Button(
                card6, text=name, font=FONT_SMALL,
                bg=BG_INPUT, fg=TEXT_PRIMARY, bd=0, relief="flat",
                activebackground=ACCENT, activeforeground=BG_DARK,
                cursor="hand2", pady=5,
                command=lambda l=ln, u=up, lo_=lo, d=di, s=sy:
                    self._apply_preset(l, u, lo_, d, s)
            )
            btn.pack(fill="x", padx=12, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=ACCENT, fg=BG_DARK))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=BG_INPUT, fg=TEXT_PRIMARY))

        # History card
        card7 = self._card(parent, "Password History")
        card7.pack(fill="both", expand=True, pady=(0, 0))

        hist_container = tk.Frame(card7, bg=BG_CARD)
        hist_container.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        scrollbar = ttk.Scrollbar(hist_container, orient="vertical")
        self.history_list = tk.Listbox(
            hist_container, bg=BG_INPUT, fg=TEXT_PRIMARY,
            font=("Cascadia Code", 9), bd=0, relief="flat",
            selectbackground=ACCENT, selectforeground=BG_DARK,
            activestyle="none", highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.history_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_list.pack(side="left", fill="both", expand=True)
        self.history_list.bind("<Double-Button-1>", self._copy_history_item)

        clr_btn = tk.Button(card7, text="🗑  Clear History", font=FONT_SMALL,
                            bg=BG_CARD, fg=WEAK_COL, bd=0, relief="flat",
                            cursor="hand2", command=self._clear_history)
        clr_btn.pack(pady=(2, 8))

        self._refresh_history_list()

    # ── Widget Helpers ────────────────────────────────────────────────
    def _card(self, parent, title):
        frame = tk.LabelFrame(
            parent, text=f"  {title}  ",
            font=FONT_HEADING, bg=BG_CARD, fg=ACCENT,
            bd=1, relief="flat",
            highlightthickness=1, highlightbackground=BORDER,
            labelanchor="nw", padx=0, pady=0
        )
        return frame

    def _btn(self, parent, text, cmd, color, side="left", padx=4, small=False):
        f = FONT_SMALL if small else FONT_BODY
        btn = tk.Button(
            parent, text=text, command=cmd,
            font=f, bg=color, fg=BG_DARK,
            bd=0, relief="flat", cursor="hand2",
            padx=10, pady=6 if not small else 4,
            activebackground=TEXT_PRIMARY, activeforeground=BG_DARK
        )
        btn.pack(side=side, padx=padx, pady=0)
        return btn

    def _checkbox(self, parent, text, var, color):
        cb = tk.Checkbutton(
            parent, text=text, variable=var,
            font=FONT_BODY, bg=BG_CARD, fg=TEXT_PRIMARY,
            selectcolor=BG_INPUT, activebackground=BG_CARD,
            activeforeground=color, cursor="hand2",
            command=self._on_generate
        )
        cb.pack(anchor="w", padx=12, pady=3)

    def _style_scale(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Horizontal.TScale",
                        background=BG_CARD, troughcolor=BG_INPUT,
                        sliderthickness=16, sliderrelief="flat")

    # ── Core Logic ────────────────────────────────────────────────────
    def _build_charset(self):
        charset = ""
        if self.use_upper.get():   charset += string.ascii_uppercase
        if self.use_lower.get():   charset += string.ascii_lowercase
        if self.use_digits.get():  charset += string.digits
        if self.use_symbols.get(): charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if self.avoid_ambig.get():
            for ch in "O0lI1|`":
                charset = charset.replace(ch, "")

        excl = self.exclude_var.get()
        for ch in excl:
            charset = charset.replace(ch, "")

        return charset

    def _generate_password(self, length, charset):
        """Generate a cryptographically secure password."""
        if not charset:
            return None

        # Guarantee at least one char from each selected type
        required = []
        pool_map = []
        if self.use_upper.get():
            up = "".join(c for c in string.ascii_uppercase if c in charset)
            if up:
                required.append(secrets.choice(up))
                pool_map.append(up)
        if self.use_lower.get():
            lo = "".join(c for c in string.ascii_lowercase if c in charset)
            if lo:
                required.append(secrets.choice(lo))
                pool_map.append(lo)
        if self.use_digits.get():
            di = "".join(c for c in string.digits if c in charset)
            if di:
                required.append(secrets.choice(di))
                pool_map.append(di)
        if self.use_symbols.get():
            sy = "".join(c for c in charset if c in "!@#$%^&*()_+-=[]{}|;:,.<>?")
            if sy:
                required.append(secrets.choice(sy))
                pool_map.append(sy)

        remaining = length - len(required)
        if remaining < 0:
            remaining = 0

        if self.avoid_repeat.get():
            pool = list(charset)
            secrets.SystemRandom().shuffle(pool)
            body = pool[:remaining]
        else:
            body = [secrets.choice(charset) for _ in range(remaining)]

        combined = required + body
        secrets.SystemRandom().shuffle(combined)
        return "".join(combined)

    def _on_generate(self, *_):
        length = self.length_var.get()
        try:
            length = int(length)
        except Exception:
            length = 16

        length = max(4, min(128, length))
        self.length_var.set(length)

        if not (self.use_upper.get() or self.use_lower.get()
                or self.use_digits.get() or self.use_symbols.get()):
            self.password_var.set("⚠ Select at least one character type")
            self._update_meter(0, 1)
            return

        charset = self._build_charset()
        if not charset:
            self.password_var.set("⚠ Charset empty after exclusions")
            self._update_meter(0, 1)
            return

        pw = self._generate_password(length, charset)
        if pw is None:
            self.password_var.set("⚠ Unable to generate")
            return

        self.password_var.set(pw)
        entropy = calc_entropy(pw, len(set(charset)))
        label, color, level = strength_label(entropy)
        self.strength_label_var.set(label)
        self.strength_lbl.config(fg=color)
        self.entropy_label_var.set(f"Entropy: {entropy:.1f} bits")
        self._update_meter(level, color)
        self._update_tips(label, length)

    def _update_meter(self, level, color):
        self.meter_canvas.update_idletasks()
        w = self.meter_canvas.winfo_width()
        if w < 2:
            w = 400
        self.meter_canvas.delete("all")
        self.meter_canvas.create_rectangle(0, 0, w, 12, fill=BG_INPUT, outline="")
        fill_w = (w * level) // 4
        self.meter_canvas.create_rectangle(0, 0, fill_w, 12, fill=color, outline="")

    def _update_tips(self, label, length):
        tips = {
            "Weak":      "💡 Use a longer password with mixed character types.",
            "Moderate":  "💡 Good start — add symbols or increase length.",
            "Strong":    "✅ Strong password. Suitable for most accounts.",
            "Very Strong": "🛡 Excellent! This password is extremely secure.",
        }
        self.strength_tips.config(text=tips.get(label, ""))

    def _on_length_change(self, val):
        self.length_var.set(int(float(val)))
        self._on_generate()

    def _on_copy(self):
        pw = self.password_var.get()
        if not pw or pw.startswith("⚠"):
            messagebox.showwarning("Nothing to Copy", "Generate a valid password first.")
            return
        try:
            pyperclip.copy(pw)
            # Add to history
            entry = {"password": pw, "timestamp": datetime.datetime.now().isoformat()}
            self.history.insert(0, entry)
            self.history = self.history[:50]
            save_history(self.history)
            self._refresh_history_list()
            self._flash_copy_success()
        except Exception as e:
            messagebox.showerror("Clipboard Error", f"Clipboard access failed:\n{e}")

    def _flash_copy_success(self):
        orig = self.pw_display.cget("fg")
        self.pw_display.config(fg=ACCENT2, state="normal")
        self.pw_display.delete(0, "end")
        self.pw_display.insert(0, "✓ Copied to clipboard!")
        self.pw_display.config(state="readonly", readonlybackground=BG_INPUT)
        self.after(1500, lambda: self._restore_pw(orig))

    def _restore_pw(self, orig_fg):
        pw = self.history[0]["password"] if self.history else ""
        self.pw_display.config(state="normal", fg=ACCENT)
        self.pw_display.delete(0, "end")
        self.pw_display.insert(0, pw)
        self.pw_display.config(state="readonly", readonlybackground=BG_INPUT)

    def _apply_preset(self, length, upper, lower, digits, symbols):
        self.length_var.set(length)
        self.use_upper.set(upper)
        self.use_lower.set(lower)
        self.use_digits.set(digits)
        self.use_symbols.set(symbols)
        self._on_generate()

    def _refresh_history_list(self):
        self.history_list.delete(0, "end")
        for item in self.history:
            ts = item.get("timestamp", "")[:16].replace("T", " ")
            self.history_list.insert("end", f"{ts}  {item['password']}")

    def _copy_history_item(self, event):
        sel = self.history_list.curselection()
        if not sel:
            return
        idx = sel[0]
        pw = self.history[idx]["password"]
        try:
            pyperclip.copy(pw)
            messagebox.showinfo("Copied", f"Password copied:\n{pw}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_history(self):
        if messagebox.askyesno("Clear History", "Delete all saved history?"):
            self.history = []
            save_history(self.history)
            self._refresh_history_list()

    def _export_txt(self):
        if not self.history:
            messagebox.showinfo("Export", "No history to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w") as f:
                for item in self.history:
                    f.write(f"{item['timestamp']}  {item['password']}\n")
            messagebox.showinfo("Exported", f"History saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _export_csv(self):
        if not self.history:
            messagebox.showinfo("Export", "No history to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "password"])
                writer.writeheader()
                writer.writerows(self.history)
            messagebox.showinfo("Exported", f"History saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
