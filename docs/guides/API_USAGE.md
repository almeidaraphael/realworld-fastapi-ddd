# API Usage Guide

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

Complete guide to using the FastAPI RealWorld Demo API, including authentication, endpoints, and practical examples.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Core Endpoints](#core-endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Error Handling](#error-handling)
- [Client Libraries](#client-libraries)

## Overview

The FastAPI RealWorld Demo implements the complete [RealWorld API specification](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/), providing a fully functional blogging platform API.

### Base URL

- **Local Development**: `http://localhost:8000`
- **API Prefix**: `/api` (for most endpoints)
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)

### API Features

- ✅ User registration and authentication
- ✅ User profiles and following
- ✅ Article CRUD operations
- ✅ Article favoriting and feeds
- ✅ Comment system
- ✅ Tag management
- ✅ Pagination support

## Authentication

The API uses JWT (JSON Web Token) based authentication with bcrypt password hashing for security.

### Authentication Flow

The following diagram illustrates the complete authentication process:

![Authentication Flow Diagram](../../diagrams/flow/authentication-flow.svg)

**Key Security Features:**
- **bcrypt Password Hashing**: Secure password storage with automatic salt generation
- **JWT Token-Based Authentication**: Stateless authentication with configurable expiration
- **Middleware Protection**: Automatic token validation and user injection
- **Consistent Error Handling**: Standardized authentication error responses

### Registration

```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "username": "johndoe",
      "email": "john@example.com",
      "password": "securepassword123"
    }
  }'
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "bio": "",
    "image": ""
  }
}
```

### Login

```bash
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "email": "john@example.com",
      "password": "securepassword123"
    }
  }'
```

### Using Authentication Token

Include the token in the `Authorization` header for protected endpoints:

```bash
curl -X GET "http://localhost:8000/api/user" \
  -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## Core Endpoints

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users` | Register user | No |
| POST | `/api/users/login` | Login user | No |
| GET | `/api/user` | Get current user | Yes |
| PUT | `/api/user` | Update current user | Yes |

### Profiles

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/profiles/{username}` | Get user profile | Optional |
| POST | `/api/profiles/{username}/follow` | Follow user | Yes |
| DELETE | `/api/profiles/{username}/follow` | Unfollow user | Yes |

### Articles

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/articles` | List articles | Optional |
| GET | `/api/articles/feed` | Get user feed | Yes |
| GET | `/api/articles/{slug}` | Get article | Optional |
| POST | `/api/articles` | Create article | Yes |
| PUT | `/api/articles/{slug}` | Update article | Yes |
| DELETE | `/api/articles/{slug}` | Delete article | Yes |
| POST | `/api/articles/{slug}/favorite` | Favorite article | Yes |
| DELETE | `/api/articles/{slug}/favorite` | Unfavorite article | Yes |

### Comments

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/articles/{slug}/comments` | Get comments | Optional |
| POST | `/api/articles/{slug}/comments` | Add comment | Yes |
| DELETE | `/api/articles/{slug}/comments/{id}` | Delete comment | Yes |

### Tags

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tags` | Get all tags | No |

## Request/Response Examples

### Create Article

**Request:**
```bash
curl -X POST "http://localhost:8000/api/articles" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "article": {
      "title": "How to Build APIs with FastAPI",
      "description": "A comprehensive guide to FastAPI development",
      "body": "FastAPI is a modern, fast web framework for building APIs with Python...",
      "tagList": ["python", "fastapi", "api", "tutorial"]
    }
  }'
```

**Response:**
```json
{
  "article": {
    "slug": "how-to-build-apis-with-fastapi",
    "title": "How to Build APIs with FastAPI",
    "description": "A comprehensive guide to FastAPI development",
    "body": "FastAPI is a modern, fast web framework for building APIs with Python...",
    "tagList": ["python", "fastapi", "api", "tutorial"],
    "createdAt": "2025-06-25T10:30:00Z",
    "updatedAt": "2025-06-25T10:30:00Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "johndoe",
      "bio": "",
      "image": "",
      "following": false
    }
  }
}
```

### List Articles with Filters

```bash
# Get articles by tag
curl "http://localhost:8000/api/articles?tag=python&limit=10&offset=0"

# Get articles by author
curl "http://localhost:8000/api/articles?author=johndoe"

# Get favorited articles by user
curl "http://localhost:8000/api/articles?favorited=johndoe"
```

**Response:**
```json
{
  "articles": [
    {
      "slug": "article-slug",
      "title": "Article Title",
      "description": "Article description",
      "body": "Article body content...",
      "tagList": ["tag1", "tag2"],
      "createdAt": "2025-06-25T10:30:00Z",
      "updatedAt": "2025-06-25T10:30:00Z",
      "favorited": false,
      "favoritesCount": 5,
      "author": {
        "username": "author",
        "bio": "Author bio",
        "image": "https://example.com/image.jpg",
        "following": false
      }
    }
  ],
  "articlesCount": 1
}
```

### Add Comment

**Request:**
```bash
curl -X POST "http://localhost:8000/api/articles/article-slug/comments" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": {
      "body": "Great article! Very helpful for beginners."
    }
  }'
```

**Response:**
```json
{
  "comment": {
    "id": 1,
    "body": "Great article! Very helpful for beginners.",
    "createdAt": "2025-06-25T11:00:00Z",
    "updatedAt": "2025-06-25T11:00:00Z",
    "author": {
      "username": "johndoe",
      "bio": "",
      "image": "",
      "following": false
    }
  }
}
```

### Update User Profile

**Request:**
```bash
curl -X PUT "http://localhost:8000/api/user" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "bio": "Experienced Python developer and FastAPI enthusiast",
      "image": "https://example.com/profile.jpg"
    }
  }'
```

## Error Handling

The API returns consistent error responses across all endpoints.

### Error Response Format

```json
{
  "errors": {
    "body": ["Error message describing what went wrong"]
  }
}
```

### Common HTTP Status Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| 200 | Success | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (email, username) |
| 422 | Validation Error | Invalid request data |
| 500 | Server Error | Internal server error |

### Example Error Responses

**Validation Error (422):**
```json
{
  "errors": {
    "body": ["Email is required", "Password must be at least 8 characters"]
  }
}
```

**Authentication Error (401):**
```json
{
  "errors": {
    "body": ["Authentication token is invalid or expired"]
  }
}
```

**Not Found Error (404):**
```json
{
  "errors": {
    "body": ["Article not found"]
  }
}
```

## Client Libraries

### Python (httpx)

```python
import httpx
import asyncio

class RealWorldClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    async def register(self, username: str, email: str, password: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/users",
                json={
                    "user": {
                        "username": username,
                        "email": email,
                        "password": password
                    }
                }
            )
            if response.status_code == 201:
                data = response.json()
                self.token = data["user"]["token"]
                return data["user"]
            return None
    
    async def get_articles(self, limit: int = 20, offset: int = 0):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/articles",
                params={"limit": limit, "offset": offset}
            )
            return response.json() if response.status_code == 200 else None

# Usage
async def main():
    client = RealWorldClient()
    user = await client.register("testuser", "test@example.com", "password123")
    articles = await client.get_articles(limit=10)
    print(f"User: {user}")
    print(f"Articles: {len(articles['articles'])}")

asyncio.run(main())
```

### JavaScript (fetch)

```javascript
class RealWorldClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.token = null;
    }
    
    async register(username, email, password) {
        const response = await fetch(`${this.baseUrl}/api/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user: { username, email, password }
            })
        });
        
        if (response.status === 201) {
            const data = await response.json();
            this.token = data.user.token;
            return data.user;
        }
        return null;
    }
    
    async getArticles(limit = 20, offset = 0) {
        const url = new URL(`${this.baseUrl}/api/articles`);
        url.searchParams.append('limit', limit);
        url.searchParams.append('offset', offset);
        
        const response = await fetch(url);
        return response.status === 200 ? await response.json() : null;
    }
    
    async createArticle(title, description, body, tagList = []) {
        const response = await fetch(`${this.baseUrl}/api/articles`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${this.token}`
            },
            body: JSON.stringify({
                article: { title, description, body, tagList }
            })
        });
        
        return response.status === 201 ? await response.json() : null;
    }
}

// Usage
const client = new RealWorldClient();
const user = await client.register('testuser', 'test@example.com', 'password123');
const articles = await client.getArticles(10);
```

## Interactive Documentation

The API includes interactive documentation powered by Swagger UI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

The interactive docs allow you to:
- Explore all endpoints
- Test API calls directly
- View request/response schemas
- Download the OpenAPI specification

For more detailed examples and advanced usage patterns, explore the test files in the `tests/e2e/` directory.
