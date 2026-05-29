"""
Startup Autopsy Agent — SIOS v2 Tier 2

Answers: "Which real companies did this before — and did they win or die?"

Compares the startup against 5-8 historical analogues (successes + failures),
diagnoses the cause of failure for failed companies, and predicts which
trajectory this startup most closely resembles.

Uses Tavily to find recent / niche analogues beyond the curated database.
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


# ── Curated Autopsy Database ─────────────────────────────────────────────────
# Key analogues across fintech, SaaS, marketplace, consumer, B2B sectors.
# Format: {domain_tag: [company, outcome, key_lesson]}
AUTOPSY_DB = {
    "fintech_india": [
        ("Niyo", "SUCCESS", "Won by targeting salaried employees + neobank positioning"),
        ("Walnut", "ACQUIRED", "Personal finance app acquired by SBI Card — distribution moat matters"),
        ("PaySense", "ACQUIRED", "BNPL credit startup acquired by PayU — regulatory licensing is the moat"),
        ("Chillr", "SHUTDOWN", "P2P payments failed before UPI — timing killed it"),
        ("Empower", "SUCCESS", "US fintech — CAC-to-LTV discipline saved it"),
    ],
    "fintech_global": [
        ("Revolut", "SUCCESS", "Cracked multi-market expansion by deferring regulation, then embracing it"),
        ("N26", "PARTIAL_EXIT", "Exited US — underestimated regulatory complexity"),
        ("Robinhood", "IPO", "Virality via referral + zero-commission disruption"),
        ("Wirecard", "FRAUD_COLLAPSE", "Regulatory arbitrage used to hide fraud — compliance matters"),
        ("Monzo", "SUCCESS", "Community-led growth + transparency built loyalty moat"),
        ("Celsius", "BANKRUPTCY", "Crypto yield product — regulatory overreach and liquidity crisis"),
    ],
    "b2b_saas": [
        ("Slack", "ACQUISITION_27B", "Bottom-up PLG, viral within teams before top-down enterprise"),
        ("Notion", "SUCCESS", "Templates + community built distribution moat at zero CAC"),
        ("Quibi", "SHUTDOWN", "Wrong platform (mobile-only) for content consumption habits"),
        ("Yammer", "ACQUIRED", "Enterprise social sold to Microsoft — product-market fit in enterprise"),
        ("Basecamp", "PROFITABLE", "Refused VC, stayed profitable — contrarian but validated"),
    ],
    "marketplace": [
        ("Dunzo", "STRUGGLING", "Hyperlocal delivery burned ₹3500+ Cr, unit economics never worked"),
        ("Blinkit", "ACQUIRED", "Quick commerce saved by Zomato acquisition — need platform"),
        ("Oyo", "STRUGGLING", "Scaled before unit economics — valuation vs reality gap"),
        ("Urban Company", "SUCCESS", "Home services marketplace — quality control = differentiation"),
        ("Grofers", "REBRANDED", "Online grocery survived by pivoting to Blinkit model"),
    ],
    "crypto_web3": [
        ("CoinDCX", "SUCCESS", "India crypto — survived multiple RBI crackdowns through compliance"),
        ("WazirX", "HACKED/STRUGGLING", "₹2000 Cr hack exposed custody risks"),
        ("FTX", "FRAUD_COLLAPSE", "Largest crypto fraud — regulatory arbitrage fatal"),
        ("Coinbase", "PUBLIC", "Compliance-first strategy = regulatory moat"),
        ("Polygon", "SUCCESS", "Layer 2 infrastructure — developer ecosystem moat"),
    ],
    "edtech": [
        ("Byju's", "COLLAPSING", "Over-leveraged, aggressive sales, pedagogy ignored"),
        ("Duolingo", "IPO", "Gamification + habit loops = 500M users"),
        ("Unacademy", "STRUGGLING", "Educator-first model, CAC war with offline coaching"),
        ("Coursera", "PUBLIC", "B2B university partnerships = sustainable revenue"),
        ("Udemy", "PUBLIC", "Marketplace model with instructor incentive alignment"),
    ],
    "healthtech": [
        ("Practo", "STRUGGLING", "India doctor discovery + EHR — monetization always lagged growth"),
        ("PharmEasy", "STRUGGLING", "Online pharmacy IPO failed, debt-heavy model"),
        ("1mg", "ACQUIRED", "Tata Health acquired — integration into conglomerate"),
        ("Teladoc", "SUCCESS/DIPPING", "US telehealth — COVID tailwind then correction"),
        ("Niramai", "SUCCESS", "AI breast cancer screening — regulation-friendly medtech"),
    ],
    "logistics": [
        ("Delhivery", "IPO", "B2B logistics network effects + IPO success"),
        ("Rivigo", "ACQUIRED", "Relay trucking model acquired by Amazon — capital intensive"),
        ("Porter", "SUCCESS", "Intra-city logistics — strong unit economics from B2B"),
        ("Shadowfax", "GROWING", "Last-mile gig economy logistics"),
    ],
    "consumer_app": [
        ("Sharechat", "GROWING", "Vernacular social — Tier 2/3 India bet paid off"),
        ("Meesho", "SUCCESS", "Social commerce through WhatsApp — reseller network moat"),
        ("Shop101", "SHUTDOWN", "Social commerce failed to hit critical mass"),
        ("Roposo", "STRUGGLING", "Short video struggled vs Reels/YouTube Shorts"),
        ("Licious", "D2C_SUCCESS", "Premium meat D2C — cold chain as moat"),
    ],
}


class StartupAutopsyAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "Startup Autopsy Agent"

    def _get_curated_analogues(self, startup: StartupInput) -> str:
        """Select the most relevant analogues from the curated database."""
        idea_lower = (startup.idea_description + " " + startup.startup_name).lower()
        geo_lower = startup.geography.lower()

        # Score each category by keyword overlap
        scores: dict[str, int] = {}
        keyword_map = {
            "fintech_india": ["payment", "wallet", "banking", "neobank", "lending", "credit", "insurance",
                              "upi", "financial", "fintech", "kyc", "rupee", "inr"],
            "fintech_global": ["payment", "wallet", "banking", "neobank", "lending", "credit",
                               "financial", "fintech", "crypto", "blockchain", "defi"],
            "b2b_saas": ["saas", "software", "platform", "b2b", "enterprise", "productivity",
                         "workflow", "automation", "api", "dashboard", "tool"],
            "marketplace": ["marketplace", "delivery", "logistics", "gig", "service", "booking",
                            "platform", "connect", "seller", "buyer", "commerce"],
            "crypto_web3": ["crypto", "blockchain", "defi", "nft", "web3", "token", "wallet",
                            "decentralized", "bitcoin", "ethereum", "solana", "stablecoin"],
            "edtech": ["education", "learning", "course", "tutoring", "school", "student",
                       "skill", "training", "upskill", "edtech", "exam", "coaching"],
            "healthtech": ["health", "medical", "doctor", "hospital", "pharmacy", "wellness",
                           "fitness", "diagnostic", "telehealth", "patient", "clinical"],
            "logistics": ["logistics", "shipping", "delivery", "freight", "warehouse", "supply chain",
                          "courier", "last mile", "trucking", "fleet", "transport"],
            "consumer_app": ["social", "community", "content", "creator", "app", "consumer",
                             "d2c", "brand", "video", "ecommerce", "retail", "shopping"],
        }

        for cat, keywords in keyword_map.items():
            score = sum(1 for kw in keywords if kw in idea_lower)
            # Bonus for India-specific categories when geography matches
            if "india" in cat and ("india" in geo_lower or "indian" in geo_lower):
                score += 2
            scores[cat] = score

        # Take top 2 categories
        top_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        selected = []
        for cat, _ in top_cats:
            if cat in AUTOPSY_DB:
                selected.extend(AUTOPSY_DB[cat])

        if not selected:
            # Fallback: use fintech_global as generic
            selected = AUTOPSY_DB["fintech_global"] + AUTOPSY_DB["b2b_saas"]

        # Format for prompt
        lines = []
        for company, outcome, lesson in selected[:8]:
            lines.append(f"• {company} [{outcome}]: {lesson}")
        return "\n".join(lines)

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)
        curated = self._get_curated_analogues(startup)

        # Tavily search for live analogues
        tavily_data = ""
        try:
            search_query = f"{startup.startup_name} similar startups {startup.geography} success failure analogues"
            results = await self.tavily.search(search_query, max_results=4)
            if results:
                snippets = [f"• {r.get('title', '')}: {r.get('content', '')[:200]}" for r in results[:4]]
                tavily_data = "\n".join(snippets)
        except Exception:
            tavily_data = "Live search unavailable."

        system_prompt = """You are a startup historian and pattern-matching analyst. You have deep knowledge
