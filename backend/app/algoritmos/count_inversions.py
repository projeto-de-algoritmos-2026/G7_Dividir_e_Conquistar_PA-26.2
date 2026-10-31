"""Evaluate a manual delivery queue using merge-sort inversion counting."""

from typing import Any, Dict, List

from app.algoritmos.minimize_lateness import sort_by_earliest_deadline


def count_inversions(values: List[int]) -> int:
    """Count reversed pairs in O(n log n) time without mutating the input."""
    ordered = list(values)
    buffer = list(values)

    def merge_count(start: int, end: int) -> int:
        if end - start < 2:
            return 0
        middle = (start + end) // 2
        inversions = merge_count(start, middle) + merge_count(middle, end)
        left, right = start, middle
        for position in range(start, end):
            if left < middle and (right >= end or ordered[left] <= ordered[right]):
                buffer[position] = ordered[left]
                left += 1
            else:
                buffer[position] = ordered[right]
                right += 1
                inversions += middle - left
        ordered[start:end] = buffer[start:end]
        return inversions

    return merge_count(0, len(ordered))


def evaluate_manual_route(orders: List[Dict[str, Any]], manual_order_ids: List[int]) -> Dict[str, Any]:
    """Compare a permutation of order IDs against the existing EDF queue."""
    ideal_order_ids = [order["id"] for order in sort_by_earliest_deadline(orders)]
    if len(set(ideal_order_ids)) != len(ideal_order_ids):
        raise ValueError("O lote contem IDs de pedidos duplicados.")
    if (len(manual_order_ids) != len(ideal_order_ids)
            or len(set(manual_order_ids)) != len(manual_order_ids)
            or set(manual_order_ids) != set(ideal_order_ids)):
        raise ValueError("A fila manual deve conter todos os pedidos do lote, sem duplicatas.")

    ideal_positions = {order_id: position for position, order_id in enumerate(ideal_order_ids)}
    inversions = count_inversions([ideal_positions[order_id] for order_id in manual_order_ids])
    maximum = len(orders) * (len(orders) - 1) // 2
    ratio = inversions / maximum if maximum else 0.0
    risk = "perfect" if inversions == 0 else "low" if ratio <= 1 / 3 else "moderate" if ratio <= 2 / 3 else "high"
    return {
        "idealOrderIds": ideal_order_ids,
        "manualOrderIds": manual_order_ids,
        "inversions": inversions,
        "maxInversions": maximum,
        "efficiencyScore": round(100 * (1 - ratio), 1),
        "riskLevel": risk,
    }