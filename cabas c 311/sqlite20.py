import sqlite3
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox, simpledialog


# Connect to the SQLite database
def connect_db(db_name):
    return sqlite3.connect (db_name)


# Fetch data from the database
def fetch_data(conn, table_name):
    cursor = conn.cursor ()
    cursor.execute (f"SELECT * FROM {table_name}")
    return cursor.fetchall (), [description[0] for description in cursor.description]


# Update data in the database
def update_data(conn, table_name, row_id, updates):
    cursor = conn.cursor ()
    set_clause = ", ".join ([f"{col} = ?" for col in updates.keys ()])
    values = list (updates.values ()) + [row_id]
    cursor.execute (f"UPDATE {table_name} SET {set_clause} WHERE id = ?", values)
    conn.commit ()


# Create the main application window
class DatabaseViewer (ttkb.Window):
    def __init__(self, db_name, table_name):
        super ().__init__ (themename="darkly")  # Set theme to darkly
        self.title ("SQLite Database Viewer")
        self.geometry ("800x600")

        # Connect to the database and fetch data
        self.db_name = db_name
        self.conn = connect_db (db_name)
        self.table_name = table_name
        self.data, self.columns = fetch_data (self.conn, table_name)

        # Set the font and style for the Treeview
        style = ttk.Style (self)
        style.configure ("Treeview.Heading", font=("Arial", 25), anchor='w')
        style.configure ("Treeview", font=("Arial", 12))

        # Create a frame for the Treeview and scrollbar
        tree_frame = ttk.Frame (self)
        tree_frame.pack (expand=True, fill='both')

        # Create the Treeview widget
        self.tree = ttk.Treeview (tree_frame, columns=self.columns, show='headings', bootstyle=PRIMARY)
        for col in self.columns:
            self.tree.heading (col, text=col)

        # Create a vertical scrollbar and attach it to the Treeview
        scrollbar = ttk.Scrollbar (tree_frame, orient="vertical", command=self.tree.yview, bootstyle=DANGER)
        self.tree.configure (yscroll=scrollbar.set)
        scrollbar.pack (side=RIGHT, fill=Y)

        # Insert data into the Treeview
        self.insert_data_into_treeview (self.data)

        # Pack the Treeview widget
        self.tree.pack (side=LEFT, expand=True, fill='both')

        # # making a frame inside a class
        # self.bottom_frame = ttk.Frame (self, width=300, height=200)
        # self.bottom_frame.pack ()

        # Add edit button
        edit_button = ttkb.Button (self, text="Edit", command=self.edit_record, bootstyle=PRIMARY)
        edit_button.pack(pady=10)
        # edit_button.grid(row=0, column=0, pady=10)

        # Add refresh button
        refresh_button = ttkb.Button (self, text="Reload", command=self.refresh_data, bootstyle=DANGER)
        refresh_button.pack(pady=10)
        # refresh_button.grid(row=0, column=1, pady=10)

    def insert_data_into_treeview(self, data):
        for row in data:
            self.tree.insert ("", END, values=row)

    def edit_record(self):
        selected_item = self.tree.selection ()
        if not selected_item:
            messagebox.showerror ("Error", "No item selected")
            return

        item = self.tree.item (selected_item)
        current_values = item['values']
        updates = {}

        for i, column in enumerate (self.columns):
            new_value = simpledialog.askstring ("Edit", f"Edit {column}:", initialvalue=current_values[i])
            if new_value:
                updates[column] = new_value

        if updates:
            row_id = current_values[0]
            update_data (self.conn, self.table_name, row_id, updates)

            # Refresh the Treeview
            self.tree.item (selected_item,
                            values=[updates.get (col, current_values[i]) for i, col in enumerate (self.columns)])

    def refresh_data(self):
        self.tree.delete (*self.tree.get_children ())  # Clear existing data
        self.conn = connect_db (self.db_name)  # Reconnect to the database
        self.data, self.columns = fetch_data (self.conn, self.table_name)  # Fetch updated data
        self.insert_data_into_treeview (self.data)  # Insert updated data into the Treeview


# Main function to run the application
def main():
    db_name = 'habib07.db'  # Replace with your database file name
    table_name = 'astm_data'  # Replace with your table name
    app = DatabaseViewer (db_name, table_name)  # Initialize the application
    app.mainloop ()


if __name__ == "__main__":
    main ()
