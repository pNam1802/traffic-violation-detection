from ultralytics import YOLO

model = YOLO('license_plate_detect.pt')

result = model.predict(source='test2', save=True, conf=0.4)
