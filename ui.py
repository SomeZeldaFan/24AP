import tkinter as tk 

class AutopilotUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("24AP")
        self.root.geometry("350x450")  
        self.root.minsize(300, 400)

        # Main Frame
        main_frame = tk.Frame(self.root, padx= 10, pady= 10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title Label
        title_label = tk.Label(main_frame, text="Autopilot Control Panel", font=("Helvetica", 16))
        title_label.pack(pady=10)

        # Other Widgets will go here

        # Quit Button
        quit_button = tk.Button(main_frame, text="Quit", command=self.root.quit)
        quit_button.pack(side=tk.BOTTOM, pady=10)