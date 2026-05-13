import os
import re
from datetime import datetime, timezone
from pathlib import Path
from html import escape
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SITE_URL = "https://0dcc0142.wattwisehub.pages.dev"

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
current_year = now.year
current_month = now.strftime("%B")

guides_dir = Path("guides")
guides_dir.mkdir(parents=True, exist_ok=True)

index_file = Path("index.html")
sitemap_file = Path("sitemap.xml")

prompt = f"""
You are WattHub's autonomous SEO content agent.

Current year: {current_year}
Current month: {current_month}

Website: WattHub / WattWiseHome
Niche: home energy efficiency
Audience: US homeowners and renters
Goal: organic SEO traffic and affiliate revenue

Task:
Create ONE complete, publishable HTML guide page.

Important rules:
- Output HTML only.
- Do not wrap output in markdown code fences.
- Do not invent Amazon links, affiliate URLs, ASINs, or product pages.
- Only mention product categories or real-world product names without direct purchase links.
- Never use outdated years.
- Use the current year when appropriate.
- Prefer evergreen + seasonal + buyer-intent topics.
- Avoid exaggerated savings claims.
- Be practical, trustworthy, and useful.

The HTML page must include:
- <!doctype html>
- <html lang="en">
- <head> with title, meta description, viewport, and link to ../styles.css
- <body>
- Header with links:
  - Home: ../index.html
  - Guides: ../index.html#guides
  - Calculator: ../calculator.html
- A main article
- H1 title
- Introduction
- Practical advice
- FAQ section
- Internal links to:
  - ../calculator.html
  - ./weatherstripping-guide.html
  - ./smart-thermostat-guide.html
- Affiliate disclosure section saying links may be added after product verification
- No fake affiliate links

Also include these HTML comments near the top:
<!-- slug: your-url-slug-here -->
<!-- summary: one short sentence summary for homepage card -->

Choose the best topic yourself.
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt,
)

html = response.output_text.strip()

# Remove accidental markdown fences
html = re.sub(r"^```html\s*", "", html, flags=re.IGNORECASE)
html = re.sub(r"^```\s*", "", html)
html = re.sub(r"\s*```$", "", html)

def extract_comment(name: str, text: str) -> str | None:
    match = re.search(rf"<!--\s*{name}:\s*(.*?)\s*-->", text, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None

def extract_tag(tag: str, text: str) -> str | None:
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    value = re.sub(r"<.*?>", "", match.group(1))
    return re.sub(r"\s+", " ", value).strip()

slug = extract_comment("slug", html)

if not slug:
    title_for_slug = extract_tag("h1", html) or f"watthub-guide-{today}"
    slug = title_for_slug.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")[:80]

title = extract_tag("h1", html) or slug.replace("-", " ").title()
summary = extract_comment("summary", html) or "A practical WattHub guide to help reduce home energy waste."

guide_filename = guides_dir / f"{slug}.html"

if guide_filename.exists():
    guide_filename = guides_dir / f"{slug}-{today}.html"
    slug = f"{slug}-{today}"

guide_filename.write_text(html, encoding="utf-8")
print(f"Created guide page: {guide_filename}")

# Update index.html
if index_file.exists():
    index_html = index_file.read_text(encoding="utf-8")

    card = f"""
  <article class="card">
    <h3><a href="guides/{slug}.html">{escape(title)}</a></h3>
    <p>{escape(summary)}</p>
    <a href="guides/{slug}.html">Read the guide →</a>
  </article>
"""

    if "<!-- AI_GUIDES_START -->" in index_html and "<!-- AI_GUIDES_END -->" in index_html:
        index_html = index_html.replace(
            "<!-- AI_GUIDES_START -->",
            "<!-- AI_GUIDES_START -->\n" + card,
            1,
        )
        index_file.write_text(index_html, encoding="utf-8")
        print("Updated index.html")
    else:
        print("WARNING: index.html does not contain AI_GUIDES_START / AI_GUIDES_END markers.")
else:
    print("WARNING: index.html not found.")

# Update sitemap.xml
new_url = f"{SITE_URL}/guides/{slug}.html"

if sitemap_file.exists():
    sitemap_xml = sitemap_file.read_text(encoding="utf-8")

    if new_url not in sitemap_xml:
        url_entry = f"""
  <url>
    <loc>{new_url}</loc>
    <lastmod>{today}</lastmod>
  </url>
"""
        sitemap_xml = sitemap_xml.replace("</urlset>", url_entry + "\n</urlset>")
        sitemap_file.write_text(sitemap_xml, encoding="utf-8")
        print("Updated sitemap.xml")
    else:
        print("Sitemap already contains this URL.")
else:
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{new_url}</loc>
    <lastmod>{today}</lastmod>
  </url>
</urlset>
"""
    sitemap_file.write_text(sitemap_xml, encoding="utf-8")
    print("Created sitemap.xml")
