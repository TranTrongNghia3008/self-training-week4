import unittest
import uuid
from unittest.mock import patch
from io import BytesIO

from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.post import Post
from app.models.media import Media
from app.core.dependencies import get_current_user


class MediaAPITestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db: Session = SessionLocal()
        self.transport = ASGITransport(app=app)
        self.base_url = "http://test"

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

        # Tạo post test
        self.test_post = Post(
            title="Test Post",
            content="Some content",
            author_id=self.test_user.id
        )
        self.db.add(self.test_post)
        self.db.commit()
        self.db.refresh(self.test_post)

        app.dependency_overrides[get_current_user] = lambda: self.test_user

    @patch("app.api.v1.blog.media.upload_media_to_cloudinary")
    async def test_upload_media(self, mock_upload):
        mock_upload.return_value = {
            "url": "http://cloudinary.com/fake.jpg",
            "public_id": "public123",
            "media_type": "image"
        }

        file_content = BytesIO(b"fake image data")
        files = {"file": ("test.jpg", file_content, "image/jpeg")}

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.post(
                f"/api/v1/blog/media/upload/{self.test_post.id}",
                files=files
            )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["url"], "http://cloudinary.com/fake.jpg")
        self.assertEqual(data["media_type"], "image")

    async def test_get_media(self):
        # Tạo media trực tiếp
        media = Media(
            url="http://cloudinary.com/test.jpg",
            public_id="test_public_id",
            media_type="image",
            post_id=self.test_post.id
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get(f"/api/v1/blog/media/{media.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["url"], "http://cloudinary.com/test.jpg")

    @patch("app.api.v1.blog.media.delete_media_from_cloudinary")
    async def test_delete_media(self, mock_delete_cloudinary):
        media = Media(
            url="http://cloudinary.com/test.jpg",
            public_id="test_public_id",
            media_type="image",
            post_id=self.test_post.id
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.delete(f"/api/v1/blog/media/{media.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Media deleted successfully")
        mock_delete_cloudinary.assert_called_once_with("test_public_id", "image")

    async def asyncTearDown(self):
        self.db.query(Media).delete()
        self.db.query(Post).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
