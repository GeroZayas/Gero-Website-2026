# Security Headers Study Guide

Reference for the security middleware in `main.py`:

```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    return response
```

---

## What each line does

| Line | Plain English |
|---|---|
| `@app.middleware("http")` | Runs this function on every request. It lets the response go through, then adds headers before sending it back. |
| `await call_next(request)` | "Let the actual route handle the request and give me its response." |
| `Strict-Transport-Security` | "Browsers, only ever talk to me over HTTPS for the next 2 years." `max-age` is in seconds (63072000 ≈ 2 years). `includeSubDomains` applies the rule to subdomains too. |
| `X-Content-Type-Options: nosniff` | "Trust my `Content-Type` label. Don't guess the file type." |
| `X-Frame-Options: DENY` | "Nobody may embed my pages in an iframe." Blocks clickjacking. |
| `Content-Security-Policy` | "Only load resources from these sources." A whitelist for scripts, styles, images, and so on. |

### CSP directives

| Directive | Controls |
|---|---|
| `default-src 'self'` | Fallback for anything not listed. `'self'` means same origin only. |
| `script-src` | Where JavaScript can come from. |
| `style-src` | Where CSS can come from. |
| `img-src` | Where images can come from. |
| `connect-src` | Where `fetch`, XHR, and SSE/Datastar requests can go. |
| `frame-ancestors 'none'` | Who may embed your page in a frame. Modern replacement for `X-Frame-Options`. |

### CSP keywords

| Keyword | Meaning |
|---|---|
| `'self'` | Same origin (same scheme, host, and port). |
| `https://cdn.jsdelivr.net` | That specific external host. |
| `'unsafe-inline'` | Allow inline `<style>`/`<script>` and `style=""` attributes. "Unsafe" because attackers can inject these too. |
| `'unsafe-eval'` | Allow `eval()` and `new Function()`. Needed here for Datastar expressions. |
| `data:` | Allow `data:` URLs, such as inline base64 images. |

---

## Flashcards

**Q: What is a security header?**
A: An HTTP response header that tells the browser how to behave safely, e.g., what to load or whether to allow framing.

**Q: Why is this middleware instead of a route decorator?**
A: Middleware runs on every request, so every page gets the headers without repeating code.

**Q: What does `await call_next(request)` do?**
A: It runs the rest of the app (the route) and returns its response, so you can modify it.

**Q: What is HSTS?**
A: `Strict-Transport-Security`. Tells browsers to use HTTPS only for the given time, blocking downgrade attacks.

**Q: What does `max-age` mean?**
A: How many seconds the browser remembers the HTTPS-only rule. 63072000 = 2 years.

**Q: What does `includeSubDomains` do?**
A: Applies the HTTPS rule to all subdomains as well.

**Q: What attack does `X-Content-Type-Options: nosniff` prevent?**
A: MIME sniffing: the browser executing a file as script even though it was served as, say, plain text.

**Q: What attack does `X-Frame-Options: DENY` prevent?**
A: Clickjacking: your site hidden in an invisible iframe on a malicious page.

**Q: What is CSP?**
A: Content-Security-Policy. A whitelist of allowed sources for scripts, styles, images, and other resources. The main defense against XSS.

**Q: What does `default-src 'self'` mean?**
A: Default for everything not specified: load only from your own origin.

**Q: What does `script-src` control?**
A: Where JavaScript may be loaded from and whether inline or eval'd JS runs.

**Q: What does `connect-src` control?**
A: Which URLs the page may call with `fetch`, XHR, or event streams (Datastar uses these).

**Q: What is `frame-ancestors 'none'`?**
A: CSP's version of `X-Frame-Options: DENY`. Nobody may frame the page. The modern standard.

**Q: What is `'unsafe-inline'` and why is it "unsafe"?**
A: It allows inline scripts/styles. It weakens CSP because injected inline code would also run.

**Q: What is `'unsafe-eval'`?**
A: Allows `eval()` and `new Function()`. Needed by some frameworks like Datastar. Avoid it if you can.

**Q: Why are the CDN URLs in `script-src` and `style-src`?**
A: Tailwind and Datastar load from jsDelivr. Without listing it, the browser blocks them.

**Q: Why doesn't HSTS hurt localhost development?**
A: Browsers ignore HSTS on plain `http://localhost`.

---

## Memory tricks

- **Headers:** No HTTP (HSTS), no sniffing (nosniff), no frames (X-Frame-Options), plus CSP as the big whitelist.
- **CSP = bouncer with a guest list.** `'self'` = your own people. Each directive = a different door (scripts, styles, images, network calls). `unsafe-*` = letting the bouncer skip checks.
- **Read a CSP left to right:** directive name, then allowed sources. Example: `script-src 'self' cdn.jsdelivr.net` = "scripts come from me or jsDelivr."
