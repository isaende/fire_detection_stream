import cv2
import numpy as np
import onnxruntime as ort

class InferenceEngine:
    def __init__(self, model_path, img_size=(640, 640), conf_thresh=0.20, iou_thresh=0.20):
        """
        Initialize inference engine and select the best execution provider.
        """
        self.img_size = img_size
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        
        # Try to use CUDA first. If not available, fall back to CPU.
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        
        try:
            self.session = ort.InferenceSession(model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            print(f"[INFERENCE] Model loaded via: {self.session.get_providers()[0]}")
        except Exception as e:
            print(f"[ERROR] Fail to load model: {e}")
            exit(1)

        # Classes padrão do YOLOv8 (ajuste se o modelo do Roboflow tiver mais/menos classes)
        self.classes = {0: "Fire", 1: "Smoke"}

    def preprocess(self, frame):
        """
        Resize, normalize, and convert the frame to the format expected by the model.
        """
        # Resize to the inference size (ex: 320x320 for faster inference)
        img = cv2.resize(frame, self.img_size)
        
        # Convert BGR to RGB (OpenCV works with BGR by default, but most models expect RGB)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Transpose from HWC (Height, Width, Channels) to CHW (Channels, Height, Width)
        blob = img.transpose((2, 0, 1))
        
        # Add batch dimension (1, C, H, W) and normalize (0-1)
        blob = np.expand_dims(blob, axis=0).astype(np.float32) / 255.0
        
        return blob

    def predict(self, frame):
        """
        Execute the inference and return the filtered bounding boxes.
        """
        orig_h, orig_w = frame.shape[:2]
        blob = self.preprocess(frame)
        
        # Run inference 
        outputs = self.session.run(None, {self.input_name: blob})
        predictions = outputs[0][0] # Shape do YOLOv8: (num_classes + 4, num_boxes)
        
        # Transpose to iterate over the boxes (num_boxes, num_classes + 4)
        predictions = predictions.T
        
        boxes = []
        scores = []
        class_ids = []

        # Process each prediction and filter by confidence threshold
        for row in predictions:
            classes_scores = row[4:]
            class_id = np.argmax(classes_scores)
            score = classes_scores[class_id]

            if score > self.conf_thresh:
                # YOLOv8 returns boxes in the format (cx, cy, w, h) normalized to [0, 1]
                cx, cy, w, h = row[0:4]
                
                # Scale back to original image size
                cx = cx / self.img_size[0] * orig_w
                cy = cy / self.img_size[1] * orig_h
                w = w / self.img_size[0] * orig_w
                h = h / self.img_size[1] * orig_h
                
                x_min = int(cx - (w / 2))
                y_min = int(cy - (h / 2))
                
                boxes.append([x_min, y_min, int(w), int(h)])
                scores.append(float(score))
                class_ids.append(class_id)

        # Apply Non-Maximum Suppression (NMS) from OpenCV
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.conf_thresh, self.iou_thresh)
        
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                box = boxes[i]
                results.append({
                    "box": box, # [x, y, w, h]
                    "score": scores[i],
                    "class_id": class_ids[i],
                    "label": self.classes.get(class_ids[i], "Unknown")
                })
                
        return results