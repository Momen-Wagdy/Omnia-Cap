import flet as ft
import threading
import csv
import os
from flask import Flask, request, jsonify
import time

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

def update_gui(page):
    while True:
        page.update()  # Refresh the page
        time.sleep(5)  # Update every 5 seconds

def create_dashboard(page):
    global people_entered_label, people_exited_label, current_count_label, noise_level_label, light_level_label

    people_entered_label = ft.Text(f"People Entered: {people_entered}")
    people_exited_label = ft.Text(f"People Exited: {people_exited}")
    current_count_label = ft.Text(f"Current Count: {current_count}")
    noise_level_label = ft.Text(f"Noise Level: {noise_level}")
    light_level_label = ft.Text(f"Light Level: {light_level}")

    page.add(
        people_entered_label,
        people_exited_label,
        current_count_label,
        noise_level_label,
        light_level_label
    )

    # Start a separate thread for updating the GUI
    threading.Thread(target=update_gui, args=(page,), daemon=True).start()

if __name__ == '__main__':
    # Start Flask in a separate thread
    threading.Thread(target=start_flask, daemon=True).start()
    
    # Start the Flet app
    ft.app(target=create_dashboard)
