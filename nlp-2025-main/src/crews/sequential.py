from time import time

from crewai import Crew, LLM

from src.crews.agents_definitions import (
    create_researcher_agent,
    create_technical_analyst_agent,
    create_fundamental_analyst_agent,
    create_reporter_agent,
)
from src.crews.tasks_definitions import create_task, TaskType
from src.config import LLMConfig


class SequentialStockAnalysisCrew:
    """Sequential execution mode - agents work in linear order with dependencies."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = LLM(
            model=self.config.model_sequential,
            api_key=self.config.api_key,
            temperature=0.2,
        )
        self._initialize_agents_and_tasks()

    def _initialize_agents_and_tasks(self):
        """Initialize all agents and tasks for sequential mode."""
        researcher = create_researcher_agent(self.llm)
        technical_analyst = create_technical_analyst_agent(self.llm)
        fundamental_analyst = create_fundamental_analyst_agent(self.llm)
        reporter = create_reporter_agent(self.llm)

        research_task = create_task(TaskType.RESEARCH, researcher)
        technical_analysis_task = create_task(TaskType.TECHNICAL_ANALYSIS, technical_analyst, context=[research_task])
        fundamental_analysis_task = create_task(TaskType.FUNDAMENTAL_ANALYSIS, fundamental_analyst, context=[research_task])
        reporting_task = create_task(TaskType.REPORTING, reporter, context=[research_task, technical_analysis_task, fundamental_analysis_task])

        self.crew = Crew(
            agents=[researcher, technical_analyst, fundamental_analyst, reporter],
            tasks=[research_task, technical_analysis_task, fundamental_analysis_task, reporting_task],
            cache=True,
            verbose=True,
        )

    def run(self, stock_symbol: str) -> dict:
        """
        Run sequential crew and return report with metadata.

        Args:
            stock_symbol: Stock ticker symbol

        Returns:
            Dictionary with mode, provider, execution_time, and report
        """
        start_time = time()
        result = self.crew.kickoff(inputs={"stock_symbol": stock_symbol.upper()})
        execution_time = time() - start_time

        return {
            "mode": "sequential",
            "provider": self.config.provider.value,
            "execution_time": execution_time,
            "report": str(result),
        }
