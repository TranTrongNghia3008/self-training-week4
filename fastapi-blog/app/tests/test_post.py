import unittest
import uuid
from unittest.mock import patch
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import async_session
from app.models import Post, User, Category, Comment, Media, RefreshToken
from app.core.dependencies import get_current_user


class PostTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        async with async_session() as session:
            # Tạo user test
            self.unique_username = f"testuser_{uuid.uuid4().hex[:6]}"
            test_user = User(
                username=self.unique_username,
                email=f"{self.unique_username}@example.com",
                hashed_password="hashed",
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            self.test_user = test_user

            # Tạo category
            result = await session.execute(
                Category.__table__.select().where(Category.name == "FastAPI")
            )
            existing_category = result.scalar_one_or_none()
            if existing_category:
                self.test_category = existing_category
            else:
                test_category = Category(name="FastAPI")
                session.add(test_category)
                await session.commit()
                await session.refresh(test_category)
                self.test_category = test_category

        self.transport = ASGITransport(app=app)
        self.base_url = "http://test"
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
        async with async_session() as session:
            session.add(post)
            await session.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 1)

    async def test_search_post_by_title_and_content(self):
        async with async_session() as session:
            post1 = Post(title="FastAPI Tutorial", content="Learn FastAPI", author_id=self.test_user.id, category_id=self.test_category.id)
            post2 = Post(title="Flask Guide", content="FastAPI vs Flask", author_id=self.test_user.id, category_id=self.test_category.id)
            post3 = Post(title="Django", content="Backend Framework", author_id=self.test_user.id, category_id=self.test_category.id)
            session.add_all([post1, post2, post3])
            await session.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/", params={"search": "fastapi"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertTrue(all("fastapi" in (p["title"] + p["content"]).lower() for p in data))

    async def test_filter_post_by_category_id(self):
        async with async_session() as session:
            category2 = Category(name="Django")
            session.add(category2)
            await session.commit()
            await session.refresh(category2)

            post1 = Post(title="Post A", content="Content A", author_id=self.test_user.id, category_id=self.test_category.id)
            post2 = Post(title="Post B", content="Content B", author_id=self.test_user.id, category_id=category2.id)
            post3 = Post(title="Post C", content="Content C", author_id=self.test_user.id, category_id=self.test_category.id)
            session.add_all([post1, post2, post3])
            await session.commit()

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
                json={"content": "Missing title and category_id"},
                headers={"Content-Type": "application/json"},
            )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    async def test_update_post(self):
        async with async_session() as session:
            post = Post(
                title="Old Title",
                content="Old content",
                author_id=self.test_user.id,
                category_id=self.test_category.id,
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)

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
        async with async_session() as session:
            post = Post(
                title="Delete Me",
                content="Some content",
                author_id=self.test_user.id,
                category_id=self.test_category.id,
            )
            session.add(post)
            await session.commit()
            await session.refresh(post)
            post_id = post.id

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.delete(f"/api/v1/blog/post/{post_id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        async with async_session() as session:
            result = await session.get(Post, post_id)
            self.assertIsNone(result)

    async def test_post_pagination(self):
        async with async_session() as session:
            posts = [
                Post(
                    title=f"Post {i}",
                    content="Content",
                    author_id=self.test_user.id,
                    category_id=self.test_category.id,
                )
                for i in range(15)
            ]
            session.add_all(posts)
            await session.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get("/api/v1/blog/", params={"limit": 10, "offset": 0})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 10)

    async def asyncTearDown(self):
        async with async_session() as session:
            for model in [RefreshToken, Comment, Media, Post, Category, User]:
                await session.execute(model.__table__.delete())
            await session.commit()

