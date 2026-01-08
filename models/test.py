import os
from ultralytics import YOLO

model = YOLO('vehicle_detect.pt')

# Chạy trên cả thư mục ảnh
results = model.predict(source='test', save=True, conf=0.4)

print("Đã xong! Ảnh kết quả nằm trong thư mục: runs/detect/predict/")