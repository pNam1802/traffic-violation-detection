import st
from src.engine.ocr import OCRService


class TrafficDetector:
    def __init__(self, vehicle_model, plate_model, ocr_model):
        self.v_model = vehicle_model
        self.p_model = plate_model
        self.ocr_service = OCRService(ocr_model)

    def detect_and_track(self, frame):
        # Tracking xe với ByteTrack hoặc Botsort (có sẵn trong YOLOv8)
        return self.v_model.track(frame, persist=True, verbose=False)[0]

    def get_license_plate(self, car_img):
        # Phát hiện vị trí biển số trong ảnh xe đã crop
        results = self.p_model(car_img, verbose=False)[0]

        if len(results.boxes) > 0:
            # Lấy biển số có confidence cao nhất
            best_box = results.boxes.xyxy[0].cpu().numpy().astype(int)
            plate_crop = car_img[best_box[1]:best_box[3], best_box[0]:best_box[2]]

            # Đưa qua bộ OCR đã xử lý sắp xếp dòng
            return self.ocr_service.process_plate_text(plate_crop), plate_crop

        return "N/A", None