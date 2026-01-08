import cv2
import numpy as np


class TrafficLightService:
    @staticmethod
    def detect_color(frame, roi):
        """
        roi: [x, y, w, h] - Vùng chứa đèn giao thông
        """
        x, y, w, h = roi
        light_crop = frame[y:y + h, x:x + w]

        # Kiểm tra nếu vùng crop rỗng
        if light_crop.size == 0:
            return "UNKNOWN"

        hsv = cv2.cvtColor(light_crop, cv2.COLOR_BGR2HSV)

        # Định nghĩa dải màu đỏ trong không gian màu HSV
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2

        # Nếu tổng lượng pixel màu đỏ vượt ngưỡng (ví dụ 5% diện tích ROI)
        red_pixel_count = np.sum(red_mask) / 255
        if red_pixel_count > (w * h * 0.05):
            return "RED"
        return "GREEN"