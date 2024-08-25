# this page is reserved for the communication and parsing data from serial communication

import customtkinter as ctk

class PageThree(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ctk.CTkLabel(self, text="Page Two", font=("Arial", 24))
        label.pack(side="top", fill="x", pady=20)

        # Add widgets and functionality specific to PageTwo here

        ctk.CTkButton(self, text="Go to Page One", command=lambda: self.controller.show_frame("PageOne")).pack(pady=10)
        ctk.CTkButton(self, text="Log In Page", command=lambda: self.controller.show_frame("LoginPage")).pack(pady=10)
        # ctk.CTkButton(self, text="Logout", command=lambda: self.controller.show_frame("LoginPage")).pack(pady=10)