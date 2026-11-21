# Font Optimization Study Guide

Notes from this project: why the Iosevka fonts are slow, and how to make them load fast.

> Reference only. No code was changed while writing these notes. The repo owner makes all code changes.

---

## 1. The key insight

**WOFF2 is already Brotli-compressed internally.** Running gzip or Brotli middleware on a `.woff2` file gains almost nothing — the file is already compressed.

The real win is making the font **smaller**, not compressing it harder. That means **subsetting**: keeping only the glyphs you actually use.

## 2. Why the fonts are so big

Iosevka ships with **thousands of glyphs** — full Unicode coverage: Cyrillic, Greek, math symbols, box drawing, powerline icons, etc. This site only uses Latin plus a few Spanish characters (`¿`, `é`, `ñ`, `¡`...). That's why each file is ~1.2 MB.

Current state (from `static/fonts/`):

| File | Size |
|---|---|
| `iosevka-regular.woff2` | ~1.2 MB |
| `iosevka-bold.woff2` | ~1.2 MB |
| `iosevka-italic.woff2` | ~1.3 MB |

Subsetting typically cuts these to **50–150 KB each — a ~90% reduction**.

## 3. The fixes, in order of impact

### 1. Subset the fonts (biggest win)

Use `pyftsubset` from the `fonttools` package:

```bash
uv add fonttools brotli

cd /Users/gero/Documents/Coding/gero-website-2026/static/fonts

# Keep basic Latin + Latin-1 (Spanish chars) + punctuation + common symbols
pyftsubset iosevka-regular.woff2 \
  --output-file=iosevka-regular-subset.woff2 \
  --flavor=woff2 \
  --layout-features='*' \
  --unicodes="U+0000-00FF,U+2000-206F,U+2070-209F,U+20A0-20BF,U+2190-21FF"

pyftsubset iosevka-bold.woff2 \
  --output-file=iosevka-bold-subset.woff2 \
  --flavor=woff2 \
  --layout-features='*' \
  --unicodes="U+0000-00FF,U+2000-206F,U+2070-209F,U+20A0-20BF,U+2190-21FF"

pyftsubset iosevka-italic.woff2 \
  --output-file=iosevka-italic-subset.woff2 \
  --flavor=woff2 \
  --layout-features='*' \
  --unicodes="U+0000-00FF,U+2000-206F,U+2070-209F,U+20A0-20BF,U+2190-21FF"
```

Check the results:

```bash
ls -la *subset*
```

If a character shows in fallback font on the site, add its Unicode range to the list and re-run.

**Unicode ranges used above:**

| Range | Covers |
|---|---|
| `U+0000-00FF` | Basic Latin + Latin-1 Supplement: all English and Spanish accents, `¿`, `¡`, etc. |
| `U+2000-206F` | General punctuation: dashes, quotes, ellipsis |
| `U+2070-209F` | Superscripts and subscripts |
| `U+20A0-20BF` | Currency symbols: €, £, ¥, ₹ |
| `U+2190-21FF` | Arrows |

### 2. Only load what the page uses

Browsers only download a `@font-face` file **if the page actually renders text in that weight/style**. Regular loads on every page; bold/italic only download when used. Check whether all three weights are really needed site-wide.

### 3. `font-display: swap` — show text immediately

In `static/style.css`, add to each `@font-face` block:

```css
@font-face {
    font-family: "Iosevka";
    src: url("/static/fonts/iosevka-regular-subset.woff2") format("woff2");
    font-weight: 400;
    font-style: normal;
    font-display: swap;   /* ← add this */
}
```

Without it, browsers hide text until the font finishes loading (the "invisible text" problem). With `swap`, text paints instantly in the fallback (`monospace`, already listed) and swaps when ready.

### 4. Preload the regular weight

In `templates/base.html` `<head>`:

```html
<link rel="preload" href="/static/fonts/iosevka-regular-subset.woff2"
      as="font" type="font/woff2" crossorigin>
```

This starts the font download immediately instead of waiting for CSS → font discovery. Preload **only the regular weight** — preloading all three wastes bandwidth on files that may never be used.

The `crossorigin` attribute is required even for same-origin fonts: fonts are always fetched in CORS mode.

### 5. Cache headers (repeat visits)

Fonts rarely change, so they should be cached hard:

```
Cache-Control: public, max-age=31536000, immutable
```

Set at the host/proxy, or via middleware. Since new font versions get new filenames (`-subset`), aggressive caching is safe.

### 6. Optional: variable font

Iosevka publishes a **variable font** — one file covers regular + bold + italic through weight axes. Caveat: even a *subset* variable font can be bigger than three small subsets. Measure before switching; three ~100 KB files that load on demand are often better.

## 4. Expected result

| | Before | After |
|---|---|---|
| Regular | ~1.2 MB | ~100 KB |
| Bold | ~1.2 MB | ~100 KB (only when used) |
| Italic | ~1.3 MB | ~100 KB (only when used) |
| Total transfer, home page | ~1.2 MB (regular only) | ~100 KB |

## 5. Flashcards

**Q: Is WOFF2 already compressed?**
A: Yes — it uses Brotli internally. Don't recompress it; subset it instead.

**Q: Why is Iosevka 1.2 MB per file?**
A: It ships thousands of glyphs (full Unicode). Most are never used on the site.

**Q: What is subsetting?**
A: Keeping only the glyphs actually used, reducing file size by ~90%.

**Q: What tool subsets fonts?**
A: `pyftsubset`, from the `fonttools` package.

**Q: What does `font-display: swap` do?**
A: Shows text immediately in a fallback font, then swaps in the web font when loaded. Prevents invisible text.

**Q: What happens without `font-display`?**
A: Browsers hide text until the font loads (FOIT — flash of invisible text).

**Q: Why preload only the regular weight?**
A: Preloading wastes bandwidth if the file is never used. Regular is the only weight guaranteed to be needed.

**Q: Why is `crossorigin` required on font preloads?**
A: Fonts are always fetched in CORS mode, even same-origin. Without the attribute, the preload is fetched twice or ignored.

**Q: Do browsers download all `@font-face` files?**
A: No — only the ones matching text actually rendered on the page.

**Q: What Cache-Control suits fonts?**
A: `public, max-age=31536000, immutable` — fonts rarely change; new versions get new filenames.

**Q: gzip or Brotli for fonts?**
A: Neither helps — WOFF2 is already compressed. Subset instead.

**Q: What is a variable font?**
A: One file covering multiple weights/styles via axes. Fewer requests, but often bigger than subsets.

## 6. Memory tricks

- **"WOFF2 = already squeezed. Subset, don't compress."**
- **Font speed = 3 moves:** make it **small** (subset), make it **early** (preload), make it **non-blocking** (`font-display: swap`).
- **Latin-1 (`U+0000-00FF`) covers English + Spanish.** Add ranges only when something renders wrong.
- **Preload one, subset all three.** Regular is the only one needed on every page.
