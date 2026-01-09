# Traffic Violation Detection System

<p align="center">
  <img width="45%" alt="Demo UI"
       src="https://github.com/user-attachments/assets/657428e1-8cab-4418-a708-76277d854478" />
  <img width="45%" alt="Violation Result"
       src="https://github.com/user-attachments/assets/2cf1de60-10e6-4fb9-804e-985c670474c3" />
</p>




This project detects traffic violations from video using Python (Streamlit + OpenCV + PyTorch models). It performs vehicle detection, license plate recognition (OCR), and violation detection (e.g., red-light running or crossing the stop line).

## Overview
- Web UI: Streamlit (`main.py`).
- Detection engines live in `src/engine` (detector, violation, ocr, traffic_light, ...).
- Model management is in `src/core/models.py` (loads vehicle/plate detectors and OCR service).
- Example model files are stored in the `models/` folder (for example `vehicle_detect.pt`, `license_plate_detect.pt`).
- Main configuration is `data/config.json` (stop-line coordinates, detection thresholds, etc.).

## Requirements
- Python 3.9+ (developed with Python 3.10)
- Required Python packages listed in `requirements.txt`
- Works on Windows / Linux / macOS

## Quick install
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Ensure the `models/` folder contains the required model files:
- `models/vehicle_detect.pt`
- `models/license_plate_detect.pt`

If any model is missing, add the appropriate model file to the `models/` folder.

## Run (Streamlit UI)
Start the Streamlit app:

```powershell
streamlit run main.py
```

Open the URL provided by Streamlit (by default `http://localhost:8501`).

In the sidebar you can:
- Upload a video file (`.mp4`, `.avi`, `.mov`).
- Click "Start processing" to begin detection.

Detected violations will appear in the sidebar (with license plate snapshots) and the annotated video will be shown in the main pane.

## Configuration file
- `data/config.json` contains parameters such as stop-line coordinates and detection thresholds. Edit this file to adapt the system to your camera/video.

## Calibration tool
- Use `pages/1_Calibration.py` to configure the stop line and geometric references. If the stop line is not correctly aligned for your footage, run the Calibration page and save updated settings.

## Output / logs
- `data/temp/` is used to store temporary uploaded videos.
- `models/runs/detect/predict*` contains example result images from previous runs (not necessarily runtime artifacts).
- The current in-memory violations list is kept in `st.session_state.violations`. If you need persistent storage, extend `ViolationEngine` to write results to a CSV, SQLite DB, or other storage.

## Development notes
- See `src/engine/detector.py` for the detection flow (vehicle detection -> plate detection -> OCR).
- See `src/engine/violation.py` to understand how violations are defined (for example based on traffic light state and vehicle position relative to the stop line).
- If you add models or modify the OCR API, update `src/core/models.py` to handle model loading.

## Common issues and troubleshooting
- Model load failures: check `models/*.pt` paths and PyTorch version compatibility.
- Streamlit does not open: check firewall and port settings, or try `streamlit run main.py --server.port 8502`.
- Video not processed: verify the file's codec and integrity; re-encode to H.264 MP4 if necessary.


