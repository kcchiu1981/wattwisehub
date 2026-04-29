import os
from datetime import datetime
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

today = datetime.utcnow().strftime("%Y-%m-%d")
draft_dir = Path("content/drafts")
draft_dir.mkdir(parents=True, exist_ok=True)

prompt = """
You are WattHub's autonomous content agent.

Website: WattHub / WattWiseHome
Niche: home energy efficiency
Audience: US homeowners and renters
Goal: organic SEO traffic and affiliate revenue

Task:
1. Choose the best article topic for this week.
2. Explain briefly why this topic is worth writing.
3. Write a publishable SEO article draft in Markdown.

Rules:
- Target buyer-intent or strong problem-solving keywords.
- Avoid fake product claims.
- Use trustworthy, practical advice.
- Include:
  - SEO title
  - meta description
  - suggested slug
  - article body
  - comparison table if useful
  - FAQ
  - internal link suggestions
  - affiliate placement suggestions

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
