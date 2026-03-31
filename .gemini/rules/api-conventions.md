# API Conventions

## REST API Design Standards

### URL Structure
- Use **kebab-case** for URL paths: `/api/user-profiles`
- Use **plural nouns** for resource collections: `/api/users`, `/api/products`
- Nest related resources: `/api/users/:id/orders`
- API version prefix: `/api/v1/...`

### HTTP Methods
| Method | Usage |
|--------|-------|
| GET | Read resources (idempotent) |
| POST | Create new resource |
| PUT | Replace entire resource |
| PATCH | Partial update |
| DELETE | Remove resource |

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | OK — Successful GET/PUT/PATCH |
| 201 | Created — Successful POST |
| 204 | No Content — Successful DELETE |
| 400 | Bad Request — Invalid input |
| 401 | Unauthorized — Not authenticated |
| 403 | Forbidden — No permission |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity — Validation failed |
| 500 | Internal Server Error |

### Request/Response Format
```json
// Success response
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}

// Error response
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": [ ... ]
  }
}

// Paginated list response
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### Naming Conventions
- Request/response body fields: **camelCase**
- Query parameters: **camelCase**
- Always return consistent field names

### Filtering & Pagination
```
GET /api/users?page=1&limit=20&sortBy=createdAt&order=desc
GET /api/products?category=electronics&minPrice=100
```

### Documentation
- Every endpoint MUST have JSDoc/Swagger annotations
- Include request body schema, response schema, and error codes
