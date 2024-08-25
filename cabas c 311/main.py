# Md. Mosaddik Habib >> From 25th June
import sqlite3
import tkinter as tk
from tkinter import ttk, Canvas, TOP, LEFT, CENTER, font, messagebox
from PIL import Image, ImageTk
import threading
import serial
import re
import requests
import json
import os



class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.geometry("1920x1080")
        self.title("hostMate | RajIT | made for RMCH")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#222D20')


        label = tk.Label(self, text="", font=("Helvetica", 16), bg='#222D20', fg='white')
        label.pack(side="top", fill="x", pady=65)

        image_path = "res/rajIT Solution Ltd EDITED.png"
        main_image = Image.open(image_path)
        resized_image = main_image.resize((300, 75))
        self.image = ImageTk.PhotoImage(resized_image)

        label_logo_image = tk.Label(self, image=self.image, bg='#222D20')
        label_logo_image.pack(side="top", pady=30)

        input_text_username = tk.StringVar()
        userName = tk.Entry(self, width=30, textvariable=input_text_username, font=("Inter", 12), justify=LEFT,
                             bg="white", fg="black")
        userName.pack(side=TOP, pady=10, ipady=5)
        userName.insert(0, "User name")

        input_text_password = tk.StringVar()
        userPass = tk.Entry(self, width=30, textvariable=input_text_password, show="*", font=("Inter", 12),
                             justify=LEFT, bg="#FFFFFF", fg="black")
        userPass.pack(side=TOP, pady=10, ipady=5)
        userPass.insert(0, "Password")

        def on_enter_username(event):
            if userName.get() == "User name":
                userName.delete(0, "end")
                userName.config(fg="black")

        def on_leave_username(event):
            if userName.get() == "":
                userName.insert(0, "User name")
                userName.config(fg="gray")

        def on_enter_password(event):
            if userPass.get() == "Password":
                userPass.delete(0, "end")
                userPass.config(fg="black", show="*")

        def on_leave_password(event):
            if userPass.get() == "":
                userPass.insert(0, "Password")
                userPass.config(fg="gray", show="")

        userName.bind("<FocusIn>", on_enter_username)
        userName.bind("<FocusOut>", on_leave_username)
        userName.config(fg="gray")

        userPass.bind("<FocusIn>", on_enter_password)
        userPass.bind("<FocusOut>", on_leave_password)
        userPass.config(fg="gray", show="")

        def login():
            username = input_text_username.get()
            password = input_text_password.get()
            if (username == "a" and password == "a") or (username == "rmch" and password == "RMCH"):
                controller.show_frame("PageOne")
            else:
                label_error.config(text="Insert the Correct Constrain")

        login_image_path = "res/figma-login-BTN.png"
        btn_image = Image.open(login_image_path)
        resized_image_btn = btn_image.resize((150,42))
        self.button_image = ImageTk.PhotoImage(resized_image_btn)

        btn_login = tk.Button(self, image=self.button_image, command=login, borderwidth=0, bg='#222D20', activebackground='#222D20')
        btn_login.image = btn_image  # Keep a reference to avoid garbage collection
        btn_login.pack(pady=10)

        label_error = tk.Label(self, text="", font=("Inter", 12), bg='#222D20', fg='white')
        label_error.pack(pady=10)

        # Temp button
        # button2 = tk.Button(self, text="Go to Page Two", command=lambda: controller.show_frame("PageTwo"), font=("Inter", 12, "bold"), bg='#AD9309', fg='white')
        # button2.pack(pady=5)


