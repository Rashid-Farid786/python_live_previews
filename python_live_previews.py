import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import threading
import time
import os


class PythonLivePreview:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Live Preview - Practice")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)

        self.process = None
        self.create_ui()
        self.load_example()

        self.root.bind("<F5>", lambda event: self.run_code())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())

    # -------------------------------------------------
    # UI
    # -------------------------------------------------
    def create_ui(self):

        # Top toolbar
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x")

        ttk.Button(
            toolbar,
            text="▶ Run (F5)",
            command=self.run_code
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="■ Stop",
            command=self.stop_code
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="Clear Output",
            command=self.clear_output
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="New",
            command=self.new_file
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="Open",
            command=self.open_file
        ).pack(side="left", padx=4)

        ttk.Button(
            toolbar,
            text="Save",
            command=self.save_file
        ).pack(side="left", padx=4)

        self.status = ttk.Label(
            toolbar,
            text="Ready",
            anchor="e"
        )
        self.status.pack(side="right", padx=10)

        # Main area
        main = ttk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL
        )
        main.pack(fill="both", expand=True, padx=8, pady=5)

        # -------------------------------------------------
        # LEFT - Code Editor
        # -------------------------------------------------
        editor_frame = ttk.Frame(main)

        title = ttk.Label(
            editor_frame,
            text="Python Code",
            font=("Arial", 12, "bold")
        )
        title.pack(anchor="w", pady=(0, 5))

        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill="both", expand=True)

        # Line numbers
        self.line_numbers = tk.Text(
            editor_container,
            width=5,
            padx=5,
            pady=8,
            state="disabled",
            bg="#eeeeee",
            fg="#555555",
            font=("Consolas", 11)
        )
        self.line_numbers.pack(side="left", fill="y")

        # Code editor
        self.code_editor = tk.Text(
            editor_container,
            wrap="none",
            undo=True,
            font=("Consolas", 11),
            padx=10,
            pady=8
        )
        self.code_editor.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Scrollbars
        y_scroll = ttk.Scrollbar(
            editor_container,
            orient="vertical",
            command=self.code_editor.yview
        )
        y_scroll.pack(side="right", fill="y")

        self.code_editor.configure(
            yscrollcommand=self.on_editor_scroll
        )

        self.code_editor.bind(
            "<KeyRelease>",
            self.update_line_numbers
        )

        self.code_editor.bind(
            "<MouseWheel>",
            self.update_line_numbers
        )

        main.add(editor_frame, weight=1)

        # -------------------------------------------------
        # RIGHT - Output
        # -------------------------------------------------
        output_frame = ttk.Frame(main)

        ttk.Label(
            output_frame,
            text="Live Output",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=(0, 5))

        self.output = tk.Text(
            output_frame,
            wrap="word",
            font=("Consolas", 11),
            bg="#111111",
            fg="#eeeeee",
            insertbackground="white",
            padx=10,
            pady=10
        )
        self.output.pack(
            fill="both",
            expand=True
        )

        main.add(output_frame, weight=1)

        # -------------------------------------------------
        # Bottom info
        # -------------------------------------------------
        bottom = ttk.Frame(
            self.root,
            padding=5
        )
        bottom.pack(fill="x")

        ttk.Label(
            bottom,
            text="F5 = Run   |   Ctrl+S = Save   |   Ctrl+O = Open",
            foreground="#555555"
        ).pack(side="left")

        self.python_version = ttk.Label(
            bottom,
            text=f"Python: {sys.version.split()[0]}"
        )
        self.python_version.pack(side="right")

    # -------------------------------------------------
    # Example Code
    # -------------------------------------------------
    def load_example(self):

        example = '''# Python Live Preview Practice

name = "Rashid"

print("Hello,", name)

numbers = [10, 20, 30, 40, 50]

total = sum(numbers)

print("Numbers:", numbers)
print("Total:", total)

for number in numbers:
    print("Number:", number)

print("\\nPractice completed!")
'''

        self.code_editor.delete("1.0", tk.END)
        self.code_editor.insert("1.0", example)

        self.update_line_numbers()

    # -------------------------------------------------
    # Line Numbers
    # -------------------------------------------------
    def update_line_numbers(self, event=None):

        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)

        lines = self.code_editor.index("end-1c").split(".")[0]

        numbers = "\n".join(
            str(i) for i in range(1, int(lines) + 1)
        )

        self.line_numbers.insert("1.0", numbers)

        self.line_numbers.config(state="disabled")

    def on_editor_scroll(self, *args):

        self.code_editor.yview(*args)

        self.line_numbers.yview_moveto(
            args[0]
        )

    # -------------------------------------------------
    # Run Code
    # -------------------------------------------------
    def run_code(self):

        if self.process is not None:
            messagebox.showinfo(
                "Running",
                "Code is already running."
            )
            return

        code = self.code_editor.get(
            "1.0",
            tk.END
        )

        if not code.strip():
            messagebox.showwarning(
                "Empty Code",
                "Please enter Python code."
            )
            return

        self.clear_output()

        self.status.config(
            text="Running..."
        )

        self.write_output(
            ">>> Running Python code...\n\n"
        )

        thread = threading.Thread(
            target=self.execute_code,
            args=(code,),
            daemon=True
        )

        thread.start()

    # -------------------------------------------------
    # Execute Python
    # -------------------------------------------------
    def execute_code(self, code):

        filename = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__)
            ),
            "_live_preview_temp.py"
        )

        try:

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(code)

            start_time = time.time()

            self.process = subprocess.Popen(
                [
                    sys.executable,
                    "-u",
                    filename
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1
            )

            while True:

                line = self.process.stdout.readline()

                if line == "" and self.process.poll() is not None:
                    break

                if line:
                    self.write_output(line)

            return_code = self.process.wait()

            elapsed = time.time() - start_time

            if return_code == 0:

                self.write_output(
                    f"\n>>> Finished successfully "
                    f"({elapsed:.2f}s)\n"
                )

                self.root.after(
                    0,
                    lambda: self.status.config(
                        text="Finished"
                    )
                )

            else:

                self.write_output(
                    f"\n>>> Program exited with code "
                    f"{return_code}\n"
                )

                self.root.after(
                    0,
                    lambda: self.status.config(
                        text="Error"
                    )
                )

        except Exception as e:

            self.write_output(
                f"\nApplication Error:\n{e}\n"
            )

            self.root.after(
                0,
                lambda: self.status.config(
                    text="Error"
                )
            )

        finally:

            self.process = None

            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except:
                pass

    # -------------------------------------------------
    # Output
    # -------------------------------------------------
    def write_output(self, text):

        self.root.after(
            0,
            lambda: self._write_output(text)
        )

    def _write_output(self, text):

        self.output.insert(
            tk.END,
            text
        )

        self.output.see(tk.END)

    def clear_output(self):

        self.output.delete(
            "1.0",
            tk.END
        )

    # -------------------------------------------------
    # Stop
    # -------------------------------------------------
    def stop_code(self):

        if self.process:

            try:
                self.process.terminate()

                self.write_output(
                    "\n>>> Program stopped by user.\n"
                )

                self.status.config(
                    text="Stopped"
                )

            except Exception as e:

                self.write_output(
                    f"\nStop Error: {e}\n"
                )

        else:

            self.status.config(
                text="Nothing running"
            )

    # -------------------------------------------------
    # New
    # -------------------------------------------------
    def new_file(self):

        if self.code_editor.get(
            "1.0",
            tk.END
        ).strip():

            answer = messagebox.askyesno(
                "New File",
                "Clear current code?"
            )

            if not answer:
                return

        self.code_editor.delete(
            "1.0",
            tk.END
        )

        self.update_line_numbers()
        self.clear_output()
        self.status.config(text="New file")

    # -------------------------------------------------
    # Open
    # -------------------------------------------------
    def open_file(self):

        filename = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[
                ("Python Files", "*.py"),
                ("All Files", "*.*")
            ]
        )

        if not filename:
            return

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as file:

                code = file.read()

            self.code_editor.delete(
                "1.0",
                tk.END
            )

            self.code_editor.insert(
                "1.0",
                code
            )

            self.update_line_numbers()

            self.status.config(
                text=f"Opened: {os.path.basename(filename)}"
            )

        except Exception as e:

            messagebox.showerror(
                "Open Error",
                str(e)
            )

    # -------------------------------------------------
    # Save
    # -------------------------------------------------
    def save_file(self):

        filename = filedialog.asksaveasfilename(
            title="Save Python File",
            defaultextension=".py",
            filetypes=[
                ("Python Files", "*.py"),
                ("All Files", "*.*")
            ]
        )

        if not filename:
            return

        try:

            code = self.code_editor.get(
                "1.0",
                tk.END
            )

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(code)

            self.status.config(
                text=f"Saved: {os.path.basename(filename)}"
            )

        except Exception as e:

            messagebox.showerror(
                "Save Error",
                str(e)
            )


# -------------------------------------------------
# Application Start
# -------------------------------------------------
if __name__ == "__main__":

    root = tk.Tk()

    app = PythonLivePreview(root)

    root.mainloop()