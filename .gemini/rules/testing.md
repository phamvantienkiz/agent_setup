# Testing Standards

## Testing Pyramid
```
         [E2E Tests]         ← Few, slow, catch integration issues
       [Integration Tests]   ← Some, test component interaction
     [Unit Tests]            ← Many, fast, test isolated logic
```

## Requirements
- Unit test coverage: **minimum 80%**
- All new features must have tests
- All bug fixes must have a regression test
- Tests run in CI before any merge

## Test File Organization
```
tests/
├── unit/
│   ├── services/user-service.test.js
│   └── utils/format.test.js
├── integration/
│   ├── routes/users.test.js
│   └── database/user-repo.test.js
└── e2e/
    └── auth-flow.test.js
```

## Unit Test Example (Jest)
```js
// tests/unit/services/user-service.test.js
import { UserService } from '../../../src/services/user-service.js';
import { mockUserRepository } from '../../mocks/user-repository.mock.js';

describe('UserService', () => {
  let userService;
  let mockRepo;

  beforeEach(() => {
    mockRepo = mockUserRepository();
    userService = new UserService(mockRepo);
  });

  describe('findById', () => {
    it('should return user when found', async () => {
      const mockUser = { id: '1', email: 'test@test.com' };
      mockRepo.findById.mockResolvedValue(mockUser);

      const result = await userService.findById('1');

      expect(result).toEqual(mockUser);
      expect(mockRepo.findById).toHaveBeenCalledWith('1');
    });

    it('should throw AppError when user not found', async () => {
      mockRepo.findById.mockResolvedValue(null);

      await expect(userService.findById('999'))
        .rejects.toThrow('User not found');
    });
  });
});
```

## Integration Test Example
```js
// tests/integration/routes/users.test.js
import request from 'supertest';
import app from '../../../src/index.js';

describe('GET /api/users/:id', () => {
  it('should return 200 with user data', async () => {
    const res = await request(app)
      .get('/api/users/1')
      .set('Authorization', `Bearer ${testToken}`);

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data).toHaveProperty('id');
  });

  it('should return 404 for unknown user', async () => {
    const res = await request(app)
      .get('/api/users/99999')
      .set('Authorization', `Bearer ${testToken}`);

    expect(res.status).toBe(404);
  });
});
```

## Test Commands
```bash
npm test                    # Run all tests
npm run test:unit           # Unit tests only
npm run test:integration    # Integration tests only
npm run test:coverage       # Generate coverage report
npm run test:watch          # Watch mode for development
```

## Naming Conventions
- Test files: `[filename].test.js`
- `describe` blocks: Match the module/function being tested
- `it` blocks: `should [expected behavior] when [condition]`
