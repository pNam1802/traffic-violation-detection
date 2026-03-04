from src.engine.ocr import OCRService
import os

class TrafficDetector:
    def __init__(self, vehicle_model, plate_model, ocr_model):
        self.v_model = vehicle_model
        self.p_model = plate_model
        self.ocr_service = OCRService(ocr_model)

    def detect_and_track(self, frame, conf=0.7):
        # Tracking xe với ByteTrack hoặc Botsort (có sẵn trong YOLOv8)
        return self.v_model.track(frame, persist=True, verbose=False, conf=conf)[0]

    def get_license_plate(self, car_img, conf_threshold=0.25):
        # Phát hiện vị trí biển số trong ảnh xe đã crop
        results = self.p_model(car_img, verbose=False, conf=conf_threshold)[0]

        if len(results.boxes) > 0:
            # Lấy biển số có confidence cao nhất
            best_idx = results.boxes.conf.argmax()
            best_box = results.boxes.xyxy[best_idx].cpu().numpy().astype(int)
            best_conf = results.boxes.conf[best_idx].cpu().numpy()
            
            # Crop biển số từ ảnh xe
            plate_crop = car_img[best_box[1]:best_box[3], best_box[0]:best_box[2]]
            
            # Kiểm tra crop có hợp lệ không
            if plate_crop.size == 0:
                return "N/A", None
            
            # Debug info (có thể bỏ comment sau)
            # print(f"Plate detected: conf={best_conf:.2f}, size={plate_crop.shape}")

            # Đưa qua bộ OCR đã xử lý sắp xếp dòng
            return self.ocr_service.process_plate_text(plate_crop), plate_crop

        return "N/A", None