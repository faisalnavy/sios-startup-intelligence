"""
GTM Intelligence Agent — SIOS v2 Tier 2

Produces a deep, channel-level Go-To-Market playbook with:
  - CAC benchmarks per acquisition channel (India + global)
  - Viral loop analysis
  - B2B vs B2C sales cycle prediction
  - Creator-led / community-led / product-led growth opportunities
  - First 100 customers strategy
  - Pricing psychology analysis

Uses Tavily to fetch current CAC benchmarks and competitor GTM intelligence.
"""
from agents.base_agent import BaseAgent
from models.startup_input import StartupInput


# ── CAC Benchmark Database (India-focused + Global) ──────────────────────────
CAC_BENCHMARKS = """
=== CAC BENCHMARKS BY CHANNEL (India Market) ===

B2C Digital Channels:
• Meta (Facebook/Instagram) Ads: ₹200-800 per install, ₹1,500-8,000 per paying user
• Google Ads (Search): ₹300-1,200 per lead, ₹2,000-12,000 per customer
• YouTube Ads: ₹50-150 CPM, ₹500-3,000 per lead
• Influencer Marketing (micro, 10K-100K): ₹5,000-25,000 per post, CAC ₹100-500
• WhatsApp Marketing: Near-zero CAC if organic, ₹1-5 per message for bulk
• Referral Programs: ₹50-300 per referred user (fintech average: ₹150)
• App Store Optimization (ASO): Near-zero, 3-6 months to see impact
• Content/SEO: ₹0 CAC but 6-18 months to traffic

B2B Channels:
• LinkedIn Outbound: ₹500-2,000 per lead, close rate 2-8%, CAC ₹8,000-50,000
• Cold Email: ₹50-200 per lead, 1-3% reply rate, CAC ₹5,000-30,000
• Events/Conferences: ₹10,000-50,000 per qualified lead
• Channel Partners/Resellers: 20-40% margin share, CAC near-zero
• Inbound (SEO+Content): ₹500-3,000 per qualified lead, 3-12 month lag
• Product-Led Growth (PLG): ₹200-800 per free user, 2-8% convert to paid

Fintech-Specific:
• UPI/Banking Referrals: ₹50-200 per active user
• Cashback Campaigns: ₹100-500 per first transaction
• Bank Partnership Integrations: Zero CAC, but 12-18 month deal cycles
• NBFC/MFI Channels: ₹200-1,000 per borrower

=== GLOBAL B2C SaaS BENCHMARKS ===
• PLG (Freemium to Paid): $15-50 CAC, 3-7% conversion
• SMB SaaS (self-serve): $200-500 CAC
• Mid-Market SaaS (sales-assisted): $1,000-5,000 CAC
• Enterprise SaaS (direct sales): $5,000-50,000 CAC
• Consumer App (US): $2-8 per install, $15-40 per registered user
"""


class GTMIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_name = "GTM Intelligence Agent"

    async def run(self, startup: StartupInput) -> dict:
        context = self._startup_context(startup)

        # Tavily: fetch live GTM intelligence for this sector
        tavily_data = ""
        try:
            sector_query = f"{startup.startup_name} {startup.geography} go-to-market strategy customer acquisition"
            results = await self.tavily.search(sector_query, max_results=4)
            if results:
                snippets = [f"• {r.get('title', '')}: {r.get('content', '')[:200]}" for r in results[:4]]
                tavily_data = "\n".join(snippets)
        except Exception:
            tavily_data = "Live market search unavailable."

        system_prompt = """You are a growth marketing expert and go-to-market strategist who has led GTM
for 50+ startups across India, Southeast Asia, and global markets. You think in unit economics,
channel-specific CAC, conversion funnels, and viral coefficients.

You do NOT give generic marketing advice. Every recommendation must be:
- Channel-specific with real CAC estimates
- Sequenced (what to do first vs later)
- Realistic for the startup's stage and capital
- Backed by comparable company data where possible

You understand the difference between growth hacks that work once and sustainable acquisition loops."""

        prompt = f"""{context}

=== CAC BENCHMARK REFERENCE DATA ===
{CAC_BENCHMARKS}

=== LIVE MARKET INTELLIGENCE ===
{tavily_data}

=== YOUR TASK: GTM INTELLIGENCE REPORT ===

Produce a comprehensive, channel-level GTM playbook for {startup.startup_name}.
Use this exact structure:

## GTM_OVERVIEW
Business type: [B2B / B2C / B2B2C / Marketplace]
Primary customer: [Exact ICP — job title, company size, behavior]
Sales motion: [Self-serve PLG / Inside Sales / Field Sales / Channel / Viral]
GTM difficulty: [EASY / MODERATE / HARD / VERY HARD]
Estimated time to first 100 customers: [X months]

## CHANNEL_PLAYBOOK
Rank channels by ROI for THIS specific startup. For each:

### Channel 1: [Channel Name] — PRIORITY: [P1/P2/P3]
**Estimated CAC:** [₹ or $ range based on benchmarks]
**Monthly budget to test:** [₹ or $]
**Expected conversion rate:** [%]
**Time to see results:** [weeks/months]
**Why this works for {startup.startup_name}:** [Specific logic]
**Exact first action:** [What to do this week]

[Repeat for top 4-5 channels]

## FIRST_100_CUSTOMERS
### The Path to Customer #1
[Exactly who is customer #1, how to reach them, what to say]

### Month 1-3: 0→10 customers
[Specific tactics — no generalities]

### Month 4-6: 10→100 customers
[Channel shift and scaling]

## VIRAL_LOOP_ANALYSIS
**Viral Potential:** [NONE / LOW / MEDIUM / HIGH]
**Natural sharing trigger:** [When/why would a user share this product?]
**Viral Coefficient (K) estimate:** [K < 1 = no viral / K > 1 = viral growth]
**Referral mechanism to build:** [Specific referral program design]

## PRICING_PSYCHOLOGY
**Recommended pricing model:** [Freemium / Trial / Direct / Usage-based / Subscription]
**Price anchoring strategy:** [How to frame price to minimize objection]
**First pricing mistake to avoid:** [Common error for this type of startup]

## B2B_SALES_CYCLE (if applicable)
**Expected sales cycle length:** [X weeks/months]
**Key decision makers:** [Who signs the contract]
**Biggest objection to overcome:** [Specific objection with script to handle it]
**Champions vs Economic Buyers:** [Who to befriend vs who approves budget]

## COMMUNITY_LED_GROWTH
**Community opportunity:** [NONE / LOW / MEDIUM / HIGH]
**Platform:** [Twitter / LinkedIn / WhatsApp / Discord / Reddit / Telegram]
**Community play:** [Specific community angle if applicable]

## GTM_RISK_FLAGS
Top 3 GTM mistakes that would kill traction for {startup.startup_name}:
1. [Mistake] → [Why it's fatal here]
2. [Mistake] → [Why it's fatal here]
3. [Mistake] → [Why it's fatal here]

## 90_DAY_GTM_SPRINT
Week 1-2: [Exact actions]
Week 3-4: [Exact actions]
Month 2: [Exact actions]
Month 3: [Exact actions + metrics to hit]"""

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
