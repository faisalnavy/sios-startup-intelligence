from tavily import TavilyClient
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import os
from typing import List, Optional

# Ensure .env is loaded regardless of working directory
load_dotenv(Path(__file__).parent.parent / ".env", override=True)


class TavilyService:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if api_key:
            try:
                self.client = TavilyClient(api_key=api_key)
            except Exception:
                self.client = None
        else:
            self.client = None

    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
    ) -> str:
        """Search and return formatted results string for agent context."""
        if not self.client:
            return "Web search unavailable: TAVILY_API_KEY not configured."

        params = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
        }
        if include_domains:
            params["include_domains"] = include_domains

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.client.search(**params))
        except Exception as e:
            return f"Web search failed: {e}"

        formatted = []
        if response.get("answer"):
            formatted.append(f"SUMMARY: {response['answer']}\n")

        for i, result in enumerate(response.get("results", []), 1):
            formatted.append(
                f"[{i}] {result.get('title', 'No title')}\n"
                f"URL: {result.get('url', '')}\n"
                f"Content: {result.get('content', '')[:600]}\n"
            )

        return "\n".join(formatted) if formatted else "No results found."

    async def research_startup(self, startup_name: str, idea: str, geography: str) -> dict:
        """Run all standard research queries for a startup analysis."""
        queries = {
            "market_size": f"{idea} market size TAM SAM SOM {geography} 2024 2025",
            "competitors": f"companies similar to {idea} {geography} startups competitors",
            "vc_investors": f"venture capital investors {idea} sector {geography} funding",
            "trends": f"{idea} industry trends 2024 2025 future growth",
            "regulations": f"{idea} business regulations {geography} legal requirements",
            "failures": f"startups failed {idea} similar business why failed lessons",
        }

        results = {}
        for key, query in queries.items():
            results[key] = await self.search(query, max_results=4)

        return results

    async def deep_search(self, queries: List[str], max_results: int = 3) -> str:
        """Run multiple queries and combine results."""
        all_results = []
        for query in queries:
            result = await self.search(query, max_results=max_results)
            all_results.append(f"[Query: {query}]\n{result}")
        return "\n\n---\n\n".join(all_results)
