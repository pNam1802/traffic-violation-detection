import os
from typing import Dict, List, Optional

import cv2


def test_plate_ocr_on_image(
    detector,
    image_path: str,
    vehicle_conf: float = 0.35,
    plate_conf: float = 0.25,
    max_vehicles: int = 10,
    save_dir: Optional[str] = None,
) -> Dict:
    """Test riêng khả năng nhận diện biển số + OCR trên 1 ảnh.

    Args:
        detector: Instance TrafficDetector đã khởi tạo model.
        image_path: Đường dẫn ảnh đầu vào.
        vehicle_conf: Ngưỡng confidence cho detect xe.
        plate_conf: Ngưỡng confidence cho detect biển số.
        max_vehicles: Số xe tối đa sẽ test trong ảnh.
        save_dir: Thư mục lưu ảnh crop/annotated (nếu cần).

    Returns:
        dict chứa summary và chi tiết từng xe.
    """
    if not os.path.exists(image_path):
        return {
            "image_path": image_path,
            "error": "Image not found",
            "vehicles_total": 0,
            "vehicles_tested": 0,
            "plates_found": 0,
            "results": [],
        }

    frame = cv2.imread(image_path)
    if frame is None:
        return {
            "image_path": image_path,
            "error": "Cannot read image",
            "vehicles_total": 0,
            "vehicles_tested": 0,
            "plates_found": 0,
            "results": [],
        }

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    vehicle_result = detector.v_model.predict(source=frame, conf=vehicle_conf, verbose=False)[0]
    total_vehicles = len(vehicle_result.boxes) if vehicle_result.boxes is not None else 0

    details: List[Dict] = []
    plates_found = 0
    annotated = frame.copy()

    if total_vehicles == 0:
        return {
            "image_path": image_path,
            "vehicles_total": 0,
            "vehicles_tested": 0,
            "plates_found": 0,
            "results": [],
        }

    boxes = vehicle_result.boxes.xyxy.cpu().numpy().astype(int)
    for idx, (x1, y1, x2, y2) in enumerate(boxes[:max_vehicles], start=1):
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)

        car_crop = frame[y1:y2, x1:x2]
        if car_crop.size == 0:
            details.append(
                {
                    "vehicle_index": idx,
                    "vehicle_bbox": [x1, y1, x2, y2],
                    "plate_detected": False,
                    "plate_text": "N/A",
                    "error": "Empty car crop",
                }
            )
            continue

        plate_text, plate_crop = detector.get_license_plate(car_crop, conf_threshold=plate_conf)
        has_plate = plate_crop is not None and plate_crop.size > 0 and plate_text not in ["N/A"]
        if has_plate:
            plates_found += 1

        details.append(
            {
                "vehicle_index": idx,
                "vehicle_bbox": [x1, y1, x2, y2],
                "vehicle_size": [int(car_crop.shape[1]), int(car_crop.shape[0])],
                "plate_detected": plate_crop is not None,
                "plate_text": plate_text,
                "plate_size": [int(plate_crop.shape[1]), int(plate_crop.shape[0])] if plate_crop is not None else None,
            }
        )

        color = (0, 255, 0) if has_plate else (0, 0, 255)
        label = f"{idx}: {plate_text}"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, label, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

        if save_dir:
            car_path = os.path.join(save_dir, f"car_{idx}.jpg")
            cv2.imwrite(car_path, car_crop)
            if plate_crop is not None and plate_crop.size > 0:
                plate_path = os.path.join(save_dir, f"car_{idx}_plate.jpg")
                cv2.imwrite(plate_path, plate_crop)

    if save_dir:
        annotated_path = os.path.join(save_dir, "annotated.jpg")
        cv2.imwrite(annotated_path, annotated)

    return {
        "image_path": image_path,
        "vehicles_total": total_vehicles,
        "vehicles_tested": min(total_vehicles, max_vehicles),
        "plates_found": plates_found,
        "results": details,
    }


def test_plate_ocr_on_folder(
    detector,
    folder_path: str,
    vehicle_conf: float = 0.35,
    plate_conf: float = 0.25,
    max_vehicles_per_image: int = 10,
    save_root: Optional[str] = None,
) -> List[Dict]:
    """Test riêng khả năng nhận diện biển số + OCR trên toàn bộ ảnh trong thư mục."""
    if not os.path.isdir(folder_path):
        return []

    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".bmp"))
    ]
    image_files.sort()

    reports: List[Dict] = []
    for file_name in image_files:
        image_path = os.path.join(folder_path, file_name)
        image_save_dir = None
        if save_root:
            image_save_dir = os.path.join(save_root, os.path.splitext(file_name)[0])

        report = test_plate_ocr_on_image(
            detector=detector,
            image_path=image_path,
            vehicle_conf=vehicle_conf,
            plate_conf=plate_conf,
            max_vehicles=max_vehicles_per_image,
            save_dir=image_save_dir,
        )
        reports.append(report)

    return reports
