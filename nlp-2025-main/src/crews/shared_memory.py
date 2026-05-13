from typing import Dict, List, Any
import json

class SharedAnalysisMemory:
    def __init__(self):
        self.stock_symbol = ""
        self.evidence_trail: List[str] = []
        self.data: Dict[str, Dict[str, Any]] = {
            'sentiment': {},
            'technical': {},
            'fundamental': {},
            'risks': {},
            'verifications': {}
        }

    def reset(self, stock_symbol: str) -> None:
        self.data = {
            'sentiment': {},
            'technical': {},
            'fundamental': {},
            'risks': {},
            'verifications': {}
        }
        self.evidence_trail = []
        self.stock_symbol = stock_symbol

    def get_summary_for_agent(self) -> str:
        """Returns a string representation of the current memory for prompt injection."""
        return json.dumps(self.data, indent=2)
