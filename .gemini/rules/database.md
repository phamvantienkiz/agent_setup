doc# Database Rules

## General Rules
- **Never** write raw SQL strings directly in business logic
- Always use an ORM (Prisma/Sequelize/TypeORM) or query builder
- All database calls must be inside try/catch blocks
- Use **transactions** for multi-step operations

## Connection Management
```js
// ✅ Use connection pooling
const pool = new Pool({ max: 10, idleTimeoutMillis: 30000 });

// ❌ Never create a new connection per request
```

## Query Best Practices
```js
// ✅ Select only needed fields
const user = await db.user.findUnique({
  where: { id },
  select: { id: true, email: true, name: true }
});

// ❌ Avoid SELECT *
const user = await db.user.findUnique({ where: { id } });

// ✅ Use pagination for lists
const users = await db.user.findMany({
  take: limit,
  skip: (page - 1) * limit,
  orderBy: { createdAt: 'desc' }
});
```

## Transactions
```js
// ✅ Use transactions for atomic operations
await db.$transaction(async (tx) => {
  const order = await tx.order.create({ data: orderData });
  await tx.inventory.update({ where: { id: productId }, data: { stock: { decrement: 1 } } });
  return order;
});
```

## Migrations
- Always use migration files, never modify the database schema directly
- Migration files are version-controlled and immutable
- Run migrations in CI/CD before deploying

## Naming Conventions
- Tables: **snake_case** plural (`user_profiles`, `order_items`)
- Columns: **snake_case** (`created_at`, `user_id`)
- Indexes: `idx_[table]_[column]`
- Foreign keys: `fk_[table]_[referenced_table]`

## Security
- Never log query results containing sensitive data (passwords, tokens)
- Use parameterized queries — never string concatenation
- Apply row-level security where applicable
