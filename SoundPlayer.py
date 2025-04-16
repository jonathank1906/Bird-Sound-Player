import tkinter as tk
from tkinter import messagebox, filedialog
import pygame
import threading
from datetime import datetime
import time as pytime
import subprocess  # For pinging

# Initialize pygame mixer
pygame.mixer.init()

class MP3SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Scheduler")

        # Variables
        self.start_time = tk.StringVar()
        self.end_time = tk.StringVar()
        self.is_playing = False
        self.play_thread = None
        self.stop_thread = None
        self.running = False  # To control the stop thread

        # GUI Layout
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="MP3 File Path").grid(row=0, column=0)
        self.file_path = tk.Entry(self.root, width=40)
        self.file_path.grid(row=0, column=1)

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)

        tk.Label(self.root, text="Start Time (HH:MM)").grid(row=1, column=0)
        tk.Entry(self.root, textvariable=self.start_time).grid(row=1, column=1)

        tk.Label(self.root, text="End Time (HH:MM)").grid(row=2, column=0)
        tk.Entry(self.root, textvariable=self.end_time).grid(row=2, column=1)

        self.start_button = tk.Button(self.root, text="Start Scheduling", command=self.start_scheduling)
        self.start_button.grid(row=3, column=0, columnspan=2)

        self.stop_button = tk.Button(self.root, text="Stop Scheduling", command=self.stop_scheduling)
        self.stop_button.grid(row=4, column=0, columnspan=2)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if file:
            self.file_path.delete(0, tk.END)
            self.file_path.insert(0, file)

    def start_scheduling(self):
        if not self.file_path.get() or not self.start_time.get() or not self.end_time.get():
            messagebox.showerror("Error", "Please provide all fields!")
            return

        try:
            self.start_time_value = datetime.strptime(self.start_time.get(), "%H:%M").time()
            self.end_time_value = datetime.strptime(self.end_time.get(), "%H:%M").time()

            if self.start_time_value >= self.end_time_value:
                messagebox.showerror("Error", "End time must be later than start time!")
                return

            self.running = True
            self.play_thread = threading.Thread(target=self.manage_playback, daemon=True)
            self.play_thread.start()

            self.stop_thread = threading.Thread(target=self.monitor_stop_time, daemon=True)
            self.stop_thread.start()

            messagebox.showinfo("Info", "Scheduling started.")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM.")

    def stop_scheduling(self):
        self.running = False
        if self.is_playing:
            self.stop_music()
        messagebox.showinfo("Info", "Scheduling stopped.")

    def manage_playback(self):
        while self.running:
            now = datetime.now().time()

            if self.start_time_value <= now < self.end_time_value and not self.is_playing:
                self.play_music()

            if self.is_playing and not pygame.mixer.music.get_busy():
                print("Music finished. Checking if within time range to restart.")
                if self.start_time_value <= now < self.end_time_value:
                    self.play_music()

            pytime.sleep(1)

    def monitor_stop_time(self):
        while self.running:
            now = datetime.now().time()

            if now >= self.end_time_value and self.is_playing:
                self.stop_music()

            pytime.sleep(1)

    def play_music(self):
        try:
            # Send a ping before playing music
            try:
                subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL)
                print(f"Ping sent before music playback at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"Ping failed before play: {e}")

            pygame.mixer.music.load(self.file_path.get())
            pygame.mixer.music.play(-1)
            self.is_playing = True
            print(f"Music started at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            messagebox.showerror("Error", f"Error playing music: {e}")

    def stop_music(self):
        try:
            # Send a ping before stopping music
            try:
                subprocess.run(["ping", "-c", "1", "8.8.8.8"], stdout=subprocess.DEVNULL)
                print(f"Ping sent before stopping music at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                print(f"Ping failed before stop: {e}")

            pygame.mixer.music.stop()
            self.is_playing = False
            print(f"Music stopped at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping music: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MP3SchedulerApp(root)
    root.mainloop()
