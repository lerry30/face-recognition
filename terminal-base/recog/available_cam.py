import cv2

def list_available_cameras():
    """Find all available camera indices"""
    available_cameras = []
    
    # Test camera indices 0-10 (usually sufficient)
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"Camera {i}: Available")
            cap.release()
        else:
            print(f"Camera {i}: Not available")
    
    return available_cameras

def test_camera(camera_index):
    """Test a specific camera and show live feed"""
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"Cannot open camera {camera_index}")
        return
    
    print(f"Testing camera {camera_index}. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Display camera info on frame
        cv2.putText(frame, f"Camera {camera_index}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow(f'Camera {camera_index}', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
