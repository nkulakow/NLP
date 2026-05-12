from time import time
from crewai import Crew, LLM
from crewai.process import Process

from src.crews.agents_definitions import (
    create_researcher_agent,
    create_technical_analyst_agent,
    create_fundamental_analyst_agent,
    create_sceptic_agent,
    create_trust_agent,
    create_reporter_agent,
)
from src.crews.tasks_definitions import create_task, TaskType
from src.crews.shared_memory import SharedAnalysisMemory
from src.config import LLMConfig
from src.tools.shared_memory_tool import create_memory_tools

class GroupChatStockAnalysisCrew:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = LLM(
            model=self.config.model_group_chat,
            api_key=self.config.api_key,
            temperature=self.config.temperature,
        )
        self.shared_memory = None

    def _initialize_agents(self, shared_memory: SharedAnalysisMemory):
        # Create tools linked to the memory instance
        memory_tools = create_memory_tools(shared_memory)

        # Initialize all agents using the unified 'extra_tools' parameter
        self.researcher = create_researcher_agent(self.llm, extra_tools=memory_tools)
        self.technical_analyst = create_technical_analyst_agent(self.llm, extra_tools=memory_tools)
        self.fundamental_analyst = create_fundamental_analyst_agent(self.llm, extra_tools=memory_tools)
        self.sceptic = create_sceptic_agent(self.llm, extra_tools=memory_tools)
        self.trust_agent = create_trust_agent(self.llm, extra_tools=memory_tools)
        self.leader = create_reporter_agent(self.llm, extra_tools=memory_tools)

    def run(self, stock_symbol: str) -> dict:
        start_time = time()
        self.shared_memory = SharedAnalysisMemory(stock_symbol)
        self._initialize_agents(self.shared_memory)

        # Define tasks (ensure create_task handles shared_memory internal summary)
        r_task = create_task(TaskType.RESEARCH, self.researcher, shared_memory=self.shared_memory)
        t_task = create_task(TaskType.TECHNICAL_ANALYSIS, self.technical_analyst, shared_memory=self.shared_memory)
        f_task = create_task(TaskType.FUNDAMENTAL_ANALYSIS, self.fundamental_analyst, shared_memory=self.shared_memory)

        s_task = create_task(TaskType.SCEPTIC, self.sceptic, context=[r_task, t_task, f_task], shared_memory=self.shared_memory)
        v_task = create_task(TaskType.TRUST, self.trust_agent, context=[r_task, t_task, f_task], shared_memory=self.shared_memory)

        final_task = create_task(TaskType.SYNTHESIS, self.leader, context=[r_task, t_task, f_task, s_task, v_task], shared_memory=self.shared_memory)

        crew = Crew(
            agents=[self.researcher, self.technical_analyst, self.fundamental_analyst, self.sceptic, self.trust_agent],
            tasks=[r_task, t_task, f_task, s_task, v_task, final_task],
            manager_agent=self.leader,
            process=Process.hierarchical,
            verbose=True
        )

        try:
            result = crew.kickoff(inputs={"stock_symbol": stock_symbol.upper()})
            return {
                "mode": "group_chat",
                "execution_time": time() - start_time,
                "report": str(result),
                "shared_memory_summary": self._generate_memory_summary(),
                "data_preservation_enabled": True
            }
        except Exception as e:
            return {"mode": "group_chat", "error": str(e), "execution_time": time() - start_time}

    def _generate_memory_summary(self) -> dict:
        if not self.shared_memory: return {}
        d = self.shared_memory.data
        return {
            "stock_symbol": self.shared_memory.stock_symbol,
            "sentiment_collected": bool(d.get("sentiment")),
            "technical_collected": bool(d.get("technical")),
            "fundamental_collected": bool(d.get("fundamental")),
            "risks_identified": len(d.get("risks", [])),
            "total_updates": len(self.shared_memory.evidence_trail),
        }