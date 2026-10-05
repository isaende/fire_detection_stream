import cv2
import threading
import queue
import time

from core.inference import InferenceEngine
from core.video import VideoProcessor
from utils.logger import EventLogger
from utils.telemetry import HardwareMonitor
from ui.dashboard import DarkDashboard

STREAM_URL = "http://127.0.0.1:8080";
MODEL_PATH = "models/yolov8n.onnx"
CONFIDENCE_THRESHOLD = 0.20

frame_queue = queue.Queue(maxsize=1)
running = True

def ai_inference_worker(inference_engine, video_processor, logger):
    global running
    
    while running:
        ret, frame = video_processor.read_frame()
        if not ret:
            time.sleep(0.1)
            continue
            
        results = inference_engine.predict(frame)
        
        is_alert = False
        for det in results:
            if det["score"] >= CONFIDENCE_THRESHOLD:
                if det["class_id"] == 0:  
                    is_alert = True
                logger.add_event(det["label"], det["score"])
                
        if not frame_queue.empty():
            try: frame_queue.get_nowait()
            except queue.Empty: pass
            
        frame_queue.put((frame, results, is_alert))

def main():
    global running

    print("[INIT] Starting Edge CV Pipeline...")
    inference = InferenceEngine(MODEL_PATH, img_size=(640, 640), conf_thresh=CONFIDENCE_THRESHOLD)
    video = VideoProcessor(STREAM_URL)
    logger = EventLogger()
    hw_monitor = HardwareMonitor()
    dashboard = DarkDashboard()

    window_name = "Edge Sentinel - Fire & Smoke Detection"
    cv2.namedWindow(window_name)

    ai_thread = threading.Thread(target=ai_inference_worker, args=(inference, video, logger))
    ai_thread.daemon = True
    ai_thread.start()

    print("[INIT] System running. Press 'q' to exit.")

    while running:
        try:
            frame, results, is_alert = frame_queue.get(timeout=0.05)
            
            for det in results:
                if det["score"] >= CONFIDENCE_THRESHOLD:
                    x, y, w, h = det["box"]
                    color = (0, 0, 255) if det["class_id"] == 0 else (0, 255, 255)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame, f"{det['label']} {det['score']:.2f}", 
                                (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            telemetry = {
                'ram': hw_monitor.get_ram_usage(),
                'temp': hw_monitor.get_temperature()
            }

            final_view = dashboard.render(frame, telemetry, logger.get_logs(), is_alert)
            cv2.imshow(window_name, final_view)

        except queue.Empty:
            pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[SHUTDOWN] Exiting gracefully...")
            running = False
            break

    ai_thread.join()
    video.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()