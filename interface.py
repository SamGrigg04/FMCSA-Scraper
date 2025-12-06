from queue import Queue
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry # type: ignore
from datetime import date
from dateutil.relativedelta import relativedelta
from threading import Thread # So the UI can run at the same time as the program without interference
from utils.config_utils import save_config

# Switches between frames
def switch_frame(frame, lastFrame=None):
    if frame == "back":
        if isinstance(lastFrame, str):
            frameObject = globals().get(f"{lastFrame}Frame")
        else:
            frameObject = lastFrame
        frameObject.grid_remove()
        errorMessageLabel.grid_remove()
        nxtbtn.grid(column=0, row=4, sticky=(tk.S, tk.E))
        quitbtn.grid(column=1, row=4, sticky=(tk.S, tk.E))
        backbtn.grid_remove()
        startbtn.grid_remove()
        initFrame.grid()
        return
    initFrame.grid_remove()
    nxtbtn.grid_remove()
    if frame == "state":
        stateFrame.grid()
        backbtn.grid(column=0, row=10, sticky=(tk.S, tk.E))
        startbtn.grid(column=1, row=10, sticky=(tk.S, tk.E))
        quitbtn.grid(column=2, row=10, sticky=(tk.S, tk.E))
        _validate_state()
        return
    if frame == "cancel":
        cancelFrame.grid()
        backbtn.grid(column=0, row=10, sticky=(tk.S, tk.E))
        startbtn.grid(column=1, row=10, sticky=(tk.S, tk.E))
        quitbtn.grid(column=2, row=10, sticky=(tk.S, tk.E))
        validate_cancel()
        return
    if frame == "renew":
        renewFrame.grid()
        backbtn.grid(column=0, row=10, sticky=(tk.S, tk.E))
        startbtn.grid(column=1, row=10, sticky=(tk.S, tk.E))
        quitbtn.grid(column=2, row=10, sticky=(tk.S, tk.E))
        validate_renew()
        return
    if frame == "newVenture":
        newVentureFrame.grid()
        backbtn.grid(column=0, row=10, sticky=(tk.S, tk.E))
        startbtn.grid(column=1, row=10, sticky=(tk.S, tk.E))
        quitbtn.grid(column=2, row=10, sticky=(tk.S, tk.E))
        validate_new_venture()
        return
    if frame == "loading":
        if isinstance(lastFrame, str):
            frameObject = globals().get(f"{lastFrame}Frame")
        else:
            frameObject = lastFrame
        frameObject.grid_remove()
        errorMessageLabel.grid_remove()
        quitbtn.grid(column=0, row=10, sticky=(tk.S))
        nxtbtn.grid_remove()
        backbtn.grid_remove()
        startbtn.grid_remove()
        loadingFrame.grid()
        run_program(lastFrame)

    else:
        raise ValueError("Something went wrong")

def run_program(lastFrame):
    # Validate one more time before running things
    valid_frames = {"state", "cancel", "renew", "newVenture"}
    if lastFrame not in valid_frames:
        errorMessage.set("You found a bug!")
        errorMessageLabel.grid(row=0, column=0, sticky=(tk.S, tk.W))
        return

    validators = {
        "state": _validate_state,
        "cancel": validate_cancel,
        "renew": validate_renew,
        "newVenture": validate_new_venture,
    }

    validator = validators.get(lastFrame)
    if validator:
        validator()

    if "disabled" not in startbtn.state():
        startbtn.state(["disabled"]) # So the user can't double run
        updated_values = {
            "mode": option.get(),
            "spreadsheet_id": stateSheetID.get() or cancelSheetID.get() or renewSheetID.get() or newVentureSheetID.get(),
            "sheet_name": stateSheetName.get() or cancelSheetName.get() or renewSheetName.get() or newVentureSheetName.get(),
            "state": stateSheetState.get().upper() if option.get() == "state" else None,
            "start_date": cancelSheetStartDateEntry.get_date().isoformat() if option.get() == "cancel" else renewSheetStartDateEntry.get_date().isoformat() if option.get() == "renew" else None,
            "end_date": cancelSheetEndDateEntry.get_date().isoformat() if option.get() == "cancel" else renewSheetEndDateEntry.get_date().isoformat() if option.get() == "renew" else None,
        }
        save_config(updated_values)
        
        from main import main as run_main
        global scraper_thread
        scraper_thread = Thread(target=run_main, args=(progress_queue,), daemon=True)
        scraper_thread.start()
    return

def on_close():
    if scraper_thread and scraper_thread.is_alive():
        if not messagebox.askyesno(
            "Confirm exit", 
            "Scraper is still running. Exit anyway?"
            ):
                return
    root.destroy()
    
