import shared_utils
import customtkinter as ctk
from CTkListbox import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import os
import json
from email_validator import validate_email, EmailNotValidError
from google_auth_oauthlib.flow import InstalledAppFlow
import keyring
import logging
import uuid

class OwletteConfigApp:
    VERSION = '0.2.1'
    FRAME_COLOR = '#28292b'
    BUTTON_COLOR = '#374448'
    BUTTON_HOVER_COLOR = '#27424a'
    BUTTON_IMPORTANT_COLOR = '#2d5e6c'

    def __init__(self, master):
        self.master = master
        self.master.title("Owlette Configuration")
        self.master.geometry("960x550")
        self.selected_process = None

        # Initialize UI
        self.setup_ui()

        # Load existing config after defining email entry widgets
        self.config = self.load_config(self.emails_to_entry)

        # Set default values if empty
        if not self.time_delay_entry.get():
            self.time_delay_entry.insert(0, 0)
        if not self.time_to_init_entry.get():
            self.time_to_init_entry.insert(0, 10)
        if not self.relaunch_attempts_entry.get():
            self.relaunch_attempts_entry.insert(0, 3)

        self.update_process_list()

    def setup_ui(self):
        # Create frame for process details
        self.process_details_frame = ctk.CTkFrame(master=self.master, fg_color=self.FRAME_COLOR)
        self.process_details_frame.grid(row=0, column=0, sticky='news', rowspan=7, columnspan=4, padx=10, pady=(10,0))

        self.process_list_frame = ctk.CTkFrame(master=self.master, fg_color=self.FRAME_COLOR)
        self.process_list_frame.grid(row=0, column=4, sticky='news', rowspan=7, columnspan=4, padx=(0, 10), pady=(10,0))

        self.alerts_frame = ctk.CTkFrame(master=self.master, fg_color=self.FRAME_COLOR)
        self.alerts_frame.grid(row=7, column=0, sticky='news', rowspan=3, columnspan=4, padx=(10,10), pady=(10,0))

        # Create a toggle switch for process
        self.autostart_process_toggle = ctk.CTkSwitch(master=self.master, text="Autostart Process", command=self.toggle_start_process, onvalue="on", offvalue="off")
        self.autostart_process_toggle.grid(row=6, column=2, sticky='w', padx=10, pady=(0, 0))
        self.autostart_process_toggle.configure(bg_color=self.FRAME_COLOR, fg_color='red', progress_color=self.BUTTON_IMPORTANT_COLOR)
        self.autostart_process_toggle.select()

        # Create Name of process field
        self.name_label = ctk.CTkLabel(self.master, text="Name:", fg_color=self.FRAME_COLOR)
        self.name_label.grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(self.master, placeholder_text="Name of your process")
        self.name_entry.grid(row=1, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

        # Create Exe path field
        self.exe_path_label = ctk.CTkLabel(self.master, text="Exe Path:", fg_color=self.FRAME_COLOR)
        self.exe_path_label.grid(row=2, column=0, sticky='e', padx=5, pady=5)
        self.exe_path_entry = ctk.CTkEntry(self.master, placeholder_text="The full path to your executable (application)")
        self.exe_path_entry.grid(row=2, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

        # Create Browse button for Exe
        self.exe_browse_button = ctk.CTkButton(self.master, text="Browse", command=self.browse_exe, width=60, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.exe_browse_button.grid(row=2, column=3, sticky='w', padx=5, pady=5)

        # Create File path / cmd line args
        self.file_path_label = ctk.CTkLabel(self.master, text="File Path / Cmd Line Args:", fg_color=self.FRAME_COLOR)
        self.file_path_label.grid(row=3, column=0, sticky='e', padx=(10, 5), pady=5)
        self.file_path_entry = ctk.CTkEntry(self.master, placeholder_text="The full path to your document or command line arguments")
        self.file_path_entry.grid(row=3, column=1, columnspan=2, sticky='ew', padx=5, pady=5)

        # Create Browse button for File
        self.file_browse_button = ctk.CTkButton(self.master, text="Browse", command=self.browse_file, width=60, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.file_browse_button.grid(row=3, column=3, sticky='w', padx=5, pady=5)

        # Create Time delay label and field
        self.time_delay_label = ctk.CTkLabel(self.master, text="Start Time Delay (s):", fg_color=self.FRAME_COLOR)
        self.time_delay_label.grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.time_delay_entry = ctk.CTkEntry(self.master, placeholder_text="0", width=60)
        self.time_delay_entry.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        # Create a label and entry for "Restart Attempts"
        self.relaunch_attempts_label = ctk.CTkLabel(self.master, text="Relaunch attempts til Restart:", fg_color=self.FRAME_COLOR)
        self.relaunch_attempts_label.grid(row=5, column=2, sticky='w', padx=10, pady=5)
        self.relaunch_attempts_entry = ctk.CTkEntry(self.master, placeholder_text="3", width=60)
        self.relaunch_attempts_entry.grid(row=5, column=3, sticky='w', padx=5, pady=5)

        # Create a label and entry for "Time to Initialize"
        self.time_to_init_label = ctk.CTkLabel(self.master, text="Time to Initialize (s):", fg_color=self.FRAME_COLOR)
        self.time_to_init_label.grid(row=6, column=0, sticky='e', padx=5, pady=5)
        self.time_to_init_entry = ctk.CTkEntry(self.master, placeholder_text="10", width=60)
        self.time_to_init_entry.grid(row=6, column=1, sticky='w', padx=5, pady=5)

        # Create Add Process button
        self.add_button = ctk.CTkButton(self.master, text="Add", command=self.add_process, width=60, fg_color=self.BUTTON_IMPORTANT_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.add_button.grid(row=6, column=3, sticky='w', padx=(5, 0), pady=(5, 10))

        # Create a label for the process details
        self.process_details_label = ctk.CTkLabel(root, text="PROCESS DETAILS", fg_color=self.FRAME_COLOR)
        self.process_details_label.grid(row=0, column=0, sticky='w', padx=(20, 10), pady=(20, 0))

        # Create a label for the process list
        self.process_list_label = ctk.CTkLabel(root, text="PROCESS STARTUP LIST", fg_color=self.FRAME_COLOR)
        self.process_list_label.grid(row=0, column=4, sticky='w', padx=10, pady=(20, 0))
        self.process_list_label.configure(width=40)

        # Create a label for the app version
        self.version_label = ctk.CTkLabel(root, text=f"v{self.VERSION}", fg_color='transparent')
        self.version_label.grid(row=9, column=4, sticky='e', padx=10, pady=(0, 0))
        self.version_label.configure(width=40)

        # Create a Listbox to display the list of processes
        self.process_list = CTkListbox(self.master, command=self.on_select)
        self.process_list.grid(row=1, column=4, columnspan=3, rowspan=5, sticky='nsew', padx=(10,20), pady=10)
        self.process_list.configure(highlight_color=self.BUTTON_IMPORTANT_COLOR, hover_color=self.BUTTON_HOVER_COLOR, width=80)

        # Up and down buttons
        self.up_button = ctk.CTkButton(self.master, text="Up", command=self.move_up, width=60, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.up_button.grid(row=6, column=5, sticky='w', padx=(10, 10), pady=(5, 10))

        self.down_button = ctk.CTkButton(self.master, text="Down", command=self.move_down, width=60, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.down_button.grid(row=6, column=6, sticky='e', padx=(10, 20), pady=(5, 10))

        # Create Delete button
        self.remove_button = ctk.CTkButton(self.master, text="Delete", command=self.remove_process, width=60, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.remove_button.grid(row=6, column=4, sticky='w', padx=(10, 20), pady=(5, 10))

        # Create Save Changes button
        self.save_button = ctk.CTkButton(self.master, text="Save Changes", command=self.update_selected_process, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.save_button.grid(row=9, column=5, columnspan=2, sticky='ew', padx=(10, 20), pady=(10, 10))

        # Create Connect to Gmail button
        self.gmail_button = ctk.CTkButton(self.master, text="Auth Gmail", command=self.get_google_auth_token, fg_color=self.BUTTON_COLOR, hover_color=self.BUTTON_HOVER_COLOR)
        self.gmail_button.grid(row=9, column=1, sticky='w', padx=(5), pady=(10, 10))

        # Create a label for the alerts section
        self.alerts_label = ctk.CTkLabel(root, text="ALERTS", fg_color=self.FRAME_COLOR)
        self.alerts_label.grid(row=7, column=0, sticky='w', padx=(20, 10), pady=(20, 10))

        # Create Labels and Entry widgets for email configuration
        self.emails_to_label = ctk.CTkLabel(self.master, text="Emails To:", fg_color=self.FRAME_COLOR)
        self.emails_to_label.grid(row=8, column=0, sticky='e', padx=5, pady=10)
        self.emails_to_entry = ctk.CTkEntry(self.master, placeholder_text="Email Addresses (comma separated)")
        self.emails_to_entry.grid(row=8, column=1, columnspan=2, sticky='ew', padx=5, pady=10)

        # Bind the Entry widgets to update the selected process when the Return key is pressed
        self.name_entry.bind('<Return>', self.update_selected_process)
        self.exe_path_entry.bind('<Return>', self.update_selected_process)
        self.file_path_entry.bind('<Return>', self.update_selected_process)
        self.emails_to_entry.bind('<Return>', self.update_email_config)
        self.time_delay_entry.bind('<Return>', self.update_selected_process)
        self.time_to_init_entry.bind('<Return>', self.update_selected_process)
        self.relaunch_attempts_entry.bind('<Return>', self.update_selected_process)

        # Make columns stretchable
        root.grid_columnconfigure(0, weight=1) # labels
        root.grid_columnconfigure(1, weight=2)
        root.grid_columnconfigure(2, weight=2)
        root.grid_columnconfigure(3, weight=2)
        root.grid_columnconfigure(4, weight=1)
        root.grid_columnconfigure(5, weight=1)
        root.grid_columnconfigure(6, weight=1)

    # CONFIG JSON
    def load_config(self, emails_to_entry):
        try:
            with open(shared_utils.get_path('../config/config.json'), 'r') as f:
                config = json.load(f)
                emails_to_entry.insert(0, ', '.join(config['email']['to']))
                return config
        except FileNotFoundError:
            logging.error(f"Failed to load config: {e}")
            return {shared_utils.generateConfigFile()}

        # Backwards compatibility
        for process in self.config.get('processes', []):
            if 'id' not in process:
                process['id'] = str(uuid.uuid4())
                
    def save_config(self, config):
        config['email']['to'] = [email.strip() for email in self.emails_to_entry.get().split(',')]
        with open(shared_utils.get_path('../config/config.json'), 'w') as f:
            json.dump(config, f, indent=4)
    
    # PROCESS HANDLING
    def toggle_start_process(self):
        if self.selected_process:
            index = shared_utils.get_process_index(self.selected_process)
            current_state = self.config['processes'][index].get('autostart_process', False)
            self.config['processes'][index]['autostart_process'] = not current_state
            self.save_config(self.config)
        else:
            tk.messagebox.showwarning("No Process Selected", "Please select a process to toggle autostart.")

    def update_selected_process(self,event=None):
        # Field Validation
        name = self.name_entry.get()
        exe_path = self.exe_path_entry.get()
        file_path = self.file_path_entry.get()
        time_delay = self.time_delay_entry.get()
        time_to_init = self.time_to_init_entry.get()
        relaunch_attempts = self.relaunch_attempts_entry.get()

        # Validate Time Delay
        try:
            if float(time_delay):  # Try converting the time delay to a float
                if float(time_delay) < 0:
                    raise ValueError("Start Time Delay must be greater than or equal to 0.")

        except ValueError:
            tk.messagebox.showwarning("Validation Error", "Start Time Delay must be a number (integer or float).")
            self.time_delay_entry.delete(0, tk.END)
            self.time_delay_entry.insert(0, 0)
            return

        # Validate Time To Init
        try:
            if float(time_to_init):  # Try converting the time to init to a float
                if float(time_to_init) < 10 or float(time_to_init) == 0:
                    raise ValueError("Time to initialize must be greater than or equal to 10 seconds.")
        except ValueError:
            tk.messagebox.showwarning("Validation Error", "Time to Initialize must be at least 10 seconds")
            self.time_to_init_entry.delete(0, tk.END)
            self.time_to_init_entry.insert(0, 10)
            return

        # Validate Relaunch Attempts
        try:
            if int(relaunch_attempts):  # Try converting the relaunch attempts to an integer
                if int(relaunch_attempts) < 0:
                    raise ValueError("Relaunch attempts must be >=0")
        except ValueError:
            tk.messagebox.showwarning("Validation Error", "Relaunch attempts must be an integer. 3 is recommended. After 3 attempts, a system restart will be attempted. Set to 0 for unlimited attempts to relaunch (no system restart).")
            self.relaunch_attempts_entry.delete(0, tk.END)
            self.relaunch_attempts_entry.insert(0, 3)
            return

        # Check if relaunch attempts is empty and set to default if so
        if not relaunch_attempts:
            relaunch_attempts = 3  # Default value

        # Check if time to init is empty and set to default if so
        if not time_to_init:
            relaunch_attempts = 60  # Default value

        # Write config
        if self.selected_process:
            # Require Name/Exe Paths
            if not name or not exe_path:
                tk.messagebox.showwarning("Validation Error", "Name and Exe Path are required fields.")
                return

            index = shared_utils.get_process_index(self.selected_process)

            self.config['processes'][index]['name'] = name
            self.config['processes'][index]['exe_path'] = exe_path
            self.config['processes'][index]['file_path'] = file_path
            self.config['processes'][index]['time_delay'] = time_delay
            self.config['processes'][index]['time_to_init'] = time_to_init
            self.config['processes'][index]['relaunch_attempts'] = relaunch_attempts

            self.save_config(self.config)
            self.update_process_list()

            # Re-select the process
            self.process_list.activate(index)

        self.update_email_config()  # Always update email config

    def add_process(self):
        # Generate a unique ID for the new process
        unique_id = str(uuid.uuid4())

        name = self.name_entry.get()
        exe_path = self.exe_path_entry.get()
        file_path = self.file_path_entry.get()
        time_delay = self.time_delay_entry.get() if self.time_delay_entry.get() else 0 # Default to 0 if empty
        time_to_init = self.time_to_init_entry.get() if self.time_to_init_entry.get() else 60 # Default to 60 if empty
        relaunch_attempts = self.relaunch_attempts_entry.get() if self.relaunch_attempts_entry.get() else 3 # Default to 3 if empty
        autostart_process = True if self.autostart_process_toggle.get() == 'on' else False
        
        if not name or not exe_path:
            tk.messagebox.showwarning("Validation Error", "Name and Exe Path are required fields.")
            return
        
        if not os.path.exists(exe_path):
            tk.messagebox.showwarning("Validation Error", "The specified Exe Path does not exist.")
            return
        
        if file_path and not os.path.exists(file_path):
            tk.messagebox.showwarning("Validation Error", "The specified File Path does not exist.")
            return

        new_process = {
            'id': unique_id,
            'name': name,
            'exe_path': exe_path,
            'file_path': file_path,
            'time_delay': time_delay,
            'time_to_init': time_to_init,
            'relaunch_attempts': relaunch_attempts,
            'autostart_process': autostart_process
        }

        self.config['processes'].append(new_process)
        self.save_config(self.config)
        self.update_process_list()

    # BROWSING FOR FILES
    def browse_exe(self):
        exe_path = filedialog.askopenfilename(initialdir="C:/", title="Select Exe File", filetypes=[("Executable files", "*.exe")])
        self.exe_path_entry.delete(0, tk.END)
        self.exe_path_entry.insert(0, exe_path)
        self.update_selected_process()

    def browse_file(self):
        file_path = filedialog.askopenfilename(initialdir="C:/", title="Select File")
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)
        self.update_selected_process()

    # PROCESS LIST
    def update_process_list(self):
        for i in range(1, self.process_list.size()):
            self.process_list.delete(i)
        for i, process in enumerate(self.config['processes']):
            self.process_list.insert(i, process['name'])

    def remove_process(self):
        if self.selected_process:
            process = shared_utils.fetch_process_by_id(self.selected_process, self.config)
            if process:
                process_name = shared_utils.fetch_process_name_by_id(self.selected_process, self.config)
                confirm = tk.messagebox.askyesno("Confirmation", f"Are you sure you want to remove {process_name}?")
                if confirm:
                    index = shared_utils.get_process_index(self.selected_process)
                    if index is not None:
                        del self.config['processes'][index]
                        self.save_config(self.config)
                        self.update_process_list()            
            else:
                tk.messagebox.showerror("Error", f"No process found with the name '{self.selected_process}'")

    def move_up(self):
        if self.selected_process:
            index = shared_utils.get_process_index(self.selected_process)
            if index > 0:
                self.config['processes'][index], self.config['processes'][index-1] = self.config['processes'][index-1], self.config['processes'][index]
                self.save_config(self.config)
                self.update_process_list()
                self.process_list.activate(index-1)

    def move_down(self):
        if self.selected_process:
            index = shared_utils.get_process_index(self.selected_process)
            if index < len(self.config['processes']) - 1:
                self.config['processes'][index], self.config['processes'][index+1] = self.config['processes'][index+1], self.config['processes'][index]
                self.save_config(self.config)
                self.update_process_list()
                self.process_list.activate(index+1)

    def on_select(self, process_name):
        process_id = shared_utils.fetch_process_id_by_name(process_name, self.config)
        self.selected_process = process_id
        process = shared_utils.fetch_process_by_id(process_id, self.config)
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, process.get('name', ''))
        self.exe_path_entry.delete(0, tk.END)
        self.exe_path_entry.insert(0, process.get('exe_path', ''))
        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, process.get('file_path', ''))
        self.time_delay_entry.delete(0, tk.END)
        self.time_delay_entry.insert(0, process.get('time_delay', ''))
        self.time_to_init_entry.delete(0, tk.END)
        self.time_to_init_entry.insert(0, process.get('time_to_init', ''))
        self.relaunch_attempts_entry.delete(0, tk.END)
        self.relaunch_attempts_entry.insert(0, process.get('relaunch_attempts', ''))
        autostart = process.get('autostart_process', True)
        if autostart:
            self.autostart_process_toggle.select()
        else:
            self.autostart_process_toggle.deselect()

    # EMAIL
    def validate_email_address(self, email):
        try:
            # validate and get info
            v = validate_email(email)
            return True
        except EmailNotValidError as e:
            # email is not valid, exception message is human-readable
            print(str(e))
            tk.messagebox.showwarning('', f"{e}")
            return False

    def update_email_config(self, event=None):
        emails_to = self.emails_to_entry.get().split(',')
        for email in emails_to:
            if email.strip():  # Skip validation for empty items in the list
                if not self.validate_email_address(email.strip()):
                    tk.messagebox.showwarning("Validation Error", f"The 'Email To' address {email} is not valid.")
                    return

        self.config['email']['to'] = [email.strip() for email in emails_to]
        self.save_config(self.config)

    def save_credentials_to_file(self, credentials, filename):
        with open(shared_utils.get_path(filename), 'w') as f:
            json.dump(json.loads(credentials.to_json()), f)

    def get_google_auth_token(self):
        # Initialize the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            shared_utils.get_path('client_secrets.json'),
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )

        # Run the flow
        credentials = flow.run_local_server(port=0)
        keyring.set_password("Owlette", "GmailRefreshToken", credentials.refresh_token)

if __name__ == "__main__":
    root = ctk.CTk()
    app = OwletteConfigApp(root)
    root.mainloop()