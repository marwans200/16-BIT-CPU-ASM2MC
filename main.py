import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Menu
import re

opcodes = ["NOP", "ADD", "SUB", "AND", "OR", "NOT", "INC", "DCR", "SHL", "SHR", "CLR", "STR", "HLT", "LDA", "MOV"]
current_file_path = None
is_dark_theme = True  # Default to dark

def to_bin(val_str, bits):
    try:
        return bin(int(val_str))[2:].zfill(bits)
    except ValueError:
        return None

def assemble_code():
    input_text = input_textbox.get("1.0", tk.END).strip().splitlines()
    output_textbox.delete("1.0", tk.END)

    for line_no, line in enumerate(input_text, start=1):
        line = line.split(";")[0].strip()  # Remove comments
        if not line:
            continue

        parts = line.strip().split()
        if not parts:
            continue

        instr = parts[0].upper()
        if instr not in opcodes:
            messagebox.showerror("Error", f"Unknown instruction '{instr}' on line {line_no}")
            return

        opcode_bin = to_bin(opcodes.index(instr), 8)
        args = parts[1:] + ['0'] * (4 - len(parts[1:]))

        write_sel_bin = to_bin(args[0], 8)
        read_sel_B_bin = to_bin(args[1], 8)
        read_sel_A_bin = to_bin(args[2], 8)
        data_bin = to_bin(args[3], 16)

        if None in [write_sel_bin, opcode_bin, read_sel_B_bin, read_sel_A_bin, data_bin]:
            messagebox.showerror("Error", f"Invalid numeric value on line {line_no}")
            return

        full_bin = write_sel_bin + opcode_bin + read_sel_B_bin + read_sel_A_bin + data_bin
        grouped = " ".join([full_bin[i:i+16] for i in range(0, 56, 16)])
        output_textbox.insert(tk.END, grouped + "\n")

def save_mar_file(as_new=False):
    global current_file_path
    if as_new or not current_file_path:
        file_path = filedialog.asksaveasfilename(defaultextension=".mar",
                                                 filetypes=[("MAR Assembly Files", "*.mar")],
                                                 title="Save .mar Assembly File")
        if not file_path:
            return
        current_file_path = file_path

    code = input_textbox.get("1.0", tk.END).strip()
    try:
        with open(current_file_path, 'w') as f:
            f.write(code)
        messagebox.showinfo("Success", f"Saved to {current_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file:\n{e}")

def open_mar_file():
    global current_file_path
    file_path = filedialog.askopenfilename(filetypes=[("MAR Assembly Files", "*.mar")],
                                           title="Open .mar Assembly File")
    if not file_path:
        return

    try:
        with open(file_path, 'r') as f:
            code = f.read()
        input_textbox.delete("1.0", tk.END)
        input_textbox.insert(tk.END, code)
        highlight_syntax()
        current_file_path = file_path
        messagebox.showinfo("Loaded", f"Loaded from {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file:\n{e}")

def save_binary_output():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")],
                                             title="Save Binary Output")
    if not file_path:
        return

    binary_output = output_textbox.get("1.0", tk.END).strip()
    try:
        with open(file_path, 'w') as f:
            f.write(binary_output)
        messagebox.showinfo("Success", f"Binary saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save binary:\n{e}")

def new_file():
    global current_file_path
    current_file_path = None
    input_textbox.delete("1.0", tk.END)
    output_textbox.delete("1.0", tk.END)

