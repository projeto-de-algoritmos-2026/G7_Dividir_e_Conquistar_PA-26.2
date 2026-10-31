"""Regression tests for manual delivery queue evaluation."""

import importlib.util
from itertools import permutations
from pathlib import Path
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.algoritmos.count_inversions import count_inversions, evaluate_manual_route


class InversionCountTests(unittest.TestCase):
    def setUp(self):
        self.orders = [
            {"id": 42, "deadline": "2026-10-31T12:00:00"},
            {"id": 7, "deadline": "2026-10-31T10:00:00"},
            {"id": 19, "deadline": "2026-10-31T11:00:00"},
        ]

    def test_all_permutations_up_to_seven_items(self):
        for size in range(8):
            for sequence in permutations(range(size)):
                values = list(sequence)
                expected = sum(
                    values[left] > values[right]
                    for left in range(size)
                    for right in range(left + 1, size)
                )
                self.assertEqual(count_inversions(values), expected)
                self.assertEqual(values, list(sequence))

    def test_repeated_values_and_large_reverse(self):
        self.assertEqual(count_inversions([2, 2, 1]), 2)
        self.assertEqual(count_inversions(list(range(10000, 0, -1))), 49995000)

    def test_ideal_and_reverse_routes_use_deadlines_not_numeric_ids(self):
        ideal = evaluate_manual_route(self.orders, [7, 19, 42])
        self.assertEqual(ideal["inversions"], 0)
        self.assertEqual(ideal["efficiencyScore"], 100)
        self.assertEqual(ideal["riskLevel"], "perfect")
        reverse = evaluate_manual_route(self.orders, [42, 19, 7])
        self.assertEqual(reverse["inversions"], 3)
        self.assertEqual(reverse["maxInversions"], 3)
        self.assertEqual(reverse["efficiencyScore"], 0)
        self.assertEqual(reverse["riskLevel"], "high")

    def test_risk_thresholds(self):
        self.assertEqual(evaluate_manual_route(self.orders, [19, 7, 42])["riskLevel"], "low")
        self.assertEqual(evaluate_manual_route(self.orders, [19, 42, 7])["riskLevel"], "moderate")

    def test_empty_and_single_order(self):
        for orders, queue in (([], []), (self.orders[:1], [42])):
            result = evaluate_manual_route(orders, queue)
            self.assertEqual(result["inversions"], 0)
            self.assertEqual(result["maxInversions"], 0)
            self.assertEqual(result["efficiencyScore"], 100)

    def test_invalid_permutations(self):
        for queue in ([7, 7, 42], [7, 19], [7, 19, 99], [7, 19, 42, 99]):
            with self.subTest(queue=queue), self.assertRaises(ValueError):
                evaluate_manual_route(self.orders, queue)
        with self.assertRaises(ValueError):
            evaluate_manual_route([self.orders[0], self.orders[0]], [42, 42])

    def test_tied_deadlines_preserve_the_existing_edf_reference(self):
        orders = [{"id": order_id, "deadline": "2026-10-31T10:00:00"} for order_id in [42, 7]]
        self.assertEqual(evaluate_manual_route(orders, [42, 7])["inversions"], 0)
        self.assertEqual(evaluate_manual_route(orders, [7, 42])["inversions"], 1)


class ManualRouteEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Load algorithm routes without unrelated auth/database initializers."""
        route_file = Path(__file__).resolve().parents[1] / "app" / "routes" / "algoritmos.py"
        spec = importlib.util.spec_from_file_location("algorithm_routes_test", route_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        app = FastAPI()
        app.include_router(module.router)
        cls.client = TestClient(app)

    def setUp(self):
        self.payload = {
            "orders": [
                {"id": 7, "deadline": "2026-10-31T09:30:00"},
                {"id": 19, "deadline": "2026-10-31T10:00:00"},
                {"id": 42, "deadline": "2026-10-31T12:00:00"},
            ],
            "manualOrderIds": [42, 19, 7],
            "startTime": "2026-10-31T09:00:00",
            "segmentDurationsMinutes": [10, 20, 30],
            "serviceTimeMinutes": 0,
        }

    def test_endpoint_preserves_manual_sequence_and_recalculates_schedule(self):
        response = self.client.post("/api/schedule/count-inversions", json=self.payload)
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["inversions"], 3)
        schedule = result["scheduleResult"]
        self.assertEqual([item["orderId"] for item in schedule["schedule"]], [42, 19, 7])
        self.assertEqual(schedule["totalServiceMinutes"], 0)
        self.assertEqual(schedule["endTimeFormatted"], "10:00")
        self.assertEqual(schedule["maxLatenessMinutes"], 30)

    def test_endpoint_rejects_bad_queues_and_durations(self):
        for changes in (
            {"manualOrderIds": [42, 42, 7]},
            {"manualOrderIds": [42, 19, 999]},
            {"segmentDurationsMinutes": [-1, 2, 3]},
            {"segmentDurationsMinutes": [10]},
            {"serviceTimeMinutes": -1},
        ):
            with self.subTest(changes=changes):
                response = self.client.post("/api/schedule/count-inversions", json={**self.payload, **changes})
                self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()