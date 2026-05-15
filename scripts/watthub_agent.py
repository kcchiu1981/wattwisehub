import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from html import escape
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

SITE_URL = "https://wattwisehome.com"

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
display_date = now.strftime("%b %d, %Y")
current_year = now.year
current_month = now.strftime("%B")

guides_dir = Path("guides")
guides_dir.mkdir(parents=True, exist_ok=True)

index_file = Path("index.html")
sitemap_file = Path("sitemap.xml")

prompt = f"""
You are WattWiseHome's autonomous SEO content agent.

Current year: {current_year}
Current month: {current_month}

Website: WattWiseHome
Niche: home energy efficiency
Audience: US homeowners and renters
Goal: organic SEO traffic and affiliate revenue

Return JSON only. No markdown. No code fences.

Choose ONE practical home energy efficiency guide topic.

Important:
- Do not invent Amazon links, affiliate URLs, ASINs, or product pages.
- Never use outdated years.
- Use current year only when it makes SEO sense.
- Prefer evergreen + seasonal + buyer-intent topics.
- Avoid exaggerated savings claims.
- Be practical, trustworthy, and useful.

JSON schema:
{{
  "slug": "url-slug-without-html",
  "title": "Article title",
  "meta_description": "SEO meta description",
  "summary": "One short sentence for homepage card",
  "read_time": "~7-9 minutes",
  "toc": [
    {{"id":"section-id","label":"Navigation label"}}
  ],
  "disclosure": "Disclosure sentence",
  "sections": [
    {{
      "id": "section-id-or-empty",
      "heading": "Section heading",
      "html": "<p>Section content in valid HTML.</p><ul><li>...</li></ul>"
    }}
  ],
  "faq": [
    {{"question":"Question text","answer":"Answer text"}}
  ],
  "next_guide": {{
    "heading": "Next guide heading",
    "text": "Short next step text",
    "url": "/guides/best-electricity-usage-monitor-2026",
    "anchor": "Read: Best Electricity Usage Monitor for Home"
  }}
}}

Requirements:
- Include 4 to 6 TOC items.
- Include at least one practical comparison table in one section.
- Include internal links to:
  /calculator
  /guides/diy-home-energy-audit
  /guides/weatherstripping-guide
  /guides/smart-thermostat-guide
- Make section HTML clean and simple.
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt,
)

raw = response.output_text.strip()
raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
raw = re.sub(r"^```\s*", "", raw)
raw = re.sub(r"\s*```$", "", raw)

data = json.loads(raw)

slug = re.sub(r"[^a-z0-9-]+", "-", data["slug"].lower()).strip("-")
title = data["title"].strip()
meta_description = data["meta_description"].strip()
summary = data["summary"].strip()
read_time = data.get("read_time", "~7-9 minutes")
disclosure = data.get(
    "disclosure",
    "Disclosure: As an Amazon Associate, WattWiseHome may earn from qualifying purchases. Product links should be verified before publishing."
)

guide_filename = guides_dir / f"{slug}.html"
if guide_filename.exists():
    slug = f"{slug}-{today}"
    guide_filename = guides_dir / f"{slug}.html"

canonical_url = f"{SITE_URL}/guides/{slug}"

toc_html = "\n".join(
    f'      <li><a href="#{escape(item["id"])}">{escape(item["label"])}</a></li>'
    for item in data["toc"]
)

sections_html = ""
for section in data["sections"]:
    section_id = section.get("id", "").strip()
    section_id_attr = f' id="{escape(section_id)}"' if section_id else ""
    sections_html += f"""
  <section{section_id_attr}>
    <h2>{escape(section["heading"])}</h2>
    {section["html"]}
  </section>
"""

faq_html = ""
for item in data["faq"]:
    faq_html += f"""
    <h3>{escape(item["question"])}</h3>
    <p>{escape(item["answer"])}</p>
