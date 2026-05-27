"""
Dual-AI Cross-Validation Service

Claude analyzes → OpenAI critiques → Claude synthesizes final output.
This cross-validation produces more robust, self-corrected intelligence.
"""
from services.claude_service import ClaudeService
from services.openai_service import OpenAIService


class DualAIService:
    def __init__(self):
        self.claude = ClaudeService()
        self.openai = OpenAIService()

    async def cross_validate(
        self,
        system_prompt: str,
        user_message: str,
        startup_context: str,
        domain: str = "startup analysis",
        max_tokens: int = 4096,
    ) -> dict:
        """
        3-step cross-validation:
        1. Claude generates initial analysis
        2. OpenAI critiques Claude's analysis
        3. Claude synthesizes an improved final output

        Returns dict with all three stages for transparency.
        """
        # Step 1: Claude analyzes
        claude_analysis = await self.claude.analyze(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=max_tokens,
        )

        # Step 2: OpenAI critiques
        openai_critique = await self.openai.critique(
            analysis_to_critique=claude_analysis,
            context=startup_context,
            domain=domain,
        )

        # Step 3: Claude synthesizes final output
        final_output = await self.claude.synthesize(
            system_prompt=system_prompt,
            original_analysis=claude_analysis,
            critique=openai_critique,
            max_tokens=max_tokens,
        )

        return {
            "claude_initial": claude_analysis,
            "openai_critique": openai_critique,
            "final_synthesis": final_output,
        }

    async def cross_validate_json(
        self,
        system_prompt: str,
        user_message: str,
        startup_context: str,
        domain: str = "startup analysis",
    ) -> dict:
        """Cross-validate and return structured JSON output."""
        result = await self.cross_validate(
            system_prompt=system_prompt,
            user_message=user_message,
            startup_context=startup_context,
            domain=domain,
        )

        # Parse the final synthesis as JSON
        final_json = await self.claude.generate_json(
            system_prompt=system_prompt,
            user_message=f"""Based on this final synthesized analysis, extract the key data as structured JSON:

{result['final_synthesis']}

Original context: {startup_context}""",
        )

        return final_json
