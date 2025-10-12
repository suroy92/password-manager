import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

class MasterPasswordDialog(tk.Toplevel):
    def __init__(self, parent, title="Set Master Password"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        tk.Label(self, text="Master password:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        tk.Label(self, text="Confirm password:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.e1 = tk.Entry(self, show="*"); self.e1.grid(row=0, column=1, padx=6, pady=6)
        self.e2 = tk.Entry(self, show="*"); self.e2.grid(row=1, column=1, padx=6, pady=6)
        self.btn = ttk.Button(self, text="Continue", command=self._ok, state="disabled")
        self.btn.grid(row=2, column=0, columnspan=2, pady=8)
        self.e1.bind("<KeyRelease>", self._check)
        self.e2.bind("<KeyRelease>", self._check)

    def _check(self, *_):
        p1, p2 = self.e1.get(), self.e2.get()
        ok = len(p1) >= 12 and p1 == p2
        self.btn.configure(state="normal" if ok else "disabled")

    def _ok(self):
        self.result = self.e1.get()
        self.destroy()

class UnlockDialog(tk.Toplevel):
    def __init__(self, parent, title="Unlock Vault"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        tk.Label(self, text="Master password:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.e1 = tk.Entry(self, show="*"); self.e1.grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(self, text="Unlock", command=self._ok).grid(row=1, column=0, columnspan=2, pady=8)

    def _ok(self):
        self.result = self.e1.get()
        self.destroy()

class PlainExportWarningDialog(tk.Toplevel):
    def __init__(self, parent, confirm_text="I UNDERSTAND"):
        super().__init__(parent)
        self.title("Danger: Plaintext Export")
        tk.Label(self, text=(
            "Exporting to plaintext JSON will write your secrets unencrypted to disk.\n"
            "This is dangerous. Type the confirmation text to proceed:"
        )).grid(row=0, column=0, padx=8, pady=8)
        self.entry = tk.Entry(self); self.entry.grid(row=1, column=0, padx=8, pady=8)
        self.entry.insert(0, confirm_text)
        self._required = confirm_text
        self.ok = False
        self.btn = ttk.Button(self, text="Proceed", command=self._ok, state="disabled")
        self.btn.grid(row=2, column=0, pady=8)
        self.entry.bind("<KeyRelease>", self._check)

    def _check(self, *_):
        self.btn.configure(state="normal" if self.entry.get() == self._required else "disabled")

    def _ok(self):
        self.ok = True
        self.destroy()

def show_error(parent, message: str):
    messagebox.showerror("Error", message, parent=parent)
