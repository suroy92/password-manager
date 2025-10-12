import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import font as tkfont

from ttkbootstrap import Window, Style
from ttkbootstrap import ttk
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import Meter

# --- App modules (existing) ---
from database import (
    create_tables, list_passwords, get_password_details,
    store_password, update_password, delete_password_entry,
    export_passwords, DB_FILE
)
from encryption import generate_secure_password, initialize_vault

# Security features
from pm_core.clipboard import copy_to_clipboard
from pm_core.export_import import export_encrypted
from pm_core.rotation import rotate_master_password


# =========================
#  GLOBAL FONT PREFERENCES
# =========================
def apply_app_fonts():
    """
    Pick the first installed font from a platform-specific preference list
    and apply it to Tk named fonts and common ttk styles.

    Windows: Inter → Segoe UI Variable → Segoe UI → Arial → Noto Sans
    macOS:   SF Pro (if available) → Helvetica Neue → Inter → Arial → Noto Sans
    Linux:   Inter → Cantarell → Ubuntu → Noto Sans → DejaVu Sans → Arial
    """
    if sys.platform == "win32":
        prefs = ("Inter", "Segoe UI Variable", "Segoe UI", "Arial", "Noto Sans")
    elif sys.platform == "darwin":
        prefs = ("SF Pro Text", "SF Pro", "Helvetica Neue", "Inter", "Arial", "Noto Sans")
    else:
        prefs = ("Inter", "Cantarell", "Ubuntu", "Noto Sans", "DejaVu Sans", "Arial")

    available = set(map(str, tkfont.families()))
    chosen = next((f for f in prefs if f in available), None)
    if not chosen:
        return  # keep system default if none found

    def conf(name, **kw):
        try:
            f = tkfont.nametofont(name)
        except tk.TclError:
            f = tkfont.Font(name=name, exists=True)
        f.configure(**kw)

    # Apply to Tk named fonts (covers most widgets)
    conf("TkDefaultFont", family=chosen, size=10)
    conf("TkTextFont",    family=chosen, size=10)
    conf("TkMenuFont",    family=chosen, size=10)
    conf("TkHeadingFont", family=chosen, size=11, weight="bold")

    # Apply to ttk styles we touch explicitly
    st = Style()
    st.configure("TLabel", font=(chosen, 10))
    st.configure("TButton", font=(chosen, 10))
    st.configure("Treeview", font=(chosen, 10))
    st.configure("Treeview.Heading", font=(chosen, 11, "bold"))