# to remember the API address + insert it automatically until replaced by new one.
# CONFIG_FILE = "config.json"


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#222D20')

        # UI setup
        self.setup_ui()

        # Serial port settings
        self.serial_port = self.controller.serial_params["com_port"]
        self.baud_rate = int(self.controller.serial_params["baud_rate"])
        self.setup_serial()

        # Start the data reading thread
        self.start_data_thread()

    def setup_ui(self):
        # UI Elements
        label_bold_font = font.Font(family="Inter", size=25, weight="bold")
        label = tk.Label(self, text="ASTM Data Viewer", font=label_bold_font, bg='#222D20', fg='#FFFFFF')
        label.pack(pady=(20, 10))

        self.frame = ttk.Frame(self)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.search_label = ttk.Label(self.frame, text="Search Sample ID:")
        self.search_label.pack(pady=5)

        self.search_entry = ttk.Entry(self.frame)
        self.search_entry.pack(pady=5)

        self.search_button = ttk.Button(self.frame, text="Search", command=self.search_data)
        self.search_button.pack(pady=5)

        self.load_button = ttk.Button(self.frame, text="Load All Data", command=self.load_data)
        self.load_button.pack(pady=10)

        self.tree = ttk.Treeview(self.frame, columns=("sample_id", "test_no", "result_with_unit"), show="headings")
        self.tree.heading("sample_id", text="Sample ID")
        self.tree.heading("test_no", text="Test No")
        self.tree.heading("result_with_unit", text="Result")

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Settings button
        settings_button = ttk.Button (self, text="Settings", command=lambda: self.controller.show_frame ("PageTwo"))
        settings_button.pack (side=tk.BOTTOM, padx=10, pady=10)

        # New Send to Server button
        send_button = ttk.Button (self.frame, text="Send to Server", command=self.run_script)
        send_button.pack (pady=10)

        # Exit button
        exit_button = ttk.Button(self, text="Exit", command=self.controller.quit())
        exit_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)
    def setup_serial(self):
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)

    def start_data_thread(self):
        self.data_thread = threading.Thread(target=self.read_serial_data)
        self.data_thread.daemon = True
        self.data_thread.start()

    def read_serial_data(self):
        current_data = None
        connection = self.connect_to_database()
        cursor = connection.cursor()

        while True:
            received_data = self.receive_data()
            if received_data:
                parsed_data = self.parse_astm(received_data)
                print(parsed_data)

                if parsed_data['sample_id']:
                    # Start new data
                    current_data = parsed_data
                elif current_data:
                    # Append results to the existing sample data
                    current_data['results'].extend(parsed_data['results'])

                # Check for the 'L' tag indicating the end of transmission
                if 'L|' in received_data:
                    if current_data:
                        self.store_data(cursor, current_data)
                        # I have to sent data to an API
                        # self.send_data_to_api (current_data)
                        current_data = None  # Reset current_data after storing

                self.send_ack()

        connection.close()

    def send_ack(self):
        self.ser.write(b'\x06')  # Sending ASCII ACK (0x06)

    def receive_data(self):
        data = self.ser.read_until(b'\x04').decode('latin-1').strip()  # Read until EOT (0x04)
        return data

    def parse_astm(self, data):
        # Extract the sample ID
        sample_id_match = re.search(r'O\|\d+\|\d+\^([\w\d]+)\s*\^', data)
        sample_id = sample_id_match.group(1) if sample_id_match else None

        # Extract test results
        test_results = re.findall(r'R\|\d+\|\^\^\^(\d+)/\|([\d\.]+)\|([\w/]+)', data)
        results = [{"test_no": res[0], "result_with_unit": f"{res[1]} {res[2]}"} for res in test_results]

        return {
            "sample_id": sample_id,
            "results": results
        }

    def store_data(self, cursor, parsed_data):
        sample_id = parsed_data['sample_id']
        json_data = json.dumps(parsed_data)

        try:
            insert_query = """
            INSERT INTO astm_data (sample_id, json_data)
            VALUES (?, ?)
            """
            record = (sample_id, json_data)
            cursor.execute(insert_query, record)
            cursor.connection.commit()
            print("Data successfully inserted")
        except sqlite3.Error as e:
            print(f"Error: {e}")

    def load_data(self):
        connection = self.connect_to_database()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM astm_data")
            records = cursor.fetchall()

            self.tree.delete(*self.tree.get_children())  # Clear existing data

            for record in records:
                sample_id = record[1]
                json_data = record[2]
                parsed_data = json.loads(json_data)
                for result in parsed_data['results']:
                    self.tree.insert("", tk.END, values=(sample_id, result['test_no'], result['result_with_unit']))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

        connection.close()

    def search_data(self):
        sample_id = self.search_entry.get().strip()
        if not sample_id:
            messagebox.showwarning("Input Error", "Please enter a Sample ID to search.")
            return

        connection = self.connect_to_database()
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM astm_data WHERE sample_id = ?", (sample_id,))
            records = cursor.fetchall()

            self.tree.delete(*self.tree.get_children())  # Clear existing data

            if records:
                for record in records:
                    json_data = record[2]
                    parsed_data = json.loads(json_data)
                    for result in parsed_data['results']:
                        self.tree.insert("", tk.END, values=(sample_id, result['test_no'], result['result_with_unit']))
            else:
                messagebox.showinfo("No Results", f"No data found for Sample ID: {sample_id}")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

        connection.close()

    def connect_to_database(self):
        try:
            connection = sqlite3.connect('habib07.db')
            cursor = connection.cursor()
            # Create the table if it doesn't exist
            cursor.execute ('''
                           CREATE TABLE IF NOT EXISTS astm_data (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               sample_id TEXT NOT NULL,
                               json_data TEXT NOT NULL,
                               sent_to_api INTEGER DEFAULT 0
                           )
                       ''')

            connection.commit ()
            print ("Connection and table creation successful")
            return connection

        except sqlite3.Error as e:
            print (f"Error: {e}")
            return None

    # send to API-----------------------
    def run_script(self):
        import subprocess
        subprocess.run (["python", "sent_to_API.py"])


    def __del__(self):
        if self.ser:
            self.ser.close()


