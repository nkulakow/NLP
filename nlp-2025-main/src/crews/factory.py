from enum import Enum
from typing import Optional

from src.crews.sequential import SequentialStockAnalysisCrew
from src.crews.group_chat import GroupChatStockAnalysisCrew, GroupChatType
from src.config import load_config


class CrewMode(Enum):
    """Enum for crew execution modes."""

    SEQUENTIAL = "sequential"
    GROUP_CHAT = "group_chat"


class StockAnalysisCrewFactory:
    """Factory for creating crew instances based on mode."""

    @staticmethod
    def create(mode: str, provider: Optional[str] = None, group_chat_type: Optional[str] = None):
        """
        Create a crew instance based on mode.

        Args:
            mode: "sequential" or "group_chat"
            provider: "gemini" or "openai". If None, uses LLM_PROVIDER from env.
            group_chat_type: Optional group chat variant if mode is group_chat.

        Returns:
            Instance of SequentialStockAnalysisCrew or GroupChatStockAnalysisCrew

        Raises:
            ValueError: If mode is not recognized or provider is invalid
        """
        config = load_config(provider)

        if mode.lower() == CrewMode.SEQUENTIAL.value:
            return SequentialStockAnalysisCrew(config)
        elif mode.lower() == CrewMode.GROUP_CHAT.value:
            selected_group_chat_type = GroupChatType.LEGACY
            if group_chat_type:
                try:
                    selected_group_chat_type = GroupChatType(group_chat_type.lower())
                except ValueError:
                    raise ValueError(
                        f"Unknown group chat type: {group_chat_type}. Use 'legacy', 'shared_memory', or 'iterative_refinement'."
                    )
            return GroupChatStockAnalysisCrew(config, selected_group_chat_type)
        else:
            raise ValueError(f"Unknown crew mode: {mode}. Use 'sequential' or 'group_chat'.")
