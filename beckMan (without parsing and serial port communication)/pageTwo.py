import customtkinter as ctk
import sqlite3
import json
import subprocess
from tkinter import ttk

class PageTwo(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Load the test_no mapping from the JSON file
        with open ("test_no_mapping.json", "r") as f:
            self.test_no_mapping = json.load (f)

        label = ctk.CTkLabel(self, text="Easy Host Mate", font=("Arial", 24))
        label.pack(side="top", fill="x", pady=20)

        # Create a frame for the all data view
        self.all_data_table_frame = ctk.CTkFrame(self)
        self.all_data_table_frame.place(relx=0.0, rely=0.1, relwidth=0.65, relheight=0.7)

        # Create a frame for the searching results
        self.searching_id_frame = ctk.CTkFrame(self)
        self.searching_id_frame.place(relx=0.6, rely=0.1, relwidth=0.35, relheight=0.7)

        # Create a style for the Treeview
        style = ttk.Style ()
        style.configure ("Custom.Treeview",
                         background="#2E2E2E",
                         foreground="#FFFFFF",
                         fieldbackground="#2E2E2E",
                         font=("Arial", 14),  # Set the font size here
                         rowheight=27)  # Set the row height here
        style.configure ("Custom.Treeview.Heading",
                         background="#4f0202",  # Heading background color
                         foreground="#000000",  # Heading font color
                         font=("Arial", 16, "bold"))  # Font size for headings
        style.map ("Custom.Treeview",
                   background=[('selected', '#41694b')])  # Set selected row background color

        # All data tree view
        self.all_data_table_view = self.create_treeview(self.all_data_table_frame)

        # Searching results frame
        search_frame = ctk.CTkFrame(self.searching_id_frame)
        search_frame.pack(side="top", padx=10, pady=10)

        search_font_Style = ctk.CTkFont(family='Inter', size=18, weight="bold")
        seach_btn_font_style = ctk.CTkFont(family='Inter', size=18, weight='bold')

        self.entry_sample_id = ctk.CTkEntry(search_frame, width=200,
                                            placeholder_text="Enter Sample ID",
                                            font=search_font_Style)
        self.entry_sample_id.pack(side="left", padx=10)
        self.entry_sample_id.bind("<Return>", lambda event: self.search_data())

        self.search_button = ctk.CTkButton(search_frame, text="Search", font=seach_btn_font_style, command=self.search_data)
        self.search_button.pack(side="left", padx=10)

        self.search_results_view = self.create_treeview(self.searching_id_frame)

        # progress bar -------------------
        # Add a progress bar above the btn_frame
        self.progress_bar = ctk.CTkProgressBar (self, width=300)
        self.progress_bar.pack (side="bottom", fill="x", padx=20, pady=(0, 60))
        self.progress_bar.set (0)  # Initialize progress bar to 0

        # Create a frame for the button (under the table)-----------------
        self.btn_frame = ctk.CTkFrame (self)
        self.btn_frame.pack (side="bottom", anchor="center", pady=(30,30) )

        # Send button
        self.send_button = ctk.CTkButton (self.btn_frame, text="Send", command=self.send_data_to_api,
                                          fg_color="#007BFF", text_color="#FFFFFF", font=("Arial", 12, "bold"))
        self.send_button.pack (side="left", padx=10)

        # Delete button
        self.delete_button = ctk.CTkButton (self.btn_frame, text="Delete", command=self.delete_selected_row,
                                            fg_color="#FF0000", text_color="#FFFFFF", font=("Arial", 12, "bold"))
        self.delete_button.pack (side="left", padx=10)

        # Reload button
        self.reload_button = ctk.CTkButton (self.btn_frame, text="Reload", command=self.reload_data,
                                            fg_color="#28A745", text_color="#FFFFFF", font=("Arial", 12, "bold"))
        self.reload_button.pack (side="left", padx=10)

        # Exit button
        self.exit_button = ctk.CTkButton (self.btn_frame, text="Exit", command=self.controller.quit,
                                          fg_color="#e34145", text_color="#FFFFFF", font=("Arial", 12, "bold"))
        self.exit_button.pack (side="left", padx=10)

        # Bind the "ctrl + R" key combination to reload the data
        self.controller.bind('<Control-r>', lambda event: self.reload_data())

        # Bind the "Delete" key to delete selected row
        self.all_data_table_view.bind('<Delete>', lambda event: self.delete_selected_row())
        self.search_results_view.bind('<Delete>', lambda event: self.delete_selected_row())

        # Load data from the database
        self.load_all_data()

    def send_data_to_api(self):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect ("database/habib07.db")
            cursor = conn.cursor ()

            # Fetch data that needs to be sent (where sent_to_api is 0)
            cursor.execute ("SELECT id, sample_id, json_data FROM astm_data WHERE sent_to_api=0")
            data_to_send = cursor.fetchall ()

            # Determine the number of items to send
            total_items = len (data_to_send)
            if total_items == 0:
                print ("No data to send.")
                return

            # Calculate the progress increment for each item
            progress_increment = 1.0 / total_items

            def send_next_item(index):
                if index < total_items:
                    row = data_to_send[index]
                    data_id = row[0]
                    sample_id = row[1]
                    json_data = row[2]

                    # Simulate sending data (replace this with actual data sending logic)
                    print (f"Sending data for Sample ID: {sample_id}")

                    # If the data was sent successfully, update the database
                    cursor.execute ("UPDATE astm_data SET sent_to_api=1 WHERE id=?", (data_id,))
                    conn.commit ()

                    # Update the progress bar
                    self.progress_bar.set ((index + 1) * progress_increment)

                    # Schedule the next item to be sent after a delay
                    self.after (500, lambda: send_next_item (index + 1))
                else:
                    conn.close ()
                    print ("All data sent successfully.")

                    # Reset progress bar after a short delay
                    self.after (5000, lambda: self.progress_bar.set (0))

            # Start sending the first item
            send_next_item (0)

        except Exception as e:
            # Handle any errors that occur during the sending process
            self.progress_bar.set (0)
            print (f"Error occurred while sending data: {e}")

    def create_treeview(self, parent):
        # Create a frame for the table
        table_frame = ctk.CTkFrame (parent)
        table_frame.pack (fill="both", expand=True)

        # Create the vertical scrollbar
        vsb = ttk.Scrollbar (table_frame, orient="vertical")
        vsb.pack (side="right", fill="y")

        # Create the table (Treeview) inside the frame with custom style
        tree = ttk.Treeview (table_frame,
                             columns=("Serial", "SampleID", "TestNo", "ResultWithUnit", "Status"),
                             show="headings",
                             style="Custom.Treeview",
                             yscrollcommand=vsb.set)
        tree.pack (fill="both", expand=True)

        # Configure the scrollbar to work with the Treeview
        vsb.config (command=tree.yview)

        # Define table column headings
        tree.heading ("Serial", text="Serial")
        tree.heading ("SampleID", text="Sample ID")
        tree.heading ("TestNo", text="Test No")
        tree.heading ("ResultWithUnit", text="Result With Unit")
        tree.heading ("Status", text="Status")

        # Set column widths and alignment
        tree.column ("Serial", width=50, anchor="center")
        tree.column ("SampleID", width=50, anchor="center")
        tree.column ("TestNo", width=50, anchor="center")
        tree.column ("ResultWithUnit", width=100, anchor="center")
        tree.column ("Status", width=50, anchor="center")

        return tree

    def load_all_data(self):
        # Connect to the SQLite database
        conn = sqlite3.connect ("database/habib07.db")
        cursor = conn.cursor ()

        # Fetch data from the database
        cursor.execute ("SELECT id, sample_id, json_data, sent_to_api FROM astm_data ORDER BY id")
        rows = cursor.fetchall ()

        # Process and display the data
        for row in rows:
            serial = row[0]
            sample_id = row[1]
            json_data = json.loads (row[2])
            sent_to_api = row[3]
            status = "Done" if sent_to_api == 1 else ""

            # Check if json_data contains the 'results' list
            if "results" in json_data:
                results = json_data["results"]
                for result in results:
                    test_no = result.get ("test_no", "")
                    result_with_unit = result.get ("result_with_unit", "")

                    # Map the test_no to the corresponding string using the JSON file
                    test_name = self.test_no_mapping.get (str (test_no), test_no)

                    self.all_data_table_view.insert ("", "end",
                                                     values=(serial, sample_id, test_name, result_with_unit, status))

        conn.close ()

        # Automatically scroll to the bottom
        self.all_data_table_view.yview_moveto (1.0)

    def search_data(self):
        # Clear the current data in the search results table
        for item in self.search_results_view.get_children ():
            self.search_results_view.delete (item)

        # Get the sample ID from the entry box
        sample_id_to_search = self.entry_sample_id.get ()

        # Connect to the SQLite database
        conn = sqlite3.connect ("database/habib07.db")
        cursor = conn.cursor ()

        # Fetch data for the specific sample ID from the database
        cursor.execute ("SELECT id, sample_id, json_data, sent_to_api FROM astm_data WHERE sample_id=?",
                        (sample_id_to_search,))
        rows = cursor.fetchall ()

        # Process and display the data
        for row in rows:
            serial = row[0]
            sample_id = row[1]
            json_data = json.loads (row[2])
            sent_to_api = row[3]
            status = "Done" if sent_to_api == 1 else ""

            # Check if json_data contains the 'results' list
            if "results" in json_data:
                results = json_data["results"]
                for result in results:
                    test_no = result.get ("test_no", "")
                    result_with_unit = result.get ("result_with_unit", "")

                    # Map the test_no to the corresponding string using the JSON file
                    test_name = self.test_no_mapping.get (str (test_no), test_no)

                    self.search_results_view.insert ("", "end",
                                                     values=(serial, sample_id, test_name, result_with_unit, status))

        conn.close ()

    def delete_selected_row(self):
        # Get selected item from all_data_table_view
        selected_item = self.all_data_table_view.selection ()
        if selected_item:
            values = self.all_data_table_view.item (selected_item, 'values')
            sample_id_to_delete = values[0]

            # Connect to the SQLite database
            conn = sqlite3.connect ("database/habib07.db")
            cursor = conn.cursor ()

            # Delete the row from the database
            cursor.execute ("DELETE FROM astm_data WHERE id=?", (sample_id_to_delete,))
            conn.commit ()

            # Update the IDs after deletion
            cursor.execute ("SELECT id FROM astm_data ORDER BY id")
            rows = cursor.fetchall ()
            for index, row in enumerate (rows, start=1):
                cursor.execute ("UPDATE astm_data SET id=? WHERE id=?", (index, row[0]))
            conn.commit ()

            conn.close ()

            # Reload data to reflect changes
            self.reload_data ()

        # Get selected item from search_results_view
        selected_item = self.search_results_view.selection ()
        if selected_item:
            values = self.search_results_view.item (selected_item, 'values')
            sample_id_to_delete = values[0]

            # Connect to the SQLite database
            conn = sqlite3.connect ("database/habib07.db")
            cursor = conn.cursor ()

            # Delete the row from the database
            cursor.execute ("DELETE FROM astm_data WHERE id=?", (sample_id_to_delete,))
            conn.commit ()

            # Update the IDs after deletion
            cursor.execute ("SELECT id FROM astm_data ORDER BY id")
            rows = cursor.fetchall ()
            for index, row in enumerate (rows, start=1):
                cursor.execute ("UPDATE astm_data SET id=? WHERE id=?", (index, row[0]))
            conn.commit ()

            conn.close ()

            # Reload data to reflect changes
            self.reload_data ()

    def reload_data(self):
        # Clear the current data in both treeviews
        for item in self.all_data_table_view.get_children():
            self.all_data_table_view.delete(item)
        for item in self.search_results_view.get_children():
            self.search_results_view.delete(item)

        # Reload the data from the database
        self.load_all_data ()