# Enable the next button upon selecting an option
def _on_option_change(*args):
    if option.get():
        nxtbtn.state(["!disabled"])
    else:
        nxtbtn.state(["disabled"])
    
# Validates the state inputs
def _validate_state(*args):
    if option.get() == "state":
        print("validating")
        if len(stateSheetState.get()) > 2:
            errorMessage.set("State must be two letters (e.g UT, VA)")
            errorMessageLabel.grid(column=0, row=9, sticky=(tk.W, tk.S))
            startbtn.state(["disabled"])
            return
        elif len(stateSheetState.get()) == 2:
            errorMessageLabel.grid_remove()
            if len(stateSheetID.get()) > 0 and len(stateSheetName.get()) > 0:
                startbtn.state(["!disabled"])
            else:
                startbtn.state(["disabled"])
        else:
            startbtn.state(["disabled"])
    else:
        print("BIG ERROR BRO WHAT HAPPENED??? (state)")
    return

def validate_cancel(*args):
    if option.get() == "cancel":
        start_date = cancelSheetStartDateEntry.get_date()
        end_date = cancelSheetEndDateEntry.get_date()
        if end_date < start_date:
            errorMessage.set("Start date must be before end date")
            errorMessageLabel.grid(column=0, row=9, sticky=(tk.W, tk.S))
            startbtn.state(["disabled"])
            return
        elif end_date >= start_date:
            errorMessageLabel.grid_remove()
            if len(cancelSheetID.get()) > 0 and len(cancelSheetName.get()) > 0:
                startbtn.state(["!disabled"])
            else:
                startbtn.state(["disabled"])
        else:
            startbtn.state(["disabled"])
    else:
        print("BIG ERROR BRO WHAT HAPPENED??? (cancel)")
    return

def validate_renew(*args):
    if option.get() == "renew":
        start_date = renewSheetStartDateEntry.get_date()
        end_date = renewSheetEndDateEntry.get_date()
        if end_date < start_date:
            errorMessage.set("Start date must be before end date")
            errorMessageLabel.grid(column=0, row=9, sticky=(tk.W, tk.S))
            startbtn.state(["disabled"])
            return
        elif end_date >= start_date:
            errorMessageLabel.grid_remove()
            if len(renewSheetID.get()) > 0 and len(renewSheetName.get()) > 0:
                startbtn.state(["!disabled"])
            else:
                startbtn.state(["disabled"])
        else:
            startbtn.state(["disabled"])
    else:
        print("BIG ERROR BRO WHAT HAPPENED??? (renew)")
    return

def validate_new_venture(*args):
    if option.get() == "newVenture":
        errorMessageLabel.grid_remove()
        if len(newVentureSheetID.get()) > 0 and len(newVentureSheetName.get()) > 0:
                startbtn.state(["!disabled"])
        else:
            startbtn.state(["disabled"])
    return

def poll_queue():
    while not progress_queue.empty():
        progress, message = progress_queue.get()
        loadingProgress.set(progress)
        loadingMessage.config(text=message)
    root.after(100, poll_queue)


# need these for stuff
scraper_thread = None
progress_queue = Queue()

# Create the root
root = tk.Tk()
root.title("SAFER Data Scraper")
root.geometry("+50+50")
root.resizable(False, False) # now I don't have to worry about resizing garbage

# Make all the frames
content = ttk.Frame(root)
initFrame = ttk.Frame(content)
stateFrame = ttk.Frame(content)
cancelFrame = ttk.Frame(content)
renewFrame = ttk.Frame(content)
newVentureFrame = ttk.Frame(content)
loadingFrame = ttk.Frame(content)

# Radio buttons for the inital frame
option = tk.StringVar()
btn1 = ttk.Radiobutton(initFrame, text="Update data for a specific state", variable=option, value="state")
btn2 = ttk.Radiobutton(initFrame, text="Get everyone who is cancelling within the specified timeframe", variable=option, value="cancel")
btn3 = ttk.Radiobutton(initFrame, text="Get everyone who is renewing withing the specified timeframe", variable=option, value="renew")
btn4 = ttk.Radiobutton(initFrame, text="Get all the new ventures", variable=option, value="newVenture")

# Widgets for the state frame
stateSheetIDLabel = ttk.Label(stateFrame, text="Spreadsheet ID: ")
stateSheetID = tk.StringVar()
stateSheetIDEntry = ttk.Entry(stateFrame, textvariable=stateSheetID)
stateSheetNameLabel = ttk.Label(stateFrame, text="Spreadsheet Name: ")
stateSheetName = tk.StringVar()
stateSheetNameEntry = ttk.Entry(stateFrame, textvariable=stateSheetName)
stateSheetStateLabel = ttk.Label(stateFrame, text="State Abbreviation: ")
stateSheetState = tk.StringVar()
stateSheetStateEntry = ttk.Entry(stateFrame, textvariable=stateSheetState)

