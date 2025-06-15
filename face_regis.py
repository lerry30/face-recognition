import cv2
import os
from datetime import datetime

def capture_and_register_face(face_system, camera_index=0):
    """
    Capture a face from camera and register it
    """
    cap = cv2.VideoCapture(camera_index)
    
    print("Face Registration Mode")
    print("Position your face in the camera and press SPACE to capture")
    print("Press 'q' to quit without capturing")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Display the frame
        cv2.putText(frame, "Press SPACE to capture face, 'q' to quit", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Register Face', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # Space bar pressed
            # Save the current frame
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_image_path = f"temp_face_{timestamp}.jpg"
            cv2.imwrite(temp_image_path, frame)
            
            # Get person's name
            cap.release()
            cv2.destroyAllWindows()
            
            name = input("Enter the person's name: ").strip()
            if name:
                success = face_system.add_known_face(temp_image_path, name)
                if success:
                    print(f"✓ Successfully registered {name}")
                    # Move image to permanent storage
                    os.makedirs("registered_faces", exist_ok=True)
                    permanent_path = f"registered_faces/{name}_{timestamp}.jpg"
                    os.rename(temp_image_path, permanent_path)
                else:
                    print(f"✗ Failed to register {name}")
                    os.remove(temp_image_path)
            else:
                os.remove(temp_image_path)
            
            return True
            
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return False
