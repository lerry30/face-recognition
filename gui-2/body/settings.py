import tkinter as tk
from tkinter import ttk
from utils.available_cam import list_available_cameras

from singleton.camera_manager import CameraManager

class Settings:
    def __init__(self, cont):
        self.cont = cont
        self.selected_cam = None

    def show(self):
        self.gen()

    def hide(self):
        print('Hide settings')

    def gen(self):
        self.cont.grid_columnconfigure(0, weight=1)
        self.cont.grid_rowconfigure(1, weight=1)

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

        if len(available_cameras) == 0:
            return

        group_radio_buttons = ttk.Frame(self.cont, style="FrameLight.TFrame")
        group_radio_buttons.grid(column=0, row=1, padx=2, pady=2, sticky="nsew")

        ttk.Label(
            group_radio_buttons,
            text='Select Camera',
            font=('Monospace', 12)
        ).grid(column=0, row=0, pady=10)

        camera_manager = CameraManager()
        cam = camera_manager.get_camera() or available_cameras[0]
        self.selected_cam = tk.StringVar(value=cam)

        for i,val in enumerate(available_cameras):
            ttk.Radiobutton(
                group_radio_buttons, 
                text=f"Camera {val}", 
                variable=self.selected_cam, 
                value=val, 
                style="RadioBtn.TRadiobutton",
                command=self.change_cam
            ).grid(column=0, row=i+1, pady=2)
    
    def change_cam(self):
        cam = self.selected_cam.get()
        camera_manager = CameraManager()
        camera_manager.set_camera(cam)




