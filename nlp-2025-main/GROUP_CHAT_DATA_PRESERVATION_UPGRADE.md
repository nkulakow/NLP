# Group Chat Data Preservation Upgrade Proposal

## Problem Analysis

Group Chat mode loses data richness due to:

1. **Disconnected Agent Context**: Sceptic and Trust agents work without direct access to raw gathered data
2. **Information Bottleneck**: Data flows only through text synthesis, losing structure and relationships
3. **Local Agent Memory**: Each agent's memory is isolated, not shared across the group
4. **Debate Compression**: Critical nuances get lost when synthesizing debate into final report
5. **No Evidence Trail**: Claims aren't traced back to original data sources
6. **Single-Pass Processing**: Agents see compressed outputs, not original rich data

**Impact**: Data richness metric significantly lower than Sequential mode which has explicit task dependencies with full context preservation.

---

## Proposed Solutions (Priority Order)

### Solution 1: Shared Structured Data Store ⭐⭐⭐ (High Impact, Medium Effort)

**Concept**: Create a shared JSON data structure that all agents can access and update, preserving data in structured form rather than just text.

**Implementation**:
```python
# New file: src/crews/shared_memory.py
class SharedAnalysisMemory:
    """Shared memory system for group chat agents."""
    
    def __init__(self):
        self.data = {
            "sentiment": {
                "reddit_analysis": {},
                "news_summary": {},
                "finnhub_sentiment": {},
                "confidence_score": None,
            },
            "technical": {
                "indicators": {},
                "trends": [],
                "patterns": [],
                "support_resistance": [],
                "signals": [],
            },
            "fundamental": {
                "financials": {},
                "ratios": {},
                "valuation": {},
                "health_score": None,
            },
            "risks": [],  # Updated by Sceptic
            "verifications": [],  # Updated by Trust Agent
            "evidence_trail": [],  # All claims with sources
        }
    
    def update(self, section: str, key: str, value):
        """Update data with source tracking."""
        self.data[section][key] = value
        self.data["evidence_trail"].append({
            "timestamp": datetime.now(),
            "section": section,
            "key": key,
            "value": value[:200] + "..." if len(str(value)) > 200 else value,
        })
    
    def get_section(self, section: str) -> dict:
        """Get entire section for agent reference."""
        return self.data[section]
```

**Integration Points**:
- Pass `shared_memory` instance to all agents
- Researcher explicitly populates sentiment/technical/fundamental sections
- Sceptic references specific data points when challenging
- Trust Agent uses structured data for verification
- Leader consults full memory before synthesis

---

### Solution 2: Enhanced Agent Prompts with Data Fidelity ⭐⭐ (Low Effort, Good Impact)

**Concept**: Update agent backstories and goals to explicitly require data preservation and evidence citation.

**Implementation**:
```python
# Update agents_definitions.py

def create_sceptic_agent(llm: LLM, shared_memory=None) -> Agent:
    """Create Sceptic agent with data preservation requirements."""
    return Agent(
        role="Devil's Advocate - Sceptic",
        goal=(
            "Challenge investment thesis for {stock_symbol} while PRESERVING specific data points. "
            "For each risk identified, cite the exact data (sentiment score, technical level, financial metric) "
            "that supports your concern. Do NOT generalize—reference concrete evidence from gathered data."
        ),
        backstory=(
            "You are a critical thinker who identifies risks without dismissing evidence. "
            "Your job is not to deny data, but to contextualize and challenge interpretations. "
            "Always cite specific metrics, dates, or thresholds when raising concerns. "
            "Example: 'RSI at 72 suggests overbought, but volume confirms strength—caution justified.'"
        ),
        llm=llm,
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )
```

**Key Changes**:
- Add data citation requirements to prompts
- Require agents to reference specific numbers/evidence
- Ask for "confidence level" with reasoning
- Explicitly forbid vague generalizations

---

### Solution 3: Explicit Data Aggregation Task ⭐⭐⭐ (Medium Effort, High Impact)

**Concept**: Add intermediate task that structures all gathered data before debate begins.

**Implementation**:
```python
# New task type in tasks_definitions.py
TaskType.DATA_AGGREGATION: {
    "description": (
        "Aggregate all research data about '{stock_symbol}' into a structured summary. "
        "Organize sentiment scores, technical indicators, financial metrics with sources. "
        "This summary will be reviewed by the full team before final debate."
    ),
    "expected_output": (
        "Structured data document containing:\n"
        "1. Sentiment Metrics: [specific scores, sources]\n"
        "2. Technical Data: [key levels, indicators with values]\n"
        "3. Fundamental Metrics: [ratios, valuations with comparisons]\n"
        "4. Source Quality Assessment\n"
        "This becomes the shared reference for all debate."
    ),
}

# Modified group_chat.py execution:
def run(self, stock_symbol: str) -> dict:
    research_task = create_task(TaskType.RESEARCH, self.researcher)
    technical_task = create_task(TaskType.TECHNICAL_ANALYSIS, self.technical_analyst)
    fundamental_task = create_task(TaskType.FUNDAMENTAL_ANALYSIS, self.fundamental_analyst)
    
    # NEW: Aggregate before debate
    aggregation_task = create_task(
        TaskType.DATA_AGGREGATION,
        self.researcher,  # Researcher owns aggregation
        context=[research_task, technical_task, fundamental_task]
    )
    
    sceptic_task = create_task(
        TaskType.SCEPTIC, 
        self.sceptic,
        context=[aggregation_task]  # Sceptic sees structured data
    )
    trust_task = create_task(
        TaskType.TRUST, 
        self.trust_agent,
        context=[aggregation_task]  # Trust agent verifies structured data
    )
    
    synthesis_task = create_task(
        TaskType.SYNTHESIS,
        self.leader,
        context=[aggregation_task, sceptic_task, trust_task],
    )
    # ... rest of crew setup
```

