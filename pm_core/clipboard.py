import tkinter as tk

def copy_to_clipboard(root: tk.Tk, text: str, timeout_seconds: int = 20) -> None:
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update_idletasks()
    def _clear():
        try:
            root.clipboard_clear()
            root.update_idletasks()
        except Exception:
            pass
    root.after(int(timeout_seconds * 1000), _clear)
