# SQLite Named Parameters Study Guide

How to use named (`:name`) parameterized queries in Python's `sqlite3`, and where they beat positional (`?`) placeholders.

> Reference only. No code was changed while writing these notes. The repo owner makes all code changes.

---

## 1. The basic rule

```python
# positional (what the project uses now): ? with a tuple
cursor.execute("SELECT * FROM gero_blog WHERE id = ?", (blog_id,))

# named: :name with a dict
cursor.execute("SELECT * FROM gero_blog WHERE id = :id", {"id": blog_id})
```

The dict keys match the placeholder names. Order no longer matters — that's the main advantage.

## 2. Supported prefix styles

`sqlite3` accepts several prefixes; `:name` is the most common:

| Style | SQL | Python |
|---|---|---|
| Named | `WHERE id = :id` | `{"id": 5}` |
| Numeric | `WHERE id = :1` | `{"1": 5}` (rarely used) |
| qmark | `WHERE id = ?` | `(5,)` |
| Go style | `WHERE id = @id` | `{"id": 5}` |
| Dollar | `WHERE id = $id` | `{"id": 5}` |

Stick with `:name` — it's the readable one.

## 3. Where named params shine

**Same value used twice — with `?` you'd pass it twice; with `:name` once:**

```python
cursor.execute(
    "SELECT * FROM gero_blog WHERE lang = :lang OR title LIKE :lang",
    {"lang": "%python%"},
)
```

**Insert with many columns — the dict keys self-document:**

```python
INSERT_ROW_QUERY = """
INSERT INTO {table_name} (title, content, tags, lang)
VALUES (:title, :content, :tags, :lang)
"""

cursor.execute(INSERT_ROW_QUERY.format(table_name="gero_blog"), {
    "title": "My post",
    "content": "# Hello",
    "tags": "python,db",
    "lang": "EN",
})
```

Nice side effect: if form data is already a dict, it can be passed **directly** as long as keys match the placeholders — no unpacking `data["title"], data["content"], ...` into a tuple.

## 4. Fitting the project's `execute_query(query, values)`

The existing signature works unchanged — just pass a dict instead of a tuple:

```python
res = execute_query(
    "SELECT * FROM {table_name} WHERE id = :id",
    {"id": blog_id},
    read_one=True,
)
```

Only caveat: `.format(table_name=...)` is fine, but **`format` is only safe for the table name because the code controls it**. Never format user input into SQL; everything user-supplied goes through `:params`.

## 5. Warning: don't build param names from user input

```python
# ❌ DANGEROUS — same injection risk as format
cursor.execute(f"SELECT * FROM t WHERE {column} = :val", {"val": x})

# ✅ safe — whitelist
ALLOWED = {"title", "tags", "lang"}
if column not in ALLOWED:
    raise ValueError("bad column")
cursor.execute(f"SELECT * FROM t WHERE {column} = :val", {"val": x})
```

Named params protect **values**. Column/table/order-by names always need whitelisting, whichever style is used.

## 6. Flashcards

**Q: What Python object do named parameters require?**
A: A dict, whose keys match the placeholder names.

**Q: What Python object do `?` placeholders require?**
A: A tuple (or sequence), values in order.

**Q: What are the five placeholder styles `sqlite3` supports?**
A: `:name`, `:1` (numeric), `?` (qmark), `@name`, `$name`.

**Q: Main advantage of named parameters?**
A: Self-documenting values, order-independent, and the same value can repeat with one dict entry.

**Q: How do you repeat a value in a query with named params?**
A: Use the same placeholder twice, e.g. `lang = :lang OR title LIKE :lang`, and pass `{"lang": ...}` once.

**Q: Can a dict be passed straight to `execute` if it has extra keys?**
A: Yes — extra keys are ignored by `sqlite3`; only the ones referenced in the SQL matter.

**Q: Why is `format(table_name=...)` acceptable but formatting user input is not?**
A: The table name is controlled by the code, so no injection risk. User input in SQL text is always an injection vector.

**Q: What do parameterized queries protect against?**
A: SQL injection of **values**. Identifiers (column/table names) need whitelisting instead.

## 7. Memory tricks

- **Tuple for `?`, dict for `:name`.**
- **Named params = labeled arguments.** The SQL says what it wants; the dict supplies it by name.
- **Params protect values; whitelists protect names.**
- **Extra dict keys are harmless** — think of it as the query picking what it needs.
