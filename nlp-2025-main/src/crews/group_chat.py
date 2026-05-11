from enum import Enum
from time import time
from typing import Optional

from crewai import Crew, LLM
from crewai.process import Process

from src.crews.agents_definitions import (
    create_researcher_agent,
    create_technical_analyst_agent,
    create_fundamental_analyst_agent,
    create_sceptic_agent,
    create_trust_agent,
    create_leader_agent,
)
from src.crews.shared_memory import SharedAnalysisMemory
from src.crews.tasks_definitions import create_task, TaskType
from src.config import LLMConfig


class GroupChatType(Enum):
    """Types of group chat execution modes."""

    LEGACY = "legacy"
    SHARED_MEMORY = "shared_memory"


class GroupChatStockAnalysisCrew:
    """Group Chat mode - 6 agents in hierarchical debate with Leader orchestrating."""

    def __init__(self, config: LLMConfig, group_chat_type: GroupChatType = GroupChatType.LEGACY):
        self.config = config
        self.group_chat_type = group_chat_type
        self.shared_memory: Optional[SharedAnalysisMemory] = None

        self.llm = LLM(
            model=self.config.model_group_chat,
            api_key=self.config.api_key,
            temperature=self.config.temperature,
        )

    def _initialize_agents(self, shared_memory: Optional[SharedAnalysisMemory] = None):
        """Initialize all 6 agents for group chat mode."""
        # Original 3 specialist agents
        self.researcher = create_researcher_agent(self.llm, shared_memory)
        self.technical_analyst = create_technical_analyst_agent(self.llm, shared_memory)
        self.fundamental_analyst = create_fundamental_analyst_agent(self.llm, shared_memory)

        # New 3 agents for debate and synthesis
        self.sceptic = create_sceptic_agent(self.llm, shared_memory)
        self.trust_agent = create_trust_agent(self.llm, shared_memory)
        self.leader = create_leader_agent(self.llm, shared_memory)

    def run(self, stock_symbol: str) -> dict:
        """
        Run group chat mode with hierarchical process - leader orchestrates 6 specialist agents.

        Uses shared memory only when the selected group chat type requires it.

        Args:
            stock_symbol: Stock ticker symbol

        Returns:
            Dictionary with mode, provider, execution_time, report, and optional shared memory metadata
        """
        start_time = time()

        if self.group_chat_type == GroupChatType.SHARED_MEMORY:
            self.shared_memory = SharedAnalysisMemory(stock_symbol.upper())
        else:
            self.shared_memory = None

        self._initialize_agents(self.shared_memory)

        research_task = create_task(
            TaskType.RESEARCH,
            self.researcher,
            shared_memory=self.shared_memory,
        )
        technical_task = create_task(
            TaskType.TECHNICAL_ANALYSIS,
            self.technical_analyst,
            shared_memory=self.shared_memory,
        )
        fundamental_task = create_task(
            TaskType.FUNDAMENTAL_ANALYSIS,
            self.fundamental_analyst,
            shared_memory=self.shared_memory,
        )
        sceptic_task = create_task(
            TaskType.SCEPTIC,
            self.sceptic,
            context=[research_task, technical_task, fundamental_task],
            shared_memory=self.shared_memory,
        )
        trust_task = create_task(
            TaskType.TRUST,
            self.trust_agent,
            context=[research_task, technical_task, fundamental_task],
            shared_memory=self.shared_memory,
        )

        synthesis_task = create_task(
            TaskType.SYNTHESIS,
            self.leader,
            context=[research_task, technical_task, fundamental_task, sceptic_task, trust_task],
            shared_memory=self.shared_memory,
        )

        crew = Crew(
            agents=[
                self.researcher,
                self.technical_analyst,
                self.fundamental_analyst,
                self.sceptic,
                self.trust_agent,
            ],
            tasks=[
                research_task,
                technical_task,
                fundamental_task,
                sceptic_task,
                trust_task,
                synthesis_task,
            ],
            manager_agent=self.leader,
            process=Process.hierarchical,
            verbose=True,
            cache=True,
        )

        try:
            result = crew.kickoff(inputs={"stock_symbol": stock_symbol.upper()})
            execution_time = time() - start_time
            memory_summary = self._generate_memory_summary() if self.shared_memory else {}

            return {
                "mode": "group_chat",
                "group_chat_type": self.group_chat_type.value,
                "provider": self.config.provider.value,
                "execution_time": execution_time,
                "report": str(result),
                "shared_memory_summary": memory_summary,
                "data_preservation_enabled": self.group_chat_type == GroupChatType.SHARED_MEMORY,
            }
        except Exception as e:
            execution_time = time() - start_time
            return {
                "mode": "group_chat",
                "group_chat_type": self.group_chat_type.value,
                "provider": self.config.provider.value,
                "execution_time": execution_time,
                "report": f"Group Chat mode failed: {str(e)}. Recommend using Sequential mode.",
                "error": str(e),
                "data_preservation_enabled": self.group_chat_type == GroupChatType.SHARED_MEMORY,
            }

    def _generate_memory_summary(self) -> dict:
        """Generate a summary of shared memory for diagnostics."""
        if not self.shared_memory:
            return {}

        return {
            "stock_symbol": self.shared_memory.stock_symbol,
            "sentiment_collected": bool(self.shared_memory.data.get("sentiment", {}).get("overall_sentiment")),
            "technical_collected": bool(self.shared_memory.data.get("technical", {}).get("price_trend")),
            "fundamental_collected": bool(self.shared_memory.data.get("fundamental", {}).get("health_score")),
            "risks_identified": len(self.shared_memory.data.get("risks", [])),
            "verified_claims": len(self.shared_memory.data.get("verifications", {}).get("verified_claims", [])),
            "contradictions_found": len(self.shared_memory.data.get("verifications", {}).get("contradictions", [])),
            "total_updates": len(self.shared_memory.evidence_trail),
        }
