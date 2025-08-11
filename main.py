import tkinter as tk
from ui import AutopilotUI

def main():

    root = tk.Tk()

    app = AutopilotUI(root)

    root.mainloop()

if __name__ == "__main__":
    main()