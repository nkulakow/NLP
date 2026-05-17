from time import time

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
from src.tools.shard_memory_tools import create_memory_tools, SHARED_MEMORY
from src.crews.tasks_definitions import create_task, TaskType
from src.config import LLMConfig


class GroupChatStockAnalysisCrew:
    """Group Chat mode - 6 agents in hierarchical debate with Leader orchestrating."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = LLM(
            model=self.config.model_group_chat,
            api_key=self.config.api_key,
            temperature=self.config.temperature,
            base_url=self.config.base_url
        )

    def _initialize_agents(self, stock_symbol: str):
        """Initialize all 6 agents for group chat mode."""
        tools = create_memory_tools(stock_symbol)
        # Original 3 specialist agents
        self.researcher = create_researcher_agent(self.llm, extra_tools=tools)
        self.technical_analyst = create_technical_analyst_agent(self.llm, extra_tools=tools)
        self.fundamental_analyst = create_fundamental_analyst_agent(self.llm, extra_tools=tools)

        # New 3 agents for debate and synthesis
        self.sceptic = create_sceptic_agent(self.llm, extra_tools=tools)
        self.trust_agent = create_trust_agent(self.llm, extra_tools=tools)
        self.leader = create_leader_agent(self.llm)

    def run(self, stock_symbol: str) -> dict:
        """
        Run group chat mode with hierarchical process - leader orchestrates 6 specialist agents.

        Uses shared memory to preserve data richness throughout the debate.

        Args:
            stock_symbol: Stock ticker symbol

        Returns:
            Dictionary with mode, provider, execution_time, report, and shared_memory_summary
        """
        start_time = time()

        # Create shared memory for this analysis

        # Initialize agents with shared memory context
        self._initialize_agents(stock_symbol)

        # Create tasks with shared memory context
        research_task = create_task(
            TaskType.RESEARCH,
            self.researcher,
            use_shared_memory=True,
        )
        technical_task = create_task(
            TaskType.TECHNICAL_ANALYSIS,
            self.technical_analyst,
            use_shared_memory=True,
        )
        fundamental_task = create_task(
            TaskType.FUNDAMENTAL_ANALYSIS,
            self.fundamental_analyst,
            use_shared_memory=True,
        )
        sceptic_task = create_task(
            TaskType.SCEPTIC,
            self.sceptic,
            use_shared_memory=True,
            context=[research_task, technical_task, fundamental_task],
        )
        trust_task = create_task(
            TaskType.TRUST,
            self.trust_agent,
            use_shared_memory=True,
            context=[research_task, technical_task, fundamental_task],
        )

        synthesis_task = create_task(
            TaskType.SYNTHESIS,
            self.leader,
            use_shared_memory=True,
            context=[research_task, technical_task, fundamental_task, sceptic_task, trust_task]
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

            # Generate shared memory summary for reference
            memory_summary = self._generate_memory_summary()

            return {
                "mode": "group_chat",
                "provider": self.config.provider.value,
                "execution_time": execution_time,
                "report": str(result),
                "shared_memory_summary": memory_summary,
                "data_preservation_enabled": True,
            }
        except Exception as e:
            execution_time = time() - start_time
            return {
                "mode": "group_chat",
                "provider": self.config.provider.value,
                "execution_time": execution_time,
                "report": f"Group Chat mode failed: {str(e)}. Recommend using Sequential mode.",
                "error": str(e),
                "data_preservation_enabled": True,
            }

    def _generate_memory_summary(self) -> dict:
        """Generate a summary of shared memory for diagnostics."""
        if not SHARED_MEMORY:
            return {}

        return {
            "stock_symbol": SHARED_MEMORY.stock_symbol,
            "sentiment_collected": bool(SHARED_MEMORY.data.get("sentiment", {}).get("overall_sentiment")),
            "technical_collected": bool(SHARED_MEMORY.data.get("technical", {}).get("price_trend")),
            "fundamental_collected": bool(SHARED_MEMORY.data.get("fundamental", {}).get("health_score")),
            "risks_identified": len(SHARED_MEMORY.data.get("risks", [])),
            "verified_claims": len(SHARED_MEMORY.data.get("verifications", {}).get("verified_claims", [])),
            "contradictions_found": len(SHARED_MEMORY.data.get("verifications", {}).get("contradictions", [])),
            "total_updates": len(SHARED_MEMORY.evidence_trail),
        }
