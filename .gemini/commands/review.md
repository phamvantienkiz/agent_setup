# Review Command

## Description
Perform a thorough code review of specified files or a pull request.

## Usage
Tell Claude: "Review [file/PR/feature]" or "Do a code review of [changes]"

## Review Checklist

### Code Quality
- [ ] Code follows style guide (`.claude/rules/code-style.md`)
- [ ] No unnecessary complexity or duplication
- [ ] Functions are small and focused (single responsibility)
- [ ] Variable and function names are descriptive

### Security
- [ ] No hardcoded secrets or credentials
- [ ] Input validation is present
- [ ] Authentication/authorization checks in place
- [ ] See `.claude/rules/security.md` for full checklist

### Error Handling
- [ ] Errors are properly caught and handled
- [ ] Meaningful error messages
- [ ] No swallowed exceptions
- [ ] See `.claude/rules/error-handling.md`

### Testing
- [ ] Unit tests cover new logic
- [ ] Edge cases are tested
- [ ] Tests are readable and maintainable
- [ ] See `.claude/rules/testing.md`

### Database
- [ ] Queries are optimized (no N+1)
- [ ] Transactions used where appropriate
- [ ] See `.claude/rules/database.md`

### API
- [ ] Endpoints follow REST conventions
- [ ] Request/response schemas are documented
- [ ] See `.claude/rules/api-conventions.md`

## Output Format
Provide feedback as:
- 🔴 **Critical** — Must fix before merge
- 🟡 **Warning** — Should fix, potential issue
- 🟢 **Suggestion** — Nice to have improvement
- ✅ **Good** — Highlight what's done well
