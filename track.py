import csv
import os
import threading
import time
import pyautogui
import pygetwindow as gw
import win32gui

class MouseTracker:
    def __init__(self):
        self.user_id = input("Enter your User ID: ")
        self.daily_tracking = {}
        self.last_active_window = None
        self.x, self.y = pyautogui.position()
        self.idle_time_limit = 0 
        self.last_movement = time.time()
        self.date_str = time.strftime("%Y-%m-%d")
        self.prev_idle = 0
        self.start_time = None  
        self.end_time = None
        self.csv_file = f"User_{self.user_id}_tracking_report.csv"
        
        if not os.path.exists(self.csv_file):
            self.write_csv_header()
        
    def get_active_window_title(self):
        try:
            active_window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            return active_window_title
        except Exception as e:
            print(f"Error getting active window title: {e}")
            return ""
    
    def calculate_idle(self, current_time):
        
        idle_time = current_time - self.last_movement

        if idle_time > 240:
            self.daily_tracking.setdefault(self.date_str, {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()})
            self.daily_tracking[self.date_str]['idle_time'] += idle_time - self.prev_idle
        else:
            self.daily_tracking.setdefault(self.date_str, {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()})
            self.daily_tracking[self.date_str]['active_time'] += idle_time - self.prev_idle
            
        self.prev_idle = idle_time
            
    def track_mouse_movement(self):
        
        while True:
            self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
            x,y = pyautogui.position()
            
            active_window_title = self.get_active_window_title()
            if self.last_active_window !=active_window_title:
                if self.last_active_window is not None:
                    self.daily_tracking.setdefault(self.date_str, {'idle_time': 0, 'active_time': 0, 'websites_and_apps': set()})
                    self.daily_tracking[self.date_str]['websites_and_apps'].add(self.last_active_window)
                
                self.last_active_window = active_window_title
            
            if self.date_str not in self.daily_tracking:
                self.daily_tracking[self.date_str] = {'idle_time': 0, 'active_time': 0,'websites_and_apps': set()}
            
            if self.x == x and self.y == y:
                self.calculate_idle(time.time())
            else:
                self.last_movement = time.time()
                self.prev_idle = 0
            self.x = x
            self.y = y
    
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
    
    tracker = MouseTracker()

    print("Mouse movement tracking started. Press Ctrl+C to stop.")
    try:
        tracker.track_mouse_movement()
    except KeyboardInterrupt:
        print(tracker.daily_tracking)
        tracker.save_tracking_data()  # Save the tracking data when the program exits
        print("Mouse movement tracking stopped.")
        
if __name__ == "__main__":
    main()