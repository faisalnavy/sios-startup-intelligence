import anthropic
import os
import json
from typing import Optional


class ClaudeService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-7"

    async def analyze(self, system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    async def synthesize(
        self,
        system_prompt: str,
        original_analysis: str,
        critique: str,
        max_tokens: int = 4096,
    ) -> str:
        synthesis_prompt = f"""You previously produced this analysis:

<original_analysis>
{original_analysis}
</original_analysis>

A peer AI reviewer raised these concerns and critiques:

<critique>
{critique}
</critique>

Now produce your FINAL, improved analysis. Incorporate valid critique points, defend positions where the critique is wrong, and produce a more robust, well-rounded output. Be specific and data-driven."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )
        return response.content[0].text

    async def generate_json(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> dict:
        full_system = (
            system_prompt
            + "\n\nIMPORTANT: Respond ONLY with valid JSON. No markdown, no explanation outside the JSON."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=full_system,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
