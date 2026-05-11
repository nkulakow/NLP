"""
Shared memory tools for group chat agents.

These tools allow agents to write structured updates into the shared memory
when the shared memory mode is enabled.
"""

from crewai.tools import tool


def make_update_sentiment_memory_tool(shared_memory):
    @tool
    def update_sentiment_memory(
        subsection: str,
        key: str,
        value: str,
        reasoning: str = "",
    ) -> str:
        """Update sentiment section in shared memory."""
        shared_memory.update(
            "sentiment",
            subsection,
            key,
            value,
            agent="Researcher",
            reasoning=reasoning,
        )
        return f"Updated sentiment {subsection}.{key} = {value}"

    return update_sentiment_memory


def make_update_technical_memory_tool(shared_memory):
    @tool
    def update_technical_memory(
        subsection: str,
        key: str,
        value: str,
        reasoning: str = "",
    ) -> str:
        """Update technical analysis section in shared memory."""
        shared_memory.update(
            "technical",
            subsection,
            key,
            value,
            agent="Technical Analyst",
            reasoning=reasoning,
        )
        return f"Updated technical {subsection}.{key} = {value}"

    return update_technical_memory


def make_update_fundamental_memory_tool(shared_memory):
    @tool
    def update_fundamental_memory(
        subsection: str,
        key: str,
        value: str,
        reasoning: str = "",
    ) -> str:
        """Update fundamental analysis section in shared memory."""
        shared_memory.update(
            "fundamental",
            subsection,
            key,
            value,
            agent="Fundamental Analyst",
            reasoning=reasoning,
        )
        return f"Updated fundamental {subsection}.{key} = {value}"

    return update_fundamental_memory


def make_add_risk_memory_tool(shared_memory):
    @tool
    def add_risk_memory(
        risk_description: str,
        evidence: str,
        probability: str,
        mitigation: str = "",
    ) -> str:
        """Add a risk with evidence to shared memory."""
        shared_memory.add_risk(
            risk_description,
            evidence,
            probability,
            mitigation=mitigation,
            agent="Sceptic",
        )
        return f"Added risk: {risk_description}"

    return add_risk_memory


def make_add_verification_memory_tool(shared_memory):
    @tool
    def add_verification_memory(
        claim: str,
        verified: bool,
        reasoning: str,
    ) -> str:
        """Add verification data to shared memory."""
        shared_memory.add_verification(
            claim,
            verified,
            reasoning,
            agent="Trust Agent",
        )
        return f"Added verification: {claim} - {'verified' if verified else 'contradiction'}"

    return add_verification_memory
