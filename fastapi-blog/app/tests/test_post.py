import unittest
import uuid
from unittest.mock import patch

from fastapi import status
from sqlalchemy.orm import Session
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import SessionLocal
from app.models.post import Post
from app.models.token import RefreshToken
from app.models.user import User
from app.models.comment import Comment
from app.models.media import Media
from app.core.dependencies import get_current_user


class PostTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db: Session = SessionLocal()
        self.transport = ASGITransport(app=app)
        self.base_url = "http://test"

        # Create test user
        self.unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
        self.test_user = User(
            username=self.unique_username,
            email=f"{self.unique_username}@example.com",
            hashed_password="hashed",  # should be mocked properly in production
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

        # Override get_current_user
        app.dependency_overrides[get_current_user] = lambda: self.test_user

    @patch("app.api.v1.blog.post.send_notification_email.delay")  
    async def test_create_post(self, mock_send_email):
        mock_send_email.return_value = None  # không làm gì cả khi gọi delay()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.post(
                "/api/v1/blog/post/",
                json={"title": "Test Post", "content": "Post content"},
                headers={"Content-Type": "application/json"},
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], "Test Post")
        self.assertEqual(response.json()["content"], "Post content")
        self.assertEqual(response.headers["content-type"], "application/json")

        mock_send_email.assert_called_once()

    async def test_get_post_list(self):
        # Create a sample post before listing
        post = Post(
            title="Example",
            content="Test content",
            author_id=self.test_user.id
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 1)
        self.assertEqual(response.headers["content-type"], "application/json")

    async def asyncTearDown(self):
        # Clean DB after each test
        self.db.query(RefreshToken).delete()
        self.db.query(Comment).delete()
        self.db.query(Media).delete()
        self.db.query(Post).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
