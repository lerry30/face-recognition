from tkinter import ttk
from utils.available_cam import list_available_cameras

class Settings:
    def __init__(self, cont):
        self.cont = cont

    def show(self):
        self.gen()

    def hide(self):
        print('Hide settings')

    def gen(self):
        nav_frame = ttk.Frame(self.cont, style="FrameLight.TFrame")
        nav_frame.grid(column=0, row=0, padx=2, pady=(2, 0), sticky="ew")

        cam_btn = ttk.Button(
            nav_frame,
            text="Camera",
            style="Button1.TButton",
            command=self.cameras
        )
        cam_btn.grid(column=0, row=0)

    # ------------------------ ACTION -------------------------
    
    def cameras(self):
        available_cameras = list_available_cameras(4)
        print(f"{available_cameras} available cameras")

