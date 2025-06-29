import tkinter as tk
from tkinter import ttk, messagebox

import cv2
from PIL import Image, ImageTk

from recog.face_recog import FaceRecognitionSystem
#from utils.timeout import set_timeout
#import time
from pathlib import Path

class VideoDisplay:
    def __init__(self, cont, root):
        self.cont = cont
        self.root = root

        self.video_label = None
        self.btn_start = None
        self.btn_stop = None

        self.detected_count = 0
        self.detected_face = None # detected info
        self.running = False

        # initialize face recognition
        self.face_system = None
        self.init_face_system()

        self.cap = cv2.VideoCapture(2)

        # video
        self.update_video()

    def show(self):
        self.create_buttons()
        self.create_video()

        self.start_video()

    def hide(self):
        print('Hide Face Recognition')
        self.stop_video()
        self.video_label = None

    # ------------------------------ UI's ---------------------------

    def create_buttons(self):
        # Create top button frame
        nav_frame = ttk.Frame(self.cont, style="FrameLight.TFrame")
        nav_frame.grid(column=0, row=0, padx=2, pady=2, sticky="ew")

        # Create two buttons at the top
        self.btn_start = ttk.Button(
            nav_frame, 
            text="Start", 
            style='Button1.TButton'
        )
        self.btn_start.grid(column=0, row=0, padx=0, pady=0)
        
        self.btn_stop = ttk.Button(
            nav_frame, 
            text="Stop", 
            style="Button1.TButton"
        )
        self.btn_stop.grid(column=1, row=0, padx=0, pady=0)

    def create_video(self):
        self.video_label = tk.Label(self.cont, bg='#1e1e1e')
        self.video_label.grid(column=0, row=1, sticky="nsew")

    # --------------------------- On something change UIs ------------------------

    def create_detected_face(self):
        if not self.detected_face:
            return

        try:
            directory = Path('../registered_faces')
            name = self.detected_face['name']
            matching_files = list(directory.glob(f"*{name}*"))
            if len(matching_files) == 0:
                raise FileNotFountError('File not found')

            img = Image.open(str(matching_files[0]))
            img = img.resize((200, 200))
            overlay_photo = ImageTk.PhotoImage(img)
        
            self.overlay_label = tk.Label(
                self.root,
                image=overlay_photo,
                bg='#2b2b2b'
            )
            self.overlay_label.image = overlay_photo
            self.overlay_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)
        except Exception as e:
            print('Unable to open image file of face matched')

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
        width = self.video_label.winfo_width() or 800
        height = self.video_label.winfo_height() or 600

        v_width = width if width > 800 else 800
        v_height = height if height > 600 else 600

        h, w = frame.shape[:2]
        # calculate scaling factor to bit within bounds
        scale = min(v_width/w, v_height/h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        return cv2.resize(frame, (new_w, new_h))

    def update_video(self):
        if self.running and self.video_label:
            ret, frame = self.cap.read()
            if ret:
                #---------
                if self.detected_count >= 3:
                    print("More that expected")
                    self.detected_count = self.detected_count + 1
                    max_frame = 40
                    if self.detected_count >= max_frame:
                        self.process_detected()
                        self.detected_count = 0
                else:
                    processed_frame, results = self.face_system.process_frame(frame, f"camera_{0}")
                    if len(results) > 0 and results[0]['confidence'] > 0.6:
                        self.detected_count = self.detected_count + 1
                        self.detected_face = results[0]

                #------------ convert grb to rgb ------------
                n_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #----------- make video responsive ----------
                n_frame = self.aspect_ratio(n_frame)
                
                img = Image.fromarray(n_frame)
                img_tk = ImageTk.PhotoImage(img)

                self.video_label.configure(image=img_tk)
                self.video_label.image = img_tk

        self.after_id = self.root.after(30, self.update_video) # ~33 fps

    def blank_display(self):
        # turn the display to blank
        self.video_label.configure(image='', bg='#333333')
        self.video_label.image = ''
        self.video_label.update()

    def process_detected(self):
        self.blank_display()
        # create pop up face detected
        self.create_detected_face()
    

    #---------------------------------- ACTIONS --------------------------------------
    def start_video(self):
        self.running = True
        
    def stop_video(self):
        self.running = False


