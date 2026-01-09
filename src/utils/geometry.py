import cv2
import numpy as np

def is_inside_polygon(point, polygon_coords):
    if polygon_coords is None or len(polygon_coords) < 3:
        return False
    # Đảm bảo format cho OpenCV
    polygon = np.array(polygon_coords, dtype=np.int32)
    # result: 1 (trong), 0 (trên cạnh), -1 (ngoài)
    result = cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), False)
    return result >= 0