"""

next_guide = data.get("next_guide", {})
next_heading = next_guide.get("heading", "Next guide")
next_text = next_guide.get("text", "Continue with the next practical WattWiseHome guide.")
next_url = next_guide.get("url", "/guides/best-electricity-usage-monitor-2026")
next_anchor = next_guide.get("anchor", "Read the next guide")

html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{escape(title)} | WattWiseHome</title>
  <meta name="description" content="{escape(meta_description)}" />
  <link rel="canonical" href="{escape(canonical_url)}" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">

  <style>
    :root {{ --max: 860px; --fg:#111; --muted:#666; --bg:#fff; --line:#e8e8e8; --link:#0b57d0; }}
    body {{ margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color:var(--fg); background:var(--bg); line-height:1.6; }}
    header, main, footer {{ max-width: var(--max); margin: 0 auto; padding: 24px; }}
    header {{ padding-top: 34px; border-bottom: 1px solid var(--line); }}
    h1 {{ font-size: 2rem; line-height: 1.2; margin: 0 0 12px; }}
    .meta {{ color: var(--muted); font-size: 0.95rem; }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    h2 {{ margin-top: 34px; font-size: 1.4rem; }}
    h3 {{ margin-top: 24px; font-size: 1.1rem; }}
    .toc {{ border:1px solid var(--line); border-radius: 10px; padding: 16px; margin: 20px 0; }}
    .toc strong {{ display:block; margin-bottom: 6px; }}
    .card {{ border:1px solid var(--line); border-radius: 12px; padding: 16px; margin: 14px 0; }}
    .note {{ color: var(--muted); font-size: 0.95rem; }}
    table {{ width:100%; border-collapse: collapse; margin: 12px 0; }}
    th, td {{ border:1px solid var(--line); padding: 10px; text-align:left; vertical-align: top; }}
    th {{ background:#fafafa; }}
    .cta {{ border: 1px solid var(--line); border-radius: 12px; padding: 16px; background:#fcfcff; }}
    footer {{ border-top: 1px solid var(--line); color: var(--muted); font-size: 0.95rem; padding-bottom: 50px; }}
    .small {{ font-size: 0.9rem; color: var(--muted); }}
  </style>
</head>

<body>
<header>
  <h1>{escape(title)}</h1>
  <div class="meta">
    Updated <time datetime="{today}">{display_date}</time> ·
    <a href="/guides/">Guides</a> ·
    Read time: {escape(read_time)}
  </div>

  <div class="toc" role="navigation" aria-label="Table of contents">
    <strong>Quick Navigation</strong>
    <ol>
{toc_html}
    </ol>
  </div>

  <p class="note">
    {escape(disclosure)}
  </p>
</header>

<main>
  <section class="cta">
    <h2 style="margin-top:0">Want a quick estimate of appliance cost?</h2>
    <p>Use our calculator to estimate how much an appliance costs to run per day/month based on watts and local electricity price.</p>
    <p><a href="/calculator">Open Electricity Cost Calculator &rarr;</a></p>
  </section>

{sections_html}

  <section id="faq">
    <h2>FAQ</h2>
{faq_html}
  </section>

  <section class="cta">
    <h2 style="margin-top:0">{escape(next_heading)}</h2>
    <p>{escape(next_text)}</p>
    <p><a href="{escape(next_url)}">{escape(next_anchor)} &rarr;</a></p>
  </section>
</main>

<footer>
  <p><strong>WattWiseHome</strong> — Practical energy-saving guides for real homes.</p>
  <p class="small">Affiliate disclosure: We may earn commissions from qualifying purchases at no extra cost to you.</p>
</footer>
</body>
</html>
"""

guide_filename.write_text(html, encoding="utf-8")
print(f"Created guide page: {guide_filename}")

# Update index.html
if index_file.exists():
    index_html = index_file.read_text(encoding="utf-8")

    card = f"""
  <article class="card">
    <h3><a href="guides/{slug}">{escape(title)}</a></h3>
    <p>{escape(summary)}</p>
    <a href="guides/{slug}">Read the guide →</a>
  </article>
"""

    if "<!-- AI_GUIDES_START -->" in index_html and "<!-- AI_GUIDES_END -->" in index_html:
        index_html = index_html.replace(
            "<!-- AI_GUIDES_START -->",
            "<!-- AI_GUIDES_START -->\\n" + card,
            1,
        )
        index_file.write_text(index_html, encoding="utf-8")
        print("Updated index.html")
    else:
        print("WARNING: index.html does not contain AI_GUIDES_START / AI_GUIDES_END markers.")
else:
    print("WARNING: index.html not found.")

# Update sitemap.xml
new_url = f"{SITE_URL}/guides/{slug}"

if sitemap_file.exists():
    sitemap_xml = sitemap_file.read_text(encoding="utf-8")

    if new_url not in sitemap_xml:
        url_entry = f"""
  <url>
    <loc>{new_url}</loc>
    <lastmod>{today}</lastmod>
  </url>
"""
        sitemap_xml = sitemap_xml.replace("</urlset>", url_entry + "\\n</urlset>")
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
