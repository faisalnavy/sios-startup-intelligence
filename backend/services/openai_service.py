from openai import AsyncOpenAI
import os
import json


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"

    async def critique(
        self,
        analysis_to_critique: str,
        context: str,
        domain: str = "startup analysis",
        max_tokens: int = 2048,
    ) -> str:
        system_prompt = f"""You are a rigorous {domain} expert acting as a critical peer reviewer.

Your job is to CHALLENGE and CRITIQUE the analysis provided. Look for:
- Unsupported assumptions
- Missing data points
- Logical inconsistencies
- Overlooked risks
- Overly optimistic projections
- Market realities that contradict the analysis
- Gaps in reasoning

Be constructive but firm. The goal is to make the final output stronger.

Context about this startup:
{context}"""

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Please critique this analysis:\n\n{analysis_to_critique}",
                },
            ],
        )
        return response.choices[0].message.content

    async def analyze(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content

    async def generate_json(
        self, system_prompt: str, user_message: str, max_tokens: int = 4096
    ) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt + "\n\nRespond with valid JSON only.",
                },
                {"role": "user", "content": user_message},
            ],
        )
        return json.loads(response.choices[0].message.content)
