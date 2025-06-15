import cv2
import face_recognition
import numpy as np
import os
import pickle
import requests
import json
import threading
import time
from datetime import datetime
import sqlite3
import logging
from collections import defaultdict

class FaceRecognitionSystem:
    def __init__(self, 
                 tolerance=0.4, 
                 model='hog',  # 'hog' for CPU, 'cnn' for GPU
                 server_url=None,
                 enable_logging=True):
        """
        Initialize the face recognition system
        
        Args:
            tolerance: Face matching tolerance (lower = stricter)
            model: Face detection model ('hog' for CPU, 'cnn' for GPU)
            server_url: Optional server URL for sending recognition data
            enable_logging: Enable detailed logging
        """
        self.tolerance = tolerance
        self.model = model
        self.server_url = server_url
        
        # Storage for known faces
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_metadata = {}
        
        # Performance tracking
        self.recognition_history = defaultdict(list)
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Database setup
        self.setup_database()
        
        # Logging setup
        if enable_logging:
            self.setup_logging()
        
        # Load existing face data
        self.load_face_database()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('face_recognition.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup SQLite database for storing recognition logs"""
        self.conn = sqlite3.connect('face_recognition.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recognition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                confidence REAL,
                timestamp DATETIME,
                camera_id TEXT,
                image_path TEXT
            )
        ''')
        self.conn.commit()
    
    def add_known_face(self, image_path, name, metadata=None):
        """
        Add a known face to the recognition database
        
        Args:
            image_path: Path to the image file
            name: Name of the person
            metadata: Additional metadata (dict)
        """
        try:
            # Load image and get face encoding
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image, model=self.model)
            
            if len(face_encodings) == 0:
                self.logger.warning(f"No face found in {image_path}")
                return False
            
            if len(face_encodings) > 1:
                self.logger.warning(f"Multiple faces found in {image_path}, using the first one")
            
            # Store the encoding and metadata
            face_encoding = face_encodings[0]
            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(name)
            
            if metadata:
                self.known_face_metadata[name] = metadata
            
            self.logger.info(f"Added face for {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding face for {name}: {str(e)}")
            return False
    
    def save_face_database(self, filename='face_database.pkl'):
        """Save the face database to a pickle file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names,
                'metadata': self.known_face_metadata
            }
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
            self.logger.info(f"Face database saved to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving face database: {str(e)}")
    
    def load_face_database(self, filename='face_database.pkl'):
        """Load the face database from a pickle file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                self.known_face_encodings = data['encodings']
                self.known_face_names = data['names']
                self.known_face_metadata = data.get('metadata', {})
                self.logger.info(f"Loaded {len(self.known_face_names)} faces from database")
        except Exception as e:
            self.logger.error(f"Error loading face database: {str(e)}")
    
    def process_frame(self, frame, camera_id="default"):
        """
        Process a single frame for face recognition
        
        Args:
            frame: OpenCV frame/image
            camera_id: Identifier for the camera source
            
        Returns:
            tuple: (processed_frame, recognition_results)
        """
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find faces and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame, model=self.model)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        recognition_results = []
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, tolerance=self.tolerance
            )
            name = "Unknown"
            confidence = 0.0
            
            if True in matches:
                # Calculate face distances
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
            
            # Draw rectangle and label
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            
            label = f"{name} ({confidence:.2f})"
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
            
            # Store recognition result
            result = {
                'name': name,
                'confidence': confidence,
                'location': (top, right, bottom, left),
                'timestamp': datetime.now(),
                'camera_id': camera_id
            }
            recognition_results.append(result)
            
            # Log to database
            self.log_recognition(result)
            
            # Send to server if configured
            if self.server_url and name != "Unknown":
                self.send_to_server(result)
        
        return frame, recognition_results
    
    def log_recognition(self, result):
        """Log recognition result to database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO recognition_logs 
                (name, confidence, timestamp, camera_id, image_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                result['name'],
                result['confidence'],
                result['timestamp'],
                result['camera_id'],
                None  # image_path can be added if needed
            ))
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"Error logging recognition: {str(e)}")
    
    def send_to_server(self, result):
        """Send recognition result to server"""
        try:
            data = {
                'name': result['name'],
                'confidence': result['confidence'],
                'timestamp': result['timestamp'].isoformat(),
                'camera_id': result['camera_id']
            }
            
            # Send in a separate thread to avoid blocking
            threading.Thread(
                target=self._post_to_server,
                args=(data,),
                daemon=True
            ).start()
            
        except Exception as e:
            self.logger.error(f"Error preparing server data: {str(e)}")
    
    def _post_to_server(self, data):
        """Internal method to post data to server"""
        try:
            response = requests.post(
                self.server_url,
                json=data,
                timeout=5
            )
            if response.status_code == 200:
                self.logger.info(f"Successfully sent data for {data['name']}")
            else:
                self.logger.warning(f"Server responded with status {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error sending to server: {str(e)}")
    
    def run_camera_recognition(self, camera_index=0, display=True):
        """
        Run real-time face recognition from camera
        
        Args:
            camera_index: Camera index (0 for default camera)
            display: Whether to display the video feed
        """
        cap = cv2.VideoCapture(camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        
        self.logger.info("Starting camera recognition...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame, results = self.process_frame(frame, f"camera_{camera_index}")
            
            # Calculate FPS
            self.frame_count += 1
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.fps_counter = self.frame_count
                self.frame_count = 0
                self.last_fps_time = current_time
            
            # Display FPS
            cv2.putText(processed_frame, f"FPS: {self.fps_counter}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            if display:
                cv2.imshow('Advanced Face Recognition', processed_frame)
                
                # Break on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        self.logger.info("Camera recognition stopped")
    
    def get_recognition_stats(self, days=7):
        """Get recognition statistics from the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT name, COUNT(*) as count, AVG(confidence) as avg_confidence
                FROM recognition_logs 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY name
                ORDER BY count DESC
            '''.format(days))
            
            results = cursor.fetchall()
            return [{'name': row[0], 'count': row[1], 'avg_confidence': row[2]} 
                   for row in results]
        except Exception as e:
            self.logger.error(f"Error getting stats: {str(e)}")
            return []
