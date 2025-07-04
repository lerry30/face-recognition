class CameraManager:
    _instance=None
    _selected_camera=None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_camera(self, camera):
        self._selected_camera = camera

    def get_camera(self):
        return self._selected_camera

    @property
    def camera(self):
        return self._selected_camera

    @camera.setter
    def camera(self, value):
        self._selected_camera = value


"""
# Usage:
camera_manager = CameraManager()
camera_manager.set_camera("Camera 1")

# In another file:
camera_manager = CameraManager()  # Same instance
print(camera_manager.get_camera())  # "Camera 1"

# Or using property:
camera_manager.camera = "Camera 2"
print(camera_manager.camera)  # "Camera 2"
"""


