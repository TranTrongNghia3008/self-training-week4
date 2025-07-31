import unittest
from httpx import AsyncClient, ASGITransport
from app.main import app
from fastapi import status
import uuid

class UserTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.transport = ASGITransport(app=app)
        self.base_url = "http://test"
        self.username = f"testuser_{uuid.uuid4().hex[:6]}"
        self.email = f"{self.username}@example.com"
        self.password = "password123"

    async def test_register_login_refresh_logout(self):
        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            # Register
            response = await ac.post("/api/v1/users/register", json={
                "username": self.username,
                "email": self.email,
                "password": self.password
            })
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Login
            response = await ac.post("/api/v1/users/login", data={
                "username": self.username,
                "password": self.password
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            tokens = response.json()
            self.assertIn("access_token", tokens)
            self.assertIn("refresh_token", tokens)

            # Refresh (JSON body)
            response = await ac.post("/api/v1/users/refresh", json={
                "refresh_token": tokens["refresh_token"]
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            refreshed = response.json()
            self.assertIn("access_token", refreshed)
            self.assertIn("refresh_token", refreshed)

            # Logout (JSON body)
            response = await ac.post("/api/v1/users/logout", json={
                "refresh_token": refreshed["refresh_token"]
            })
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json()["message"], "Logout successful")