of thousands of startup trajectories — what made them win, what killed them, and the specific
inflection points that determined their fate.

Your job is to find the real-world analogues to this startup, diagnose what happened to those companies,
and predict which trajectory this startup is most likely to follow. Be specific, honest, and data-driven.

You must reference real companies. No vague generalizations."""

        prompt = f"""{context}

=== CURATED ANALOGUES DATABASE ===
{curated}

=== LIVE MARKET INTELLIGENCE (Tavily) ===
{tavily_data}

=== YOUR TASK: STARTUP AUTOPSY ANALYSIS ===

Perform a complete startup autopsy comparison. Use this exact structure:

## TRAJECTORY_PREDICTION
In 2-3 sentences: Which real company does this startup most resemble, and why?
What is the most likely outcome based on that analogy?

## SIMILAR_COMPANIES
Analyze 5-6 most relevant analogues (mix of success and failure):

### [Company Name] — [OUTCOME: SUCCESS / FAILURE / ACQUIRED / IPO / STRUGGLING]
**Similarity to {startup.startup_name}:** [Specific reasons — business model, geography, timing, founder type]
**Why they succeeded/failed:** [Root cause analysis — 2-3 specific reasons]
**Key lesson for {startup.startup_name}:** [1-2 actionable lessons]
**Critical difference:** [What's different about {startup.startup_name}'s situation]

