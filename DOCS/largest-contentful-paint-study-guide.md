# Largest Contentful Paint (LCP) Study Guide

Notes from this project: what LCP is, what was found on this site, and how to export images for it.

> Reference only. No code was changed while writing these notes. The repo owner makes all code changes.

---

## 1. Core concepts

**LCP (Largest Contentful Paint)** is the time from when the page starts loading until the largest visible element (i◊mage or block of text) is painted on screen.

- It measures *perceived load speed*: "when does the main content appear?"
- Google's targets (Core Web Vitals, measured at the 75th percentile of real users):
  - **Good:** 2.5 s or less
  - **Needs improvement:** 2.5 s to 4.0 s
  - **Poor:** more than 4.0 s

**Typical LCP elements:** hero/banner images, the profile picture at the top of a page, or a large heading.

**What delays LCP:**
1. Slow server response (TTFB)
2. Render-blocking CSS or JS in `<head>`
3. Slow resource loading (large images, large fonts)
4. Image not discovered early (no `preload` / `fetchpriority`)
5. Client-side rendering delays

**Tools to measure:**
- Chrome DevTools > Lighthouse (run in incognito, mobile and desktop)
- Chrome DevTools > Performance panel (look for the "LCP" marker)
- PageSpeed Insights (https://pagespeed.web.dev)

---

## 2. Glossary

| Term | Meaning |
|---|---|
| **TTFB** | Time To First Byte: how fast the server starts responding. |
| **Render-blocking** | A resource the browser must finish before painting (e.g. a `<script>` in `<head>` without `defer`). |
| **`defer` / `async`** | Script attributes that let the HTML keep parsing while the script downloads. |
| **`preload`** | `<link rel="preload">` tells the browser to fetch a resource now, because it will be needed soon. |
| **`fetchpriority="high"`** | Hint that an image is important and should download first. |
| **`loading="lazy"`** | Delay downloading images that are off-screen. Don't use it on the LCP image. |
| **`width` / `height`** | Reserve space for an image so the layout doesn't jump (CLS). |
| **`font-display: swap`** | Show fallback text immediately, then swap in the web font when it loads. |
| **WOFF2** | Compressed web font format. Smaller than TTF/OTF. |
| **WebP / AVIF** | Modern image formats, much smaller than PNG/JPEG at similar quality. |
| **Retina / 2x** | Screens with double pixel density. Serve images at 2x the displayed CSS size for sharpness. |
| **Gzip / Brotli** | Compression for text responses (HTML, CSS, JS). |
| **Cache-Control** | Response header telling browsers how long to keep a file. |

---

## 3. Findings for this site

| Area | What was found | Why it matters for LCP |
|---|---|---|
| Profile picture | `static/images/profile-1.png` is **512x512 PNG, about 292 KB**, displayed at **5rem (about 80px)** | Probably the LCP element on the home page. It's far larger than needed. |
| Tailwind | `@tailwindcss/browser@4` loaded as a normal `<script>` in `<head>` | Render-blocking. Generates CSS at runtime, which delays the first paint. |
| Fonts | Three Iosevka `.woff2` files, about **1.2 MB each** (about 3.7 MB total) | Large downloads. Text can be delayed while the font loads. No `font-display` or `preload` set. |
| Card images | 640px JPEGs, up to about 89 KB, displayed at about 120px | Larger than needed. No `loading="lazy"` and no `width`/`height` set. |
| Compression | No `GZipMiddleware` in `main.py` | HTML/CSS/JS sent uncompressed unless the host does it. |
| Caching | `StaticFiles` sets no `Cache-Control` | Repeat visits re-download everything. |

### Priority order for fixes

1. **Shrink and optimize the profile image** (cheapest, biggest impact on the likely LCP element)
2. **Make fonts smaller and load them better** (subset, `font-display: swap`, preload regular weight)
3. **Stop blocking rendering with Tailwind** (compile CSS for production instead of the browser build)
4. **Lazy-load and size card images** (`loading="lazy"`, `width`, `height`, smaller files)
5. **Enable gzip** (`GZipMiddleware`)
6. **Set cache headers on `/static`**

---

## 4. How to export profile-1.png as WebP or AVIF

Target: **160x160 pixels** (2x the 80px display size), WebP or AVIF, well under 20 KB.

Run these from the repo's `static/images` folder:

```bash
cd /Users/gero/Documents/Coding/gero-website-2026/static/images
```

### Option A: Command line (recommended)

Install once:

```bash
brew install webp            # provides cwebp
brew install imagemagick     # optional, provides magick
brew install libavif         # optional, only for AVIF
```

**WebP with ImageMagick:**

```bash
magick profile-1.png -resize 160x160 -strip profile-1.webp
```

**WebP without ImageMagick (sips + cwebp):**

```bash
sips -z 160 160 profile-1.png --out /tmp/profile-160.png
cwebp -q 80 /tmp/profile-160.png -o profile-1.webp
```

**AVIF:**

```bash
sips -z 160 160 profile-1.png --out /tmp/profile-160.png
avifenc --qcolor 60 /tmp/profile-160.png profile-1.avif
```

### Option B: Browser (no install)

1. Go to https://squoosh.app
2. Drag in `static/images/profile-1.png`
3. Right panel: choose **WebP** (or **AVIF**), quality about 80
4. Under **Resize**, set width to 160 (the image is square)
5. Download and save as `static/images/profile-1.webp`

### Option C: Preview / Photoshop

Preview can resize (**Tools > Adjust Size**) but can't export WebP or AVIF. Use Squoosh or the command line instead.

### Verify the result

```bash
file static/images/profile-1.webp
ls -la static/images/profile-1.webp
```

Expected: 160x160, well under 20 KB.

### Notes

- **WebP vs AVIF:** AVIF is usually smaller, but WebP encodes faster and is supported everywhere. WebP is the simpler default.
- **Keep the original PNG** until the new file is in use and checked.
- **The new file isn't used automatically.** The template must reference it. Relevant file: `templates/jinja_components/header_home.html`.

---

## 5. How the new image should be used (for reference)

The HTML would look roughly like this. Study it; the repo owner applies the change.

```html
<img
  src="static/images/profile-1.webp"
  width="80"
  height="80"
  fetchpriority="high"
  alt="Gero Zayas profile picture"
/>
```

| Attribute | Why |
|---|---|
| `width` / `height` | Reserves space so the layout doesn't shift (CLS). |
| `fetchpriority="high"` | Tells the browser to download this image first. |
| No `loading="lazy"` | Lazy loading would delay the LCP image. Only use it below the fold. |
| `alt` | Accessibility and SEO. Use a real description, not an empty string, for a meaningful image. |

For a fallback to PNG in older browsers, use `<picture>`:

```html
<picture>
  <source srcset="static/images/profile-1.avif" type="image/avif" />
  <source srcset="static/images/profile-1.webp" type="image/webp" />
  <img src="static/images/profile-1.png" width="80" height="80" fetchpriority="high" alt="Gero Zayas profile picture" />
</picture>
```

---

## 6. Flashcards

**Q: What is LCP?**
A: Time until the largest visible content element is painted. Good is 2.5 s or less.

**Q: What are the three LCP thresholds?**
A: Good is 2.5 s or less, needs improvement is 2.5 to 4.0 s, poor is over 4.0 s.

**Q: Why shouldn't you use `loading="lazy"` on the LCP image?**
A: Lazy loading delays the download, which delays the LCP. Lazy-load only images below the fold.

**Q: What does `fetchpriority="high"` do?**
A: Hints to the browser to download this resource before other images.

**Q: Why set `width` and `height` on images?**
A: The browser reserves the space before the image loads, which prevents layout shift (CLS).

**Q: Why serve images at 2x the displayed size?**
A: High-density (retina) screens need twice the pixels to look sharp.

**Q: Why is a 512x512 PNG shown at 80px wasteful?**
A: The browser downloads about 40 times more pixels than it displays, so the page loads slower.

**Q: WebP or AVIF, which should you use by default?**
A: WebP. It's simpler and supported everywhere. AVIF is smaller but slower to encode.

**Q: What does `font-display: swap` do?**
A: Shows fallback text right away, then swaps in the web font when it has loaded.

**Q: Why is a render-blocking script bad for LCP?**
A: The browser must download and run it before painting, which delays the first visible content.

**Q: What does `preload` do?**
A: Tells the browser to fetch a critical resource now, instead of waiting until it discovers it.

**Q: What's the difference between `defer` and `async` on scripts?**
A: `defer` runs after HTML parsing in order. `async` runs as soon as it downloads, in any order.

**Q: What does `GZipMiddleware` do in FastAPI?**
A: Compresses responses (HTML, CSS, JS) to reduce transfer size.

**Q: Why use `<picture>` with WebP/AVIF sources?**
A: The browser picks the best format it supports and falls back to PNG if none match.

---

## 7. Memory tricks

- **LCP = "when does the biggest thing show up?"**
- **Three fixes for the biggest image:** make it **small**, make it **early** (`fetchpriority`, `preload`), and give it **room** (`width`/`height`).
- **Don't block the page:** if it's in `<head>` and it's not needed to paint, use `defer` or move it out.
- **Lazy = later.** Only use `loading="lazy"` for things *below* the fold.
