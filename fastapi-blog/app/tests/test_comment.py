import unittest
import uuid

from httpx import AsyncClient, ASGITransport
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.token import RefreshToken
from app.core.dependencies import get_current_user


class CommentAPITestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db: Session = SessionLocal()
        self.transport = ASGITransport(app=app)
        self.base_url = "http://test"

        # Create test user
        self.username = f"user_{uuid.uuid4().hex[:6]}"
        self.test_user = User(
            username=self.username,
            email=f"{self.username}@example.com",
            hashed_password="fakehashed"
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

        # Create test post
        self.test_post = Post(
            title="Test Post",
            content="Post content",
            author_id=self.test_user.id
        )
        self.db.add(self.test_post)
        self.db.commit()
        self.db.refresh(self.test_post)

        # Dependency override
        app.dependency_overrides[get_current_user] = lambda: self.test_user

    async def test_create_comment(self):
        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.post(
                f"/api/v1/blog/comments/post/{self.test_post.id}",
                json={"content": "This is a comment"},
                headers={"Content-Type": "application/json"}
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["content"], "This is a comment")

    async def test_get_comments(self):
        # Create comment manually
        comment = Comment(
            content="Comment A",
            post_id=self.test_post.id,
            author_id=self.test_user.id
        )
        self.db.add(comment)
        self.db.commit()

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.get(f"/api/v1/blog/comments/post/{self.test_post.id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreaterEqual(len(response.json()), 1)

    async def test_update_comment(self):
        # Create comment
        comment = Comment(
            content="Original",
            post_id=self.test_post.id,
            author_id=self.test_user.id
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.put(
                f"/api/v1/blog/comments/{comment.id}",
                json={"content": "Updated comment"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Updated comment")

    async def test_delete_comment(self):
        comment = Comment(
            content="To be deleted",
            post_id=self.test_post.id,
            author_id=self.test_user.id
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)

        async with AsyncClient(transport=self.transport, base_url=self.base_url) as ac:
            response = await ac.delete(f"/api/v1/blog/comments/{comment.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Comment deleted successfully")

    async def asyncTearDown(self):
        self.db.query(RefreshToken).delete()
        self.db.query(Comment).delete()
        self.db.query(Post).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()