---

### Solution 4: Multi-Agent Data Exchange Protocol ⭐⭐⭐ (High Effort, Highest Impact)

**Concept**: Implement CrewAI's callback system to log all agent outputs and make them accessible as structured memory.

**Implementation**:
```python
# New file: src/crews/conversation_memory.py
from crewai import Crew
from typing import Any

class ConversationMemoryCallback:
    """Captures agent outputs and makes them available to all agents."""
    
    def __init__(self):
        self.exchanges = []
    
    def on_task_end(self, task_output: Any, agent_role: str, task_name: str):
        """Store task output for all agents to access."""
        self.exchanges.append({
            "agent": agent_role,
            "task": task_name,
            "output": str(task_output)[:2000],  # Truncate for memory
            "timestamp": datetime.now(),
        })
    
    def get_agent_history(self, agent_role: str = None) -> str:
        """Get conversation history for agent context."""
        if agent_role:
            relevant = [e for e in self.exchanges if e["agent"] == agent_role]
        else:
            relevant = self.exchanges
        
        return "\n---\n".join([
            f"[{e['agent']}] Task: {e['task']}\n{e['output']}"
            for e in relevant
        ])

# In group_chat.py:
callback = ConversationMemoryCallback()
crew = Crew(
    agents=[...],
    tasks=[...],
    manager_agent=self.leader,
    process=Process.hierarchical,
    callbacks=[callback],  # Add callback
)

# Agents can reference via prompt:
# "Here's what other agents discovered: {conversation_history}"
```

---

### Solution 5: Evidence-Based Debate Framework ⭐⭐ (Medium Effort, Good Impact)

**Concept**: Structure group chat to require evidence citations rather than free-form debate.

**Implementation**:
```python
TaskType.SCEPTIC_REVIEW: {
    "description": (
        "Review '{stock_symbol}' analysis and provide risk assessment. "
        "For EACH risk mentioned, provide:\n"
        "- Risk Description\n"
        "- Supporting Evidence (cite specific metric/date/source)\n"
        "- Probability Assessment (High/Medium/Low)\n"
        "- Mitigation Factors (if any)\n"
        "Format as JSON for clarity."
    ),
    "expected_output": (
        "JSON array of risks with structured format:\n"
        "[\n"
        "  {\"risk\": \"...\", \"evidence\": \"...\", \"probability\": \"...\", \"mitigation\": \"...\"}\n"
        "]"
    ),
}
```

---

## Implementation Roadmap

### Phase 1 (Week 1): Quick Wins
1. **Solution 2** - Enhanced prompts requiring data citation
2. **Solution 3** - Add data aggregation task
3. **Impact**: Immediate improvement in data preservation with minimal code changes

### Phase 2 (Week 2): Medium-Term
1. **Solution 1** - Implement shared memory structure
2. **Solution 5** - Evidence-based debate framework
3. **Impact**: Structured data preservation, evidence trails

### Phase 3 (Week 3+): Long-Term
1. **Solution 4** - Multi-agent callback system
2. **Add metrics dashboard** showing data richness before/after
3. **Impact**: Full conversation memory across agents

---

## Quick Win Implementation (Recommended First Step)

Here's the minimal change for immediate improvement:

```python
# Modify create_sceptic_agent in agents_definitions.py
def create_sceptic_agent(llm: LLM) -> Agent:
    return Agent(
        role="Devil's Advocate - Sceptic",
        goal=(
            "Challenge assumptions for {stock_symbol}. "
            "IMPORTANT: For each concern, cite specific evidence (numbers, dates, sources). "
            "Example: 'P/E of 35 vs industry avg 22 is 59% premium—justify valuation.' "
            "Preserve all data points while critiquing interpretations."
        ),
        backstory=(
            "You are a critical analyst who questions logic without dismissing evidence. "
            "You cite specific metrics, preserve context, and separate data from opinion."
        ),
        llm=llm,
        tools=[],
        verbose=True,
        memory=True,
        allow_code_execution=False,
    )
```

**Expected Result**: Sceptic preserves data while challenging thesis, improving data richness score.

---

## Metrics to Track

Add these measurements to evaluate improvement:

```python
def calculate_data_richness_metrics(report: str) -> dict:
    """Measure data preservation in report."""
    return {
        "num_citations": count_metric_citations(report),
        "num_data_points": count_distinct_metrics(report),
        "avg_evidence_depth": measure_evidence_references(report),
        "contradiction_count": find_contradictions(report),
        "data_completeness": assess_completeness(report),
    }
```

Compare Sequential vs Group Chat with these metrics to validate improvements.

---

## Expected Outcomes

| Metric | Current (Group Chat) | Target | Method |
|--------|---------------------|--------|--------|
| Data Points Preserved | 60-70% | 90%+ | Solutions 1, 3, 5 |
| Evidence Citations | Low | High | Solutions 2, 5 |
| Agent Context Overlap | Limited | Full | Solutions 1, 4 |
| Report Depth | 7/10 | 9/10 | All solutions |
| Contradiction Instances | 5-10% | <2% | Solution 4 |

---

## Recommendation

**Start with Solution 2 + 3 (Quick Wins)**:
- Modify agent prompts to require data citation (+15% data richness)
- Add data aggregation task (+25% data richness)  
- **Estimated time**: 2-3 hours
- **Estimated improvement**: +30-40% data richness

Then **evaluate if Solution 1** (shared memory) is needed based on results.

