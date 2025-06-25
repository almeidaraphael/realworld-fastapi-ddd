"""
End-to-end test for comment functionality.
"""

from httpx import AsyncClient


async def test_comment_crud_flow(async_client: AsyncClient):
    """
    GIVEN a user and an article
    WHEN creating, reading, and deleting comments
    THEN all operations should work correctly
    """
    # Create user
    user_data = {
        "user": {
            "username": "commentuser",
            "email": "commentuser@example.com",
            "password": "password123",
        }
    }

    response = await async_client.post("/api/users", json=user_data)
    assert response.status_code == 201
    user_token = response.json()["user"]["token"]

    # Create article
    article_data = {
        "article": {
            "title": "Test Article for Comments",
            "description": "Testing comment functionality",
            "body": "This article will have comments",
            "tagList": ["test", "comments"],
        }
    }

    headers = {"Authorization": f"Token {user_token}"}
    article_response = await async_client.post("/api/articles", json=article_data, headers=headers)
    assert article_response.status_code == 201

    article_slug = article_response.json()["article"]["slug"]

    # Create comment
    comment_data = {"comment": {"body": "This is a test comment on the article"}}

    comment_response = await async_client.post(
        f"/api/articles/{article_slug}/comments", json=comment_data, headers=headers
    )
    assert comment_response.status_code == 201

    created_comment = comment_response.json()["comment"]
    assert created_comment["body"] == "This is a test comment on the article"
    assert created_comment["author"]["username"] == "commentuser"
    comment_id = created_comment["id"]

    # Get comments for article
    get_comments_response = await async_client.get(f"/api/articles/{article_slug}/comments")
    assert get_comments_response.status_code == 200

    comments_data = get_comments_response.json()
    assert len(comments_data["comments"]) == 1
    assert comments_data["comments"][0]["body"] == "This is a test comment on the article"

    # Delete comment
    delete_response = await async_client.delete(
        f"/api/articles/{article_slug}/comments/{comment_id}", headers=headers
    )
    assert delete_response.status_code == 204

    # Verify comment is deleted
    final_comments_response = await async_client.get(f"/api/articles/{article_slug}/comments")
    assert final_comments_response.status_code == 200

    final_comments_data = final_comments_response.json()
    assert len(final_comments_data["comments"]) == 0
