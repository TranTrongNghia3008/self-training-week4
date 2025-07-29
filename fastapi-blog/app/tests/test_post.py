def test_create_post(client):
    response = client.post("/api/v1/posts/", json={
        "title": "Test post",
        "content": "This is a test"
    })
    assert response.status_code == 200
