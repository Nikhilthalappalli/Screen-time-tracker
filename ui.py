import csv
import os
import threading
import time
import pyautogui
import pygetwindow as gw
import win32gui
import tkinter as tk
from tkinter import Entry, Button, Label, messagebox

class MouseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Time Tracker")
        self.root.geometry("400x250")  
        
        self.user_id_label = Label(root, text="Enter your User ID:")
        self.user_id_label.pack(pady=10)
        
        self.user_id_entry = Entry(root, width=20, font=("Helvetica", 14))
        self.user_id_entry.pack(pady=10)
        
        self.start_button = Button(root, text="Start Tracking", command=self.start_tracking, width=20, height=2, font=("Helvetica", 14))
        self.start_button.pack(pady=10)
        
        self.stop_button = Button(root, text="Stop Tracking", command=self.stop_tracking, width=20, height=2, font=("Helvetica", 14), state=tk.DISABLED)
        self.stop_button.pack(pady=10)
        
        
        self.status_label = Label(root, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)
        
        self.daily_tracking = {}
        self.last_active_window = None
        self.x, self.y = pyautogui.position()
        self.last_movement = time.time()
        self.date_str = time.strftime("%Y-%m-%d")
        self.prev_idle = 0
        self.idle_time_limit = 240
        self.start_time = None  
        self.end_time = None
        self.csv_file = ""
        self.tracking = False
        self.tracking_type = ""  
        
    def get_active_window_title(self):
        try:
            active_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            return active_window_title
        except Exception as e:
            print(f"Error getting active window title: {e}")
            return ""
    
    def calculate_idle(self, current_time):
        idle_time = current_time - self.last_movement

        if idle_time > self.idle_time_limit:
            if self.tracking_type != "Idle Time":
                self.tracking_type = "Idle Time"
                self.status_label.config(text="Idle Time")
            self.daily_tracking.setdefault(self.date_str, {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()})
            self.daily_tracking[self.date_str]['idle_time'] += idle_time - self.prev_idle
        else:
            if self.tracking_type != "Active Time":
                self.tracking_type = "Active Time"
                self.status_label.config(text="Active Time")
            self.daily_tracking.setdefault(self.date_str, {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()})
            self.daily_tracking[self.date_str]['active_time'] += idle_time - self.prev_idle
            
        self.prev_idle = idle_time
            
    def track_mouse_movement(self):
        while self.tracking:
            self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
            x, y = pyautogui.position()
            
            active_window_title = self.get_active_window_title()
            if self.last_active_window != active_window_title:
                if self.last_active_window is not None:
                    self.daily_tracking.setdefault(self.date_str, {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()})
                    self.daily_tracking[self.date_str]['websites_and_apps'].add(self.last_active_window)
                
                self.last_active_window = active_window_title
            
            if self.date_str not in self.daily_tracking:
                self.daily_tracking[self.date_str] = {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()}
            
            if self.x == x and self.y == y:
                self.calculate_idle(time.time())
            else:
                self.last_movement = time.time()
                self.prev_idle = 0
            self.x = x
            self.y = y
    
    def start_tracking(self):
        self.user_id = self.user_id_entry.get()
        
        if not self.user_id or not self.user_id.strip():
            messagebox.showerror("Error", "Please enter a valid User ID.")
            return
        
        self.csv_file = f"User_{self.user_id}_tracking_report.csv"
        
        if not os.path.exists(self.csv_file):
            self.write_csv_header()
        
        self.tracking = True
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Tracking started")
        
        self.tracking_type = "Active Time"  # Initialize tracking type
        self.status_label.config(text="Active Time")
        
        self.track_thread = threading.Thread(target=self.track_mouse_movement)
        self.track_thread.start()

    def stop_tracking(self):
        self.tracking = False
        self.stop_button.config(state=tk.DISABLED)
        self.save_tracking_data()
        self.status_label.config(text="Tracking stopped, details saved")
        
    def write_csv_header(self):
        with open(self.csv_file, "w", newline="") as csvfile:
            fieldnames = ["Date", "Start Time", "End Time", "Active Time (seconds)", "Idle Time (seconds)", "Total Time(Seconds)", "Websites and Apps"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
    def save_tracking_data(self):
        self.end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.csv_file, "a", newline="") as csvfile:
            fieldnames = ["Date","Start Time","End Time", "Active Time (seconds)", "Idle Time (seconds)" ,"Total Time(Seconds)", "Websites and Apps"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
            for date_str, data in self.daily_tracking.items():
                writer.writerow({
                    "Date": date_str,
                    "Start Time": self.start_time,
                    "End Time": self.end_time,
                    "Active Time (seconds)": data['active_time'],
                    "Idle Time (seconds)": data['idle_time'],
                    "Total Time(Seconds)": data['active_time']+data["idle_time"],
                    "Websites and Apps": ", ".join(data['websites_and_apps'])
                })

def main():
    root = tk.Tk()
    tracker = MouseTracker(root)
    root.mainloop()
        
if __name__ == "__main__":
    main()
