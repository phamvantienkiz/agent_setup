# Code Style Guide

## General Principles
- **Clarity over cleverness** — Write code that is easy to read and understand
- **Consistency** — Follow existing patterns in the codebase
- **DRY** — Don't Repeat Yourself, but don't over-abstract

## JavaScript / TypeScript

### Formatting
- Indentation: **2 spaces** (no tabs)
- Max line length: **100 characters**
- Use **single quotes** for strings
- Always use **semicolons**
- Trailing commas in multi-line structures

### Naming
```js
// Variables and functions: camelCase
const userProfile = {};
function getUserById(id) {}

// Classes and interfaces: PascalCase
class UserService {}
interface UserRepository {}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;
const API_BASE_URL = 'https://api.example.com';

// Files: kebab-case
// user-service.js, auth-middleware.js
```

### Functions
```js
// ✅ Good — Arrow functions for simple operations
const double = (x) => x * 2;

// ✅ Good — Named functions for complex logic
function processUserData(user) {
  // ...
}

// ❌ Avoid — Functions longer than 30 lines (extract helpers)
```

### Async/Await
```js
// ✅ Always use async/await over raw promises
async function fetchUser(id) {
  try {
    const user = await userRepository.findById(id);
    return user;
  } catch (error) {
    throw new AppError('User not found', 404);
  }
}

// ❌ Avoid promise chains
fetchUser(id).then(...).catch(...);
```

### Imports
```js
// Order: 1. Node built-ins, 2. External deps, 3. Internal modules
import path from 'path';
import express from 'express';
import { UserService } from './user-service.js';
```

## Comments
```js
// ✅ Explain WHY, not WHAT
// We retry 3 times because the external API has transient failures
const MAX_RETRIES = 3;

// ❌ Avoid obvious comments
// Set x to 5
const x = 5;
```

## File Organization
- One class/service per file
- Group related files in feature folders
- Index files for clean imports