# Need this for the next two
default = date.today() + relativedelta(months=+1)

# Widgets for the cancel frame
cancelSheetIDLabel = ttk.Label(cancelFrame, text="Spreadsheet ID: ")
cancelSheetID = tk.StringVar()
cancelSheetIDEntry = ttk.Entry(cancelFrame, textvariable=cancelSheetID)
cancelSheetNameLabel = ttk.Label(cancelFrame, text="Spreadsheet Name: ")
cancelSheetName = tk.StringVar()
cancelSheetNameEntry = ttk.Entry(cancelFrame, textvariable=cancelSheetName)
cancelSheetStartDateLabel = ttk.Label(cancelFrame, text="Starting Date: ")
cancelSheetStartDate = tk.StringVar()
cancelSheetStartDateEntry = DateEntry(cancelFrame, textvariable=cancelSheetStartDate, date_pattern="mm-dd-yyyy")
cancelSheetEndDateLabel = ttk.Label(cancelFrame, text="Ending Date: ")
cancelSheetEndDate = tk.StringVar()
cancelSheetEndDateEntry = DateEntry(cancelFrame, textvariable=cancelSheetEndDate, date_pattern="mm-dd-yyyy")
cancelSheetEndDateEntry.set_date(default)

# Widgets for the renewal frame
renewSheetIDLabel = ttk.Label(renewFrame, text="Spreadsheet ID: ")
renewSheetID = tk.StringVar()
renewSheetIDEntry = ttk.Entry(renewFrame, textvariable=renewSheetID)
renewSheetNameLabel = ttk.Label(renewFrame, text="Spreadsheet Name: ")
renewSheetName = tk.StringVar()
renewSheetNameEntry = ttk.Entry(renewFrame, textvariable=renewSheetName)
renewSheetStartDateLabel = ttk.Label(renewFrame, text="Starting Date: ")
renewSheetStartDate = tk.StringVar()
renewSheetStartDateEntry = DateEntry(renewFrame, textvariable=renewSheetStartDate, date_pattern="mm-dd-yyyy")
renewSheetEndDateLabel = ttk.Label(renewFrame, text="Ending Date: ")
renewSheetEndDate = tk.StringVar()
renewSheetEndDateEntry = DateEntry(renewFrame, textvariable=renewSheetEndDate, date_pattern="mm-dd-yyyy")
renewSheetEndDateEntry.set_date(default)

# Widgets for the new venture frame
newVentureSheetIDLabel = ttk.Label(newVentureFrame, text="Spreadsheet ID: ")
newVentureSheetID = tk.StringVar()
newVentureSheetIDEntry = ttk.Entry(newVentureFrame, textvariable=newVentureSheetID)
newVentureSheetNameLabel = ttk.Label(newVentureFrame, text="Spreadsheet Name: ")
newVentureSheetName = tk.StringVar()
newVentureSheetNameEntry = ttk.Entry(newVentureFrame, textvariable=newVentureSheetName)

# Widgets for the loading frame
loadingProgress = tk.IntVar()
progressBar = ttk.Progressbar(loadingFrame, variable=loadingProgress, mode="determinate", length=500)
loadingMessage = tk.Label(loadingFrame, text="Starting...")

# Buttons at the bottom
backbtn = ttk.Button(content, text="Back", command=lambda: (switch_frame("back", option.get())))
nxtbtn = ttk.Button(content, text="Next", command=lambda: (switch_frame(option.get())), state=["disabled"])
startbtn = ttk.Button(content, text="Start", command=lambda: (switch_frame("loading", option.get())), state=["disabled"])
quitbtn = ttk.Button(content, text="Quit", command=on_close)
root.protocol("WM_DELETE_WINDOW", on_close)
errorMessage = tk.StringVar()
errorMessageLabel = ttk.Label(content)
errorMessageLabel["textvariable"] = errorMessage
errorMessageLabel["foreground"] = "red"


# Add functionality to buttons/entries
option.trace_add("write", _on_option_change)

stateSheetID.trace_add("write", _validate_state)
stateSheetName.trace_add("write", _validate_state)
stateSheetState.trace_add("write", _validate_state)

cancelSheetID.trace_add("write", validate_cancel)
cancelSheetName.trace_add("write", validate_cancel)
cancelSheetStartDateEntry.bind("<<DateEntrySelected>>", validate_cancel)
cancelSheetEndDateEntry.bind("<<DateEntrySelected>>", validate_cancel)

