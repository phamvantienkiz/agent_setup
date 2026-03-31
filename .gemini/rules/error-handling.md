# Error Handling

## Core Principles
- **Never swallow errors silently** — always log or rethrow
- Use a centralized error handler
- Return consistent error responses to the API
- Distinguish between operational errors (expected) and programmer errors (bugs)

## Custom Error Class
```js
// src/utils/app-error.js
class AppError extends Error {
  constructor(message, statusCode = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

export default AppError;
```

## Throwing Errors
```js
// ✅ Use AppError for known operational errors
if (!user) {
  throw new AppError('User not found', 404, 'USER_NOT_FOUND');
}

if (!hasPermission) {
  throw new AppError('Forbidden', 403, 'ACCESS_DENIED');
}
```

## Async Error Handling
```js
// ✅ Always wrap async route handlers
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

router.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await userService.findById(req.params.id);
  res.json({ success: true, data: user });
}));
```

## Global Error Handler (Express)
```js
// middleware/error-handler.js
export function errorHandler(err, req, res, next) {
  const statusCode = err.statusCode || 500;
  const isOperational = err.isOperational || false;

  // Log all errors
  logger.error({ err, req: { method: req.method, url: req.url } });

  // Don't expose internal errors to clients
  if (!isOperational) {
    return res.status(500).json({
      success: false,
      error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' }
    });
  }

  res.status(statusCode).json({
    success: false,
    error: { code: err.code, message: err.message }
  });
}
```

## Validation Errors
```js
// Use a validation library (Zod/Joi/Yup) and throw structured errors
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2)
});

function validateUser(data) {
  const result = userSchema.safeParse(data);
  if (!result.success) {
    throw new AppError('Validation failed', 422, 'VALIDATION_ERROR');
  }
  return result.data;
}
```