class PasswordManagerApp:
    def __init__(self, root: Window):
        self.root = root
        self.root.title("Password Manager")

        # Search & status
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")

        # Sorting state
        self._sort_state = {"id": False, "title": False, "username": False}

        # Build UI
        self._build_menu()
        self._build_searchbar()
        self._build_tree()
        self._build_statusbar()

        # Shortcuts
        self._bind_shortcuts()

        create_tables()
        self.load_passwords()

    # =========================
    #       UI STRUCTURE
    # =========================
    def _build_menu(self):
        menubar = tk.Menu(self.root)

        # File menu (actions moved here)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Store New Ctrl+N", command=self.store_password_dialog)
        file_menu.add_command(label="Generate Password Ctrl+G", command=self.generate_password_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Export (Plaintext) Ctrl+E", command=self.export_passwords_file)
        file_menu.add_command(label="Export (Encrypted) Ctrl+Shift+E", command=self.export_encrypted_action)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Security menu
        security_menu = tk.Menu(menubar, tearoff=0)
        security_menu.add_command(
            label="Change Master Password",
            command=self.change_master_password_action
        )
        menubar.add_cascade(label="Security", menu=security_menu)

        self.root.config(menu=menubar)

    def _build_searchbar(self):
        bar = ttk.Frame(self.root, padding=(10, 10, 10, 0))
        bar.pack(fill=tk.X)

        ttk.Label(bar, text="Search:").pack(side=tk.LEFT, padx=(0, 6))
        entry = ttk.Entry(bar, textvariable=self.search_var, width=32)
        entry.pack(side=tk.LEFT)
        self.search_var.trace_add("write", lambda *_: self.load_passwords())

    def _build_tree(self):
        # Style tweaks
        style = Style()
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading")

        # Table (manual striping)
        columns = ("id", "title", "username")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.tree.heading("id", text="ID", command=lambda: self.sort_by("id", 0))
        self.tree.heading("title", text="Title", command=lambda: self.sort_by("title", 1))
        self.tree.heading("username", text="Username", command=lambda: self.sort_by("username", 2))

        self.tree.column("id", width=60, anchor=tk.CENTER)
        self.tree.column("title", width=320, anchor=tk.W)
        self.tree.column("username", width=280, anchor=tk.W)

        self._configure_row_striping()

        # Selection handling
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Context menu
        self._ctx = tk.Menu(self.root, tearoff=0)
        self._ctx.add_command(label="View Details", command=self.view_details)
        self._ctx.add_command(label="Copy Password", command=self.copy_password)
        self._ctx.add_separator()
        self._ctx.add_command(label="Update", command=self.update_password_dialog)
        self._ctx.add_command(label="Delete", command=self.delete_password_dialog)
        self.tree.bind("<Button-3>", self._open_context)

        # Action buttons (optional, kept for discoverability)
        actions = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        actions.pack(fill=tk.X)

        self.view_button = ttk.Button(actions, text="View Details", command=self.view_details, state=tk.DISABLED)
        self.view_button.pack(side=tk.LEFT, padx=4)

        self.update_button = ttk.Button(actions, text="Update", command=self.update_password_dialog, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=4)

        self.delete_button = ttk.Button(actions, text="Delete", command=self.delete_password_dialog, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=4)

        self.copy_button = ttk.Button(actions, text="Copy Password", command=self.copy_password, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=4)

    def _build_statusbar(self):
        bar = ttk.Frame(self.root, padding=(10, 6))
        bar.pack(fill=tk.X)
        ttk.Label(bar, textvariable=self.status_var, anchor="w").pack(side=tk.LEFT)

    def _bind_shortcuts(self):
        self.root.bind_all("<Control-n>", lambda e: self.store_password_dialog())
        self.root.bind_all("<Control-g>", lambda e: self.generate_password_dialog())
        self.root.bind_all("<Control-e>", lambda e: self.export_passwords_file())
        self.root.bind_all("<Control-E>", lambda e: self.export_passwords_file())   # some platforms
        self.root.bind_all("<Control-Shift-E>", lambda e: self.export_encrypted_action())

    # =========================
    #        HELPERS
    # =========================
    def _is_dark_theme(self) -> bool:
        try:
            return "dark" in Style().theme.name.lower()
        except Exception:
            return False

    def _configure_row_striping(self):
        """Set tag colors for odd/even rows based on current theme."""
        if self._is_dark_theme():
            even_bg = "#1f1f1f"
            odd_bg = "#242424"
        else:
            even_bg = "#ffffff"
            odd_bg = "#f6f7f9"
        self.tree.tag_configure("even", background=even_bg)
        self.tree.tag_configure("odd", background=odd_bg)

    def set_status(self, msg: str):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def show_toast(self, title: str, message: str, duration_ms: int = 2000):
        try:
            ToastNotification(
                title=title,
                message=message,
                duration=duration_ms,
                alert=True,
                position=(self.root.winfo_x() + 40, self.root.winfo_y() + 40),
            ).show_toast()
        except Exception:
            self.set_status(f"{title}: {message}")

    def _open_context(self, event):
        if self.tree.identify_row(event.y):
            self.tree.selection_set(self.tree.identify_row(event.y))
            self._ctx.tk_popup(event.x_root, event.y_root)

    # =========================
    #       DATA & TABLE
    # =========================
    def load_passwords(self):
        q = (self.search_var.get() or "").strip().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = list_passwords()
        if q:
            rows = [r for r in rows if q in str(r[1]).lower() or q in str(r[2]).lower()]

        for i, pwd in enumerate(rows):
            tag = "odd" if i % 2 else "even"
            self.tree.insert("", tk.END, values=pwd, tags=(tag,))

        self.on_tree_select()
        self.set_status(f"{len(rows)} item(s)")

    def sort_by(self, colname: str, idx: int):
        self._sort_state[colname] = not self._sort_state[colname]
        reverse = self._sort_state[colname]

        rows = [(self.tree.set(k, colname), k) for k in self.tree.get_children("")]
        try:
            rows.sort(key=lambda t: int(t[0]) if colname == "id" else t[0].lower(), reverse=reverse)
        except Exception:
            rows.sort(key=lambda t: t[0], reverse=reverse)

        for i, (_, k) in enumerate(rows):
            self.tree.move(k, "", i)

    def on_tree_select(self, event=None):
        selected = self.tree.selection()
        state = tk.NORMAL if selected else tk.DISABLED
        for btn in (self.view_button, self.update_button, self.delete_button, self.copy_button):
            btn.config(state=state)

    def on_tree_double_click(self, event=None):
        self.view_details()

    # =========================
    #        DIALOGS
    # =========================
    def store_password_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Store New Password")
        dialog.geometry("520x420")
        dialog.transient(self.root)
        dialog.grab_set()

        pad = dict(padx=8, pady=6)

        ttk.Label(dialog, text="Title").pack(**pad)
        title_entry = ttk.Entry(dialog, width=40)
        title_entry.pack(**pad)

        ttk.Label(dialog, text="Username").pack(**pad)
        username_entry = ttk.Entry(dialog, width=40)
        username_entry.pack(**pad)

        ttk.Label(dialog, text="Password").pack(**pad)
        pw_frame = ttk.Frame(dialog)
        pw_frame.pack(**pad)
        password_entry = ttk.Entry(pw_frame, show="*", width=34)
        password_entry.pack(side=tk.LEFT, padx=(0, 6))

        # Show/Hide toggle
        def toggle_show():
            password_entry.configure(show="" if password_entry.cget("show") == "*" else "*")
            show_btn.configure(text="Hide" if password_entry.cget("show") == "" else "Show")
        show_btn = ttk.Button(pw_frame, text="Show", command=toggle_show, bootstyle="secondary")
        show_btn.pack(side=tk.LEFT)

        # Strength meter
        meter = Meter(dialog, metersize=150, amounttotal=100, amountused=0, stripethickness=6, bootstyle="info")
        meter.pack(pady=(0, 4))
        strength_lbl = ttk.Label(dialog, text="Strength: ")
        strength_lbl.pack()

        def update_strength(*_):
            s, label = self._password_strength(password_entry.get())
            meter.configure(amountused=int(s))
            meter.configure(bootstyle=("danger" if s < 40 else "warning" if s < 70 else "success"))
            strength_lbl.configure(text=f"Strength: {label}")

        password_entry.bind("<KeyRelease>", update_strength)

        ttk.Label(dialog, text="Recovery Codes").pack(**pad)
        recovery_entry = ttk.Entry(dialog, width=40)
        recovery_entry.pack(**pad)

        def save():
            if not title_entry.get().strip():
                messagebox.showerror("Validation", "Title is required.", parent=dialog)
                return
            store_password(title_entry.get(), username_entry.get(), password_entry.get(), recovery_entry.get())
            self.show_toast("Saved", "Password stored")
            dialog.destroy()
            self.load_passwords()

        btns = ttk.Frame(dialog)
        btns.pack(pady=10)
        ttk.Button(btns, text="Save", command=save, bootstyle="success").pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Cancel", command=dialog.destroy, bootstyle="secondary").pack(side=tk.LEFT, padx=6)

        title_entry.focus_set()

    def generate_password_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Password")
        dialog.geometry("420x300")
        dialog.transient(self.root)
        dialog.grab_set()

        pad = dict(padx=8, pady=6)

        ttk.Label(dialog, text="Password Length").pack(**pad)
        length_entry = ttk.Entry(dialog, width=10)
        length_entry.insert(0, "12")
        length_entry.pack(**pad)

        numbers_var = tk.IntVar(value=1)
        symbols_var = tk.IntVar(value=1)
        ttk.Checkbutton(dialog, text="Include Numbers", variable=numbers_var).pack(**pad)
        ttk.Checkbutton(dialog, text="Include Symbols", variable=symbols_var).pack(**pad)

        ttk.Label(dialog, text="Generated Password").pack(**pad)
        result_entry = ttk.Entry(dialog, width=36)
        result_entry.pack(**pad)

        def do_generate():
            try:
                length = int(length_entry.get())
            except Exception:
                length = 12
            pw = generate_secure_password(length, bool(numbers_var.get()), bool(symbols_var.get()))
            result_entry.delete(0, tk.END)
            result_entry.insert(0, pw)

        ttk.Button(dialog, text="Generate", command=do_generate, bootstyle="primary").pack(pady=10)
        ttk.Button(dialog, text="Close", command=dialog.destroy, bootstyle="secondary").pack()

    def view_details(self):
        selected = self.tree.selection()
        if not selected:
            return
        entry_id = self.tree.item(selected[0], 'values')[0]
        details = get_password_details(entry_id)
        if details:
            messagebox.showinfo(
                "Password Details",
                f"ID: {details['id']}\nTitle: {details['title']}\nUsername: {details['username']}\n"
                f"Password: {details['password']}\nRecovery Codes: {details['recovery_codes']}\nCreated At: {details['created_at']}",
                parent=self.root
            )

    def update_password_dialog(self):
        selected = self.tree.selection()
        if not selected:
            return
        entry_id = self.tree.item(selected[0], 'values')[0]
        details = get_password_details(entry_id)
        if not details:
            messagebox.showerror("Error", "Password not found!", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Update Password for {details['title']}")
        dialog.geometry("520x430")
        dialog.transient(self.root)
        dialog.grab_set()

        pad = dict(padx=8, pady=6)

        ttk.Label(dialog, text="Title").pack(**pad)
        title_entry = ttk.Entry(dialog, width=40); title_entry.insert(0, details['title']); title_entry.pack(**pad)

        ttk.Label(dialog, text="Username").pack(**pad)
        username_entry = ttk.Entry(dialog, width=40); username_entry.insert(0, details['username']); username_entry.pack(**pad)

        ttk.Label(dialog, text="Password").pack(**pad)
        pw_frame = ttk.Frame(dialog); pw_frame.pack(**pad)
        password_entry = ttk.Entry(pw_frame, width=34, show="*"); password_entry.insert(0, details['password']); password_entry.pack(side=tk.LEFT, padx=(0,6))

        def toggle_show():
            password_entry.configure(show="" if password_entry.cget("show") == "*" else "*")
            show_btn.configure(text="Hide" if password_entry.cget("show") == "" else "Show")
        show_btn = ttk.Button(pw_frame, text="Show", command=toggle_show, bootstyle="secondary")
        show_btn.pack(side=tk.LEFT)

        # Strength meter
        meter = Meter(dialog, metersize=150, amounttotal=100, amountused=0, stripethickness=6, bootstyle="info")
        meter.pack(pady=(0, 4))
        strength_lbl = ttk.Label(dialog, text="Strength: "); strength_lbl.pack()

        def update_strength(*_):
            s, label = self._password_strength(password_entry.get())
            meter.configure(amountused=int(s))
            meter.configure(bootstyle=("danger" if s < 40 else "warning" if s < 70 else "success"))
            strength_lbl.configure(text=f"Strength: {label}")
        password_entry.bind("<KeyRelease>", update_strength)
        update_strength()

        ttk.Label(dialog, text="Recovery Codes").pack(**pad)
        recovery_entry = ttk.Entry(dialog, width=40); recovery_entry.insert(0, details['recovery_codes']); recovery_entry.pack(**pad)

        def save_update():
            update_password(entry_id, title_entry.get(), username_entry.get(), password_entry.get(), recovery_entry.get())
            self.show_toast("Saved", "Password updated")
            dialog.destroy()
            self.load_passwords()

        btns = ttk.Frame(dialog); btns.pack(pady=10)
        ttk.Button(btns, text="Save", command=save_update, bootstyle="success").pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Cancel", command=dialog.destroy, bootstyle="secondary").pack(side=tk.LEFT, padx=6)

        title_entry.focus_set()

    def delete_password_dialog(self):
        selected = self.tree.selection()
        if not selected:
            return
        entry_id = self.tree.item(selected[0], 'values')[0]
        if messagebox.askyesno("Delete", "Are you sure you want to delete this entry?", parent=self.root):
            delete_password_entry(entry_id)
            self.show_toast("Deleted", "Entry removed")
            self.load_passwords()

    def copy_password(self):
        selected = self.tree.selection()
        if not selected:
            return
        entry_id = self.tree.item(selected[0], 'values')[0]
        details = get_password_details(entry_id)
        if details:
            copy_to_clipboard(self.root, details['password'], timeout_seconds=20)
            self.show_toast("Copied", "Password copied (clears in ~20s)")
            self.set_status("Password copied to clipboard (auto-clears)")

    # =========================
    #     SECURITY ACTIONS
    # =========================
    def change_master_password_action(self):
        old_pw = simpledialog.askstring("Change Master Password", "Enter current master password:", show="*")
        if not old_pw:
            return
        new1 = simpledialog.askstring("Change Master Password", "Enter new master password:", show="*")
        new2 = simpledialog.askstring("Change Master Password", "Confirm new master password:", show="*")
        if not new1 or new1 != new2:
            messagebox.showerror("Change Master Password", "New passwords do not match.", parent=self.root)
            return

        try:
            updated = rotate_master_password(
                db_path=DB_FILE,
                old_password=old_pw,
                new_password=new1,
                table_name="passwords",
                encrypted_fields=("password",),  # extend when encrypting more columns
                id_column="id",
            )
            messagebox.showinfo("Change Master Password", f"Re-encrypted {updated} row(s) under the new master password.", parent=self.root)
            self.set_status("Master password changed")
        except Exception as e:
            messagebox.showerror("Change Master Password", f"Failed to rotate key: {e}", parent=self.root)

    def export_encrypted_action(self):
        default_name = "vault.pmjson.enc"
        out_path = filedialog.asksaveasfilename(
            title="Save Encrypted Export",
            defaultextension=".pmjson.enc",
            initialfile=default_name,
            filetypes=[("Encrypted Export", "*.pmjson.enc"), ("All Files", "*.*")]
        )
        if not out_path:
            return

        use_pass = messagebox.askyesno(
            "Encrypted Export",
            "Use a SEPARATE export passphrase (recommended)?\n\n"
            "Yes  → Protect with a passphrase you enter now (portable export).\n"
            "No   → Protect with your current vault master password.",
            parent=self.root
        )

        try:
            if use_pass:
                p1 = simpledialog.askstring("Export Passphrase", "Enter export passphrase:", show="*", parent=self.root)
                p2 = simpledialog.askstring("Export Passphrase", "Confirm export passphrase:", show="*", parent=self.root)
                if not p1 or p1 != p2:
                    messagebox.showerror("Encrypted Export", "Passphrases do not match.", parent=self.root)
                    return
                out = export_encrypted(DB_FILE, table="passwords", out_path=out_path, master_password="", passphrase=p1)
            else:
                master = simpledialog.askstring("Master Password", "Enter your master password:", show="*", parent=self.root)
                if not master:
                    return
                out = export_encrypted(DB_FILE, table="passwords", out_path=out_path, master_password=master)

            self.show_toast("Exported", os.path.basename(out))
            messagebox.showinfo("Encrypted Export", f"Encrypted export created:\n{out}", parent=self.root)
            self.set_status(f"Encrypted export saved: {out}")
        except Exception as e:
            messagebox.showerror("Encrypted Export", f"Failed: {e}", parent=self.root)

    # =========================
    #   PASSWORD STRENGTH
    # =========================
    @staticmethod
    def _password_strength(pw: str):
        if not pw:
            return 0, "Empty"
        score = 0
        length = len(pw)
        classes = sum([
            any(c.islower() for c in pw),
            any(c.isupper() for c in pw),
            any(c.isdigit() for c in pw),
            any(not c.isalnum() for c in pw),
        ])
        # Heuristic scoring
        score += min(60, length * 4)              # length weight
        score += (classes - 1) * 10               # diversity
        if length >= 16 and classes >= 3:
            score += 10
        score = max(0, min(100, score))
        label = "Weak" if score < 40 else "Okay" if score < 70 else "Strong"
        return score, label

    # =========================
    #  PLAIN-TEXT EXPORT (EXISTING)
    # =========================
    def export_passwords_file(self):
        try:
            message = export_passwords()
            messagebox.showinfo("Export Successful", message, parent=self.root)
            self.set_status("Plaintext export created")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred: {e}", parent=self.root)


if __name__ == "__main__":
    # Create themed window (light by default)
    root = Window(themename="darkly")  # change theme string here if you prefer another ttkbootstrap theme
    root.geometry("900x650")

    # Apply global fonts (Windows prefers Inter if installed)
    apply_app_fonts()

    # Initialize/Unlock the vault (first run shows setup dialog)
    initialize_vault(root)

    # Start UI
    app = PasswordManagerApp(root)
    root.mainloop()
