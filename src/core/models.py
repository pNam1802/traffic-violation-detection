# src/core/models.py
from ultralytics import YOLO
from paddleocr import PaddleOCR
import streamlit as st

class ModelManager:
    @st.cache_resource
    def get_vehicle_model(_self, path):
        return YOLO(path)

    @st.cache_resource
    def get_plate_model(_self, path):
        return YOLO(path)

    @st.cache_resource
    def get_ocr_service(_self):
        # Không truyền bất kỳ tham số bổ sung nào để tránh ValueError
        # PaddleOCR sẽ tự động nhận diện CPU/GPU và các cấu hình mặc định
        return PaddleOCR(lang='en')