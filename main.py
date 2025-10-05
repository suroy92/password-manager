import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import (
    create_tables, list_passwords, get_password_details,
    store_password, update_password, delete_password_entry,
    export_passwords
)
from encryption import generate_secure_password

class PasswordManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("800x600")

        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 10))
        
        create_tables()
        self.create_widgets()
        self.load_passwords()

    def create_widgets(self):
        # Top buttons
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(top_frame, text="Store New", command=self.store_password_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Generate Password", command=self.generate_password_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Export Passwords", command=self.export_passwords_file).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ("id", "title", "username")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("username", text="Username")
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("title", width=250)
        self.tree.column("username", width=250)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree.bind("<Double-1>", self.on_tree_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Action buttons
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill=tk.X)

        self.view_button = ttk.Button(action_frame, text="View Details", command=self.view_details, state=tk.DISABLED)
        self.view_button.pack(side=tk.LEFT, padx=5)

        self.update_button = ttk.Button(action_frame, text="Update", command=self.update_password_dialog, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(action_frame, text="Delete", command=self.delete_password_dialog, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.copy_button = ttk.Button(action_frame, text="Copy Password", command=self.copy_password, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=5)

    def on_tree_select(self, event=None):
        selected = self.tree.selection()
        state = tk.NORMAL if selected else tk.DISABLED
        self.view_button.config(state=state)
        self.update_button.config(state=state)
        self.delete_button.config(state=state)
        self.copy_button.config(state=state)

    def on_tree_double_click(self, event=None):
        self.view_details()

    def load_passwords(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for pwd in list_passwords():
            self.tree.insert("", tk.END, values=pwd)
        self.on_tree_select()

    def store_password_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Store New Password")
        dialog.geometry("600x400")

        tk.Label(dialog, text="Title:").pack(pady=5)
        title_entry = tk.Entry(dialog); title_entry.pack()
        tk.Label(dialog, text="Username:").pack(pady=5)
        username_entry = tk.Entry(dialog); username_entry.pack()
        tk.Label(dialog, text="Password:").pack(pady=5)
        password_entry = tk.Entry(dialog, show="*"); password_entry.pack()
        tk.Label(dialog, text="Recovery Codes:").pack(pady=5)
        recovery_entry = tk.Entry(dialog); recovery_entry.pack()

        def save():
            store_password(title_entry.get(), username_entry.get(), password_entry.get(), recovery_entry.get())
            messagebox.showinfo("Success", "Password stored successfully!")
            dialog.destroy()
            self.load_passwords()

        tk.Button(dialog, text="Save", command=save).pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def generate_password_dialog(self):
        class GenerateDialog(simpledialog.Dialog):
            def body(self, master):
                tk.Label(master, text="Password Length:").grid(row=0, column=0, padx=5, pady=5)
                self.length_entry = tk.Entry(master); self.length_entry.insert(0, "10"); self.length_entry.grid(row=0, column=1, padx=5, pady=5)

                self.numbers_var = tk.IntVar()
                self.symbols_var = tk.IntVar()

                self.numbers_check = tk.Checkbutton(master, text="Include Numbers", variable=self.numbers_var)
                self.numbers_check.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

                self.symbols_check = tk.Checkbutton(master, text="Include Symbols", variable=self.symbols_var)
                self.symbols_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

                tk.Button(master, text="Generate", command=self.generate).grid(row=3, column=0, columnspan=2, pady=5)

                tk.Label(master, text="Generated Password:").grid(row=4, column=0, padx=5, pady=5)
                self.result_entry = tk.Entry(master)
                self.result_entry.grid(row=4, column=1, padx=5, pady=5)
                return self.length_entry

            def generate(self):
                length = int(self.length_entry.get())
                numbers = self.numbers_var.get() == 1
                symbols = self.symbols_var.get() == 1
                self.result_entry.delete(0, tk.END)
                self.result_entry.insert(0, generate_secure_password(length, numbers, symbols))

        GenerateDialog(self.root)

    def view_details(self):
        selected = self.tree.selection()
        if not selected: return
        entry_id = self.tree.item(selected[0], 'values')[0]
        details = get_password_details(entry_id)
        if details:
            messagebox.showinfo(
                "Password Details",
                f"ID: {details['id']}\nTitle: {details['title']}\nUsername: {details['username']}\n"
                f"Password: {details['password']}\nRecovery Codes: {details['recovery_codes']}\nCreated At: {details['created_at']}"
            )

    def update_password_dialog(self):
        selected = self.tree.selection()
        if not selected: return
        entry_id = self.tree.item(selected[0], 'values')[0]
        details = get_password_details(entry_id)
        if not details:
            messagebox.showerror("Error", "Password not found!"); return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Update Password for {details['title']}")
        dialog.geometry("600x400")

        tk.Label(dialog, text="Title:").pack(pady=5)
        title_entry = tk.Entry(dialog); title_entry.insert(0, details['title']); title_entry.pack()
        tk.Label(dialog, text="Username:").pack(pady=5)
        username_entry = tk.Entry(dialog); username_entry.insert(0, details['username']); username_entry.pack()
        tk.Label(dialog, text="Password:").pack(pady=5)
        password_entry = tk.Entry(dialog); password_entry.insert(0, details['password']); password_entry.pack()
        tk.Label(dialog, text="Recovery Codes:").pack(pady=5)
        recovery_entry = tk.Entry(dialog); recovery_entry.insert(0, details['recovery_codes']); recovery_entry.pack()

        def save_update():
            update_password(entry_id, title_entry.get(), username_entry.get(), password_entry.get(), recovery_entry.get())
            messagebox.showinfo("Success", "Password updated successfully!"); dialog.destroy(); self.load_passwords()

        tk.Button(dialog, text="Save", command=save_update).pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def delete_password_dialog(self):
        selected = self.tree.selection()
        if not selected: return
        entry_id = self.tree.item(selected[0], 'values')[0]
        if messagebox.askyesno("Delete", "Are you sure you want to delete this entry?"):
            delete_password_entry(entry_id)
            messagebox.showinfo("Deleted", "Password deleted successfully!")
            self.load_passwords()

    def copy_password(self):
        selected = self.tree.selection()
        if not selected: return
        entry_id = self.tree.item(selected[0], 'values')[0]
        details = get_password_details(entry_id)
        if details:
            self.root.clipboard_clear()
            self.root.clipboard_append(details['password'])
            messagebox.showinfo("Copied", "Password copied to clipboard!")

    def export_passwords_file(self):
        try:
            message = export_passwords()
            messagebox.showinfo("Export Successful", message)
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
