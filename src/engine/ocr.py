# src/engine/ocr.py
import cv2

class OCRService:
    def __init__(self, ocr_model):
        self.ocr = ocr_model

    def preprocess_plate_image(self, plate_img):
        """Tiền xử lý ảnh biển số để cải thiện OCR"""
        if plate_img is None or plate_img.size == 0:
            return None
        
        h, w = plate_img.shape[:2]
        
        # Upscale mạnh nếu ảnh quá nhỏ
        if h < 100:
            # Scale lên ít nhất 150px chiều cao
            scale = max(2.0, 150 / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            plate_img = cv2.resize(plate_img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # Chuyển sang grayscale
        if len(plate_img.shape) == 3:
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_img
        
        # Tăng contrast bằng CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Thresholding để làm biển rõ hơn
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphology để fill holes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Chuyển lại sang BGR cho PaddleOCR
        result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        return result

    def process_plate_text(self, plate_img):
        """Nhận diện text từ ảnh biển số"""
        if plate_img is None or plate_img.size == 0:
            return "Unknown"

        try:
            # Tiền xử lý ảnh
            processed_img = self.preprocess_plate_image(plate_img)
            if processed_img is None:
                return "Unknown"
            
            # Gọi OCR
            result = self.ocr.ocr(processed_img)
            
            # Debug: check if image was rotated
            if result and result[0] and isinstance(result[0], dict):
                angle = result[0].get('angle', 0)
                if abs(angle) > 45:
                    print(f"[OCR Debug] ⚠️  Image rotated: {angle}°")

            # Kiểm tra kết quả
            if not result or not result[0]:
                return "Unknown"

            ocr_result = result[0]
            texts = []

            # Format 1: Dict với rec_texts / rec_scores (PaddleX/PaddleOCR mới)
            if isinstance(ocr_result, dict) and "rec_texts" in ocr_result and "rec_scores" in ocr_result:
                for text, conf in zip(ocr_result['rec_texts'], ocr_result['rec_scores']):
                    if conf > 0.2 and str(text).strip():
                        texts.append(str(text).strip())
            
            # Format 2: OCRResult object
            elif hasattr(ocr_result, "rec_texts") and hasattr(ocr_result, "rec_scores"):
                for text, conf in zip(ocr_result.rec_texts, ocr_result.rec_scores):
                    if conf > 0.2 and str(text).strip():
                        texts.append(str(text).strip())
            
            # Format 3: List cũ
            elif isinstance(ocr_result, list):
                for line in ocr_result:
                    if len(line) >= 2 and isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                        text = line[1][0]
                        conf = line[1][1]
                        if conf > 0.2 and str(text).strip():
                            texts.append(str(text).strip())

            if not texts:
                return "Unknown"
            
            # Kết hợp text
            combined = "".join(texts).upper().strip()
            
            return combined if combined else "Unknown"

        except Exception as e:
            print(f"[OCR Error] {str(e)}")
            return "Unknown"