# additional classes to save parameters====================================================================
def load_serial_params():
    try:
        with open("serial_params.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default parameters if file is not found or corrupted
        return {
            "com_port": "COM13",
            "baud_rate": "9600",
            "data_bits": "8",
            "parity": "NONE",
            "stop_bits": "1"
        }


def save_serial_params(params):
    with open("serial_params.json", "w") as f:
        json.dump(params, f)


# active start Page --------
class Controller(tk.Tk):
    def __init__(self):
        super().__init__()

        self.serial_params = load_serial_params()

        self.title("hostMate | RajIT | made for RMCH")
        self.geometry("1000x500")
        self.resizable(True, True)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def update_serial_params(self, params):
        self.serial_params.update(params)
        save_serial_params(self.serial_params)
# ==============================


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg='#222D20')

        label_bold_font = font.Font(family="Inter", size=25, weight="bold")
        label = tk.Label(self, text="Communication Parameter", font=label_bold_font, bg='#222D20', fg='#FFFFFF')
        label.pack(pady=(175, 20))

        style = ttk.Style()
        style.configure("Green.TFrame", background="#222D20")
        style.configure("PageTwoBack.TButton", font=("Inter", 12, "bold"), background='#0A717E', foreground='black')
        style.configure("PageTwoSave.TButton", font=("Inter", 12, "bold"), background='#FF5733', foreground='black')

        frame = ttk.Frame(self, width=300, height=100, padding="10", style="Green.TFrame")
        frame.pack_propagate(False)
        frame.pack(padx=10, pady=10)

        # COM - Port - Selection Sector_____________________________________________________
        com_port_button_image = "res/COM Port.png"
        self.comImg = self.load_image(com_port_button_image, (100, 30))
        image_label = tk.Label(frame, image=self.comImg, bg="#222D20")
        image_label.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.com_port_input = ttk.Entry(frame, width=35, font=('Inter', 16))
        self.com_port_input.grid(row=0, column=1, padx=(5, 0), pady=5)
        self.com_port_input.insert(0, controller.serial_params["com_port"])

        # Baudrate selection____________________________________________________________
        baud_rate_button_image = "res/Baud Rate.png"
        self.baudRateImg = self.load_image(baud_rate_button_image, (100, 30))
        image_label = tk.Label(frame, image=self.baudRateImg, bg="#222D20")
        image_label.grid(row=1, column=0, padx=(0, 5), pady=5, sticky="ew")

        baud_rate_options = ["1200", "2400", "4800", "9600", "19200", "38400", "57600"]
        self.baud_rate_combobox = ttk.Combobox(frame, values=baud_rate_options, font=('Inter', 16), state="readonly", width=34)
        self.baud_rate_combobox.grid(row=1, column=1, padx=(5, 0), pady=5)
        self.baud_rate_combobox.set(controller.serial_params["baud_rate"])

        self.option_add('*TCombobox*Listbox.font', ('Inter', 16))

        # Data Bits selection_________________________________________________________________
        dataBits_button_image = 'res/dataBits.png'
        self.dataBitsImg = self.load_image(dataBits_button_image, (100, 30))
        image_label = tk.Label(frame, image=self.dataBitsImg, bg="#222D20")
        image_label.grid(row=2, column=0, padx=(0, 5), pady=5, sticky="ew")

        dataBit_options = ["8", "7"]
        self.dataBit_combobox = ttk.Combobox(frame, values=dataBit_options, font=('Inter', 16), state="readonly", width=34)
        self.dataBit_combobox.grid(row=2, column=1, padx=(5, 0), pady=5)
        self.dataBit_combobox.set(controller.serial_params["data_bits"])

        # Parity Bits selection
        parityBit_image = 'res/ParityBits.png'
        self.parityBitImg = self.load_image(parityBit_image, (100, 30))
        image_label = tk.Label(frame, image=self.parityBitImg, bg="#222D20")
        image_label.grid(row=3, column=0, padx=(0, 5), pady=5, sticky="ew")

        parityBit_options = ["EVEN", "ODD", "NONE"]
        self.parityBit_combobox = ttk.Combobox(frame, values=parityBit_options, font=('Inter', 16), state="readonly", width=34)
        self.parityBit_combobox.grid(row=3, column=1, padx=(5, 0), pady=5)
        self.parityBit_combobox.set(controller.serial_params["parity"])

        # Stop Bits selection
        stopBit_image = 'res/stopBit.png'
        self.stopBitImg = self.load_image(stopBit_image, (100, 30))
        image_label = tk.Label(frame, image=self.stopBitImg, bg="#222D20")
        image_label.grid(row=4, column=0, padx=(0, 5), pady=5, sticky="ew")

        stopBit_options = ["1", "2"]
        self.stopBit_combobox = ttk.Combobox(frame, values=stopBit_options, font=('Inter', 16), state="readonly", width=34, background="lightblue", foreground="black")
        self.stopBit_combobox.grid(row=4, column=1, padx=(5, 0), pady=5)
        self.stopBit_combobox.set(controller.serial_params["stop_bits"])

        # API Link input
        api_link_button_image = "res/APILink.png"
        self.apiLinkImg = self.load_image(api_link_button_image, (100, 30))
        image_label = tk.Label(frame, image=self.apiLinkImg, bg="#222D20")
        image_label.grid(row=5, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.api_link_input = ttk.Entry(frame, width=35, font=('Inter', 16))
        self.api_link_input.grid(row=5, column=1, padx=(5, 0), pady=5)
        self.api_link_input.insert(0, controller.serial_params.get("api_link", ""))

        # Save and Back buttons----------------------------------------
        button_frame = ttk.Frame(self, style="Green.TFrame")
        button_frame.pack(pady=10)

        save_button = ttk.Button(button_frame, text="Save", command=self.save_params, style="PageTwoSave.TButton")
        save_button.pack(side=tk.LEFT, padx=5, pady=10)

        back_button = ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("PageOne"),
                                 style="PageTwoBack.TButton")
        back_button.pack(side=tk.LEFT, padx=5, pady=10)

    def load_image(self, path, size):
        try:
            img_open = Image.open(path)
            res_img = img_open.resize(size)
            return ImageTk.PhotoImage(res_img)
        except FileNotFoundError:
            print(f"File not found: {path}")
            return None

    def save_params(self):
        params = {
            "com_port": self.com_port_input.get(),
            "baud_rate": self.baud_rate_combobox.get(),
            "data_bits": self.dataBit_combobox.get(),
            "parity": self.parityBit_combobox.get(),
            "stop_bits": self.stopBit_combobox.get(),
            "api_link": self.api_link_input.get()  # Ensure API link is captured here
        }
        self.controller.update_serial_params(params)
        messagebox.showinfo("Info", "Communication parameters saved successfully.")


if __name__ == "__main__":
    app = Controller()
    app.mainloop()