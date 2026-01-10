import pydirectinput
import pygetwindow as gw
import time
import numpy as np
import pytweening

# Define Tween Function

def totally_human_mouse_movement(x, y, duration=1.0):
    start_x, start_y = pydirectinput.position()
    smoothness = 500 # Increase this to make the mouse movement more realistic, it's more resource intensive though
    steps = int(duration * smoothness)

    tween_points = np.linspace(0, 1, steps)

    step_duration = duration / steps

    for point in tween_points:
        tween_val = pytweening.easeInOutQuad(point)

        new_x = int(start_x + (x - start_x) * tween_val)
        new_y = int(start_y + (y - start_y) * tween_val)

        pydirectinput.moveTo(new_x, new_y)

        time.sleep(duration / steps)
    


# Configuration
BANK_OFFSET = 300

# Main Script
print("Searching for Roblox window...")
try:
    roblox_win = gw.getWindowsWithTitle('Roblox')[0]
except IndexError:
    print("Roblox window not found. Please make sure the game is running.")
    exit()

CENTER_X = roblox_win.left + (roblox_win.width // 2)
CENTER_Y = roblox_win.top + (roblox_win.height // 2)

print("Found Roblox window. Starting test...")
print("!!! To stop the script, press Ctrl+C in the terminal. !!!")
time.sleep(2)


roblox_win.activate() # Focus on Roblox
try:
    while True:
        # Bank Left     
        totally_human_mouse_movement(CENTER_X - BANK_OFFSET, CENTER_Y, duration=0.25)
        pydirectinput.doubleClick()
        time.sleep(2) 

        # Bank Right
        totally_human_mouse_movement(CENTER_X + BANK_OFFSET, CENTER_Y, duration=0.25)
        pydirectinput.doubleClick()
        time.sleep(2) 

except KeyboardInterrupt:
    print("\nScript stopped by user.")