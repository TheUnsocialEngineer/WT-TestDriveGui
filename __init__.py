import tkinter as tk
from tkinter import ttk, filedialog
import json
import os
import webbrowser

# Variable to store the last selected nation and its value
last_selected = {"nation": None, "value": None}

# Load the vehicles data from vehicles.json
with open("vehicles.json", "r") as f:
    vehicles_data = json.load(f)

# Load the config from config.json
def load_config():
    global config
    if os.path.exists("config.json"):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print("Error decoding JSON. Initializing with default values.")
            initialize_default_config()
    else:
        # If config file doesn't exist, initialize a default config
        print("Config file not found. Creating new config with default values.")
        initialize_default_config()

# Function to initialize the default config
def initialize_default_config():
    global config
    config = {
        "game_type": "steam",
        "warthunder_install_path": "",
        "steam_install_path": "",
        "user_vehicle_path": "",  # To store the user vehicle path
        "has_run": False,  # Track if the program has been run before
        "custom_mission_path": ""  # To store the custom mission path
    }
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# Function to get the WarThunder installation path dynamically
def get_warthunder_path():
    username = os.getlogin()  # Get the current user's username
    return f"C:\\Users\\{username}\\AppData\\Local\\WarThunder\\"

# Function to check if the program has been run before
def first_run_check():
    if not config["has_run"]:
        # If it's the first run, check and set the game type
        print("First run detected. Checking install paths.")
        check_game_install_path()
        # Set the user_vehicle_path
        set_user_vehicle_path()
        # Mark as run and save config
        config["has_run"] = True
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        update_game_type_label()  # Update the label immediately on first run
        check_custom_mission_path()  # Prompt for custom mission path if not set
    else:
        # If it has been run before, just load the game type and path
        print(f"Program has been run before. Current game type: {config['game_type']}")
        update_game_type_label()  # Update the label on subsequent runs as well

# Function to check if the custom_mission_path exists, and prompt the user if it doesn't
def check_custom_mission_path():
    if not config.get("custom_mission_path"):  # Check if it's empty or not set
        print("custom_mission_path is not set. Prompting for file selection.")
        select_custom_mission_path()

# Function to set the user vehicle path based on the game type
def set_user_vehicle_path():
    if config["game_type"] == "warthunder":
        # If the game type is WarThunder, set the default vehicle path
        config["user_vehicle_path"] = os.path.join(get_warthunder_path(), "content\\pkg_local\\gameData\\units\\tankmodels\\userVehicles\\us_m2a4.blk")
    else:
        # For Steam or other games, ask the user to select the path and append the vehicle model path
        select_game_install_path()
        config["user_vehicle_path"] = os.path.join(config["steam_install_path"], "content\\pkg_local\\gameData\\units\\tankModels\\userVehicles\\us_m2a4.blk")
    # Save the updated config
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

# Function to check if WarThunder or Steam install path exists and update game type accordingly
def check_game_install_path():
    # Set the WarThunder path using dynamic username
    config["warthunder_install_path"] = get_warthunder_path()

    # Check if WarThunder install path exists
    if not os.path.exists(config["warthunder_install_path"]):
        print("WarThunder path does not exist. Prompting for path selection.")
        # Ask the user to select the game install path
        select_game_install_path()
    else:
        config["game_type"] = "warthunder"
    
    # Check if Steam install path exists only if WarThunder path was not selected
    if config["game_type"] != "warthunder" and not os.path.exists(config["steam_install_path"]):
        print("Steam path does not exist. Prompting for path selection.")
        select_game_install_path()

# Function to update the game type label in the GUI
def update_game_type_label():
    game_type_label.config(text=f"Game Type: {config['game_type'].capitalize()}")

# Function to prompt the user to select the custom mission file (only .blk files)
def select_custom_mission_path():
    selected_file = filedialog.askopenfilename(
        title="Select Custom Mission File", 
        filetypes=[("Mission Files", "*.blk"), ("All Files", "*.*")]
    )
    
    if selected_file:
        config["custom_mission_path"] = selected_file
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        print(f"Custom mission path set to: {selected_file}")
    else:
        print("No file selected for custom mission path.")

# Function to prompt the user to select the game install directory
def select_game_install_path():
    selected_path = filedialog.askdirectory(title="Select Game Install Directory")
    
    if selected_path:
        if not os.path.exists(config["warthunder_install_path"]):
            config["warthunder_install_path"] = selected_path
            config["game_type"] = "warthunder"
        else:
            config["steam_install_path"] = selected_path
            config["game_type"] = "steam"
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        update_game_type_label()  # Update GUI to show the current game type

# Function to handle dropdown selection change
def on_dropdown_change(nation, event):
    last_selected["nation"] = nation
    last_selected["value"] = event.widget.get()

