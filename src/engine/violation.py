import cv2
from src.engine.traffic_light import TrafficLightService
from src.utils.geometry import is_passed_line, is_inside_lane
import numpy as np
import time
class ViolationEngine:
    def __init__(self, detector, config):
        self.detector = detector
        self.config = config
        self.violated_ids = set()
        # Khởi tạo service đèn giao thông
        self.light_service = TrafficLightService()

    def process_frame(self, frame):
        light_status = self.light_service.detect_color(frame, self.config['light_roi'])
        new_violations = []
        results = self.detector.detect_and_track(frame)


        if results.boxes.id is not None:
            boxes = results.boxes.xyxy.cpu().numpy()
            ids = results.boxes.id.cpu().numpy().astype(int)

            for box, track_id in zip(boxes, ids):
                x1, y1, x2, y2 = map(int, box)
                foot_point = ((x1 + x2) // 2, y2)

                # 1. Xác định trạng thái hiển thị mặc định
                is_already_violated = track_id in self.violated_ids
                color = (0, 0, 255) if is_already_violated else (0, 255, 0)
                thickness = 3 if is_already_violated else 2
                label = f"VIOLATION ID:{track_id}" if is_already_violated else f"ID:{track_id}"

                # 2. Logic kiểm tra vi phạm (Chỉ chạy nếu chưa bị đánh dấu vi phạm trước đó)
                if not is_already_violated and light_status == "RED":
                    # Chỉ phạt nếu xe nằm trong làn và VỪA MỚI vượt vạch
                    if is_inside_lane(foot_point, self.config['lane_polygon']) and \
                            is_passed_line(foot_point, self.config['stop_line']):
                        self.violated_ids.add(track_id)

                        # Xử lý hình ảnh bằng chứng
                        car_crop = frame[max(0, y1):y2, max(0, x1):x2].copy()

                        # Lưu vào danh sách chờ OCR (nên xử lý async ở thực tế)
                        plate_text, _ = self.detector.get_license_plate(car_crop)

                        new_violations.append({
                            "id": track_id,
                            "plate": plate_text,
                            "image": car_crop,
                            "time": time.time()
                        })

                        # Cập nhật hiển thị ngay lập tức cho frame hiện tại
                        color, thickness, label = (0, 0, 255), 3, f"NEW VIOLATION:{track_id}"

                # 3. Vẽ Bounding Box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # 4. Vẽ UI (Chỉ gọi 1 lần sau khi xong vòng lặp xe)
        self._draw_ui(frame, light_status)
        return frame, new_violations, light_status

    def _draw_ui(self, frame, status):
        # 1. Tạo overlay để vẽ các mảng màu trong suốt
        overlay = frame.copy()

        # 2. Bôi màu toàn bộ làn đường (Lane Polygon)
        # Thay vì offset 60px, ta dùng vùng polygon chuẩn của làn đường
        lane_pts = np.array(self.config['lane_polygon'], dtype=np.int32)

        # Màu xanh lá nhạt (0, 255, 0) để chỉ thị đây là vùng giám sát
        cv2.fillPoly(overlay, [lane_pts], (0, 255, 0))

        # 3. Vẽ vạch dừng (Stop Line) để làm mốc vi phạm
        line = self.config['stop_line']
        p1, p2 = tuple(line[0]), tuple(line[1])

        # Nếu đèn đỏ, vạch dừng hiện màu đỏ rực để cảnh báo, ngược lại để màu trắng
        line_color = (0, 0, 255) if status == "RED" else (255, 255, 255)
        line_thickness = 4 if status == "RED" else 2
        cv2.line(frame, p1, p2, line_color, line_thickness)

        # 4. Hòa trộn overlay vào ảnh gốc (alpha=0.2 giúp màu rất nhẹ, không che mất mặt đường)
        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)

        # 5. Vẽ vùng check đèn (ROI)
        rx, ry, rw, rh = self.config['light_roi']
        light_color = (0, 0, 255) if status == "RED" else (0, 255, 0)
        cv2.rectangle(frame, (rx, ry), (rx + rw, ry + rh), light_color, 2)
        cv2.putText(frame, f"LIGHT: {status}", (rx, ry - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, light_color, 2)

        # Nếu đèn đỏ, vẽ thêm một mảng đỏ mỏng ngay trên vạch để cảnh báo
        if status == "RED":
            cv2.line(frame, p1, p2, (0, 0, 255), 5)  # Vạch đỏ đậm
        else:
            cv2.line(frame, p1, p2, (255, 255, 255), 2)  # Vạch trắng bình thường

        # Hòa trộn mảng màu xanh vào ảnh gốc (độ trong suốt 0.3)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # 3. Vẽ vùng check đèn (ROI) như cũ
        x, y, w, h = self.config['light_roi']
        color = (0, 0, 255) if status == "RED" else (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, f"LIGHT: {status}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)