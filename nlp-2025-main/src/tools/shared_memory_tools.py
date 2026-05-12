"""
Shared memory tools for group chat agents.

These tools allow agents to write structured updates into the shared memory
when the shared memory mode is enabled.
"""

from crewai.tools import tool


def make_update_sentiment_memory_tool(shared_memory):
    @tool
    def update_sentiment_memory(
        key: str,
        value: str,
        subsection: str = "",
        reasoning: str = "",
    ) -> str:
        """Update sentiment section in shared memory."""
        try:
            shared_memory.update(
                "sentiment",
                subsection if subsection else None,
                key,
                value,
                agent="Researcher",
                reasoning=reasoning,
            )
            result = f"Updated sentiment {subsection}.{key} = {value}" if subsection else f"Updated sentiment {key} = {value}"
            print(f"[SHARED_MEMORY_UPDATE] {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to update sentiment memory: {str(e)}"
            print(f"[SHARED_MEMORY_ERROR] {error_msg}")
            return error_msg

    return update_sentiment_memory


def make_update_technical_memory_tool(shared_memory):
    @tool
    def update_technical_memory(
        key: str,
        value: str,
        subsection: str = "",
        reasoning: str = "",
    ) -> str:
        """Update technical analysis section in shared memory."""
        try:
            shared_memory.update(
                "technical",
                subsection if subsection else None,
                key,
                value,
                agent="Technical Analyst",
                reasoning=reasoning,
            )
            result = f"Updated technical {subsection}.{key} = {value}" if subsection else f"Updated technical {key} = {value}"
            print(f"[SHARED_MEMORY_UPDATE] {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to update technical memory: {str(e)}"
            print(f"[SHARED_MEMORY_ERROR] {error_msg}")
            return error_msg

    return update_technical_memory


def make_update_fundamental_memory_tool(shared_memory):
    @tool
    def update_fundamental_memory(
        key: str,
        value: str,
        subsection: str = "",
        reasoning: str = "",
    ) -> str:
        """Update fundamental analysis section in shared memory."""
        shared_memory.update(
            "fundamental",
            subsection if subsection else None,
            key,
            value,
            agent="Fundamental Analyst",
            reasoning=reasoning,
        )
        return f"Updated fundamental {subsection}.{key} = {value}" if subsection else f"Updated fundamental {key} = {value}"

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
        try:
            shared_memory.add_risk(
                risk_description,
                evidence,
                probability,
                mitigation=mitigation,
                agent="Sceptic",
            )
            result = f"Added risk: {risk_description}"
            print(f"[SHARED_MEMORY_UPDATE] {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to add risk to memory: {str(e)}"
            print(f"[SHARED_MEMORY_ERROR] {error_msg}")
            return error_msg

    return add_risk_memory


def make_add_verification_memory_tool(shared_memory):
    @tool
    def add_verification_memory(
        claim: str,
        verified: bool,
        reasoning: str,
    ) -> str:
        """Add verification data to shared memory."""
        try:
            shared_memory.add_verification(
                claim,
                verified,
                reasoning,
                agent="Trust Agent",
            )
            status = "verified" if verified else "contradiction"
            result = f"Added verification: {claim} - {status}"
            print(f"[SHARED_MEMORY_UPDATE] {result}")
            return result
        except Exception as e:
            error_msg = f"Failed to add verification to memory: {str(e)}"
            print(f"[SHARED_MEMORY_ERROR] {error_msg}")
            return error_msg

    return add_verification_memory
