import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time
from datetime import datetime
import os

from recog.face_recog import FaceRecognitionSystem

"""
    Methods:
        setup_window
        init_face_system
        create_widgets
        create_control_panel(self, parent)
        create_video_display(self, parent)
        create_status_panel(self, parent)
        create_side_panel
        on_tolerance_change(self, value)
        toggle_appearance_mode
        start_camera
        stop_camera
        update_video
        process_frame_with_recognition(self, frame)
        prepare_frame_for_display(self, frame)
        update_status(self, recognition_results)
        register_face_from_camera
        register_face_from_file
        register_face_from_path(self, image_path, name)
        get_name_dialog
        update_faces_list
        delete_selected_face
        toggle_fullscreen(self, event=None)
        on_closing
"""

class ModernFaceRecognitionGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Face recognition system
        self.face_system = None
        self.init_face_system()
        
        # Camera variables
        self.cap = None
        self.is_running = False
        self.current_frame = None
        
        # GUI variables
        self.video_label = None
        self.status_var = ctk.StringVar(value="Ready")
        self.fps_var = ctk.StringVar(value="FPS: 0")
        self.face_count_var = ctk.StringVar(value="Registered: 0")
        self.tolerance_var = ctk.DoubleVar(value=0.6)
        
        # Create GUI elements
        self.create_widgets()
        
        # Start camera automatically if not in registration mode
        self.start_camera()
    
    def setup_window(self):
        """Setup main window with CustomTkinter styling"""
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")  # "light" or "dark"
        ctk.set_default_color_theme("dark-blue")  # "blue", "green", "dark-blue"
        
        self.root.title("Face Recognition System")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size
        if screen_width <= 1024:  # Small screens
            self.root.attributes('-fullscreen', True)
            self.fullscreen = True
        else:
            window_width = min(1400, screen_width - 100) # 100 for gap
            window_height = min(900, screen_height - 100)
            self.root.geometry(f"{window_width}x{window_height}")
            self.fullscreen = False
        
        # Center window
        if not self.fullscreen:
            x = (screen_width - window_width) // 2 # // round to down to the nearest whole number
            y = (screen_height - window_height) // 2
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Bind escape key to toggle fullscreen
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # Make window resizable
        self.root.resizable(True, True)
    
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
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Configure grid weights for responsive design

        """
        grid_columnconfigure(0, weight=3): Column 0 gets 3/4 of available width
        grid_columnconfigure(1, weight=1): Column 1 gets 1/4 of available width
        grid_rowconfigure(1, weight=1): Row 1 expands to fill available height
        Higher weight values take more space when window is resized
        """

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self.root, 
            text="Face Recognition System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="ew")
        
        # Main content frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Video display area
        self.create_video_display(main_frame)
        
        # Status panel
        self.create_status_panel(main_frame)
        
        # Side panel
        self.create_side_panel()
    
    def create_control_panel(self, parent):
        """Create top control panel"""
        control_frame = ctk.CTkFrame(parent)
        control_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        control_frame.grid_columnconfigure(4, weight=1)
        
        # Control buttons
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="Start Camera",
            command=self.start_camera,
            width=120,
            height=35
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="Stop Camera",
            command=self.stop_camera,
            width=120,
            height=35
        )
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.register_camera_btn = ctk.CTkButton(
            control_frame,
            text="Register Face",
            command=self.register_face_from_camera,
            width=120,
            height=35
        )
        self.register_camera_btn.grid(row=0, column=2, padx=(0, 10))
        
        self.register_file_btn = ctk.CTkButton(
            control_frame,
            text="Load Image",
            command=self.register_face_from_file,
            width=120,
            height=35
        )
        self.register_file_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Right side buttons
        if not self.fullscreen:
            self.fullscreen_btn = ctk.CTkButton(
                control_frame,
                text="Fullscreen",
                command=self.toggle_fullscreen,
                width=100,
                height=35
            )
            self.fullscreen_btn.grid(row=0, column=5, padx=(0, 10), sticky="e")
        
        self.exit_btn = ctk.CTkButton(
            control_frame,
            text="Exit",
            command=self.on_closing,
            width=80,
            height=35,
            fg_color="red",
            hover_color="darkred"
        )
        self.exit_btn.grid(row=0, column=6, sticky="e")
    
    def create_video_display(self, parent):
        """Create video display area"""
        video_frame = ctk.CTkFrame(parent)
        video_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        video_frame.grid_columnconfigure(0, weight=1)
        video_frame.grid_rowconfigure(0, weight=1)
        
        # Video label
        self.video_label = ctk.CTkLabel(
            video_frame,
            text="Camera Feed Will Appear Here",
            font=ctk.CTkFont(size=18),
            fg_color="black",
            corner_radius=8
        )
        self.video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    def create_status_panel(self, parent):
        """Create bottom status panel"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Status labels
        self.status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.face_count_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.face_count_var,
            font=ctk.CTkFont(size=12)
        )
        self.face_count_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        self.fps_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.fps_var,
            font=ctk.CTkFont(size=12)
        )
        self.fps_label.grid(row=0, column=3, padx=10, pady=10, sticky="e")
    
    def create_side_panel(self):
        """Create side panel for settings and face list"""
        side_frame = ctk.CTkFrame(self.root)
        side_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        side_frame.grid_columnconfigure(0, weight=1)
        side_frame.grid_rowconfigure(2, weight=1)
        
        # Settings section
        settings_label = ctk.CTkLabel(
            side_frame,
            text="Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        settings_inner_frame = ctk.CTkFrame(side_frame)
        settings_inner_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        settings_inner_frame.grid_columnconfigure(0, weight=1)
        
        # Tolerance setting
        tolerance_label = ctk.CTkLabel(
            settings_inner_frame,
            text="Recognition Tolerance:",
            font=ctk.CTkFont(size=12)
        )
        tolerance_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.tolerance_slider = ctk.CTkSlider(
            settings_inner_frame,
            from_=0.3,
            to=1.0,
            number_of_steps=70,
            variable=self.tolerance_var,
            command=self.on_tolerance_change
        )
        self.tolerance_slider.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        self.tolerance_value_label = ctk.CTkLabel(
            settings_inner_frame,
            text=f"Value: {self.tolerance_var.get():.2f}",
            font=ctk.CTkFont(size=11)
        )
        self.tolerance_value_label.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")
        
        # Appearance mode switch
        appearance_label = ctk.CTkLabel(
            settings_inner_frame,
            text="Appearance Mode:",
            font=ctk.CTkFont(size=12)
        )
        appearance_label.grid(row=3, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.appearance_switch = ctk.CTkSwitch(
            settings_inner_frame,
            text="Dark Mode",
            command=self.toggle_appearance_mode,
            onvalue="dark",
            offvalue="light"
        )
        self.appearance_switch.grid(row=4, column=0, padx=15, pady=(0, 15), sticky="w")
        self.appearance_switch.select()  # Default to dark mode
        
        # Registered faces section
        faces_label = ctk.CTkLabel(
            side_frame,
            text="Registered Faces",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        faces_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Scrollable frame for faces list
        self.faces_scrollable_frame = ctk.CTkScrollableFrame(
            side_frame,
            label_text="",
            corner_radius=8
        )
        self.faces_scrollable_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.faces_scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Face management buttons
        face_buttons_frame = ctk.CTkFrame(side_frame)
        face_buttons_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        face_buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.refresh_faces_btn = ctk.CTkButton(
            face_buttons_frame,
            text="Refresh List",
            command=self.update_faces_list,
            height=32
        )
        self.refresh_faces_btn.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        
        self.delete_face_btn = ctk.CTkButton(
            face_buttons_frame,
            text="Delete Selected",
            command=self.delete_selected_face,
            height=32,
            fg_color="red",
            hover_color="darkred"
        )
        self.delete_face_btn.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")
        
        # Initialize faces list
        self.update_faces_list()
    
    def on_tolerance_change(self, value):
        """Handle tolerance slider change"""
        self.tolerance_value_label.configure(text=f"Value: {value:.2f}")
        if self.face_system:
            # Update face system tolerance
            self.face_system.tolerance = value
            pass
    
    def toggle_appearance_mode(self):
        """Toggle between light and dark mode"""
        if self.appearance_switch.get() == "dark":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
    
    def start_camera(self):
        """Start camera capture"""
        if not self.is_running:
            self.cap = cv2.VideoCapture(2)
            if self.cap.isOpened():
                self.is_running = True
                self.status_var.set("Camera running...")
                self.start_btn.configure(state="disabled")
                self.stop_btn.configure(state="normal")
                self.update_video()
            else:
                messagebox.showerror("Error", "Could not open camera")
    
    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        self.status_var.set("Camera stopped")
        self.video_label.configure(image=None, text="Camera Stopped")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
    
    def update_video(self):
        """Update video display"""
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Process frame with face recognition
                processed_frame, results = self.process_frame_with_recognition(frame)
                
                # Convert to display format
                display_frame = self.prepare_frame_for_display(processed_frame)
                
                # Update GUI
                photo = ImageTk.PhotoImage(image=display_frame)
                self.video_label.configure(image=photo, text="")
                self.video_label.image = photo
                
                # Update status
                self.update_status(results)
        
        if self.is_running:
            self.root.after(30, self.update_video)  # ~33 FPS
    
    def process_frame_with_recognition(self, frame):
        """Process frame with face recognition"""
        if self.face_system:
            return self.face_system.process_frame(frame, "gui_camera")
            pass
        
        # Placeholder processing - just return the frame with a rectangle
        height, width = frame.shape[:2]
        cv2.rectangle(frame, (50, 50), (width-50, height-50), (0, 255, 0), 2)
        cv2.putText(frame, "Face Recognition Active", (60, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame, []
    
    def prepare_frame_for_display(self, frame):
        """Prepare frame for tkinter display"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get current video label size
        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()
        
        if label_width > 1 and label_height > 1:
            # Resize to fit label while maintaining aspect ratio
            height, width = rgb_frame.shape[:2]
            ratio = min(label_width/width, label_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            rgb_frame = cv2.resize(rgb_frame, (new_width, new_height))
        
        # Convert to PIL Image
        return Image.fromarray(rgb_frame)
    
    def update_status(self, recognition_results):
        """Update status information"""
        # Update FPS
        current_time = time.time()
        if hasattr(self, 'last_time'):
            fps = 1.0 / (current_time - self.last_time)
            self.fps_var.set(f"FPS: {fps:.1f}")
        self.last_time = current_time
        
        # Update face count
        registered_count = len(self.face_system.known_face_names) if self.face_system else 0
        self.face_count_var.set(f"Registered: {registered_count}")
        
        # Update recognition status
        if recognition_results:
            names = [r['name'] for r in recognition_results if r['name'] != 'Unknown']
            if names:
                self.status_var.set(f"Recognized: {', '.join(names)}")
            else:
                self.status_var.set("Unknown faces detected")
        else:
            self.status_var.set("No faces detected")
    
    def register_face_from_camera(self):
        """Register face from current camera frame"""
        if not self.is_running:
            messagebox.showwarning("Warning", "Please start the camera first")
            return
        
        # Capture current frame
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Save temporary image
                temp_path = f"temp_capture_{int(time.time())}.jpg"
                cv2.imwrite(temp_path, frame)
                
                # Get name from user
                name = self.get_name_dialog()
                if name:
                    self.register_face_from_path(temp_path, name)
                
                # Clean up
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    def register_face_from_file(self):
        """Register face from image file"""
        file_path = filedialog.askopenfilename(
            title="Select Face Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            name = self.get_name_dialog()
            if name:
                self.register_face_from_path(file_path, name)
    
    def register_face_from_path(self, image_path, name):
        """Register face from image path"""
        if self.face_system:
            success = self.face_system.add_known_face(image_path, name)
            
            if success:
                messagebox.showinfo("Success", f"Successfully registered {name}")
                self.update_faces_list()
                # self.face_system.save_face_database()
            else:
                messagebox.showerror("Error", f"Failed to register {name}")
        else:
            messagebox.showerror("Error", "Face recognition system not initialized")
    
    def get_name_dialog(self):
        """Get name from user dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Enter Name")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        dialog.geometry(f"350x200+{x}+{y}")
        
        # Dialog content
        ctk.CTkLabel(
            dialog,
            text="Enter person's name:",
            font=ctk.CTkFont(size=16)
        ).pack(pady=30)
        
        name_var = ctk.StringVar()
        entry = ctk.CTkEntry(
            dialog,
            textvariable=name_var,
            font=ctk.CTkFont(size=14),
            width=250,
            height=35
        )
        entry.pack(pady=10)
        entry.focus()
        
        result = {'name': None}
        
        def on_ok():
            result['name'] = name_var.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="OK",
            command=on_ok,
            width=100,
            height=35
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=100,
            height=35
        ).pack(side="left", padx=10)
        
        entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        dialog.wait_window()
        return result['name'] if result['name'] else None
    
    def update_faces_list(self):
        """Update the list of registered faces"""
        # Clear existing widgets
        for widget in self.faces_scrollable_frame.winfo_children():
            widget.destroy()
        
        if self.face_system:
            faces = self.face_system.known_face_names
            pass
        else:
            # Placeholder faces
            faces = ["Sample Person 1", "Sample Person 2", "John Doe", "Jane Smith"]
        
        for i, name in enumerate(faces):
            face_frame = ctk.CTkFrame(self.faces_scrollable_frame)
            face_frame.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            face_frame.grid_columnconfigure(0, weight=1)
            
            name_label = ctk.CTkLabel(
                face_frame,
                text=name,
                font=ctk.CTkFont(size=12)
            )
            name_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    
    def delete_selected_face(self):
        """Delete selected face from database"""
        # This would need to be implemented with your face system
        messagebox.showinfo("Info", "Delete face functionality not implemented yet")
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        
        if hasattr(self, 'fullscreen_btn'):
            if self.fullscreen:
                self.fullscreen_btn.configure(text="Windowed")
            else:
                self.fullscreen_btn.configure(text="Fullscreen")
    
    def on_closing(self):
        """Handle application closing"""
        self.stop_camera()
        self.root.quit()
        self.root.destroy()

def main():
    root = ctk.CTk()
    app = ModernFaceRecognitionGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_closing()

if __name__ == "__main__":
    main()
