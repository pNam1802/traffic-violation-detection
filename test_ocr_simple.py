#!/usr/bin/env python
"""
Simple OCR Test Tool - Nhận diện biển xe từ ảnh

Cách sử dụng:
    python test_ocr_simple.py <image_path>
    python test_ocr_simple.py models/test/aaa.jpg
    python test_ocr_simple.py "C:/path/to/image.jpg"
"""

import sys
import os

# Setup path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from models.test_plate_ocr import simple_test

def main():
    if len(sys.argv) < 2:
        # Interactive mode
        print("=" * 60)
        print("🚗 OCR Test Tool - Nhận diện biển số xe")
        print("=" * 60)
        image_path = input("\n📸 Nhập đường dẫn ảnh (hoặc Enter để dùng mặc định): ").strip()
        
        if not image_path:
            image_path = "models/test/aaa.jpg"
            print(f"ℹ️  Sử dụng ảnh mặc định: {image_path}")
        
        vehicle_conf_str = input("🚗 Confidence xe (Enter=0.35): ").strip()
        vehicle_conf = float(vehicle_conf_str) if vehicle_conf_str else 0.35
        
        plate_conf_str = input("📋 Confidence biển (Enter=0.25): ").strip()
        plate_conf = float(plate_conf_str) if plate_conf_str else 0.25
    else:
        # Command line mode
        image_path = sys.argv[1]
        vehicle_conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.35
        plate_conf = float(sys.argv[3]) if len(sys.argv) > 3 else 0.25
    
    # Check file exists
    if not os.path.exists(image_path):
        print(f"❌ Lỗi: Không tìm thấy ảnh: {image_path}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"📸 Ảnh: {image_path}")
    print(f"🚗 Vehicle Confidence: {vehicle_conf}")
    print(f"📋 Plate Confidence: {plate_conf}")
    print(f"{'='*60}\n")
    
    # Run test
    try:
        simple_test(image_path, vehicle_conf=vehicle_conf, plate_conf=plate_conf, save_output=True)
        
        # Show output location
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = f"models/test_output/simple_test/{base_name}"
        
        print(f"\n{'='*60}")
        print(f"✅ Hoàn thành! Kết quả lưu tại:")
        print(f"   📁 {output_dir}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
