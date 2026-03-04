import os
import sys
import cv2

# Setup path để import từ src
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.models import ModelManager
from src.engine.detector import TrafficDetector

def simple_test(image_path: str, vehicle_conf=0.35, plate_conf=0.25, save_output=True):
    """
    Test đơn giản để nhận diện biển số từ ảnh.
    
    Args:
        image_path: Đường dẫn ảnh
        vehicle_conf: Ngưỡng detect xe (0-1)
        plate_conf: Ngưỡng detect biển (0-1)
        save_output: Có lưu ảnh kết quả không
    """
    print("⏳ Loading models...")
    
    model_manager = ModelManager()
    vehicle_model = model_manager.get_vehicle_model("models/vehicle_detect.pt")
    plate_model = model_manager.get_plate_model("models/license_plate_detect.pt")
    ocr_model = model_manager.get_ocr_service()
    
    detector = TrafficDetector(vehicle_model, plate_model, ocr_model)
    
    print(f"🚀 Đang xử lý: {image_path}\n")
    
    # Đọc ảnh
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Không đọc được ảnh: {image_path}")
        return
    
    # Tạo thư mục output nếu cần
    output_dir = None
    if save_output:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = f"models/test_output/simple_test/{base_name}"
        os.makedirs(output_dir, exist_ok=True)
    
    # Detect xe
    vehicle_results = vehicle_model.predict(source=img, conf=vehicle_conf, verbose=False)[0]
    
    if len(vehicle_results.boxes) == 0:
        print("❌ Không tìm thấy xe nào trong ảnh")
        return
    
    print(f"✅ Tìm thấy {len(vehicle_results.boxes)} xe\n")
    print("=" * 60)
    
    # Tạo ảnh annotated
    annotated_img = img.copy()
    
    # Xử lý từng xe
    for i, box in enumerate(vehicle_results.boxes, 1):
        xyxy = box.xyxy.cpu().numpy()[0].astype(int)
        x1, y1, x2, y2 = xyxy
        
        # Crop xe
        car_crop = img[y1:y2, x1:x2]
        
        # Detect biển số
        plate_text, plate_crop = detector.get_license_plate(car_crop, conf_threshold=plate_conf)
        
        # In kết quả
        status = "✅" if plate_text not in ["N/A", "Unknown"] else "⚠️" if plate_text == "Unknown" else "❌"
        print(f"Xe #{i:2d}: {status} Biển số: '{plate_text}'")
        
        if plate_crop is not None:
            h, w = plate_crop.shape[:2]
            print(f"        └─ Kích thước biển: {w}x{h}px")
        
        # Lưu ảnh nếu cần
        if save_output and output_dir:
            # Lưu ảnh xe crop
            cv2.imwrite(f"{output_dir}/car_{i}.jpg", car_crop)
            
            # Lưu ảnh biển số crop nếu có
            if plate_crop is not None:
                cv2.imwrite(f"{output_dir}/car_{i}_plate.jpg", plate_crop)
            
            # Vẽ box lên ảnh annotated
            color = (0, 255, 0) if plate_text not in ["N/A", "Unknown"] else (0, 165, 255) if plate_text == "Unknown" else (0, 0, 255)
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), color, 3)
            cv2.putText(annotated_img, f"#{i}: {plate_text}", (x1, max(15, y1-10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    # Lưu ảnh annotated
    if save_output and output_dir:
        cv2.imwrite(f"{output_dir}/annotated.jpg", annotated_img)
        print("\n" + "=" * 60)
        print(f"💾 Ảnh đã lưu tại: {output_dir}")
        print(f"   - annotated.jpg (ảnh gốc có khung đánh dấu)")
        print(f"   - car_X.jpg (ảnh xe crop)")
        print(f"   - car_X_plate.jpg (ảnh biển số crop)")
    
    print("=" * 60)

if __name__ == "__main__":
    # Test với ảnh mặc định
    simple_test("models/test/aaa.jpg", vehicle_conf=0.3, plate_conf=0.1)
    
    # Thử thêm ảnh khác (uncomment để test)
    # simple_test("models/test/traffic1.jpg")
    # simple_test("models/test2/lp5.webp")