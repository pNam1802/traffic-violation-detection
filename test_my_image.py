"""
File demo đơn giản để test nhận diện biển số + OCR
Chỉ cần sửa đường dẫn ảnh và chạy!
"""

from models.test_plate_ocr import test_image

# ========================================
# THAY ĐỔI ĐƯỜNG DẪN ẢNH Ở ĐÂY:
# ========================================

# Ví dụ 1: Test với ảnh mẫu
test_image("models/test/traffic1.jpg")

# Ví dụ 2: Test với ảnh khác
# test_image("models/test2/lp5.webp")

# Ví dụ 3: Test với ảnh của bạn
# test_image("D:/Pictures/my_traffic_photo.jpg")

# Tùy chỉnh thêm tham số:
# test_image(
#     "models/test/traffic3.jpg",
#     vehicle_conf=0.4,      # Ngưỡng detect xe (0-1)
#     plate_conf=0.3,        # Ngưỡng detect biển số (0-1) 
#     max_vehicles=5,        # Số xe tối đa test
#     save_output=True       # Có lưu ảnh kết quả không
# )
