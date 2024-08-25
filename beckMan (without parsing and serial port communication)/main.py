import customtkinter as ctk
from PIL import Image as PILImage, ImageTk
from tkinter import Tk, Label
import json
import os

# Import other pages
from pageOne import PageOne
from pageTwo import PageTwo
from pageThree import PageThree
# from pageFour

class MultiPageApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Custom Tkinter Multi-Page Application")
        self.geometry("800x600")

        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginPage, PageOne, PageTwo, PageThree):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        log_in_button_style = ctk.CTkFont(family="Arial", size=16, weight="bold")

        # Load the original image and resize it
        self.logo_image_path = "res/logo.png"
        original_logo = PILImage.open(self.logo_image_path).convert("RGBA")
        resized_logo = original_logo.resize((350, 75))

        # Create a background image with the desired color
        background_color = (51, 51, 51, 255)  # RGBA for #333333 with full opacity
        background_image = PILImage.new("RGBA", resized_logo.size, background_color)

        # Composite the logo image on top of the background using a mask to handle transparency
        combined_image = PILImage.alpha_composite(background_image, resized_logo)

        # Convert to PhotoImage for use in tkinter
        self.tk_logo_image = ImageTk.PhotoImage(combined_image)

        # Display the image using tkinter's Label widget
        self.logo_image_label = Label(self, image=self.tk_logo_image,
                                       bg="#333333")  # Set the background color to match
        self.logo_image_label.pack(pady=(140, 0), padx=(0, 30))

        # Container Frame
        self.container_frame = ctk.CTkFrame(self)
        self.container_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the container frame

        fontStyle = ctk.CTkFont(family='Inter', size=20, weight="bold")
        error_label_font = ctk.CTkFont(family='Inter', size=17)
        titleStyle = ctk.CTkFont(family="Inter", size=24, weight='bold')

        # Title Label
        self.title_label = ctk.CTkLabel(self.container_frame, text="Log in", font=titleStyle)
        self.title_label.pack(side="top", fill="x", pady=20, padx=10)

        # Username Entry
        self.username = ctk.StringVar()
        self.username_entry = ctk.CTkEntry(self.container_frame, textvariable=self.username, width=200, font=fontStyle)
        self.username_entry.pack(pady=5, padx=30)
        self.username_entry.insert(0, "Username")
        self.username_entry.bind("<FocusIn>", self.clear_placeholder)
        self.username_entry.bind("<FocusOut>", self.add_placeholder)
        self.username_entry.bind("<Return>", lambda event: self.login())  # Bind Enter key to login

        # Password Entry
        self.password = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(self.container_frame, textvariable=self.password, width=200, font=fontStyle, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "Password")
        self.password_entry.bind("<FocusIn>", self.clear_placeholder)
        self.password_entry.bind("<FocusOut>", self.add_placeholder)
        self.password_entry.bind("<Return>", lambda event: self.login())  # Bind Enter key to login

        # Login Button
        self.login_button = ctk.CTkButton(self.container_frame,
                                          text="Login",
                                          font=log_in_button_style,
                                          command=self.login,
                                          width=100)
        self.login_button.pack(pady=20)

        # Label for error message
        self.error_label = ctk.CTkLabel(self.container_frame, text="", text_color="#eb8d91", font=error_label_font)
        self.error_label.pack(pady=10, padx=15)

        # Center the LoginPage frame in the parent container
        self.grid(row=0, column=0, sticky="nsew")
        self.update_idletasks()  # Force update to recalculate the layout

        # Load credentials from JSON file
        self.credentials_file = "loginInfo.json"
        self.load_credentials()

    def load_credentials(self):
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "r") as file:
                self.credentials = json.load(file)
        else:
            self.credentials = {"username": "a", "password": "a"}  # Default credentials if file doesn't exist

    def clear_placeholder(self, event):
        widget = event.widget
        if widget.get() in ["Username", "Password"]:
            widget.delete(0, "end")
            if widget == self.password_entry:
                widget.configure(show="*")

    def add_placeholder(self, event):
        widget = event.widget
        if not widget.get():
            if widget == self.username_entry:
                widget.insert(0, "Username")
            elif widget == self.password_entry:
                widget.insert(0, "Password")
                widget.configure(show="")  # Handle show attribute for password

    def login(self):
        # Get the entered values
        entered_username = self.username.get()
        entered_password = self.password.get()

        # Debug print statements
        print(f"Entered Username: {entered_username}")
        print(f"Entered Password: {entered_password}")

        # Validate the credentials
        if (entered_username == self.credentials["username"] and
                entered_password == self.credentials["password"]):
            self.controller.show_frame("PageOne")
        else:
            # Update the error label with the error message
            self.error_label.configure(text="Incorrect username or password")
            # Force a redraw to ensure the label is updated immediately
            self.update_idletasks()

        # ctk.CTkButton (self, text="Go to Page three", command=lambda: self.controller.show_frame ("PageOne")).pack (pady=10)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"

    app = MultiPageApp()
    app.mainloop()
