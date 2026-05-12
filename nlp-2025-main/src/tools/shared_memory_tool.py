from crewai.tools import tool
from src.crews.shared_memory import SharedAnalysisMemory

def create_memory_tools(shared_memory: SharedAnalysisMemory):
    @tool("update_analysis_data")
    def update_analysis_data(section: str, key: str, value: str, reasoning: str, subsection: str = None):
        """
        Update the shared data memory. Use this to save metrics, trends, or outlooks.
        Sections: 'sentiment', 'technical', 'fundamental'.
        """
        shared_memory.update(
            section=section,
            subsection=subsection,
            key=key,
            value=value,
            agent="Agent", # You can pass the agent name here if needed
            reasoning=reasoning
        )
        return f"Successfully updated {section} in shared memory."

    @tool("add_market_risk")
    def add_market_risk(description: str, evidence: str, probability: str, mitigation: str = ""):
        """Add a specific risk found during analysis to shared memory."""
        shared_memory.add_risk(description, evidence, probability, mitigation)
        return "Risk added to shared memory."

    return [update_analysis_data, add_market_risk]
