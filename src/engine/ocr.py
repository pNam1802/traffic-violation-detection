# src/engine/ocr.py

class OCRService:
    def __init__(self, ocr_model):
        self.ocr = ocr_model

    def process_plate_text(self, plate_img):
        # Kiểm tra ảnh đầu vào có hợp lệ không
        if plate_img is None or plate_img.size == 0:
            return "plate None"

        try:
            result = self.ocr.ocr(plate_img)

            # Kiểm tra kết quả trả về từ PaddleOCR
            if not result or not result[0]:
                return "Unknown"

            # Trích xuất hộp tọa độ và nội dung văn bản
            # Cấu trúc result[0]: [[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, score)], ...]
            dt_boxes = [line[0] for line in result[0]] # tọa độ
            rec_res = [line[1] for line in result[0]] # text and score

            # Kiểm tra dt_boxes có dữ liệu và đúng định dạng trước khi sắp xếp
            if not dt_boxes or not all(isinstance(box, (list, tuple)) and len(box) > 0 for box in dt_boxes):
                return "Unknown format"

            # Sắp xếp theo y (dòng) rồi đến x (cột) để xử lý biển 2 dòng
            # Dùng .get() hoặc kiểm tra index thủ công để tránh lỗi out of range
            sorted_indices = sorted(
                range(len(dt_boxes)),
                key=lambda i: (dt_boxes[i][0][1], dt_boxes[i][0][0])
            )

            combined_text = []
            for i in sorted_indices:
                text = rec_res[i][0]
                conf = rec_res[i][1]
                if conf > 0.4:  # Chỉ lấy kết quả có độ tin cậy > 40%
                    combined_text.append(str(text))

            return " ".join(combined_text).upper() if combined_text else "Unknown"

        except Exception as e:
            print(f"Lỗi xử lý OCR: {e}")
            return "orc error"