def highlight_syntax(event=None):
    input_textbox.tag_remove("opcode", "1.0", tk.END)
    input_textbox.tag_remove("comment", "1.0", tk.END)
    input_textbox.tag_remove("number", "1.0", tk.END)

    lines = input_textbox.get("1.0", tk.END).splitlines()
    for i, line in enumerate(lines):
        idx = f"{i+1}.0"

        # Highlight opcodes
        for op in opcodes:
            start = line.find(op)
            if start != -1:
                input_textbox.tag_add("opcode", f"{i+1}.{start}", f"{i+1}.{start+len(op)}")

        # Highlight comments
        if ";" in line:
            start = line.find(";")
            input_textbox.tag_add("comment", f"{i+1}.{start}", f"{i+1}.end")

        # Highlight numbers
        for match in re.finditer(r"\b\d+\b", line):
            input_textbox.tag_add("number", f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")

def toggle_theme():
    global is_dark_theme
    is_dark_theme = not is_dark_theme
    apply_theme()

def apply_theme():
    bg = "#1e1e1e" if is_dark_theme else "white"
    fg = "#d4d4d4" if is_dark_theme else "black"
    code_bg = "#2d2d2d" if is_dark_theme else "white"
    code_fg = "#dcdcdc" if is_dark_theme else "black"

    root.configure(bg=bg)
    input_textbox.configure(bg=code_bg, fg=code_fg, insertbackground=fg)
    output_textbox.configure(bg=code_bg, fg=code_fg, insertbackground=fg)
    for widget in [label_input, label_output]:
        widget.configure(bg=bg, fg=fg)

    input_textbox.tag_config("opcode", foreground="#4FC1FF")
    input_textbox.tag_config("comment", foreground="#6A9955")
    input_textbox.tag_config("number", foreground="#FFD700")

# ==== GUI SETUP ====
root = tk.Tk()
root.title("MAR Assembler")
root.geometry("900x620")

# Menu bar
menu = Menu(root)
file_menu = Menu(menu, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_mar_file)
file_menu.add_command(label="Save", command=lambda: save_mar_file(False))
file_menu.add_command(label="Save As...", command=lambda: save_mar_file(True))
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu.add_cascade(label="File", menu=file_menu)

build_menu = Menu(menu, tearoff=0)
build_menu.add_command(label="Assemble", command=assemble_code)
build_menu.add_command(label="Save Binary Output", command=save_binary_output)
menu.add_cascade(label="Build", menu=build_menu)

view_menu = Menu(menu, tearoff=0)
view_menu.add_command(label="Toggle Dark/Light", command=toggle_theme)
menu.add_cascade(label="View", menu=view_menu)

root.config(menu=menu)

# Toolbar buttons
toolbar = tk.Frame(root, pady=5)
toolbar.pack()
tk.Button(toolbar, text="Build", command=assemble_code).pack(side=tk.LEFT, padx=4)
tk.Button(toolbar, text="Open", command=open_mar_file).pack(side=tk.LEFT, padx=4)
tk.Button(toolbar, text="Save", command=lambda: save_mar_file(False)).pack(side=tk.LEFT, padx=4)
tk.Button(toolbar, text="Save As", command=lambda: save_mar_file(True)).pack(side=tk.LEFT, padx=4)
tk.Button(toolbar, text="Save Binary", command=save_binary_output).pack(side=tk.LEFT, padx=4)
tk.Button(toolbar, text="Toggle Theme", command=toggle_theme).pack(side=tk.LEFT, padx=4)

# Assembly input
label_input = tk.Label(root, text="Assembly Code (write readB readA data16):")
label_input.pack()
input_textbox = scrolledtext.ScrolledText(root, height=12, width=100, undo=True)
input_textbox.pack(padx=10, pady=5)
input_textbox.bind("<KeyRelease>", highlight_syntax)

# Output
label_output = tk.Label(root, text="Binary Output (Grouped 16-bit):")
label_output.pack(pady=(10, 0))
output_textbox = scrolledtext.ScrolledText(root, height=12, width=100)
output_textbox.pack(padx=10, pady=5)

# Initial styling
apply_theme()
highlight_syntax()

root.mainloop()

import sys

# Load file passed via command-line (e.g., double-clicked)
if len(sys.argv) > 1:
    arg_file = sys.argv[1]
    if arg_file.endswith(".mar"):
        try:
            with open(arg_file, 'r') as f:
                code = f.read()
            input_textbox.delete("1.0", tk.END)
            input_textbox.insert(tk.END, code)
            highlight_syntax()
            current_file_path = arg_file
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {arg_file}\n\n{e}")
