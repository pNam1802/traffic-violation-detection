import cv2
import streamlit as st
import numpy as np
from datetime import datetime
import os
# Import từ cấu trúc thư mục mới
from src.engine.detector import TrafficDetector
from src.engine.violation import ViolationEngine
from src.utils.config_loader import load_config
from src.core.models import ModelManager

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Phát hiện Vi phạm", layout="wide")


# --- 2. KHỞI TẠO MODELS (CACHE) ---
@st.cache_resource
def init_system():
    mm = ModelManager()
    vehicle_model = mm.get_vehicle_model('models/vehicle_detect.pt')
    plate_model = mm.get_plate_model('models/license_plate_detect.pt')
    ocr_model = mm.get_ocr_service()

    detector = TrafficDetector(vehicle_model, plate_model, ocr_model)
    return detector


detector = init_system()

# --- 3. LOAD CONFIG & STATE ---
config = load_config("data/config.json")
if "violations" not in st.session_state:
    st.session_state.violations = []  # Lưu danh sách vi phạm tạm thời

# --- 4. GIAO DIỆN SIDEBAR ---
st.sidebar.title("🎮 Điều khiển")
video_file = st.sidebar.file_uploader("Tải video giao thông", type=["mp4", "avi", "mov"])
process_btn = st.sidebar.button("Bắt đầu xử lý")

# Hiển thị danh sách vi phạm bên sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🚨 Danh sách vi phạm mới")
violation_container = st.sidebar.container()

# --- 5. GIAO DIỆN CHÍNH ---
st.title("🚦 Giám sát Giao thông Real-time")

col_video, col_info = st.columns([3, 1])

with col_video:
    st_frame = st.empty()  # Khung hình video

with col_info:
    st.subheader("Trạng thái hệ thống")
    st_light = st.empty()
    st_fps = st.empty()

# --- 6. LOGIC XỬ LÝ CHÍNH ---
if video_file and process_btn:
    # --- THÊM ĐOẠN NÀY ĐỂ TỰ TẠO THƯ MỤC ---
    temp_dir = "data/temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    temp_video_path = os.path.join(temp_dir, "temp_video.mp4")

    # Lưu file
    with open(temp_video_path, "wb") as f:
        f.write(video_file.getbuffer())

    cap = cv2.VideoCapture("data/temp/temp_video.mp4")

    # Khởi tạo engine vi phạm
    engine = ViolationEngine(detector, config)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Xử lý frame qua Engine
        # Trả về: frame đã vẽ, danh sách vi phạm mới trong frame đó, và trạng thái đèn
        processed_frame, new_violations, light_status = engine.process_frame(frame)

        # Cập nhật danh sách vi phạm vào session_state
        for v in new_violations:
            v['time'] = datetime.now().strftime("%H:%M:%S")
            st.session_state.violations.insert(0, v)  # Thêm vào đầu danh sách

            # Hiển thị nhanh lên sidebar
            with violation_container.expander(f"Xe ID: {v['id']} - {v['plate']}"):
                st.image(cv2.cvtColor(v['image'], cv2.COLOR_BGR2RGB))
                st.write(f"Thời gian: {v['time']}")

        # Hiển thị trạng thái đèn lên UI
        light_color = "🔴 ĐỎ" if light_status == "RED" else "🟢 XANH"
        st_light.metric("Trạng thái đèn", light_color)

        # Render frame lên Streamlit
        st_frame.image(cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB), channels="RGB")

    cap.release()
    st.success("Đã xử lý xong video!")
else:
    st.info("Vui lòng tải video và nhấn 'Bắt đầu xử lý' hoặc qua trang Cấu hình để thiết lập vạch dừng.")