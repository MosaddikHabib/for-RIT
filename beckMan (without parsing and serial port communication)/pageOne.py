import customtkinter as ctk
import json
import os

class PageOne(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        button_font_style = ctk.CTkFont(family="Arial", size=16, weight="bold")
        label_font_style = ctk.CTkFont(family="Arial", size=24, weight="bold")

        # Create the label with text color
        label = ctk.CTkLabel(self, text="PARAMETERS", font=label_font_style, text_color="#fcf349")
        label.pack(side="top", fill="x", pady=175)

        # Create a new frame inside PageOne
        config_entry_frame = ctk.CTkFrame(self)
        config_entry_frame.place(relx=0.5, rely=0.5, anchor="center")

        # com-port label and entry box
        entry_box_style = ctk.CTkFont(family="Inter", size=20)
        com_port_label = ctk.CTkLabel(config_entry_frame, text="COM port :", font=("Arial", 18))
        com_port_label.grid(row=0, column=0, padx=(25, 0), pady=(25, 5), sticky="e")
        self.com_port_entry = ctk.CTkEntry(config_entry_frame, width=200, font=entry_box_style)
        self.com_port_entry.grid(row=0, column=1, padx=(5, 25), pady=(25, 5))

        # Baud rate combo-box
        baud_rate_label = ctk.CTkLabel(config_entry_frame, text="Baud Rate :", font=("Arial", 18))
        baud_rate_label.grid(row=1, column=0, padx=(25, 0), pady=(0, 5), sticky="e")
        self.baud_rate_combo = ctk.CTkComboBox(config_entry_frame, values=["4800", "9600", "19200", "38400", "57600", "115200"], font=entry_box_style, width=200, state="readonly")
        self.baud_rate_combo.grid(row=1, column=1, padx=(5, 25), pady=(5, 5))

        # data bits combo-box
        data_bit_label = ctk.CTkLabel(config_entry_frame, text="Data Bits :", font=("Arial", 18))
        data_bit_label.grid(row=2, column=0, padx=(25, 0), pady=(0, 5), sticky="e")
        self.data_bit_combo = ctk.CTkComboBox(config_entry_frame, values=["8", "7"], font=entry_box_style, width=200, state="readonly")
        self.data_bit_combo.grid(row=2, column=1, padx=(5, 25), pady=(5, 5))

        # stop bit combo-box
        stop_bit_label = ctk.CTkLabel(config_entry_frame, text="Stop bits :", font=("Arial", 18))
        stop_bit_label.grid(row=3, column=0, padx=(25, 0), pady=(0, 5), sticky="e")
        self.stop_bits_combo = ctk.CTkComboBox(config_entry_frame, values=["1", "2"], font=entry_box_style, width=200, state="readonly")
        self.stop_bits_combo.grid(row=3, column=1, padx=(5, 25), pady=(5, 5))


        # Parity combo box
        parity_label = ctk.CTkLabel (config_entry_frame, text="Parity :", font=("Arial", 18))
        parity_label.grid (row=4, column=0, padx=(25, 0), pady=(0, 5), sticky="e")
        self.parity_combo = ctk.CTkComboBox (config_entry_frame, values=["None", "Odd", "Even"], font=entry_box_style, width=200, state="readonly")
        self.parity_combo.grid (row=4, column=1, padx=(5, 25), pady=(5, 5))

        # API Link insertion
        api_link_label = ctk.CTkLabel(config_entry_frame, text="Server :", font=("Arial", 18))
        api_link_label.grid(row=5, column=0, padx=(25, 0), pady=(5, 40), sticky="e")
        self.api_entry = ctk.CTkEntry(config_entry_frame, width=200, font=entry_box_style)
        self.api_entry.grid(row=5, column=1, padx=(5, 25), pady=(5, 40))

        # Save button
        def save_params():
            com_port = self.com_port_entry.get()
            baud_rate = self.baud_rate_combo.get()
            data_bit = self.data_bit_combo.get()
            stop_bit = self.stop_bits_combo.get()
            api_link = self.api_entry.get()
            parity = self.parity_combo.get()

            error_message = ""
            if not com_port:
                error_message += "COM port is required.\n"
            if not baud_rate:
                error_message += "Baud Rate is required.\n"
            if not data_bit:
                error_message += "Data Bits are required.\n"
            if not stop_bit:
                error_message += "Stop Bits are required.\n"
            if not api_link:
                error_message += "API link is required.\n"
            if not parity:
                error_message += "Parity is required.\n"

            if not error_message:
                params = {
                    "com_port": com_port,
                    "baud_rate": baud_rate,
                    "data_bits": data_bit,
                    "stop_bits": stop_bit,
                    "api_link": api_link,
                    "parity": parity
                }
                with open('params.json', 'w') as json_file:
                    json.dump(params, json_file)
                self.controller.show_frame("PageTwo")
            else:
                if not hasattr(self, 'error_label'):
                    self.error_label = ctk.CTkLabel(config_entry_frame, text=error_message.strip(), font=("Inter", 15), text_color="yellow")
                    self.error_label.grid(row=6, column=0, columnspan=2, pady=(5, 25))
                else:
                    self.error_label.config(text=error_message.strip())

        # Clear error message when editing
        def clear_error_message(event):
            if hasattr(self, 'error_label'):
                self.error_label.grid_forget()
                delattr(self, 'error_label')

        self.com_port_entry.bind("<Key>", clear_error_message)
        self.baud_rate_combo.bind("<Key>", clear_error_message)
        self.data_bit_combo.bind("<Key>", clear_error_message)
        self.stop_bits_combo.bind("<Key>", clear_error_message)
        self.parity_combo.bind("<Key>", clear_error_message)
        self.baud_rate_combo.bind("<<ComboboxSelected>>", clear_error_message)
        self.data_bit_combo.bind("<<ComboboxSelected>>", clear_error_message)
        self.stop_bits_combo.bind("<<ComboboxSelected>>", clear_error_message)
        self.api_entry.bind("<Key>", clear_error_message)
        self.parity_combo.bind("<<ComboboxSelected>>", clear_error_message)

        save_button = ctk.CTkButton(
            config_entry_frame,
            text="Save",
            command=save_params,
            font=button_font_style
            # fg_color="red",  # Set the background color of the button
            # text_color="white",  # Set the text color of the button
            # hover_color="darkgreen"
        )
        save_button.grid(row=6, column=0, columnspan=2, pady=(0, 20), padx=25)

        # Bind Enter key to save_params for all relevant widgets
        self.com_port_entry.bind("<Return>", lambda event: save_params())
        self.baud_rate_combo.bind("<Return>", lambda event: save_params())
        self.data_bit_combo.bind("<Return>", lambda event: save_params())
        self.stop_bits_combo.bind("<Return>", lambda event: save_params())
        self.api_entry.bind("<Return>", lambda event: save_params())
        self.parity_combo.bind("<Return>", lambda event: save_params())

        # Add navigation buttons
        # ctk.CTkButton(self, text="Log In Page", command=lambda: self.controller.show_frame("LoginPage")).pack(pady=10)

        # Load settings from JSON file
        self.load_params()

    def load_params(self):
        if os.path.exists('params.json'):
            with open('params.json', 'r') as json_file:
                params = json.load(json_file)
                self.com_port_entry.insert(0, params.get('com_port', ''))
                self.baud_rate_combo.set(params.get('baud_rate', ''))
                self.data_bit_combo.set(params.get('data_bits', ''))
                self.stop_bits_combo.set(params.get('stop_bits', ''))
                self.api_entry.insert(0, params.get('api_link', ''))
                self.parity_combo.set(params.get('parity', ''))
