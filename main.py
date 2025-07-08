import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Menu
import re
import sys

# Opcodes
opcodes = ["NOP", "ADD", "SUB", "AND", "OR", "NOT", "INC", "DCR", "SHL", "SHR", "PH0","PH1","PH2","PH3","PH4","PH5","CLR", "LDA", "HLT", "STR", "MOV"]

current_file_path = None
is_dark_theme = True
toolbar_buttons = []

# Store references to output fields
binary_outputs = []

# Helper functions
def to_bin(val_str, bits):
    try:
        return bin(int(val_str))[2:].zfill(bits)
    except ValueError:
        return None

def assemble_code():
    # Clear output fields
    for box in binary_outputs:
        box.delete("1.0", tk.END)

    # Initialize field contents
    field_contents = [[], [], []]

    input_text = input_textbox.get("1.0", tk.END).strip().splitlines()
    for line_no, line in enumerate(input_text, start=1):
        line = line.split(";")[0].strip().upper()
        if not line:
            continue

        parts = line.split()
        if not parts:
            continue

        instr = parts[0]
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

        field1 = write_sel_bin + opcode_bin
        field2 = read_sel_B_bin + read_sel_A_bin
        field3 = data_bin

        field_contents[0].append(field1)
        field_contents[1].append(field2)
        field_contents[2].append(field3)

    for i in range(3):
        binary_outputs[i].insert(tk.END, "\n".join(field_contents[i]))

def copy_column(col_index):
    text = binary_outputs[col_index].get("1.0", tk.END).strip()
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()

def save_mar_file(as_new=False):
    global current_file_path
    if as_new or not current_file_path:
        file_path = filedialog.asksaveasfilename(defaultextension=".mar", filetypes=[("MAR Assembly Files", "*.mar")])
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
    file_path = filedialog.askopenfilename(filetypes=[("MAR Assembly Files", "*.mar")])
    if not file_path:
        return
    try:
        with open(file_path, 'r') as f:
            code = f.read()
        input_textbox.delete("1.0", tk.END)
        input_textbox.insert(tk.END, code)
        highlight_syntax()
        current_file_path = file_path
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file:\n{e}")

def save_binary_output():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if not file_path:
        return
    try:
        with open(file_path, 'w') as f:
            lines = zip(*(box.get("1.0", tk.END).strip().splitlines() for box in binary_outputs))
            for line in lines:
                f.write("\t".join(line) + "\n")
        messagebox.showinfo("Success", f"Binary saved to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save binary:\n{e}")

def new_file():
    global current_file_path
    current_file_path = None
    input_textbox.delete("1.0", tk.END)
    for box in binary_outputs:
        box.delete("1.0", tk.END)

def highlight_syntax(event=None):
    input_textbox.tag_remove("opcode", "1.0", tk.END)
    input_textbox.tag_remove("comment", "1.0", tk.END)
    input_textbox.tag_remove("number", "1.0", tk.END)

    lines = input_textbox.get("1.0", tk.END).splitlines()
    for i, line in enumerate(lines):
        idx = f"{i+1}.0"
        line = line.upper()

        for op in opcodes:
            start = line.find(op)
            if start != -1:
                input_textbox.tag_add("opcode", f"{i+1}.{start}", f"{i+1}.{start+len(op)}")

        if ";" in line:
            start = line.find(";")
            input_textbox.tag_add("comment", f"{i+1}.{start}", f"{i+1}.end")

        for match in re.finditer(r"\b\d+\b", line):
            input_textbox.tag_add("number", f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")

def toggle_theme():
    global is_dark_theme
    is_dark_theme = not is_dark_theme
    apply_theme()

def apply_theme():
    global output_fg, entry_bg, header_bg, btn_bg, btn_fg
    bg = "#1e1e1e" if is_dark_theme else "white"
    fg = "#d4d4d4" if is_dark_theme else "black"
    code_bg = "#2d2d2d" if is_dark_theme else "white"
    code_fg = "#dcdcdc" if is_dark_theme else "black"
    btn_bg = "#444444" if is_dark_theme else "#f0f0f0"
    btn_fg = "#ffffff" if is_dark_theme else "#000000"
    entry_bg = "#2b2b2b" if is_dark_theme else "#ffffff"
    header_bg = bg
    output_fg = code_fg

    root.configure(bg=bg)
    input_textbox.configure(bg=code_bg, fg=code_fg, insertbackground=fg)
    for widget in [label_input, label_output]:
        widget.configure(bg=bg, fg=fg)

    for btn in toolbar_buttons:
        btn.configure(bg=btn_bg, fg=btn_fg, activebackground=btn_bg, activeforeground=btn_fg)

    input_textbox.tag_config("opcode", foreground="#4FC1FF")
    input_textbox.tag_config("comment", foreground="#6A9955")
    input_textbox.tag_config("number", foreground="#FFD700")

    for box in binary_outputs:
        box.configure(bg=entry_bg, fg=output_fg, insertbackground=output_fg)

# GUI setup
root = tk.Tk()
root.title("MAR Assembler")
root.geometry("1000x700")

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

# Toolbar
toolbar = tk.Frame(root, pady=5)
toolbar.pack()
def add_toolbar_button(text, command):
    btn = tk.Button(toolbar, text=text, command=command)
    btn.pack(side=tk.LEFT, padx=4)
    toolbar_buttons.append(btn)

add_toolbar_button("Build", assemble_code)
add_toolbar_button("Open", open_mar_file)
add_toolbar_button("Save", lambda: save_mar_file(False))
add_toolbar_button("Save As", lambda: save_mar_file(True))
add_toolbar_button("Save Binary", save_binary_output)
add_toolbar_button("Toggle Theme", toggle_theme)

# Input
label_input = tk.Label(root, text="Assembly Code:")
label_input.pack()
input_textbox = scrolledtext.ScrolledText(root, height=10, font=("Consolas", 11), undo=True)
input_textbox.pack(padx=10, pady=5, fill='x')
input_textbox.bind("<KeyRelease>", highlight_syntax)

# Output
label_output = tk.Label(root, text="Binary Output Fields:")
label_output.pack()

paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
paned.pack(fill="both", expand=True, padx=10, pady=5)

headers = ["Write+Opcode", "ReadB+ReadA", "Data (16-bit)"]
output_frames = []

for i in range(3):
    frame = tk.Frame(paned)
    header = tk.Label(frame, text=headers[i], font=("Consolas", 11, "bold"))
    header.pack(anchor="w")

    output_box = scrolledtext.ScrolledText(frame, height=20, font=("Consolas", 11), wrap=tk.NONE)
    output_box.pack(fill="both", expand=True)
    binary_outputs.append(output_box)

    copy_btn = tk.Button(frame, text="Copy", command=lambda c=i: copy_column(c))
    copy_btn.pack(pady=5)
    toolbar_buttons.append(copy_btn)

    paned.add(frame)

# Apply theme
apply_theme()

# If opened via file
if len(sys.argv) > 1:
    try:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
        input_textbox.insert(tk.END, content)
        highlight_syntax()
        current_file_path = sys.argv[1]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open file:\n{e}")

root.mainloop()