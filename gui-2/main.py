import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk, ThemedStyle

from style.style_config import Style

from body.video_display import VideoDisplay
from body.settings import Settings

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition")

        self.r_dimension = {'width': 800, 'height': 600}

        self.root.geometry(f"{self.r_dimension['width']}x{self.r_dimension['height']}")

        style = Style()

        self.content_classes = None
        self.current_content = None;
        
        # ui
        self.create_widget()

    #------------------------- UI ------------------------------
        
    def create_widget(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.create_title()
        self.create_nav()
        self.create_main_content()

    def create_title(self):
        max_height = int(self.r_dimension['height'] * 0.04)
        title_frame = ttk.Frame(self.root, height=max_height, style="Frame.TFrame")
        title_frame.grid(column=0, row=0, ipady=4, sticky="ew")

        title = ttk.Label(
            self.root,
            text='Face Recognition',
            font=('Monospace', 14),
            style='Label.TLabel'
        )
        title.grid(column=0, row=0)

    def create_nav(self):
        # Create top button frame
        max_height = int(self.r_dimension['height'] * 0.04)
        nav_frame = ttk.Frame(self.root, height=max_height, style="Frame.TFrame")
        nav_frame.grid(column=0, row=1, ipady=4, sticky="ew")
        
        self.btn_video = ttk.Button(
            nav_frame, 
            text="Face Recog",
            style='Button1.TButton',
            command=lambda: self.switch_content('video')
        )
        self.btn_video.grid(column=0, row=0, padx=10, pady=0)
        
        self.btn_settings = ttk.Button(
            nav_frame, 
            text="Settings", 
            style="Button1.TButton",
            command=lambda: self.switch_content('settings')
        )
        self.btn_settings.grid(column=1, row=0, padx=0, pady=0)

    def create_main_content(self):
        self.main_content = ttk.Frame(self.root, style="FrameLight.TFrame")
        self.main_content.grid(column=0, row=2, padx=10, pady=(0, 10), sticky='nsew')
        # default grid layout
        # self.main_content.grid_columnconfigure(0, weight=1)
        # self.main_content.grid_rowconfigure(0, weight=1)

        self.content_classes = {
            'video': VideoDisplay(self.main_content, self.root),
            'settings': Settings(self.main_content)
        }

        # By default video display should be initialized
        self.content_classes['video'].show()
        self.current_content = 'video'

    #---------------------------------- ACTIONS --------------------------------------

    def switch_content(self, content_name):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        self.content_classes[self.current_content].hide()
        self.content_classes[content_name].show()
        self.current_content = content_name


def main():
    root = ThemedTk(theme='equilux');
    app = App(root)
    style = ThemedStyle(root)
    style.configure('Dark.TFrame', background="#2b2b2b")
    root.configure(bg='#2b2b2b')

    def on_closing():
        try:
            video_display = app.content_classes['video']
            video_display.running = False
            if video_display.cap.isOpened():
                video_display.cap.release()
        except Exception as e:
            print("Closing OpenCV error")
        finally:
            root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()



"""
def detected(self):
    #if hasattr(self, 'after_id'):
    #    self.root.after_cancel(self.after_id)
    #-------------- start timeout ------------- 
    timeout = 5
    def restart():
        time.sleep(timeout)
        print(f"Found {face['name']}");
        # delete detected face pop up
        self.overlay_label.destroy()
    result, error = set_timeout(restart, timeout)
"""

