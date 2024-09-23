import mss
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import subprocess
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

regions = [
    {'top': 360, 'left': 920, 'width': 250, 'height': 150},
    {'top': 547, 'left': 246, 'width': 180, 'height': 85},
    {'top': 547, 'left': 17, 'width': 180, 'height': 85},
    {'top': 714, 'left': 247, 'width': 180, 'height': 85},
    {'top': 716, 'left': 18, 'width': 180, 'height': 85},
    {'top': 881, 'left': 249, 'width': 170, 'height': 85},
    {'top': 886, 'left': 20, 'width': 170, 'height': 85}
]

selected_roi = None
dragging = False
drag_start = (0, 0)
screen_snapshot = None
capture_process = None

def capture_screen():
    """Capture the entire screen."""
    global screen_snapshot
    with mss.mss() as sct:
        screen = sct.grab(sct.monitors[0])
        screen_snapshot = np.array(screen)

def draw_rois_with_matplotlib(ax):
    """Draw all regions of interest on the matplotlib figure."""
    for i, region in enumerate(regions):
        color = 'green' if selected_roi != i else 'red'
        rect = Rectangle(
            (region['left'], region['top']),
            region['width'],
            region['height'],
            linewidth=2, edgecolor=color, facecolor='none'
        )
        ax.add_patch(rect)

def on_click(event):
    """Matplotlib mouse click callback to select and drag ROIs."""
    global selected_roi, dragging, drag_start
    x, y = int(event.xdata), int(event.ydata)
    if event.button == 1:  # Left click
        for i, region in enumerate(regions):
            if region['left'] <= x <= region['left'] + region['width'] and region['top'] <= y <= region['top'] + region['height']:
                selected_roi = i
                dragging = True
                drag_start = (x, y)
                break

def on_motion(event):
    """Matplotlib mouse motion callback to drag the selected ROI."""
    global dragging, drag_start
    if dragging and selected_roi is not None:
        dx = int(event.xdata) - drag_start[0]
        dy = int(event.ydata) - drag_start[1]
        regions[selected_roi]['left'] += dx
        regions[selected_roi]['top'] += dy
        drag_start = (int(event.xdata), int(event.ydata))
        update_plot()

def on_release(event):
    """Matplotlib mouse release callback to stop dragging."""
    global dragging
    dragging = False

def save_rois_to_file():
    """Save the regions of interest to a text file."""
    with open('rois.txt', 'w') as file:
        for region in regions:
            file.write(f"{region['top']},{region['left']},{region['width']},{region['height']}\n")

def update_plot():
    """Update the matplotlib plot to reflect changes to the ROIs."""
    plt.cla()  # Clear the current plot
    img_rgb = cv2.cvtColor(screen_snapshot, cv2.COLOR_BGR2RGB)
    plt.imshow(img_rgb)
    draw_rois_with_matplotlib(plt.gca())
    plt.draw()

def show_rois_with_matplotlib():
    """Show ROIs and allow the user to adjust them using matplotlib."""
    global screen_snapshot
    if screen_snapshot is None:
        return

    # Set up matplotlib figure
    fig, ax = plt.subplots()
    img_rgb = cv2.cvtColor(screen_snapshot, cv2.COLOR_BGR2RGB)
    ax.imshow(img_rgb)
    draw_rois_with_matplotlib(ax)

    # Connect the mouse events for interaction
    cid_click = fig.canvas.mpl_connect('button_press_event', on_click)
    cid_motion = fig.canvas.mpl_connect('motion_notify_event', on_motion)
    cid_release = fig.canvas.mpl_connect('button_release_event', on_release)

    plt.title("Adjust ROIs - Close the window when done")
    plt.show()

    # Save the updated ROIs to file
    save_rois_to_file()

def on_show_rois_button_click():
    """Handle the button click event to capture screen and show ROIs."""
    capture_screen()
    show_rois_with_matplotlib()

def on_start_logging_button_click():
    """Start the main.py script to begin logging."""
    global capture_process
    if not os.path.exists('stop_logging.txt'):  # Ensure stop flag is not there
        open('stop_logging.txt', 'w').close()  # Create an empty file
    capture_process = subprocess.Popen(['python', 'main.py'])

def on_stop_logging_button_click():
    """Stop the capture process by creating a stop flag file."""
    if capture_process:
        with open('stop_logging.txt', 'w') as f:
            f.write('stop')
        capture_process.terminate()

# GUI setup using tkinter
root = tk.Tk()
root.title("ROI Viewer")
root.geometry("350x200")

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10)

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

show_rois_button = ttk.Button(frame, text="Show ROIs", command=on_show_rois_button_click, style="TButton")
show_rois_button.pack(fill=tk.X, pady=5)

start_logging_button = ttk.Button(frame, text="Start Logging", command=on_start_logging_button_click, style="TButton")
start_logging_button.pack(fill=tk.X, pady=5)

stop_logging_button = ttk.Button(frame, text="Stop Logging", command=on_stop_logging_button_click, style="TButton")
stop_logging_button.pack(fill=tk.X, pady=5)

instructions_label = tk.Label(frame, text="Close the window after adjusting the ROIs.\nClick Stop to terminate logging.")
instructions_label.pack(pady=10)

root.mainloop()
