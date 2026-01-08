import cv2
import numpy as np

def is_passed_line(point, line):
    """
    Kiểm tra điểm đã vượt qua đường thẳng chưa bằng Cross Product.
    """
    (x, y) = point
    (x1, y1), (x2, y2) = line
    val = (y - y1) * (x2 - x1) - (x - x1) * (y2 - y1)
    return val < 0

def is_inside_lane(point, lane_polygon):
    """
    Kiểm tra điểm có nằm trong vùng đa giác của làn đường không.
    """
    polygon = np.array(lane_polygon, dtype=np.int32)
    # result: 1 (trong), 0 (trên cạnh), -1 (ngoài)
    result = cv2.pointPolygonTest(polygon, (float(point[0]), float(point[1])), False)
    return result >= 0