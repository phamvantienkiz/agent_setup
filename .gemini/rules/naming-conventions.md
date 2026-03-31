# Naming Conventions

> Standard naming rules for cache keys, database identifiers, queues, events, environment variables, and more.

## 🔑 Cache Key Naming

### Format
```
{app}:{version}:{entity}:{identifier}:{variant}
```

### Rules
- Use **colons** (`:`) as separators
- Use **lowercase snake_case** for each segment
- Always prefix with app/service name to avoid collision
- Include version for easy cache invalidation

### Examples
```
# User data
myapp:v1:user:12345
myapp:v1:user:12345:profile
myapp:v1:user:12345:permissions

# Lists / collections
myapp:v1:users:active:list
myapp:v1:products:category:electronics:page:1

# Sessions
myapp:v1:session:abc123xyz

# Rate limiting
myapp:v1:rate_limit:user:12345:api
myapp:v1:rate_limit:ip:192.168.1.1

# Feature flags
myapp:v1:feature:new_checkout:enabled

# Temporary locks (mutex)
myapp:v1:lock:payment:order:99999

# Aggregates / computed
myapp:v1:dashboard:user:12345:stats:daily
```

### TTL Conventions
| Data Type | Recommended TTL |
|-----------|----------------|
| User session | 7 days |
| Auth tokens | 15 minutes |
| User profile | 1 hour |
| Product catalog | 6 hours |
| Config/settings | 24 hours |
| Rate limit windows | 15 minutes |
| Temporary locks | 30 seconds |

---

## 🗄️ Database Naming

### Tables
```sql
-- snake_case, plural nouns
users
order_items
product_categories
user_role_mappings    -- junction tables: entity1_entity2_mappings
```

### Columns
```sql
-- snake_case
id                    -- primary key (always 'id')
user_id               -- foreign key: {referenced_table_singular}_id
created_at            -- timestamps: {event}_at
updated_at
deleted_at            -- soft delete
is_active             -- booleans: is_, has_, can_
has_verified_email
email                 -- data fields: plain descriptive name
full_name
```

### Indexes
```sql
-- Pattern: idx_{table}_{columns}
idx_users_email
idx_orders_user_id_created_at
idx_products_category_id_is_active

-- Unique indexes
uniq_users_email
uniq_products_sku

-- Full-text search
fts_products_name_description
```

### Foreign Keys
```sql
-- Pattern: fk_{child_table}_{parent_table}
fk_orders_users
fk_order_items_orders
fk_order_items_products
```

### Stored Procedures / Functions
```sql
-- snake_case verbs
get_user_by_email()
calculate_order_total()
archive_old_sessions()
```

---

## 📨 Message Queue / Event Naming

### Queue Names
```
# Pattern: {app}.{entity}.{action}
# Use dots as separators for queues

myapp.email.send
myapp.payment.process
myapp.order.fulfillment
myapp.notification.push
myapp.report.generate
```

### Event Names (Domain Events)
```
# Pattern: {entity}.{past_tense_verb}
# Events describe things that HAPPENED

user.registered
user.email_verified
order.placed
order.payment_received
order.fulfilled
order.cancelled
payment.failed
product.stock_depleted
```

### Dead Letter Queues (DLQ)
```
myapp.email.send.dlq
myapp.payment.process.dlq
```

---

## 🌍 Environment Variables

### Rules
- **UPPER_SNAKE_CASE** for all env vars
- Prefix with app/service name for non-standard vars
- Be descriptive, avoid abbreviations

### Standard Variables
```bash
# App
NODE_ENV=production
PORT=3000
APP_NAME=myapp
APP_URL=https://myapp.com
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://...
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp_production
DB_USER=myapp_user
DB_PASSWORD=...
DB_POOL_MIN=2
DB_POOL_MAX=10

# Cache
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=...
CACHE_TTL_DEFAULT=3600

# Auth
JWT_SECRET=...
JWT_EXPIRES_IN=15m
JWT_REFRESH_SECRET=...
JWT_REFRESH_EXPIRES_IN=7d
BCRYPT_ROUNDS=12

# External Services
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-southeast-1
S3_BUCKET_NAME=...

# Monitoring
SENTRY_DSN=...
GRAFANA_API_KEY=...
```

---

## 📁 File & Folder Naming

```
# Files: kebab-case
user-service.js
auth-middleware.js
order-repository.js
send-welcome-email.js  # specific action scripts

# Folders: kebab-case, plural for collections
controllers/
services/
repositories/
utils/
middleware/
config/

# Test files: match source file + .test
user-service.test.js
auth-middleware.test.js

# Config files
.env.development
.env.production
docker-compose.dev.yml
docker-compose.prod.yml
```

---

## 🌐 URL / Route Naming

```
# REST: plural nouns, kebab-case, versioned
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

# Nested resources
GET    /api/v1/users/:id/orders
POST   /api/v1/users/:id/orders

# Actions that don't fit CRUD (use verbs sparingly)
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/refresh
POST   /api/v1/payments/:id/refund
```
