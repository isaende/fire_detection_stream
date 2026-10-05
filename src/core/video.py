import cv2
import time

class VideoProcessor:
    def __init__(self, stream_url=0):
        self.stream_url = stream_url
        self.connect()

    def connect(self):
        """Initializes or re-initializes the video capture."""
        self.cap = cv2.VideoCapture(self.stream_url)
        # Limit buffer to avoid latency on live streams
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def read_frame(self):
        """Reads a frame and automatically restarts if the video ends."""
        ret, frame = self.cap.read()
        
        if not ret:
            print("[VIDEO] Source lost or video ended. Restarting...")
            self.cap.release()
            time.sleep(0.5) # Brief pause before reconnecting
            self.connect()
            ret, frame = self.cap.read()
            
        return ret, frame

    def release(self):
        self.cap.release()