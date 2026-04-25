from enum import Enum
from typing import Optional

from src.crews.sequential import SequentialStockAnalysisCrew
from src.crews.group_chat import GroupChatStockAnalysisCrew
from src.config import load_config


class CrewMode(Enum):
    """Enum for crew execution modes."""

    SEQUENTIAL = "sequential"
    GROUP_CHAT = "group_chat"


class StockAnalysisCrewFactory:
    """Factory for creating crew instances based on mode."""

    @staticmethod
    def create(mode: str, provider: Optional[str] = None):
        """
        Create a crew instance based on mode.

        Args:
            mode: "sequential" or "group_chat"
            provider: "gemini" or "openai". If None, uses LLM_PROVIDER from env.

        Returns:
            Instance of SequentialStockAnalysisCrew or GroupChatStockAnalysisCrew

        Raises:
            ValueError: If mode is not recognized or provider is invalid
        """
        config = load_config(provider)

        if mode.lower() == CrewMode.SEQUENTIAL.value:
            return SequentialStockAnalysisCrew(config)
        elif mode.lower() == CrewMode.GROUP_CHAT.value:
            return GroupChatStockAnalysisCrew(config)
        else:
            raise ValueError(f"Unknown crew mode: {mode}. Use 'sequential' or 'group_chat'.")
