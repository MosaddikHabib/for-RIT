from cx_Freeze import setup, Executable
import sys
import os

# Include additional files
include_files = ['habib07.db', 'serial_params.json', 'res/']

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {
    'packages': ['os', 'tkinter'],
    'include_files': include_files
}

# Base option for GUI applications
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'  # Use 'Win32GUI' for a Tkinter application to hide the console

# Executable configuration
executables = [
    Executable('main.py', base=base, target_name='MainApp.exe'),
    Executable('sent_to_API.py', base=base, target_name='SentToAPI.exe')
]

# Setup configuration
setup(
    name='HostMate',
    version='1.0',
    description='developed by rajIT',
    options={'build_exe': build_exe_options},
    executables=executables
)
