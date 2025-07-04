from tkinter import ttk, messagebox

class Style:
    def __init__(self):
        # Style Config
        style = ttk.Style()
        style.configure('Label.TLabel', background='#2b2b2b', foreground='white')
        style.configure('Frame.TFrame', background='#2b2b2b')
        style.configure('FrameLight.TFrame', background='#3f3f3f')
        style.configure('Button1.TButton', background='#585858', font=('Monospace', 12), foreground='white')

        style.configure('Test.TFrame', background='#red')
