import cv2
import json
import os
import numpy as np


def calibrate(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Không thể đọc video!")
        return

    # --- CẢI TIẾN: Resize để hiển thị vừa màn hình ---
    original_h, original_w = frame.shape[:2]
    display_w = 1280
    display_h = int(original_h * (display_w / original_w))
    display_frame = cv2.resize(frame, (display_w, display_h))

    # Bản copy để vẽ mà không bị chồng chéo
    temp_canvas = display_frame.copy()

    if not os.path.exists('data'):
        os.makedirs('data')

    # Bước 1: Chọn vùng Đèn giao thông
    print("--- BƯỚC 1: Quét vùng ĐÈN GIAO THÔNG rồi nhấn ENTER ---")
    roi_resized = cv2.selectROI("Calibration", display_frame, fromCenter=False, showCrosshair=True)

    # Bước 2: Chọn vùng giới hạn làn (4 điểm)
    print("--- BƯỚC 2: Click 4 ĐIỂM để tạo VÙNG LÀN ĐƯỜNG (Polygon). ---")
    print("Gợi ý: Click theo thứ tự vòng tròn. Nhấn phím bất kỳ sau khi chọn đủ 4 điểm.")

    points_resized = []

    def click_event(event, x, y, flags, param):
        nonlocal temp_canvas
        if event == cv2.EVENT_LBUTTONDOWN:
            if len(points_resized) < 4:
                points_resized.append([x, y])
                # Vẽ điểm
                cv2.circle(temp_canvas, (x, y), 5, (0, 0, 255), -1)

                # Vẽ đường nối nếu có từ 2 điểm trở lên
                if len(points_resized) > 1:
                    cv2.line(temp_canvas, tuple(points_resized[-2]), tuple(points_resized[-1]), (0, 255, 0), 2)

                # Nối điểm cuối với điểm đầu khi đủ 4 điểm
                if len(points_resized) == 4:
                    cv2.line(temp_canvas, tuple(points_resized[3]), tuple(points_resized[0]), (0, 255, 0), 2)
                    print("Đã nhận đủ 4 điểm. Nhấn phím bất kỳ để lưu.")

                cv2.imshow("Calibration", temp_canvas)

    cv2.setMouseCallback("Calibration", click_event)
    cv2.imshow("Calibration", temp_canvas)
    cv2.waitKey(0)

    # --- QUAN TRỌNG: Quy đổi tọa độ về kích thước gốc ---
    scale = original_w / display_w

    # --- THAY THẾ TỪ ĐOẠN NÀY ---
    if len(points_resized) == 4:
        # 1. Quy đổi ROI đèn
        light_roi = [int(i * scale) for i in roi_resized]

        # 2. Quy đổi 4 điểm vùng làn đường
        lane_polygon = [[int(pt[0] * scale), int(pt[1] * scale)] for pt in points_resized]

        # 3. Xác định vạch dừng (Cạnh đầu tiên: Điểm 0 và Điểm 1)
        stop_line = [lane_polygon[0], lane_polygon[1]]

        # 4. TỰ ĐỘNG TẠO VIOLATION_ZONE (Vùng vi phạm)
        # Vì xe đi từ TRÊN xuống, vùng vi phạm sẽ nằm giữa vạch dừng và phần cuối làn đường
        # Chúng ta sẽ lấy 2 điểm của vạch dừng và 2 điểm cuối cùng của lane_polygon
        # Điều này giúp vùng vi phạm khớp hoàn toàn với hình dáng làn đường
        violation_zone = [
            lane_polygon[0],  # Trái trên (tại vạch dừng)
            lane_polygon[1],  # Phải trên (tại vạch dừng)
            lane_polygon[2],  # Phải dưới (cuối làn)
            lane_polygon[3]  # Trái dưới (cuối làn)
        ]

        config_data = {
            "light_roi": light_roi,
            "lane_polygon": lane_polygon,
            "stop_line": stop_line,
            "violation_zone": violation_zone  # Thêm cái này để hết lỗi KeyError
        }

        with open("data/config.json", "w") as f:
            json.dump(config_data, f, indent=4)

        print("\n" + "=" * 30)
        print("THÀNH CÔNG!")
        print(f"Vùng vi phạm (Violation Zone) đã được khởi tạo khớp với phần dưới làn đường.")
        print("=" * 30)
    else:
        print(f"Lỗi: Bạn mới chọn {len(points_resized)} điểm. Cần đúng 4 điểm!")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    calibrate("models/red_light_violation.mp4")