import tkinter as tk
import threading
import csv
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
csv_file_path = 'data.csv'

# Ensure CSV file exists
if not os.path.exists(csv_file_path):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'People Entered', 'People Exited', 'Current Count', 'Noise Level', 'Light Level'])

# Initialize the counts
people_entered = 0
people_exited = 0
current_count = 0
noise_level = 0
light_level = 0

@app.route('/data', methods=['POST'])
def receive_data():
    global people_entered, people_exited, current_count, noise_level, light_level
    data = request.get_json()

    # Update counts from incoming data
    people_entered += data.get('people_entered', 0)
    people_exited += data.get('people_exited', 0)
    current_count = people_entered - people_exited
    noise_level = data.get('noise_level', noise_level)
    light_level = data.get('light_level', light_level)

    # Write to CSV
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data['timestamp'], people_entered, people_exited, current_count, noise_level, light_level])

    return jsonify({'status': 'success'})

def start_flask():
    app.run(host='0.0.0.0', port=5000)

def update_gui():
    # Update the GUI labels
    people_entered_label.config(text=f"People Entered: {people_entered}")
    people_exited_label.config(text=f"People Exited: {people_exited}")
    current_count_label.config(text=f"Current Count: {current_count}")
    noise_level_label.config(text=f"Noise Level: {noise_level}")
    light_level_label.config(text=f"Light Level: {light_level}")

    # Schedule the next update
    root.after(1000, update_gui)

def open_gui():
    global root, people_entered_label, people_exited_label, current_count_label, noise_level_label, light_level_label
    root = tk.Tk()
    root.title("Room Simulation Data")

    # Create GUI components
    people_entered_label = tk.Label(root, text=f"People Entered: {people_entered}")
    people_entered_label.pack()

    people_exited_label = tk.Label(root, text=f"People Exited: {people_exited}")
    people_exited_label.pack()

    current_count_label = tk.Label(root, text=f"Current Count: {current_count}")
    current_count_label.pack()

    noise_level_label = tk.Label(root, text=f"Noise Level: {noise_level}")
    noise_level_label.pack()

    light_level_label = tk.Label(root, text=f"Light Level: {light_level}")
    light_level_label.pack()

    # Start the Tkinter GUI loop
    update_gui()
    root.mainloop()

if __name__ == '__main__':
    # Start Flask in a separate thread
    threading.Thread(target=start_flask, daemon=True).start()
    # Open the Tkinter GUI
    open_gui()
