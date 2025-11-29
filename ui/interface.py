# Libraries for a progress bar animation
import tkinter as tk # Python's built-in GUI library
from tkinter import ttk # Contains styled wigets like progress bars
import threading # So the UI can run at the same time as the program without interference


#Progress bar shenanagins
root = tk.Tk() # Creates the main GUI window
root.title("Running Program") # Sets the window title
root.geometry("400x120") # Sets the window size

progress_var = tk.IntVar() # A variable that can be liked to a widget
progress = ttk.Progressbar(root, variable=progress_var, maximum=100) # Creates the bar and updates it every time progress_var is set. Full bar is set at 100%
progress.pack(fill="x", expand=True, padx=20, pady=(20, 10)) # Places the widget in the window with padding

status_label = tk.Label(root, text="Starting...", anchor="center") # Displays text in the popup
status_label.pack() # Positions the text in the window

def update_progress(percent):
    progress_var.set(percent)
    root.update_idletasks()
    

def update_status(message):
    status_label.config(text=message)
    root.update_idletasks()

start_button = tk.button(root, text="Run", command=start_scraper)
start_button.pack(pady=5)

root.mainloop()

def start_scraper():
    thread = threading.Thread(target=run)
    thread.start()
