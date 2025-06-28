import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk, ThemedStyle

import cv2
from PIL import Image, ImageTk

from recog.face_recog import FaceRecognitionSystem

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition")
        self.root.geometry("800x600")

        # Style Config
        style = ttk.Style()
        style.configure('Label.TLabel', background='#2b2b2b', foreground='white')
        style.configure('Frame.TFrame', background='#2b2b2b')
        style.configure('Button1.TButton', background='#585858', font=('Monospace', 12), foreground='white')

        self.running = False
        self.cap = cv2.VideoCapture(2)
        
        # ui
        self.create_widget()
        # video
        self.update_video()

        # initialize face recognition
        self.face_system = None
        self.init_face_system()

    #------------------------- UI ------------------------------
        
    def create_widget(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.create_title()
        self.create_nav()
        self.create_video()

    def create_title(self):
        title = ttk.Label(
            self.root,
            text='Face Recognition',
            font=('Monospace', 14),
            style='Label.TLabel'
        )
        title.grid(column=0, row=0, columnspan=2, pady=10)

    def create_nav(self):
        # Create top button frame
        nav_frame = ttk.Frame(self.root, style="Frame.TFrame")
        nav_frame.grid(column=0, row=1, padx=10, pady=10, sticky="ew")
        
        # Create two buttons at the top
        self.btnStart = ttk.Button(
            nav_frame, 
            text="Start", 
            style='Button1.TButton',
            command=self.start_video
        )
        self.btnStart.grid(column=0, row=0, padx=0, pady=10)
        
        self.btnStop = ttk.Button(
            nav_frame, 
            text="Stop", 
            style="Button1.TButton",
            command=self.stop_video
        )
        self.btnStop.grid(column=1, row=0, padx=0, pady=10)

    def create_video(self):
        self.video_label = tk.Label(self.root, bg='#1e1e1e')
        self.video_label.grid(column=0, row=2, padx=10, pady=10, sticky='nsew')

    #-------------------------------- PROCESS -----------------------------------------

    def init_face_system(self):
        """Initialize face recognition system"""
        try:
            self.face_system = FaceRecognitionSystem(
                tolerance=0.43,
                model='hog',
                enable_logging=True
            )
            
            print("Face recognition system initialized")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize face recognition: {str(e)}")

    def aspect_ratio(self, frame):
        v_width = self.video_label.winfo_width() or 640
        v_height = self.video_label.winfo_height() or 480

        h, w = frame.shape[:2]
        # calculate scaling factor to bit within bounds
        scale = min(v_width/w, v_height/h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        return cv2.resize(frame, (new_w, new_h))

    def update_video(self):    
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                #---------
                processed_frame, results = self.face_system.process_frame(frame, f"camera_{0}")

                if len(results) > 0:
                    print(results[0]['name'])

                #------------ convert grb to rgb ------------
                n_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #----------- make video responsive ----------
                n_frame = self.aspect_ratio(n_frame)
                
                img = Image.fromarray(n_frame)
                img_tk = ImageTk.PhotoImage(img)

                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk


        self.root.after(30, self.update_video) # ~33 fps


    #---------------------------------- ACTIONS --------------------------------------

    def start_video(self):
        self.running = True
        
    def stop_video(self):
        self.running = False
        
def main():
    root = ThemedTk(theme='equilux');
    app = App(root)
    style = ThemedStyle(root)
    style.configure('Dark.TFrame', background="#2b2b2b")
    root.configure(bg='#2b2b2b')

    def on_closing():
        app.running = False
        if app.cap.isOpened():
            app.cap.release()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
