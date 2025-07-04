import tkinter as tk
from tkinter import ttk, messagebox

import cv2
from PIL import Image, ImageTk

from recog.face_recog import FaceRecognitionSystem
#from utils.timeout import set_timeout
#import time
from pathlib import Path

from utils.available_cam import list_available_cameras

from singleton.camera_manager import CameraManager

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

        self.cap = None

        # video
        self.update_video()

    def show(self):
        try:
            self.close_open_cam()

            camera_manager = CameraManager()
            cam = camera_manager.get_camera()

            if not cam:
                available_cameras = list_available_cameras(4)
                if len(available_cameras) == 0:
                    self.create_label_empty_cam()
                    raise ValueError('Camera not found')
                cam = available_cameras[0]

            n_cam = int(cam)
            self.cap = cv2.VideoCapture(n_cam)

            self.create_buttons()
            self.create_video()
            self.start_video()
        except Exception as e:
            print('Camera error')

    def hide(self):
        print('Hide Face Recognition')

        self.stop_video()
        self.video_label = None

        self.close_open_cam()

        # reset the containers layout
        self.cont.grid_columnconfigure(0, weight=0)
        self.cont.grid_rowconfigure(0, weight=0)

    # ------------------------------ UI's ---------------------------

    def create_label_empty_cam(self):
        self.cont.grid_columnconfigure(0, weight=1)
        self.cont.grid_rowconfigure(0, weight=1)
        ttk.Label(
            self.cont,
            text='No Camera Found.',
            font=('Monospace', 14)
        ).grid(column=0, row=0)

    def create_buttons(self):
        # Create top button frame
        nav_frame = ttk.Frame(self.cont, style="FrameLight.TFrame")
        nav_frame.grid(column=0, row=0, padx=2, pady=4, sticky="ew")

        # Create two buttons at the top
        self.btn_start = ttk.Button(
            nav_frame, 
            text="Start", 
            style='Button1.TButton',
            command=self.start_video
        )
        self.btn_start.grid(column=0, row=0, padx=0, pady=0)
        
        self.btn_stop = ttk.Button(
            nav_frame, 
            text="Stop", 
            style="Button1.TButton",
            command=self.stop_video
        )
        self.btn_stop.grid(column=1, row=0, padx=0, pady=0)

    def create_video(self):
        self.video_label = tk.Label(self.cont, bg='#1e1e1f')
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

    def cont_dimension(self):
        geom = self.root.geometry()
        r_width, r_height = map(int, geom.split('+')[0].split('x'))

        width = r_width - 20 # 20 padding
        height = r_height - (int(r_height * 0.04 + 8) * 2)
        if height <= 0:
            return (0, 0)
        return (width, height)

    def center_video_horizontaly(self, space):
        padding_x = space // 2
        self.video_label.grid_configure(padx=padding_x)

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
        width, height = self.cont_dimension()

        if width <= 0 or height <= 0:
            return frame

        h, w = frame.shape[:2]
        # calculate scaling factor to bit within bounds
        scale = min(width/w, height/h)

        new_w = int(w * scale)
        new_h = int(h * scale)

        self.center_video_horizontaly(width - new_w)

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

    def close_open_cam(self):
        if hasattr(self.cap, 'isOpened') and self.cap.isOpened():
            self.cap.release()

    #---------------------------------- ACTIONS --------------------------------------
    def start_video(self):
        self.running = True
        
    def stop_video(self):
        self.running = False 

