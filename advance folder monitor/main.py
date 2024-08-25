# 9th June of 2024 - Md Mosaddik Habib
import sys
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import os
import pandas as pd
import json
import psutil
import requests
import ttkbootstrap as tb
from ttkbootstrap import Style, Button
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser
import subprocess

# from APIInput01 import resource_path, set_placeholder

CONFIG_FILE = "config.ini"


def save_config(url, remember):
    config = configparser.ConfigParser()
    config['SERVER'] = {'URL': url, 'Remember': str(remember)}
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None, False
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    url = config['SERVER'].get('URL', '')
    remember = config['SERVER'].getboolean('Remember', True)
    return url, remember


def login():
    username = user_entry.get()
    password = pass_entry.get()
    if (username == "rmch" and password == "rmch") or (username == "rajITadmin" and password == "rajIT"):
        login_frame.forget()
        show_message_and_select_folder()
    else:
        error_label.config(text="Invalid login CREDENTIALS, Please provide the correct one.")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class FolderMonitorApp:
    def __init__(self, root, initial_folder):
        self.root = root
        self.folder_to_watch = initial_folder

        # Load URL and remember setting from config
        self.server_url, self.remember = load_config()

        self.check_interval = 5000  # Check for new files every 5000 milliseconds (5 seconds)

        self.style = Style(theme="solar")
        self.style.configure('.', font=('Helvetica', 12))

        # Define the subset of columns to display
        self.display_columns = ["TR_SampleID", "TR_Value", "TR_Unit", "TR_ResultDT", "TR_TestNo"]

        # Create the treeview inside a frame for margin
        treeview_frame = ttk.Frame(self.root, padding=20)
        treeview_frame.pack(fill=tk.BOTH, expand=True)

        self.treeview = ttk.Treeview(treeview_frame, columns=self.display_columns, show='headings')
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Set column headings and align them to the left
        for col in self.display_columns:
            self.treeview.heading(col, text=col, anchor='n')
            self.treeview.column(col, anchor='n')

        # Create a toolbar frame
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=20, pady=10)

        # Create the settings button
        settings_button = tb.Button(toolbar_frame,
                                     text="⚙",
                                     command=self.prompt_server_url,
                                     bootstyle="warning outline")
        settings_button.pack(side=tk.RIGHT)

        # Create the exit button
        exit_button = tb.Button(self.root, text="Exit", command=self.on_closing, width=20, style="warning outline")
        exit_button.pack(pady=10)

        # Initialize file observer
        self.file_observer = Observer()
        self.file_observer.schedule(FileHandler(self), initial_folder, recursive=False)
        self.file_observer.start()

        # Make sure to stop the observer when the app is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start the periodic check for new files using after method
        self.check_files_loop()

    def prompt_server_url(self):
        new_url = simpledialog.askstring("Server URL", "Enter the new server URL:", initialvalue=self.server_url)
        if new_url:
            self.server_url = new_url
            save_config(self.server_url, self.remember)
            print(f"Server URL updated to: {self.server_url}")

    def check_files_loop(self):
        self.update_folder_contents()
        self.root.after(self.check_interval, self.check_files_loop)

    def update_folder_contents(self):
        files = [f for f in os.listdir (self.folder_to_watch) if f.endswith ('.xlsx') and not f.startswith ('~$')]
        if files:
            file = files[0]  # Assuming only one file is being monitored at a time
            file_path = os.path.join (self.folder_to_watch, file)
            if self.is_excel_open (file_path):
                self.close_excel (file_path)
            self.display_xlsx_file (file)
        else:
            self.clear_treeview ()

    def is_excel_open(self, file_path):
        # Check if the Excel file is open by checking the processes
        for proc in psutil.process_iter():
            try:
                if "EXCEL.EXE" in proc.name():
                    for item in proc.open_files():
                        if file_path in item.path:
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def close_excel(self, file_path):
        # Close the Excel file by terminating the process
        for proc in psutil.process_iter():
            try:
                if "EXCEL.EXE" in proc.name():
                    for item in proc.open_files():
                        if file_path in item.path:
                            proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def display_xlsx_file(self, file):
        file_path = os.path.join (self.folder_to_watch, file)
        try:
            # Close Excel if it's open
            subprocess.run (["taskkill", "/f", "/im", "excel.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Read data from the Excel file
            df = pd.read_excel (file_path)

            # Add data to treeview
            self.add_data_to_treeview (df)

            # Save data to JSON and send to database
            self.save_to_json_and_send_to_database (df)

            # Delete the .xlsx file after processing
            os.remove (file_path)
        except Exception as e:
            print (f"Error reading file '{file}': {str (e)}")  # Log the error instead of showing a pop-up

    def add_data_to_treeview(self, df):
        self.clear_treeview()
        for _, row in df[self.display_columns].iterrows():
            self.treeview.insert("", "end", values=row.tolist())

    def clear_treeview(self):
        for item in self.treeview.get_children ():
            self.treeview.delete (item)

    def save_to_json_and_send_to_database(self, df):
        file_path = os.path.join (self.folder_to_watch, "selected_data.json")
        data = df[self.display_columns].to_dict (orient="records")

        with open (file_path, 'w') as json_file:
            json.dump (data, json_file)

        self.send_to_database (file_path)

    def send_to_database(self, file_path):
        url = self.server_url
        with open (file_path, 'r') as json_file:
            data = json.load(json_file)
            payload = {
                'data': data,
            }
        response = requests.post (url, json=payload)

        if response.status_code == 200:
            print(response.json())
            os.remove(file_path)  # Delete the JSON file after successful sending
        else:
            print (f"Failed to send data to database: {response.text}")  # Log the error instead of showing a pop-up

    def on_closing(self):
        if self.file_observer.is_alive ():
            self.file_observer.stop ()
            self.file_observer.join ()
        self.root.destroy ()


class FileHandler(FileSystemEventHandler):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def on_created(self, event):
        if event.is_directory:
            return
        self.app.update_folder_contents()

    def on_deleted(self, event):
        if event.is_directory:
            return
        self.app.update_folder_contents()

    def on_modified(self, event):
        if event.is_directory:
            return
        self.app.update_folder_contents()

    def on_moved(self, event):
        if event.is_directory:
            return
        self.app.update_folder_contents()


def start_monitoring(selected_folder):
    initial_folder = selected_folder
    app = FolderMonitorApp(root, initial_folder)


def show_message_and_select_folder():
    # Clear the root window and show the message
    for widget in root.winfo_children():
        widget.destroy()

    message_label = tk.Label(root, text="Select your target folder to monitor", font=("Helvetica", 16))
    message_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    browse_button = tb.Button(root, text="Browse Folder",
                              bootstyle="warning outline", command=select_folder)
    browse_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


def select_folder():
    selected_folder = filedialog.askdirectory()
    if selected_folder:
        start_monitoring(selected_folder)
    else:
        print("No folder selected.")


def set_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg='white')

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg='white')

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    entry.bind('<FocusIn>', on_focus_in)
    entry.bind('<FocusOut>', on_focus_out)


