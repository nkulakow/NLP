"""
Shared memory system for group chat agents.

Provides a centralized data store that all agents can access and update,
preserving data richness throughout the debate process.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json


class SharedAnalysisMemory:
    """
    Shared memory structure for group chat analysis.

    Maintains structured data about sentiment, technical, fundamental analyses,
    plus risk assessments and verification results, accessible to all agents.
    """

    def __init__(self, stock_symbol: str):
        """Initialize shared memory with empty data structure."""
        self.stock_symbol = stock_symbol
        self.created_at = datetime.now()

        self.data: Dict[str, Any] = {
            "stock_symbol": stock_symbol,
            "sentiment": {
                "reddit_analysis": {
                    "summary": None,
                    "sentiment_score": None,  # -1 to 1
                    "key_themes": [],
                    "sample_posts": [],
                },
                "news_analysis": {
                    "summary": None,
                    "article_count": 0,
                    "key_articles": [],
                    "sentiment_trend": None,
                },
                "finnhub_sentiment": {
                    "sentiment_score": None,
                    "positive_ratio": None,
                    "negative_ratio": None,
                },
                "overall_sentiment": None,  # positive, negative, neutral, mixed
                "confidence": None,  # 0-1
            },
            "technical": {
                "current_price": None,
                "price_trend": None,  # uptrend, downtrend, consolidation
                "indicators": {
                    "moving_averages": {},  # SMA/EMA values
                    "momentum": {},  # MACD, RSI, Stochastics
                    "volatility": {},  # Bollinger Bands, ATR
                    "volume": {},  # OBV, Volume analysis
                },
                "key_levels": {
                    "support": [],
                    "resistance": [],
                },
                "patterns": [],  # Chart patterns identified
                "signals": [],  # Bullish/bearish signals
                "overall_outlook": None,  # bullish, bearish, neutral
                "confidence": None,  # 0-1
            },
            "fundamental": {
                "company_overview": None,
                "financial_metrics": {
                    "valuations": {},  # P/E, P/S, P/B, etc.
                    "profitability": {},  # Margins, ROE, ROIC, etc.
                    "growth": {},  # Revenue, EPS growth rates
                    "liquidity": {},  # Current ratio, Quick ratio, etc.
                    "solvency": {},  # Debt-to-equity, Interest coverage, etc.
                },
                "trends": {
                    "revenue": None,
                    "earnings": None,
                    "cash_flow": None,
                },
                "valuation_assessment": None,  # overvalued, undervalued, fair
                "health_score": None,  # 1-10
                "overall_outlook": None,  # positive, negative, neutral
                "confidence": None,  # 0-1
            },
            "risks": [],  # List of identified risks with evidence
            "verifications": {
                "data_quality": {},  # Source reliability assessments
                "contradictions": [],  # Data contradictions found
                "verified_claims": [],  # Claims confirmed across sources
            },
            "evidence_trail": [],  # All updates with timestamps and sources
        }

    def update(
        self,
        section: str,
        subsection: Optional[str],
        key: str,
        value: Any,
        agent: str = "unknown",
        reasoning: str = "",
    ) -> None:
        """
        Update data in shared memory with full tracking.

        Args:
            section: Top-level section (sentiment, technical, fundamental, risks, verifications)
            subsection: Subsection if applicable (None for top-level sections)
            key: Key to update
            value: New value
            agent: Agent making the update
            reasoning: Why this value was set
        """
        timestamp = datetime.now().isoformat()

        # Navigate to target location
        if subsection:
            if section not in self.data:
                self.data[section] = {}
            if subsection not in self.data[section]:
                self.data[section][subsection] = {}
            self.data[section][subsection][key] = value
        else:
            if section not in self.data:
                self.data[section] = {}
            self.data[section][key] = value

        # Add to evidence trail
        self.evidence_trail.append({
            "timestamp": timestamp,
            "agent": agent,
            "section": section,
            "subsection": subsection,
            "key": key,
            "value": self._truncate_value(value),
            "reasoning": reasoning,
        })

    def add_risk(
        self,
        risk_description: str,
        evidence: str,
        probability: str,  # High, Medium, Low
        mitigation: str = "",
        agent: str = "Sceptic",
    ) -> None:
        """Add a risk to the shared memory."""
        self.data["risks"].append({
            "description": risk_description,
            "evidence": evidence,
            "probability": probability,
            "mitigation": mitigation,
            "identified_by": agent,
            "timestamp": datetime.now().isoformat(),
        })
        self.evidence_trail.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "section": "risks",
            "key": "risk_added",
            "value": risk_description[:100],
            "reasoning": f"Evidence: {evidence}",
        })

    def add_verification(
        self,
        claim: str,
        verified: bool,
        reasoning: str,
        agent: str = "Trust Agent",
    ) -> None:
        """Add verification result to shared memory."""
        if verified:
            self.data["verifications"]["verified_claims"].append({
                "claim": claim,
                "verified_by": agent,
                "reasoning": reasoning,
                "timestamp": datetime.now().isoformat(),
            })
        else:
            self.data["verifications"]["contradictions"].append({
                "claim": claim,
                "issue": reasoning,
                "flagged_by": agent,
                "timestamp": datetime.now().isoformat(),
            })

        self.evidence_trail.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "section": "verifications",
            "key": "verified" if verified else "contradiction",
            "value": claim[:100],
            "reasoning": reasoning,
        })

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire section data for agent reference."""
        return self.data.get(section, {})

    def get_summary_for_agent(self) -> str:
        """
        Generate a formatted summary of all gathered data for agents to reference.

        Returns:
            Formatted string with all key data points.
        """
        summary = f"=== SHARED DATA MEMORY FOR {self.stock_symbol} ===\n\n"

        # Sentiment summary
        sentiment = self.data.get("sentiment", {})
        summary += "SENTIMENT ANALYSIS:\n"
        summary += f"- Overall Sentiment: {sentiment.get('overall_sentiment', 'N/A')}\n"
        summary += f"- Confidence: {sentiment.get('confidence', 'N/A')}\n"
        if sentiment.get("reddit_analysis", {}).get("key_themes"):
            summary += f"- Key Themes: {', '.join(sentiment['reddit_analysis']['key_themes'][:3])}\n"
        summary += "\n"

        # Technical summary
        technical = self.data.get("technical", {})
        summary += "TECHNICAL ANALYSIS:\n"
        summary += f"- Price Trend: {technical.get('price_trend', 'N/A')}\n"
        summary += f"- Overall Outlook: {technical.get('overall_outlook', 'N/A')}\n"
        if technical.get("key_levels", {}).get("support"):
            summary += f"- Support Levels: {technical['key_levels']['support']}\n"
        if technical.get("key_levels", {}).get("resistance"):
            summary += f"- Resistance Levels: {technical['key_levels']['resistance']}\n"
        summary += "\n"

        # Fundamental summary
        fundamental = self.data.get("fundamental", {})
        summary += "FUNDAMENTAL ANALYSIS:\n"
        summary += f"- Valuation: {fundamental.get('valuation_assessment', 'N/A')}\n"
        summary += f"- Health Score: {fundamental.get('health_score', 'N/A')}/10\n"
        summary += f"- Overall Outlook: {fundamental.get('overall_outlook', 'N/A')}\n"
        summary += "\n"

        # Risks summary
        risks = self.data.get("risks", [])
        if risks:
            summary += f"IDENTIFIED RISKS ({len(risks)}):\n"
            for i, risk in enumerate(risks[:3], 1):  # Show top 3
                summary += f"{i}. {risk['description']} (Probability: {risk['probability']})\n"
            summary += "\n"

        # Verifications summary
        verifications = self.data.get("verifications", {})
        verified_count = len(verifications.get("verified_claims", []))
        contradiction_count = len(verifications.get("contradictions", []))
        summary += f"VERIFICATION STATUS:\n"
        summary += f"- Verified Claims: {verified_count}\n"
        summary += f"- Contradictions Found: {contradiction_count}\n"
        summary += "\n"

        return summary

    def get_full_data_json(self) -> str:
        """
        Get full data structure as JSON for agent reference.

        Returns:
            JSON string of complete data.
        """
        return json.dumps(self.data, indent=2, default=str)

    def get_evidence_trail(self) -> List[Dict[str, Any]]:
        """Get all updates with traceability."""
        return self.evidence_trail

    @property
    def evidence_trail(self) -> List[Dict[str, Any]]:
        """Get evidence trail from data."""
        return self.data.get("_evidence_trail", [])

    @evidence_trail.setter
    def evidence_trail(self, value: List[Dict[str, Any]]) -> None:
        """Set evidence trail in data."""
        self.data["_evidence_trail"] = value

    @staticmethod
    def _truncate_value(value: Any, max_length: int = 200) -> str:
        """Truncate value for storage in evidence trail."""
        str_value = str(value)
        if len(str_value) > max_length:
            return str_value[:max_length] + "..."
        return str_value

    def __repr__(self) -> str:
        """String representation of shared memory."""
        return (
            f"SharedAnalysisMemory(stock='{self.stock_symbol}', "
            f"updates={len(self.evidence_trail)})"
        )
