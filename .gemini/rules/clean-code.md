# Clean Code — JavaScript Rules
> Source: [clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) by Ryan McDermott

## 📦 Variables

### ✅ Use meaningful, pronounceable names
```js
// ❌ Bad
const yyyymmdstr = moment().format('YYYY/MM/DD');

// ✅ Good
const currentDate = moment().format('YYYY/MM/DD');
```

### ✅ Same vocabulary for same type
```js
// ❌ getUserInfo(), getClientData(), getCustomerRecord()
// ✅ getUser()
```

### ✅ Use searchable names (no magic numbers)
```js
// ❌ setTimeout(blastOff, 86400000);
const MILLISECONDS_PER_DAY = 60 * 60 * 24 * 1000;
setTimeout(blastOff, MILLISECONDS_PER_DAY); // ✅
```

### ✅ Use explanatory variables
```js
// ❌ Bad
saveCityZipCode(address.match(regex)[1], address.match(regex)[2]);

// ✅ Good
const [_, city, zipCode] = address.match(cityZipCodeRegex) || [];
saveCityZipCode(city, zipCode);
```

### ✅ Avoid mental mapping — be explicit
```js
// ❌ locations.forEach(l => { dispatch(l); });
// ✅ locations.forEach(location => { dispatch(location); });
```

### ✅ Don't add redundant context
```js
// ❌ const Car = { carMake, carModel, carColor }
// ✅ const Car = { make, model, color }
```

### ✅ Use default parameters
```js
// ❌ const name = name || 'Default';
// ✅ function create(name = 'Default') {}
```

---

## 🔧 Functions

### ✅ 2 arguments or fewer — use object destructuring for more
```js
// ❌ function createMenu(title, body, buttonText, cancellable) {}
// ✅ function createMenu({ title, body, buttonText, cancellable }) {}
```

### ✅ Functions should do ONE thing
```js
// ❌ emailClients() — fetches DB + checks active + sends email
// ✅ emailActiveClients() calls isActiveClient() separately
```

### ✅ Function names should say what they do
```js
// ❌ addToDate(date, 1)     → unclear what is added
// ✅ addMonthToDate(1, date) → crystal clear
```

### ✅ One level of abstraction per function
```js
// ❌ parseBetterJSAlternative() — tokenizes + parses + AST walks in one function
// ✅ parseBetterJSAlternative() → calls tokenize() → calls parse()
```

### ✅ Remove duplicate code — extract shared logic
### ✅ No flag parameters — split into separate functions
```js
// ❌ function createFile(name, isTemp) { if (isTemp) ... }
// ✅ function createFile(name) {}
//    function createTempFile(name) {}
```

### ✅ Avoid Side Effects
- Don't mutate global state
- Don't mutate function arguments (use copies)
```js
// ✅ Return new array instead of mutating
function addItemToCart(cart, item) {
  return [...cart, { item, date: Date.now() }];
}
```

### ✅ Favor functional programming
```js
// ❌ for loop with mutations
// ✅ filter(), map(), reduce()
const totalOutput = programmerOutput
  .filter(p => p.linesOfCode > 0)
  .reduce((acc, p) => acc + p.linesOfCode, 0);
```

### ✅ Encapsulate conditionals
```js
// ❌ if (fsm.state === 'fetching' && isEmpty(listNode)) {}
// ✅ if (shouldShowSpinner(fsmInstance, listNodeInstance)) {}
```

### ✅ Avoid negative conditionals
```js
// ❌ if (!isNotDOMNodePresent(node)) {}
// ✅ if (isDOMNodePresent(node)) {}
```

### ✅ Remove dead code immediately

---

## 🏛️ Classes

### ✅ Prefer ES6 classes
### ✅ Use method chaining (builder pattern)
```js
class QueryBuilder {
  select(fields) { this.fields = fields; return this; }
  from(table) { this.table = table; return this; }
  build() { return `SELECT ${this.fields} FROM ${this.table}`; }
}
new QueryBuilder().select('*').from('users').build();
```

### ✅ Prefer composition over inheritance
> "Favor has-a over is-a"

---

## 🧱 SOLID Principles

| Principle | Rule |
|-----------|------|
| **S** — Single Responsibility | One class = one job. Never combine unrelated concerns |
| **O** — Open/Closed | Open for extension, closed for modification |
| **L** — Liskov Substitution | Subclasses must be substitutable for their base class |
| **I** — Interface Segregation | Clients shouldn't depend on interfaces they don't use |
| **D** — Dependency Inversion | Depend on abstractions, not concretions |

```js
// ✅ D — Dependency Inversion
class InventoryService {
  constructor(inventoryRequester) { // inject the dependency
    this.inventoryRequester = inventoryRequester;
  }
  requestItems(customer) {
    return this.inventoryRequester.requestItem(customer.purchaseHistory);
  }
}
```

---

## ⚡ Concurrency

### ✅ Use Promises over callbacks
### ✅ Use async/await over Promises
```js
// ✅ Clearest form
async function getCleanCodeArticle() {
  try {
    const response = await request.get(cleanCodeUrl);
    await fs.writeFile('article.html', response);
  } catch (err) {
    console.error(err);
  }
}
```

---

## 🗒️ Comments

### ✅ Only comment business logic complexity
### ❌ Never leave commented-out code
### ❌ No journal comments (use git log instead)
### ❌ No positional markers (`/////`)
```js
// ✅ Good comment — explains WHY
// We retry 3x because OAuth2 tokens can have clock skew
const MAX_RETRIES = 3;
```

---

## 📐 Formatting

- Use consistent capitalization (camelCase for vars/fns, PascalCase for classes, UPPER_SNAKE for constants)
- Keep callers and callees close in the file
- Related code should appear together
