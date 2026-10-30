# API Documentation: SearchWorkbench

## 1. Authentication

The API uses token-based authentication.
Every request must include an Authorization header.

Example:
Authorization: Bearer YOUR_API_TOKEN

If the token is missing or invalid, the server returns HTTP 401 Unauthorized.

## 2. User Endpoints

### GET /api/users

Returns a list of registered users.

Optional parameters:
- limit: Maximum number of users to return.
- page: Page number for pagination.

### POST /api/users

Creates a new user account.

Required fields:
- username: A unique username.
- email: A valid email address.
- password: A secure password.

The server returns HTTP 201 when the user is created successfully.

## 3. Database Configuration

The application connects to PostgreSQL.

The database connection uses these environment variables:

- DB_HOST: Database server address.
- DB_PORT: Database port, usually 5432.
- DB_NAME: Database name.
- DB_USER: Database username.
- DB_PASSWORD: Database password.

Never store database passwords directly in source code.

## 4. Error Handling

The API uses standard HTTP status codes.

- 200: Request successful.
- 201: Resource created.
- 400: Invalid request.
- 401: Authentication required.
- 403: Permission denied.
- 404: Resource not found.
- 500: Internal server error.

## 5. Rate Limiting

The API limits requests to protect server resources.

The default limit is 100 requests per minute per user.

When the limit is exceeded, the server returns HTTP 429 Too Many Requests.

## 6. Caching

GET responses may be cached to improve performance.

The Cache-Control header tells clients how long a response can be stored.

## 7. Logging and Monitoring

The application records request timestamps, response status codes, and request duration.

Sensitive information such as passwords and access tokens must never appear in logs.

## 8. Search Configuration

The search engine supports keyword search and semantic search.

Keyword search uses BM25 to find exact terms.

Semantic search uses vector embeddings to find documents with similar meaning.

The default result limit is 5 documents.

## 9. Custom Configuration

The system supports a custom setting named CUSTOM_CONFIG_FLAG_XYZ.

This setting enables advanced document indexing.

When CUSTOM_CONFIG_FLAG_XYZ is enabled, the indexer stores additional metadata for each document.

## 10. Document Chunking

Fixed-size chunking divides documents into pieces of a selected token length.

Overlapping chunks share some content to preserve context between neighboring sections.

Structure-aware chunking uses Markdown headings to identify meaningful sections.

Code examples should remain together whenever possible.

## 11. Vector Search

Dense vector search converts text into numerical embeddings.

The system compares query embeddings with document embeddings using cosine similarity.

A higher cosine similarity indicates a closer semantic match.

## 12. Benchmarking

The benchmark system evaluates retrieval quality.

Hit Rate at K measures whether at least one relevant result appears in the top K results.

Mean Reciprocal Rank measures the position of the first relevant result.

Average latency measures the time required to complete a search.

## 13. API Security

Use HTTPS for production API requests.

Validate user input before processing requests.

Apply authentication and authorization to protected endpoints.

Store secrets in environment variables rather than source code.
