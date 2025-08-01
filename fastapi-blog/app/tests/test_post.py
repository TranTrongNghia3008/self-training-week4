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
from app.models.category import Category
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
            hashed_password="hashed",
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

        # Create or get test category
        existing_category = self.db.query(Category).filter_by(name="FastAPI").first()
        if existing_category:
            self.test_category = existing_category
        else:
            self.test_category = Category(name="FastAPI")
            self.db.add(self.test_category)
            self.db.commit()
            self.db.refresh(self.test_category)

        # Override auth
        app.dependency_overrides[get_current_user] = lambda: self.test_user

    @patch("app.services.blog.post_service.send_notification_email.delay")
    async def test_create_post(self, mock_send_email):
        mock_send_email.return_value = None

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.post(
                "/api/v1/blog/post/",
                json={
                    "title": "Test Post",
                    "content": "Post content",
                    "category_id": self.test_category.id,
                },
                headers={"Content-Type": "application/json"},
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], "Test Post")
        self.assertEqual(response.json()["content"], "Post content")
        self.assertEqual(response.json()["category"]["id"], self.test_category.id)
        mock_send_email.assert_called_once()

    async def test_get_post_list(self):
        post = Post(
            title="Example",
            content="Test content",
            author_id=self.test_user.id,
            category_id=self.test_category.id,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 1)

    async def test_search_post_by_title_and_content(self):
        post1 = Post(title="FastAPI Tutorial", content="Learn FastAPI", author_id=self.test_user.id, category_id=self.test_category.id)
        post2 = Post(title="Flask Guide", content="FastAPI vs Flask", author_id=self.test_user.id, category_id=self.test_category.id)
        post3 = Post(title="Django", content="Backend Framework", author_id=self.test_user.id, category_id=self.test_category.id)

        self.db.add_all([post1, post2, post3])
        self.db.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/", params={"search": "fastapi"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertTrue(all("fastapi" in (p["title"] + p["content"]).lower() for p in data))

    async def test_filter_post_by_category_id(self):
        # Create second category
        category2 = Category(name="Django")
        self.db.add(category2)
        self.db.commit()
        self.db.refresh(category2)

        post1 = Post(title="Post A", content="Content A", author_id=self.test_user.id, category_id=self.test_category.id)
        post2 = Post(title="Post B", content="Content B", author_id=self.test_user.id, category_id=category2.id)
        post3 = Post(title="Post C", content="Content C", author_id=self.test_user.id, category_id=self.test_category.id)

        self.db.add_all([post1, post2, post3])
        self.db.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/", params={"category_id": self.test_category.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertTrue(all(p["category"]["id"] == self.test_category.id for p in data))

    async def test_create_post_validation_error(self):
        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.post(
                "/api/v1/blog/post/",
                json={  # Thiếu title và category_id
                    "content": "Missing title and category_id"
                },
                headers={"Content-Type": "application/json"},
            )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("detail", response.json())

    async def test_update_post(self):
        # Tạo bài viết ban đầu
        post = Post(
            title="Old Title",
            content="Old content",
            author_id=self.test_user.id,
            category_id=self.test_category.id,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.put(
                f"/api/v1/blog/post/{post.id}",
                json={
                    "title": "New Title",
                    "content": "Updated content",
                    "author_id": post.author_id,
                    "category_id": post.category_id,
                },
                headers={"Content-Type": "application/json"},
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["title"], "New Title")
        self.assertEqual(data["content"], "Updated content")

    async def test_delete_post(self):
        post = Post(
            title="Delete Me",
            content="Some content",
            author_id=self.test_user.id,
            category_id=self.test_category.id,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.delete(f"/api/v1/blog/post/{post.id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Kiểm tra không còn trong DB
        deleted = self.db.query(Post).filter_by(id=post.id).first()
        self.assertIsNone(deleted)

    async def test_post_pagination(self):
        # Tạo 15 bài viết
        posts = [
            Post(
                title=f"Post {i}",
                content="Content",
                author_id=self.test_user.id,
                category_id=self.test_category.id,
            )
            for i in range(15)
        ]
        self.db.add_all(posts)
        self.db.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/", params={"limit": 10, "offset": 0})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 10)



    async def asyncTearDown(self):
        self.db.query(RefreshToken).delete()
        self.db.query(Comment).delete()
        self.db.query(Media).delete()
        self.db.query(Post).delete()
        self.db.query(Category).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
