from tkinter import ttk

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
            command=lambda: print('open camera settings')
        )
        cam_btn.grid(column=0, row=0)
