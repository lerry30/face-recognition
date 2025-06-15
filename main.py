from face_recog import FaceRecognitionSystem
from face_regis import capture_and_register_face
from available_cam import list_available_cameras

def registration_menu():
    """Interactive menu for face registration"""
    face_system = FaceRecognitionSystem(
        tolerance=0.42,
        model='hog',
        enable_logging=True
    )
    
    while True:
        print("\n=== Face Recognition System ===")
        print("1. Register new face from camera")
        print("2. Register face from image file") 
        print("3. List registered faces")
        print("4. Start recognition")
        print("5. List Available Cameras")
        print("6. Exit")
        
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            capture_and_register_face(face_system, camera_index=2)
            face_system.save_face_database()
            
        elif choice == '2':
            image_path = input("Enter image path: ").strip()
            name = input("Enter person's name: ").strip()
            if os.path.exists(image_path) and name:
                success = face_system.add_known_face(image_path, name)
                if success:
                    print(f"✓ Successfully registered {name}")
                else:
                    print(f"✗ Failed to register {name}")
                face_system.save_face_database()
            else:
                print("Invalid image path or name")
                
        elif choice == '3':
            print(f"\nRegistered faces ({len(face_system.known_face_names)}):")
            for i, name in enumerate(face_system.known_face_names, 1):
                print(f"{i}. {name}")
                
        elif choice == '4':
            if len(face_system.known_face_names) == 0:
                print("No faces registered yet. Please register faces first.")
            else:
                print("Starting recognition... Press 'q' to stop")
                face_system.run_camera_recognition(camera_index=2, display=True)
                
        elif choice == '5':
            cameras = list_available_cameras()
            print(f"\nAvailable cameras: {cameras}")

        elif choice == '6':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    registration_menu()
