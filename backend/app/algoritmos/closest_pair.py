import math
from typing import List, Dict, Any, Tuple, Optional

def euclidean_distance(p1: Dict[str, Any], p2: Dict[str, Any]) -> float:
    dx = p1["x"] - p2["x"]
    dy = p1["y"] - p2["y"]
    return math.sqrt(dx * dx + dy * dy)

def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    return 2.0 * R * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

def merge_by_y(
    left: List[Dict[str, Any]], right: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    merged = []
    i, j = 0, 0
    
    while i < len(left) and j < len(right):
        if left[i]["y"] <= right[j]["y"]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged

def sort_and_closest_pair(
    points_sorted_by_x: List[Dict[str, Any]],
    division_lines: List[float],
    checked_pairs: List[Tuple[Any, Any]],
) -> Tuple[List[Dict[str, Any]], float, Optional[Tuple[Dict[str, Any], Dict[str, Any]]]]:
    
    n = len(points_sorted_by_x)

    if n <= 3:
        min_dist = float("inf")
        best_pair = None
        for i in range(n):
            for j in range(i + 1, n):
                p1, p2 = points_sorted_by_x[i], points_sorted_by_x[j]
                d = euclidean_distance(p1, p2)
                checked_pairs.append((p1["id"], p2["id"]))
                
                if d < min_dist:
                    min_dist = d
                    best_pair = (p1, p2)
                    
        points_sorted_by_y = sorted(points_sorted_by_x, key=lambda p: p["y"])
        return points_sorted_by_y, min_dist, best_pair

    mid = n // 2
    left_half = points_sorted_by_x[:mid]
    right_half = points_sorted_by_x[mid:]
    
    line_l_x = (left_half[-1]["x"] + right_half[0]["x"]) / 2.0
    division_lines.append(line_l_x)

    left_by_y, delta1, pair1 = sort_and_closest_pair(
        left_half, division_lines, checked_pairs
    )
    right_by_y, delta2, pair2 = sort_and_closest_pair(
        right_half, division_lines, checked_pairs
    )

    if delta1 <= delta2:
        delta = delta1
        best_pair = pair1
    else:
        delta = delta2
        best_pair = pair2

    all_points_by_y = merge_by_y(left_by_y, right_by_y)

    strip = [p for p in all_points_by_y if abs(p["x"] - line_l_x) < delta]

    strip_len = len(strip)
    for i in range(strip_len):
        for j in range(i + 1, min(i + 8, strip_len)):
            p1, p2 = strip[i], strip[j]
            d = euclidean_distance(p1, p2)
            checked_pairs.append((p1["id"], p2["id"]))
            
            if d < delta:
                delta = d
                best_pair = (p1, p2)

    return all_points_by_y, delta, best_pair