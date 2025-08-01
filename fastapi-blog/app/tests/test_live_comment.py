import unittest
import uuid
import asyncio
import json
import websockets

import httpx

from app.db.session import SessionLocal
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.token import RefreshToken
from app.core.security import create_access_token

class LiveCommentWebSocketTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = SessionLocal()
        self.base_url = "http://localhost:8000"

        # Tạo user test
        self.username = f"user_{uuid.uuid4().hex[:6]}"
        self.test_user = User(
            username=self.username,
            email=f"{self.username}@example.com",
            hashed_password="fakehashed"
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

        # Tạo JWT token
        token = create_access_token({"sub": str(self.test_user.id)})
        self.auth_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Tạo post test
        self.test_post = Post(
            title="Post for WS",
            content="WS content",
            author_id=self.test_user.id
        )
        self.db.add(self.test_post)
        self.db.commit()
        self.db.refresh(self.test_post)

        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def test_create_update_delete_comment_broadcast(self):
        try:
            uri = f"ws://host.docker.internal:8000/api/v1/ws/comments/{self.test_post.id}"

            async with websockets.connect(uri) as websocket:
                await asyncio.sleep(0.2)

                # Gửi comment mới
                response = await self.client.post(
                    f"/api/v1/blog/comments/post/{self.test_post.id}",
                    json={"content": "Live comment"},
                    headers=self.auth_headers
                )
                await asyncio.sleep(0.5)
                self.assertEqual(response.status_code, 201)
                new_comment = response.json()

                # Recieve broadcast new comment
                message = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(message)
                print("Received WS message:", data)

                self.assertEqual(data["type"], "new_comment")
                self.assertEqual(data["data"]["content"], "Live comment")

                # Update comment
                response = await self.client.put(
                    f"/api/v1/blog/comments/{new_comment['id']}",
                    json={"content": "Updated live comment"},
                    headers=self.auth_headers
                )
                self.assertEqual(response.status_code, 200)

                # Nhận broadcast cập nhật
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                print("Received WS message:", data)

                self.assertEqual(data["type"], "update_comment")
                self.assertEqual(data["data"]["content"], "Updated live comment")

                # Xoá comment
                response = await self.client.delete(
                    f"/api/v1/blog/comments/{new_comment['id']}",
                    headers=self.auth_headers
                )
                self.assertEqual(response.status_code, 200)

                # Nhận broadcast xoá
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                print("Received WS message:", data)

                self.assertEqual(data["type"], "delete_comment")
                self.assertEqual(data["data"]["id"], new_comment["id"])

        except Exception as e:
            print(f"WebSocket test failed: {e}")
            raise

    async def asyncTearDown(self):
        await self.client.aclose()
        self.db.query(RefreshToken).delete()
        self.db.query(Comment).delete()
        self.db.query(Post).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
