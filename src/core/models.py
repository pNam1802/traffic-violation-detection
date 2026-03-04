# src/core/models.py
import os
from ultralytics import YOLO
from paddleocr import PaddleOCR
import streamlit as st

# Workaround cho lỗi oneDNN/PIR trên một số bản PaddlePaddle (Windows CPU)
os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("FLAGS_enable_pir_api", "0")

class ModelManager:
    @st.cache_resource
    def get_vehicle_model(_self, path):
        return YOLO(path)

    @st.cache_resource
    def get_plate_model(_self, path):
        return YOLO(path)

    @st.cache_resource
    def get_ocr_service(_self):
        # Khởi tạo OCR với fallback theo phiên bản PaddleOCR
        # Ưu tiên tắt mkldnn để tránh NotImplementedError ở onednn_instruction
        # Tắt document preprocessor vì license plates không cần
        init_options = [
            {"lang": "en", "enable_mkldnn": False, "use_angle_cls": False, 
             "use_doc_orientation_classify": False, "use_doc_unwarping": False},
            {"lang": "en", "enable_mkldnn": False, "use_angle_cls": False},
            {"lang": "en", "enable_mkldnn": False},
            {"lang": "en", "use_angle_cls": False},
            {"lang": "en"},
        ]

        last_error = None
        for kwargs in init_options:
            try:
                return PaddleOCR(**kwargs)
            except Exception as exc:
                last_error = exc

        raise RuntimeError(f"Không thể khởi tạo PaddleOCR: {last_error}")