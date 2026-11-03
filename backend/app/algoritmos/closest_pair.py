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
    depth: int = 0,
    side: str = "RAIZ",
) -> Tuple[List[Dict[str, Any]], float, Optional[Tuple[Dict[str, Any], Dict[str, Any]]]]:

    n = len(points_sorted_by_x)
    indent = "  " * depth
    ids = [f"#{p['id']}" for p in points_sorted_by_x]

    # CASO BASE
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
        pair_str = f"(#{best_pair[0]['id']}, #{best_pair[1]['id']})" if best_pair else "Vazio"
        dist_str = f"{min_dist:.6f}" if min_dist != float("inf") else "inf"
        print(f"{indent}[CASO BASE - {side}] Pontos: {ids} | Par: {pair_str} | delta = {dist_str}")
        return points_sorted_by_y, min_dist, best_pair

    # 1. DIVIDIR
    mid = n // 2
    left_half = points_sorted_by_x[:mid]
    right_half = points_sorted_by_x[mid:]

    line_l_x = (left_half[-1]["x"] + right_half[0]["x"]) / 2.0
    division_lines.append(line_l_x)

    print(f"{indent}[DIVISAO - {side}] n={n} {ids} | Linha L (X = {line_l_x:.5f})")

    # 2. CONQUISTAR
    left_by_y, delta1, pair1 = sort_and_closest_pair(
        left_half, division_lines, checked_pairs, depth + 1, "ESQ"
    )
    right_by_y, delta2, pair2 = sort_and_closest_pair(
        right_half, division_lines, checked_pairs, depth + 1, "DIR"
    )

    if delta1 <= delta2:
        delta = delta1
        best_pair = pair1
    else:
        delta = delta2
        best_pair = pair2

    # 3. COMBINAR
    all_points_by_y = merge_by_y(left_by_y, right_by_y)

    strip = [p for p in all_points_by_y if abs(p["x"] - line_l_x) < delta]
    strip_ids = [f"#{p['id']}" for p in strip]

    improved_in_strip = False
    strip_len = len(strip)
    for i in range(strip_len):
        for j in range(i + 1, min(i + 8, strip_len)):
            p1, p2 = strip[i], strip[j]
            d = euclidean_distance(p1, p2)
            checked_pairs.append((p1["id"], p2["id"]))

            if d < delta:
                delta = d
                best_pair = (p1, p2)
                improved_in_strip = True

    pair_str = f"(#{best_pair[0]['id']}, #{best_pair[1]['id']})" if best_pair else "Nenhum"
    status_strip = "Atualizado na faixa" if improved_in_strip else "Manteve melhor das metades"
    print(
        f"{indent}[COMBINACAO - {side}] Faixa (2*delta): {strip_ids} "
        f"| Menor par: {pair_str} (delta = {delta:.6f}) [{status_strip}]"
    )

    return all_points_by_y, delta, best_pair


def find_closest_pair(points: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(points) < 2:
        raise ValueError("Sao necessarios pelo menos 2 pontos para encontrar o par mais proximo.")

    normalized_points = []
    for p in points:
        lat = float(p.get("lat") if p.get("lat") is not None else p.get("latitude"))
        lon = float(p.get("lon") if p.get("lon") is not None else p.get("longitude"))
        normalized_points.append({
            **p,
            "lat": lat,
            "lon": lon,
            "x": lon,
            "y": lat,
        })

    points_sorted_by_x = sorted(normalized_points, key=lambda p: p["x"])

    print("\n------ CLOSEST PAIR OF POINTS (DIVIDIR E CONQUISTAR) ------")
    print(f"Total de pontos analisados: {len(normalized_points)}")
    print(
        "Ordenacao inicial por X (Longitude): "
        + " -> ".join([f"#{p['id']} ({p['x']:.4f})" for p in points_sorted_by_x])
    )
    print("-----------------------------------------------------------")

    division_lines: List[float] = []
    checked_pairs: List[Tuple[Any, Any]] = []

    _, delta, best_pair = sort_and_closest_pair(
        points_sorted_by_x, division_lines, checked_pairs
    )

    p1, p2 = best_pair
    distance_m = haversine_meters(p1["lat"], p1["lon"], p2["lat"], p2["lon"])

    print("-----------------------------------------------------------")
    print(f"Par mais proximo encontrado: Pedido #{p1['id']} e Pedido #{p2['id']}")
    print(f"Distancia Euclidiana (2D):   {delta:.6f} graus")
    print(f"Distancia Real (Haversine):  {distance_m:.2f} m ({distance_m / 1000.0:.3f} km)")
    print(f"Comparacoes realizadas:      {len(checked_pairs)}")
    print("-----------------------------------------------------------\n")

    return {
        "point1": p1,
        "point2": p2,
        "euclidean_distance_deg": delta,
        "distance_meters": round(distance_m, 2),
        "distance_km": round(distance_m / 1000.0, 3),
        "division_lines_lon": division_lines,
        "checked_pairs": checked_pairs,
        "total_points": len(normalized_points),
    }