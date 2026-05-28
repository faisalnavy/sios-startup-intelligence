"""
Profile Service — fetches and summarises founder/co-founder profiles.

Supports:
  • GitHub  — public REST API (no auth required for basic data)
  • LinkedIn — Tavily search + scrape (public profiles only)
  • Twitter/X, personal sites — Tavily web scrape
"""
import re
import httpx
import asyncio
from typing import List, Optional
from services.tavily_service import TavilyService


class ProfileService:
    def __init__(self):
        self.tavily = TavilyService()
        self._github_api = "https://api.github.com"
        self._headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "SIOS-ProfileService/2.0",
        }

    # ── Public entry point ────────────────────────────────────────────

    async def fetch_all(self, profile_urls: List[str]) -> str:
        """
        Fetch all profiles and return a combined text summary
        suitable for injecting into agent prompts.
        """
        if not profile_urls:
            return ""

        tasks = [self._fetch_one(url.strip()) for url in profile_urls if url.strip()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        summaries = []
        for url, result in zip(profile_urls, results):
            if isinstance(result, Exception):
                summaries.append(f"[{url}] — Could not fetch profile: {result}")
            elif result:
                summaries.append(result)

        return "\n\n---\n\n".join(summaries) if summaries else ""

    # ── Dispatch by platform ──────────────────────────────────────────

    async def _fetch_one(self, url: str) -> str:
        platform = self._detect_platform(url)
        if platform == "github":
            return await self._fetch_github(url)
        elif platform == "linkedin":
            return await self._fetch_linkedin(url)
        else:
            return await self._fetch_generic(url)

    @staticmethod
    def _detect_platform(url: str) -> str:
        url_lower = url.lower()
        if "github.com" in url_lower:
            return "github"
        elif "linkedin.com" in url_lower:
            return "linkedin"
        return "generic"

    # ── GitHub ────────────────────────────────────────────────────────

    async def _fetch_github(self, url: str) -> str:
        """Fetch GitHub profile via public API — repos, languages, bio, activity."""
        username = self._extract_github_username(url)
        if not username:
            return f"[GitHub] Could not parse username from: {url}"

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                # Fetch user profile + repos in parallel
                user_resp, repos_resp = await asyncio.gather(
                    client.get(f"{self._github_api}/users/{username}", headers=self._headers),
                    client.get(f"{self._github_api}/users/{username}/repos?sort=updated&per_page=10", headers=self._headers),
                )

            if user_resp.status_code != 200:
                return f"[GitHub] Profile not found: github.com/{username}"

            user = user_resp.json()
            repos = repos_resp.json() if repos_resp.status_code == 200 else []

            # Aggregate languages
            language_counts: dict = {}
            if isinstance(repos, list):
                for repo in repos:
                    lang = repo.get("language")
                    if lang:
                        language_counts[lang] = language_counts.get(lang, 0) + 1

            top_langs = sorted(language_counts, key=lambda x: language_counts[x], reverse=True)[:5]
            total_stars = sum(r.get("stargazers_count", 0) for r in repos if isinstance(r, dict))

            summary = f"""[GitHub Profile] github.com/{username}
Name: {user.get('name') or username}
Bio: {user.get('bio') or 'Not provided'}
Location: {user.get('location') or 'Not specified'}
Company: {user.get('company') or 'Not specified'}
Public Repos: {user.get('public_repos', 0)}
Followers: {user.get('followers', 0)}
Total Stars (top 10 repos): {total_stars}
Top Languages: {', '.join(top_langs) if top_langs else 'Not available'}
Account Since: {user.get('created_at', '')[:4]}
Recent Repos: {', '.join(r.get('name', '') for r in repos[:5] if isinstance(r, dict))}"""

            return summary

        except Exception as e:
            return f"[GitHub] Fetch error for {url}: {str(e)}"

    @staticmethod
    def _extract_github_username(url: str) -> Optional[str]:
        match = re.search(r"github\.com/([a-zA-Z0-9_-]+)", url)
        return match.group(1) if match else None

    # ── LinkedIn ──────────────────────────────────────────────────────

    async def _fetch_linkedin(self, url: str) -> str:
        """Fetch LinkedIn profile data via Tavily search (public profiles only)."""
        try:
            # Tavily search for the LinkedIn profile
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.tavily.client.search(
                    query=f"site:linkedin.com {url}",
                    max_results=3,
                    include_raw_content=True,
                )
            )

            content_parts = []
            if results and "results" in results:
                for r in results["results"]:
                    raw = r.get("raw_content") or r.get("content") or ""
                    if raw and len(raw) > 100:
                        content_parts.append(raw[:1500])

            if content_parts:
                combined = "\n".join(content_parts)
                return f"[LinkedIn Profile] {url}\n{combined[:2000]}"
            else:
                return f"[LinkedIn] {url} — Profile is private or not indexed. Using URL as reference only."

        except Exception as e:
            return f"[LinkedIn] Fetch error for {url}: {str(e)}"

    # ── Generic (personal site, Twitter, etc.) ────────────────────────

    async def _fetch_generic(self, url: str) -> str:
        """Fetch any public URL via Tavily extract."""
        try:
            results = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.tavily.client.search(
                    query=url,
                    max_results=2,
                    include_raw_content=True,
                )
            )

            if results and "results" in results:
                for r in results["results"]:
                    raw = r.get("raw_content") or r.get("content") or ""
                    if raw and len(raw) > 100:
                        return f"[Profile] {url}\n{raw[:1500]}"

            return f"[Profile] {url} — Could not extract content."

        except Exception as e:
            return f"[Profile] Fetch error for {url}: {str(e)}"
