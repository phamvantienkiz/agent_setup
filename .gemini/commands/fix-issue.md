# Fix Issue Command

## Description

Analyze and fix a reported bug or issue systematically.

## Usage

Tell Claude: "Fix issue: [describe the issue]" or "Fix bug in [file/module]"

## Process

### 1. Understand the Issue

- Read the error message or bug description carefully
- Identify the affected component(s)
- Reproduce the issue locally if possible

### 2. Root Cause Analysis

- Check recent git changes: `git log --oneline -20`
- Review affected files
- Look for related tests that may reveal expected behavior

### 3. Plan the Fix

- Identify the minimal change needed
- Consider side effects on other components
- Update or add tests to cover the fix

### 4. Implement

- Make the targeted fix
- Ensure code follows `.gemini/rules/code-style.md`
- Handle errors per `.gemini/rules/error-handling.md`

### 5. Verify

- Run relevant tests: `npm test -- --testPathPattern=[affected]`
- Run full test suite: `npm test`
- Check linting: `npm run lint`

### 6. Commit

Follow `.gemini/rules/git-workflow.md`:

```
fix: [short description of the fix]

Closes #[issue-number]
```
