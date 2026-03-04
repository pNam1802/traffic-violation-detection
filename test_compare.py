"""
Test so sánh nhiều ảnh và ngưỡng khác nhau
"""
from models.test_plate_ocr import test_image

print("\n" + "="*70)
print("TEST SO SÁNH NHIỀU ẢNH VÀ NGƯỠNG")
print("="*70)

# 1. Test aaa.jpg với ngưỡng thấp hơn
print("\n\n🔍 TEST 1: aaa.jpg với plate_conf=0.15 (thấp hơn)")
test_image("models/test/aaa.jpg", plate_conf=0.15, max_vehicles=5)

print("\n\n🔍 TEST 2: aaa.jpg với plate_conf=0.1 (rất thấp)")
test_image("models/test/aaa.jpg", plate_conf=0.1, vehicle_conf=0.3, max_vehicles=5)

# 2. Test với ảnh khác có nhiều xe
print("\n\n🔍 TEST 3: traffic1.jpg (nhiều xe)")
test_image("models/test/traffic1.jpg", max_vehicles=5)

# 3. Test với ảnh biển số rõ
print("\n\n🔍 TEST 4: lp5.webp (ảnh biển số rõ)")
test_image("models/test2/lp5.webp", max_vehicles=3)

print("\n\n" + "="*70)
print("✅ ĐÃ HOÀN THÀNH TẤT CẢ TEST!")
print("💾 Xem kết quả ảnh trong: models/test_output/plate_ocr/")
print("="*70)