renewSheetID.trace_add("write", validate_renew)
renewSheetName.trace_add("write", validate_renew)
renewSheetStartDateEntry.bind("<<DateEntrySelected>>", validate_renew)
renewSheetEndDateEntry.bind("<<DateEntrySelected>>", validate_renew)

newVentureSheetID.trace_add("write", validate_new_venture)
newVentureSheetName.trace_add("write", validate_new_venture)


# Initial Frame Layout
content.grid(padx=10, pady=10)
initFrame.grid()
btn1.grid(column=0, row=0, sticky=(tk.N, tk.W))
btn2.grid(column=0, row=1, sticky=(tk.N, tk.W))
btn3.grid(column=0, row=2, sticky=(tk.N, tk.W))
btn4.grid(column=0, row=3, sticky=(tk.N, tk.W))
nxtbtn.grid(column=0, row=4, sticky=(tk.S, tk.E))
quitbtn.grid(column=1, row=4, sticky=(tk.S, tk.E))

# State Frame Layout
stateFrame.grid()
stateSheetIDLabel.grid(column=0, row=0, sticky=(tk.E, tk.S), pady=2)
stateSheetIDEntry.grid(column=1, row=0, pady=5)
stateSheetIDEntry["width"] = 30
stateSheetNameLabel.grid(column=0, row=1, sticky=(tk.E, tk.S), pady=2)
stateSheetNameEntry.grid(column=1, row=1, pady=5)
stateSheetNameEntry["width"] = 30
stateSheetStateLabel.grid(column=0, row=2, sticky=(tk.E, tk.S), pady=2)
stateSheetStateEntry.grid(column=1, row=2, pady=5)
stateSheetStateEntry["width"] = 30
stateFrame.grid_remove()

# Cancel Frame Layout
cancelFrame.grid()
cancelSheetIDLabel.grid(column=0, row=0, sticky=(tk.E, tk.S), pady=2)
cancelSheetIDEntry.grid(column=1, row=0, pady=5)
cancelSheetIDEntry["width"] = 30
cancelSheetNameLabel.grid(column=0, row=1, sticky=(tk.E, tk.S), pady=2)
cancelSheetNameEntry.grid(column=1, row=1, pady=5)
cancelSheetNameEntry["width"] = 30
cancelSheetStartDateLabel.grid(column=0, row=3, sticky=(tk.E, tk.S), pady=2)
cancelSheetStartDateEntry.grid(column=1, row=3, pady=5, sticky=(tk.W))
cancelSheetEndDateLabel.grid(column=0, row=4, sticky=(tk.E, tk.S), pady=2)
cancelSheetEndDateEntry.grid(column=1, row=4, pady=5, sticky=(tk.W))
cancelFrame.grid_remove()

# Renewal Frame Layout
renewFrame.grid()
renewSheetIDLabel.grid(column=0, row=0, sticky=(tk.E, tk.S), pady=2)
renewSheetIDEntry.grid(column=1, row=0, pady=5)
renewSheetIDEntry["width"] = 30
renewSheetNameLabel.grid(column=0, row=1, sticky=(tk.E, tk.S), pady=2)
renewSheetNameEntry.grid(column=1, row=1, pady=5)
renewSheetNameEntry["width"] = 30
renewSheetStartDateLabel.grid(column=0, row=3, sticky=(tk.E, tk.S), pady=2)
renewSheetStartDateEntry.grid(column=1, row=3, pady=5, sticky=(tk.W))
renewSheetEndDateLabel.grid(column=0, row=4, sticky=(tk.E, tk.S), pady=2)
renewSheetEndDateEntry.grid(column=1, row=4, pady=5, sticky=(tk.W))
renewFrame.grid_remove()

# New Venture Frame Layout
newVentureFrame.grid()
newVentureSheetIDLabel.grid(column=0, row=0, sticky=(tk.E, tk.S), pady=2)
newVentureSheetIDEntry.grid(column=1, row=0, pady=5)
newVentureSheetIDEntry["width"] = 30
newVentureSheetNameLabel.grid(column=0, row=1, sticky=(tk.E, tk.S), pady=2)
newVentureSheetNameEntry.grid(column=1, row=1, pady=5)
newVentureSheetNameEntry["width"] = 30
newVentureFrame.grid_remove()

# Loading Frame Layout
loadingFrame.grid()
progressBar.grid(row=0)
loadingMessage.grid(row=1)
loadingFrame.grid_remove()


poll_queue()
root.mainloop()