# Function to update the values in the files specified by user_vehicle_path and custom_mission_path
def update_values(selected_vehicle_id):
    # 1. Update the user_vehicle_path (editing the include statement)
    if config["user_vehicle_path"]:
        try:
            # Open the user_vehicle_path file
            with open(config["user_vehicle_path"], "r") as file:
                file_data = file.readlines()
            
            # Iterate through the lines to find the 'include' statement and update it
            for i, line in enumerate(file_data):
                if line.strip().startswith('include'):
                    # Replace the .blk part with the selected vehicle ID
                    file_data[i] = f'include "#/develop/gameBase/gameData/units/tankModels/{selected_vehicle_id}.blk"\n'
                    break
            
            # Write the updated lines back to the file
            with open(config["user_vehicle_path"], "w") as file:
                file.writelines(file_data)
            print(f"Updated user vehicle file: {config['user_vehicle_path']}")
        except Exception as e:
            print(f"Error updating user vehicle file: {e}")
    
    # 2. Update the custom_mission_path (changing the weapons value)
    if config["custom_mission_path"]:
        try:
            # Open the custom mission file
            with open(config["custom_mission_path"], "r") as file:
                # Read all lines
                lines = file.readlines()
            # Iterate through each line and replace the weapons:t="{config.last_selected}" with the new value
            updated_lines = []
            for line in lines:
                if f'weapons:t="{config["last_selected"]}_default"' in line:
                    # Replace the old value with the new vehicle ID (selected_vehicle_id)
                    line = line.replace(f'weapons:t="{config["last_selected"]}_default"', f'weapons:t="{selected_vehicle_id}_default"')
                updated_lines.append(line)
            
            # Write the updated lines back to the custom mission file
            with open(config["custom_mission_path"], "w") as file:
                file.writelines(updated_lines)
            
            print(f"Updated custom mission file: {config['custom_mission_path']}")
        
        except Exception as e:
            print(f"Error updating custom mission file: {e}")

# Function to handle the "Select" button click
def on_select():
    nation = last_selected["nation"]
    value = last_selected["value"]
    if nation and value:
        # Fetch the selected vehicle ID
        selected_vehicle_id = f"{value.replace(' ', '_').lower()}"
        print(f"Selected Vehicle ID: {selected_vehicle_id}")
        
        # Update the files with the selected vehicle ID
        update_values(selected_vehicle_id)
        # Update last_selected in the config
        config["last_selected"] = value
        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)
        
        # Update the label
        selected_vehicle_label.config(text=f"Selected Vehicle: {nation} - {value}")
    else:
        print("No option selected yet!")

# Function to populate all dropdowns with vehicle IDs
def populate_all_dropdowns():
    for nation in vehicles_data:
        # Check if the nation exists in the dropdowns dictionary
        if nation in dropdowns:
            nation_vehicle_ids = vehicles_data[nation]
            # Get the current dropdown for the nation
            combobox = dropdowns.get(nation)
            if combobox:
                # Set the dropdown options to vehicle IDs
                combobox['values'] = nation_vehicle_ids
                # Set the default option to the first vehicle ID in the list, if available
                if nation_vehicle_ids:
                    combobox.set(nation_vehicle_ids[0])


# Initialize main window
root = tk.Tk()
root.title("WT Test Drive GUI")
root.geometry("600x550")  # Window size
root.resizable(False, False)

# Load configuration and check if it's the first run
load_config()

# Create a label to display the game type before checking if it has been run
game_type_label = ttk.Label(root, text=f"Game Type: {config['game_type'].capitalize()}", font=("Arial", 12))
game_type_label.grid(row=0, column=0, padx=10, pady=10)

# Check if it's the first run after creating the label
first_run_check()

# List of nations
nations = ["USA", "Germany", "USSR", "Great Britain", "Japan", "China", "Italy", "France", "Sweden", "Israel"]

# Placeholder options for dropdowns
dropdown_options = {
    "USA": ["Select an option"],  # Initially empty, will be populated with vehicle IDs later
    "Germany": ["Option 1", "Option 2", "Option 3"],
    "USSR": ["Option 1", "Option 2", "Option 3"],
    "Great Britain": ["Option 1", "Option 2", "Option 3"],
    "Japan": ["Option 1", "Option 2", "Option 3"],
    "China": ["Option 1", "Option 2", "Option 3"],
    "Italy": ["Option 1", "Option 2", "Option 3"],
    "France": ["Option 1", "Option 2", "Option 3"],
    "Sweden": ["Option 1", "Option 2", "Option 3"],
    "Israel": ["Option 1", "Option 2", "Option 3"]
}

# Dictionary to store comboboxes
dropdowns = {}

# Create frames for each nation
for idx, nation in enumerate(nations):
    frame = ttk.Frame(root)
    frame.grid(row=idx + 1, column=0, padx=10, pady=5, sticky="w")

    # Add nation label
    label = ttk.Label(frame, text=nation, font=("Arial", 12, "bold"))
    label.grid(row=0, column=0, padx=5)

    # Add dropdown for each nation
    combobox = ttk.Combobox(frame, values=dropdown_options[nation], state="readonly", width=30)
    combobox.grid(row=0, column=1, padx=5)
    combobox.bind("<<ComboboxSelected>>", lambda event, nation=nation: on_dropdown_change(nation, event))

    # Store combobox for later population
    dropdowns[nation] = combobox

# Button to select the vehicle
select_button = ttk.Button(root, text="Select Vehicle", command=on_select)
select_button.grid(row=len(nations) + 1, column=0, padx=10, pady=10)

# Label to display selected vehicle
selected_vehicle_label = ttk.Label(root, text="Selected Vehicle: None", font=("Arial", 12))
selected_vehicle_label.grid(row=len(nations) + 2, column=0, padx=10, pady=10)

# Label to display thanks
thanks_label = ttk.Label(root, text="Thanks to Ask3lad for providing the files and IDs that make this possible ", font=("Arial", 12))
thanks_label.grid(row=len(nations) + 3, column=0, padx=10, pady=10)

# label for Ask3lads discord
def callback(url):
    webbrowser.open_new(url)
hyperlink = ttk.Label(root, text="Ask3lad's Discord")
hyperlink.grid(row=len(nations) + 4, column=0, padx=10, pady=10)
hyperlink.bind("<Button-1>", lambda e: callback("https://discord.gg/XX3RXMBY"))

# Populate USA dropdown with vehicle IDs
populate_all_dropdowns()

# Start the GUI event loop
root.mainloop()
