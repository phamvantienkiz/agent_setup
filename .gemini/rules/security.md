# Security Rules

## 🚨 CRITICAL — Never Violate These

- **Never** hardcode secrets, API keys, passwords, or tokens in source code
- **Never** commit `.env` files to version control
- **Never** log sensitive data (passwords, tokens, PII)
- **Never** use `eval()` or `Function()` with user input
- **Always** validate and sanitize all user inputs

## Environment Variables
```js
// ✅ Always use environment variables for secrets
const dbPassword = process.env.DB_PASSWORD;
const jwtSecret = process.env.JWT_SECRET;

// ❌ Never hardcode secrets
const dbPassword = 'mypassword123';
```

## Input Validation
```js
// ✅ Validate all incoming data with a schema
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128)
});

// Sanitize HTML to prevent XSS
import DOMPurify from 'dompurify';
const cleanContent = DOMPurify.sanitize(userInput);
```

## Authentication
- Use **JWT** with short expiry (15 min access token, 7 day refresh token)
- Hash passwords with **bcrypt** (rounds: 12+)
- Implement rate limiting on auth endpoints
```js
import bcrypt from 'bcrypt';
const SALT_ROUNDS = 12;
const hashed = await bcrypt.hash(password, SALT_ROUNDS);
```

## Authorization
```js
// ✅ Check permissions on every protected route
router.delete('/posts/:id', authenticate, authorize('admin'), asyncHandler(deletePost));

// ✅ Verify resource ownership
if (post.authorId !== req.user.id && req.user.role !== 'admin') {
  throw new AppError('Forbidden', 403);
}
```

## HTTP Security Headers
```js
// Use Helmet.js
import helmet from 'helmet';
app.use(helmet());

// Configure CORS strictly
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
  credentials: true
}));
```

## Rate Limiting
```js
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 });
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 5 });

app.use('/api/', apiLimiter);
app.use('/api/auth/', authLimiter);
```

## SQL Injection Prevention
- Always use ORM parameterized queries
- Never concatenate user input into SQL strings

## Dependency Security
```bash
# Regularly audit dependencies
npm audit
npm audit fix
```
