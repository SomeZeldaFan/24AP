import tkinter as tk 

class AutopilotUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("24AP")
        self.root.geometry("350x450")  
        self.root.minsize(300, 400)

        self.root.columnconfigure(1, weight=1)

        # Master AP Button
        self.btn_ap_master = tk.Button(self.root, text="AP MASTER - OFF", bg="gray30", font=("Helvetica", 12, "bold"))
        self.btn_ap_master.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # Altitude Control
        self.lbl_alt = tk.Label(self.root, text="ALTITUDE")
        self.ent_alt = tk.Entry(self.root, width=10)
        self.btn_alt_engage = tk.Button(self.root, text="ENGAGE ALT")

        self.lbl_alt.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.ent_alt.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.btn_alt_engage.grid(row=1, column=2, padx=10, pady=5)