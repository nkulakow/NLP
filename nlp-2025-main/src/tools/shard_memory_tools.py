from src.crews.shared_memory import SharedAnalysisMemory
from crewai.tools import tool
import json

SHARED_MEMORY = SharedAnalysisMemory()

def create_memory_tools(stock_symbol: str):
    SHARED_MEMORY.reset(stock_symbol)
    @tool("memory_tool")
    def memory_tool(category: str = "", key: str = "", value: str = "") -> str:
        """
        Writes specific metrics or findings to shared memory.
        Categories: 'sentiment', 'technical', 'fundamental', 'risks', 'verifications'.
        """
        if category in SHARED_MEMORY.data:
            SHARED_MEMORY.data[category][key] = value
            SHARED_MEMORY.evidence_trail.append(f"Updated {category}: {key}")
        return json.dumps(SHARED_MEMORY.data)

    return [memory_tool]