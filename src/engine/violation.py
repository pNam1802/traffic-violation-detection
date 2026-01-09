import cv2
from src.engine.traffic_light import TrafficLightService
from src.utils.geometry import is_inside_polygon
import numpy as np
import time


class ViolationEngine:
    def __init__(self, detector, config):
        self.detector = detector
        self.config = config
        self.violated_ids = set()
        self.light_service = TrafficLightService()

    def process_frame(self, frame):
        # 1. Nhận diện trạng thái đèn
        light_status = self.light_service.detect_color(frame, self.config['light_roi'])
        new_violations = []

        # 2. Vẽ UI nền (Lane, Zone) trước khi vẽ xe để không đè chữ
        frame = self._draw_ui(frame, light_status)

        # 3. Detect và Track
        results = self.detector.detect_and_track(frame)

        if results and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            # classes = results[0].boxes.cls.cpu().numpy().astype(int) # Nếu cần lọc loại xe

            for box, track_id in zip(boxes, ids):
                x1, y1, x2, y2 = map(int, box)
                # Điểm chân xe (giữa cạnh dưới)
                foot_point = ((x1 + x2) // 2, y2)

                is_already_violated = track_id in self.violated_ids

                # Logic kiểm tra vi phạm
                if not is_already_violated and light_status == "RED":
                    # Kiểm tra xe có nằm trong vùng vi phạm hay không
                    if is_inside_polygon(foot_point, self.config['violation_zone']):
                        self.violated_ids.add(track_id)

                        # Xử lý crop ảnh
                        car_crop = frame[max(0, y1):min(y2, frame.shape[0]),
                        max(0, x1):min(x2, frame.shape[1])].copy()

                        # Tối ưu: Chỉ gọi OCR khi thực sự cần hoặc đẩy vào luồng riêng
                        # Ở đây tạm thời giữ nguyên nhưng cảnh báo về hiệu suất
                        plate_text, _ = self.detector.get_license_plate(car_crop)

                        new_violations.append({
                            "id": track_id,
                            "plate": plate_text,
                            "image": car_crop,
                            "time": time.strftime("%H:%M:%S")
                        })
                        is_already_violated = True

                # 4. Vẽ Bounding Box và Label
                color = (0, 0, 255) if is_already_violated else (0, 255, 0)
                thickness = 3 if is_already_violated else 2
                label = f"VIOLATION ID:{track_id}" if is_already_violated else f"ID:{track_id}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame, new_violations, light_status

    def _draw_ui(self, frame, status):
        overlay = frame.copy()

        # Vẽ làn đường
        lane_pts = np.array(self.config['lane_polygon'], dtype=np.int32)
        cv2.fillPoly(overlay, [lane_pts], (0, 255, 0))

        # Vẽ vùng vi phạm (chỉ hiện màu đỏ khi đèn đỏ)
        violation_pts = np.array(self.config['violation_zone'], dtype=np.int32)
        zone_color = (0, 0, 255) if status == "RED" else (100, 100, 100)
        cv2.fillPoly(overlay, [violation_pts], zone_color)

        # Áp dụng Overlay
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

        # Vẽ Stop Line
        line = self.config['stop_line']
        cv2.line(frame, tuple(line[0]), tuple(line[1]), (255, 255, 255), 2)

        # Vẽ Đèn (ROI)
        x, y, w, h = self.config['light_roi']
        light_color = (0, 0, 255) if status == "RED" else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + w, y + h), light_color, 2)
        cv2.putText(frame, f"LIGHT: {status}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, light_color, 2)

        return frame