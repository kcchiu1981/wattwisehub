import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Current date info
now = datetime.utcnow()
today = now.strftime("%Y-%m-%d")
current_year = now.year
current_month = now.strftime("%B")

draft_dir = Path("content/drafts")
draft_dir.mkdir(parents=True, exist_ok=True)

prompt = f"""
You are WattHub's autonomous content strategist and SEO agent.

Current year: {current_year}
Current month: {current_month}

Website: WattHub / WattWiseHome
Niche: home energy efficiency
Audience: US homeowners and renters
Goal: organic SEO traffic and affiliate revenue

Task:
1. Analyze what type of home energy topic is seasonally relevant right now.
2. Choose the BEST article topic for this week.
3. Explain briefly why this topic is strategically valuable.
4. Write a publishable SEO article draft in Markdown.

Content Strategy Rules:
- Use the CURRENT YEAR dynamically when appropriate.
- Never use outdated years.
- Prefer evergreen + high buyer intent topics.
- Prefer seasonally relevant topics.
- Avoid duplicate topics already commonly found on WattHub.
- Focus on practical consumer problems and energy savings.
- Use realistic product categories and home improvement scenarios.
- Avoid fake claims or exaggerated savings.

Include:
- SEO title
- Meta description
- Suggested URL slug
- Introduction
- Article body
- Comparison table if useful
- FAQ section
- Internal link suggestions
- Affiliate placement suggestions

Output in Markdown only.
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt,
)

content = response.output_text

filename = draft_dir / f"{today}-watthub-agent-draft.md"
filename.write_text(content, encoding="utf-8")

print(f"Created draft: {filename}")
