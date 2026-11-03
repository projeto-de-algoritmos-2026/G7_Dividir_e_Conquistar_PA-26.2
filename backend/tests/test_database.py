import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app import database
from app.routes.auth import health_check


class DatabaseConnectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_configured_but_disconnected_health_reports_demo(self):
        with patch("app.routes.auth.db") as client, patch(
            "app.routes.auth.AuthService._is_configured", return_value=True
        ):
            client.is_connected.return_value = False
            health = await health_check()

        self.assertTrue(health["database_configured"])
        self.assertFalse(health["database_connected"])
        self.assertEqual(health["mode"], "demo_mock")

    async def test_failed_connection_disconnects_partial_engine(self):
        client = MagicMock()
        client.is_connected.side_effect = [False, True]
        client.connect = AsyncMock(side_effect=asyncio.TimeoutError)
        client.disconnect = AsyncMock()

        with patch.object(database, "db", client), patch.object(
            database, "DATABASE_URL", "postgresql://test"
        ):
            await database.connect_db()

        client.disconnect.assert_awaited_once()

    async def test_successful_connection_is_not_disconnected(self):
        client = MagicMock()
        client.is_connected.return_value = False
        client.connect = AsyncMock()
        client.disconnect = AsyncMock()

        with patch.object(database, "db", client), patch.object(
            database, "DATABASE_URL", "postgresql://test"
        ):
            await database.connect_db()

        client.connect.assert_awaited_once()
        client.disconnect.assert_not_awaited()