# Initialize the main window
root = tb.Window(themename='superhero')
root.title("Advance Folder Monitor")
root.geometry("1200x600")

# Set the theme
style = Style(theme="superhero")

# Create the logo
logo_image_path = resource_path("resources/l01.png")
logo_image = tk.PhotoImage(file=logo_image_path)
logo_label = tk.Label(root, image=logo_image, bg=style.colors.primary)
logo_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# Create the login frame
login_frame = tk.Frame(root, bg=style.colors.primary)
login_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)  # Center the frame

# Font settings
# font_settings = ("Helvetica", 16)

# Username entry with placeholder
user_entry = tk.Entry(login_frame, highlightbackground="yellow",
                      font=("Helvetica", 16),
                      background='white', foreground='black',
                       insertbackground='white', width=20
                      )

# user_entry = tb.Entry(login_frame,
#                       font=("Helvetica",16),
#                       fg="white",
#                       width=20)

set_placeholder(user_entry, "Username")
user_entry.pack(pady=(0, 10))
# user_entry.pack(pady=10)

# Password entry with placeholder
pass_entry = tk.Entry(login_frame, show="*", highlightbackground="yellow", font=("Helvetica", 16), fg='white',
                       bg='black', insertbackground='white')
set_placeholder(pass_entry, "Password")
pass_entry.pack(pady=(0, 10))
root.bind("<Return>", lambda event: login())

# Login button
login_button = tb.Button(login_frame, bootstyle="warning, outline", text="Log in",
                         width=37,
                         command=login)
login_button.pack(pady=20)


# Error label (initially empty)
error_label = tk.Label(login_frame, text="", fg="red", bg=style.colors.primary, font=("Helvetica", 12))
error_label.pack(pady=(10, 0))

# root.bind("<Return>", login)
# Run the main loop
root.mainloop()