[Repeat for each company]

## DNA_MATCH
### Most Similar Success Story: [Company]
Why: [3-4 sentences on the parallel]
What {startup.startup_name} must replicate: [Specific actions]

### Most Similar Failure Story: [Company]
Why: [3-4 sentences on the parallel]
What {startup.startup_name} must avoid: [Specific pitfalls]

## FAILURE_PATTERN_DIAGNOSIS
Looking at the failures among analogues, what are the top 3 failure patterns most likely to hit {startup.startup_name}?

1. **[Pattern Name]** — [Probability: HIGH/MEDIUM/LOW] — [Specific risk for this startup]
2. **[Pattern Name]** — [Probability: HIGH/MEDIUM/LOW] — [Specific risk for this startup]
3. **[Pattern Name]** — [Probability: HIGH/MEDIUM/LOW] — [Specific risk for this startup]

## SUCCESS_PATTERN_EXTRACTION
From the successful analogues, what 3 behaviors most correlate with survival?

1. [Behavior] → [How {startup.startup_name} should apply this]
2. [Behavior] → [How {startup.startup_name} should apply this]
3. [Behavior] → [How {startup.startup_name} should apply this]

## TRAJECTORY_VERDICT
**Most Likely Trajectory:** [Pick one: Acquisition Target / IPO Candidate / Lifestyle Business / Failure Risk / Pivot Required]
**Timeline:** [When will fate be decided?]
**The Defining Moment:** [What single decision or milestone will determine if this startup wins or dies?]"""

        analysis = await self.dual_ai.analyze_with_critique(
            system_prompt=system_prompt,
            user_message=prompt,
            max_tokens=3500,
        )

        return {
            "agent": self.agent_name,
            "analysis": analysis.get("claude_analysis", ""),
            "openai_critique": analysis.get("openai_critique", ""),
            "status": "completed",
        }
