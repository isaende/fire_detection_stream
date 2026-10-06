# Fire Detection Stream - Real-Time Fire & Smoke Detection
<img src="https://github.com/isaende/fire_detection_stream/blob/main/assets/alert.jpeg" width="600">
A climate tech project designed with a focus on environmental monitoring, sustainable development, and computer vision. The application leverages artificial intelligence to detect early-stage wildfires and smoke plumes. The system is structurally optimized for deployment on embedded hardware, such as the NVIDIA Jetson Nano, ensuring reliable, low-latency video processing in the field.

## Key Features

* **Edge-Optimized Architecture:** Engineered specifically for deployment on constrained embedded hardware.
* **Hardware-Accelerated Inference:** Leverages ONNX Runtime (`CUDAExecutionProvider` and `TensorrtExecutionProvider`) to maximize parallel processing on NVIDIA GPUs, maintaining high frame rates.
* **Custom OpenCV Dashboard:** Features a modern, dark-themed user interface built entirely with OpenCV primitives (including custom rounded cards). It displays live video feeds alongside real-time hardware telemetry (RAM usage, temperature) and an event log.

## Prerequisites

To run this pipeline with maximum performance, your environment must support hardware acceleration:

* **Python:** 3.10
* **OS:** Windows (Development) / Linux for Tegra (Deployment)
* **Hardware:** NVIDIA GPU with CUDA Toolkit and cuDNN installed.

## Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/your-username/fire_detection_stream.git](https://github.com/your-username/fire_detection_stream.git)
cd fire_detection_stream
```


**2. Create and activate a virtual environment:**
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/Jetson:
source .venv/bin/activate
```

**3. Install the required dependencies:**
Ensure you install the GPU version of ONNX Runtime to enable CUDA.

```bash
pip install opencv-python numpy psutil
pip install onnxruntime-gpu
```

**4. Prepare the Model:**
This system requires a custom-trained YOLOv8 model for environmental monitoring.
* Download the pre-trained Fire and Smoke YOLOv8 weights directly from [SHOU-ISD/fire-and-smoke on Hugging Face](https://huggingface.co/SHOU-ISD/fire-and-smoke).
* Export the weights to ONNX format using an image size of 640x640:
```bash
  yolo export model=best.pt format=onnx imgsz=640
```

Place the resulting .onnx file inside the models/ directory.

Update MODEL_PATH in src/main.py and ensure the class dictionary in src/core/inference.py matches your model's classes (e.g., {0: "Fire", 1: "Smoke"}).

**Usage**
Run the pipeline from the root directory of the project:

```bash
python src/main.py
```

Video Source: Can use this variable to a local .mp4 file or an HTTP stream URL for drone/IP camera feeds.

Exit: Press q while focused on the dashboard window to safely terminate the threads and release the camera.

## Acknowledgments
* The custom YOLOv8 weights for fire and smoke detection used in this pipeline were trained and provided by [SHOU-ISD](https://huggingface.co/SHOU-ISD/fire-and-smoke).
