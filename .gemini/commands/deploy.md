# Deploy Command

## Description
Deploy the application to the target environment.

## Usage
Tell Claude: "Run the deploy command" or "Deploy to [environment]"

## Steps

### 1. Pre-deploy Checklist
- [ ] All tests pass (`npm test`)
- [ ] No linting errors (`npm run lint`)
- [ ] Environment variables are configured
- [ ] Database migrations are ready

### 2. Build
```bash
npm run build
```

### 3. Deploy
```bash
# Development
npm run deploy:dev

# Production
npm run deploy:prod
```

### 4. Post-deploy Verification
- Check application health endpoint
- Verify logs for errors
- Run smoke tests

## Rollback
If deployment fails:
```bash
npm run rollback
```
