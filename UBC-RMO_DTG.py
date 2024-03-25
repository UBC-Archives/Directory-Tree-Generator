#Directory Tree Generator
#Version: 1.0
#https://recordsmanagement.ubc.ca
#https://www.gnu.org/licenses/gpl-3.0.en.html

import os
import time
from datetime import datetime
import csv
import tkinter as tk
from tkinter import filedialog
import threading
import subprocess

rows_written = 0

def list_folders_with_lines_to_file(startpath, max_level):
    global rows_written
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = f'Directory-Tree_{timestamp}.txt'
    output_file = os.path.join(os.getcwd(), filename)

    def list_folders_recursive(folder, current_level, max_level, prefix="", file_handle=None):
        global rows_written
        if current_level > max_level:
            return
    
        with os.scandir(folder) as it:
            try:
                dirs = [entry.name for entry in it if entry.is_dir()]
                for i, directory in enumerate(dirs):
                    connector = "├───" if i < len(dirs) - 1 else "└───"
                    file_handle.write(f"{prefix}{connector}{directory}\n")
                    rows_written += 1
                    if progress_var:
                        progress_var.set(str(rows_written))
                    new_prefix = prefix + ("│   " if i < len(dirs) - 1 else "    ")
                    list_folders_recursive(os.path.join(folder, directory), current_level + 1, max_level, new_prefix, file_handle)
            except PermissionError as pe:
                log_error(f"PermissionError: {pe}")
            except Exception as e:
                log_error(f"Unexpected error for {e}")

    with open(output_file, 'w', encoding='utf-8') as file_handle:
        file_handle.write(startpath + "\n")
        list_folders_recursive(startpath, 0, max_level, file_handle=file_handle)
    
    return output_file

def log_error(error_message):
    global timestamp
    with open(f'Error-Log_{timestamp}.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{error_message}\n")

def show_completion_message(execution_time_str, output_file, error_log_path):
    completion_window = tk.Toplevel(root)
    completion_window.title("Directory tree generated!")

    message = f"Execution completed in {execution_time_str}.\n\nOutput file saved as {output_file}"

    completion_label = tk.Label(completion_window, text=message)
    completion_label.pack(padx=20, pady=5)

    open_button = tk.Button(completion_window, text="Open Output File", command=lambda: open_output_file(output_file))
    open_button.pack(pady=5)

    if os.path.exists(error_log_path):
        error_log_label = tk.Label(completion_window, text=f"Error log saved as {error_log_path}")
        error_log_label.pack(pady=5)

        open_log_button = tk.Button(completion_window, text="Open Error Log", command=lambda: open_output_file(error_log_path))
        open_log_button.pack(pady=5)

def open_output_file(output_file):
    try:
        subprocess.run(['start', '', output_file], shell=True)
    except Exception as e:
        tk.messagebox.showerror("Error", f"Error opening file: {str(e)}")

def list_files_in_thread():
    global thread
    global progress_var
    global timestamp
    global rows_written
    rows_written = 0

    path_to_list = input_path_entry.get()
    if not os.path.exists(path_to_list):
        output_label.config(fg="red")
        output_text.set("Invalid path!")
        return

    output_text.set("")

    max_level_str = directory_level_entry.get()
    if max_level_str:
        try:
            max_level = int(max_level_str)
        except ValueError:
            output_label.config(fg="red")
            output_text.set("Invalid directory level!")
            return
    else:
        max_level = float('inf')

    start_time = time.time()

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

    output_file = list_folders_with_lines_to_file(path_to_list, max_level)
    error_log_path = os.path.join(os.getcwd(), f'Error-Log_{timestamp}.txt')

    end_time = time.time()
    execution_time = end_time - start_time
    execution_time_str = time.strftime("%H:%M:%S", time.gmtime(execution_time))

    show_completion_message(execution_time_str, output_file, error_log_path)


thread = threading.Thread(target=list_files_in_thread, daemon=True)

def execute_button_callback():
    global thread

    if thread.is_alive():
        output_text.set("A process is already running.")
    else:
        input_path_entry.config(state=tk.DISABLED)
        execute_button.config(state=tk.DISABLED)
        browse_button.config(state=tk.DISABLED)
        directory_level_entry.config(state=tk.DISABLED)

        thread = threading.Thread(target=list_files_in_thread, daemon=True)
        thread.start()

        root.after(100, check_thread_status)

def check_thread_status():
    if thread.is_alive():
        root.after(100, check_thread_status)
    else:
        input_path_entry.config(state=tk.NORMAL)
        execute_button.config(state=tk.NORMAL)
        browse_button.config(state=tk.NORMAL)
        directory_level_entry.config(state=tk.NORMAL)

def browse_button_callback():
    selected_path = filedialog.askdirectory()
    if selected_path:
        input_path_entry.delete(0, tk.END)
        input_path_entry.insert(0, selected_path)
        output_label.config(fg="black")
        output_text.set("")
    directory_level_entry.delete(0, tk.END)
    output_text.set("")
    progress_var.set("0")

# File menu functions
def exit_app():
    if threading.active_count() > 1:
        confirm = tk.messagebox.askyesno("Exit?", "A process is running. Are you sure you want to exit?")
        if not confirm:
            return
    root.destroy()

def clear_fields():
    # Enable the Path entry
    input_path_entry.config(state=tk.NORMAL)

    # Enable the Max Directory Depth entry
    directory_level_entry.config(state=tk.NORMAL)

    # Clear the fields
    input_path_entry.delete(0, tk.END)
    directory_level_entry.delete(0, tk.END)
    output_text.set("")
    progress_var.set("0")

def show_help():
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    help_window.resizable(False, False)

    help_message = "This program generates directory tree structures.\n\n" \
                   "Use 'Browse' to select the path, set the maximum directory depth, and click Generate Directory Tree.\n\n" \
                   "The output is saved in a txt file."

    help_label = tk.Label(help_window, text=help_message, justify=tk.LEFT)
    help_label.pack(padx=20, pady=10)


def show_about():
    about_message = "Directory Tree Generator\nVersion 1.0"
   
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.resizable(False, False)

    about_label = tk.Label(about_window, text=about_message)
    about_label.pack(padx=20, pady=10)

    # Frame for UBC RMO
    ubc_frame = tk.Frame(about_window)
    ubc_frame.pack(padx=20, pady=20)

    ubc_label = tk.Label(ubc_frame, text="Developed by\nRecords Management Office\nThe University of British Columbia")
    ubc_label.pack()

    ubc_link_label = tk.Label(ubc_frame, text="https://recordsmanagement.ubc.ca", fg="blue", cursor="hand2")
    ubc_link_label.pack()

    def open_ubc_link(event):
        import webbrowser
        webbrowser.open("https://recordsmanagement.ubc.ca")

    ubc_link_label.bind("<Button-1>", open_ubc_link)

    # Frame for license
    license_frame = tk.Frame(about_window)
    license_frame.pack(padx=20, pady=10)

    license_label = tk.Label(license_frame, text="License: ")
    license_label.pack(side='left')

    license_link_label = tk.Label(license_frame, text="GPL-3.0", fg="blue", cursor="hand2")
    license_link_label.pack(side='left')

    def open_license_link(event):
        import webbrowser
        webbrowser.open("https://www.gnu.org/licenses/gpl-3.0.en.html")

    license_link_label.bind("<Button-1>", open_license_link)

# Main window
root = tk.Tk()
root.title("Directory Tree Generator")
root.geometry("600x150")
root.resizable(False, False)

# Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

# File menu options
file_menu.add_command(label="Clear Fields", command=clear_fields)
file_menu.add_command(label="Exit", command=exit_app)

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)

