# Git Workflow

## Branch Strategy (Git Flow)

```
main          — Production-ready code only
develop       — Integration branch for features
feature/*     — New features
fix/*         — Bug fixes
hotfix/*      — Urgent production fixes
release/*     — Release preparation
```

## Branch Naming
```
feature/user-authentication
feature/payment-integration
fix/login-redirect-bug
fix/order-calculation-issue
hotfix/critical-security-patch
release/v1.2.0
```

## Commit Message Format (Conventional Commits)

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types
| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructure, no feature/fix |
| `test` | Adding or fixing tests |
| `chore` | Build process, dependencies |
| `perf` | Performance improvement |

### Examples
```
feat(auth): add JWT refresh token support

fix(orders): correct total price calculation when discount applied

docs(api): add Swagger annotations to user endpoints

test(users): add unit tests for UserService.findById

chore: upgrade express to v5.0.0
```

## Pull Request Rules
- PRs must reference an issue: `Closes #123`
- Minimum 1 reviewer approval required
- All CI checks must pass
- No direct commits to `main` or `develop`
- PR title must follow conventional commit format

## Commit Best Practices
- Commit frequently with small, focused changes
- Each commit should be a single logical change
- Never commit: `.env` files, secrets, `node_modules`
- Always run tests before committing

## Tags & Releases
```bash
# Tag a release
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```
