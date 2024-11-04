Here's the documentation in pure markdown format:

# Citizens LLM Chat API Documentation

## Overview

The Citizens LLM Chat API provides a secure interface for managing AI-powered chat conversations. Built with Django REST Framework, it enables authenticated users to create, manage, and interact with chat conversations using the Qwen2.5-72B-Instruct language model.

## Base URL

`http://localhost:8000`

## Authentication

The API uses token-based authentication. First, obtain a token:

#### Login
`POST /chat/login/`

Authenticates a user and returns an authentication token.

**Headers:**

## Endpoints

### Authentication

#### Login
`POST /chat/login/`

Authenticates a user and returns an authentication token.

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

### Conversations

#### List Conversations
`GET /chat/conversations/`

Returns all conversations for the authenticated user.

**Response:** `200 OK`
```json
[
    {
        "id": 1,
        "title": "Conversation Title",
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z",
        "messages": []
    }
]
```

#### Create Conversation
`POST /chat/conversations/`

Creates a new conversation.

**Request Body:**
```json
{
    "title": "New Chat Conversation"
}
```

**Response:** `201 Created`

#### Get Conversation
`GET /chat/conversations/{conversation_id}/`

Retrieves a specific conversation and its messages.

**Response:** `200 OK`
```json
{
    "id": 1,
    "title": "Conversation Title",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z",
    "messages": [
        {
            "id": 1,
            "content": "Message content",
            "is_user": true,
            "created_at": "2024-01-01T12:00:00Z"
        }
    ]
}
```

#### Update Conversation
`PUT /chat/conversations/{conversation_id}/`

Updates a conversation's title.

**Request Body:**
```json
{
    "title": "Updated Conversation Title"
}
```

**Response:** `200 OK`

#### Delete Conversation
`DELETE /chat/conversations/{conversation_id}/`

Deletes a conversation and all its messages.

**Response:** `204 No Content`

### Messages

#### Send Message
`POST /chat/conversations/{conversation_id}/send_message/`

Sends a message in a conversation and receives an AI response.

**Request Body:**
```json
{
    "message": "Hello, AI assistant!"
}
```

**Response:** `200 OK`
```json
{
    "message": "AI assistant response"
}
```

## Error Responses

The API uses standard HTTP status codes:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a message:
```json
{
    "error": "Error message description"
}
```

## Rate Limiting

The API uses Hugging Face's rate limiting for LLM requests. Monitor the response headers for rate limit information.

## Model Information

The API uses the Qwen2.5-72B-Instruct model for generating responses. Maximum response length is set to 150 tokens with a temperature of 0.7.