# Help menu options
help_menu.add_command(label="Help", command=show_help)
help_menu.add_command(label="About", command=show_about)

# Main window padding
root.option_add('*TButton*Padding', 5)
root.option_add('*TButton*highlightThickness', 0)
root.option_add('*TButton*highlightColor', 'SystemButtonFace')

# Frame to hold the path input field and the "Browse" button
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Input field for the path
input_label = tk.Label(frame, text="Directory Path:")
input_label.pack(side='left')

input_path_entry = tk.Entry(frame, width=60)
input_path_entry.pack(side='left', padx=10)

# "Browse" button
browse_button = tk.Button(frame, text="Browse", command=browse_button_callback)
browse_button.pack(side='left', padx=10)

# Frame to hold the directory level input field
frameD = tk.Frame(root)
frameD.pack(padx=10, pady=10)

# Label for the directory level input field
directory_level_label = tk.Label(frameD, text="Max Directory Depth:")
directory_level_label.pack(side='left')

# Entry field for the directory level
directory_level_entry = tk.Entry(frameD, width=5)
directory_level_entry.pack(side='left', padx=10)

# Hint label for directory level field
hint_label_text = " (Root = 0; Leave empty for deepest level)"
hint_label = tk.Label(frameD, text=hint_label_text, font=("Arial", 8), fg="gray")
hint_label.pack(side='left')

# Frame to hold the "Execute" button
frameE = tk.Frame(root)
frameE.pack(padx=10, pady=10)

# "Execute" button
execute_button = tk.Button(frameE, text="Generate Directory Tree", command=execute_button_callback)
execute_button.pack(side='left', padx=10)

# Output label to display invalid path messages
output_text = tk.StringVar()
output_label = tk.Label(frameE, textvariable=output_text)
output_label.pack(side='left', padx=10)

# Progress label
progress_label = tk.Label(frameE, text="Processed folders:")
progress_label.pack(side='left', padx=10)

# Shared variable to store the number of rows written
progress_var = tk.StringVar()
progress_var.set("0")

# Label to display the number of rows written
rows_written_label = tk.Label(frameE, textvariable=progress_var)
rows_written_label.pack(side='left')

root.protocol("WM_DELETE_WINDOW", exit_app)

if __name__ == "__main__":
    root.mainloop()