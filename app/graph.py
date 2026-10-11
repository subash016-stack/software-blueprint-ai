"""Stateful LangGraph orchestration pipeline connecting Modules 1 through 5."""

import logging
import time
from langgraph.graph import StateGraph, START, END
from app.state import BlueprintState
from app.agents.requirement_agent import requirement_agent_node
from app.agents.planning_agent import planning_agent_node
from app.agents.architecture_agent import architecture_agent_node
from app.agents.rag_agent import rag_agent_node
from app.agents.validation_agent import validation_agent_node
from app.llm.factory import MetricsTracker

logger = logging.getLogger("software-blueprint-ai.graph")


def _timed_node(name: str, node_func):
    """Timing decorator for LangGraph node execution."""
    def wrapper(state: BlueprintState) -> BlueprintState:
        t0 = time.time()
        res = node_func(state)
        duration_ms = round((time.time() - t0) * 1000.0, 2)
        meta = dict(res.get("metadata") or state.get("metadata") or {})
        timings = dict(meta.get("timings") or {})
        timings[name] = duration_ms
        meta["timings"] = timings
        res["metadata"] = meta
        return res
    return wrapper


def build_blueprint_graph():
    """Build and compile the multi-agent LangGraph workflow.
    
    Graph Topology:
    START 
      ↓
    requirement_agent (Module 1)
      ↓
    planning_agent (Module 2)
      ↓
    architecture_agent (Module 3)
      ↓
    rag_agent (Module 4)
      ↓
    validation_agent (Module 5)
      ↓
    END
    """
    workflow = StateGraph(BlueprintState)

    # 1. Add Agent Nodes with timing tracking
    workflow.add_node("requirement_agent", _timed_node("requirement_agent", requirement_agent_node))
    workflow.add_node("planning_agent", _timed_node("planning_agent", planning_agent_node))
    workflow.add_node("architecture_agent", _timed_node("architecture_agent", architecture_agent_node))
    workflow.add_node("rag_agent", _timed_node("rag_agent", rag_agent_node))
    workflow.add_node("validation_agent", _timed_node("validation_agent", validation_agent_node))

    # 2. Add Linear Flow Edges
    workflow.add_edge(START, "requirement_agent")
    workflow.add_edge("requirement_agent", "planning_agent")
    workflow.add_edge("planning_agent", "architecture_agent")
    workflow.add_edge("architecture_agent", "rag_agent")
    workflow.add_edge("rag_agent", "validation_agent")
    workflow.add_edge("validation_agent", END)

    return workflow.compile()


# Global compiled workflow instance
blueprint_graph = build_blueprint_graph()


def run_blueprint_generation(project_idea: str, project_id: str = "proj-default") -> BlueprintState:
    """Execute the complete multi-agent blueprint generation pipeline with latency tracking."""
    t_start = time.time()
    initial_state: BlueprintState = {
        "project_id": project_id,
        "project_idea": project_idea,
        "requirements": None,
        "project_plan": None,
        "architecture": None,
        "rag_recommendations": [],
        "validation_report": None,
        "version": 1,
        "errors": [],
        "metadata": {"timings": {}}
    }
    
    final_state = blueprint_graph.invoke(initial_state)
    total_time_ms = round((time.time() - t_start) * 1000.0, 2)
    
    meta = dict(final_state.get("metadata") or {})
    meta["total_execution_time_ms"] = total_time_ms
    final_state["metadata"] = meta

    # Record pipeline metrics to central MetricsTracker
    MetricsTracker.record_pipeline_execution(
        total_time_ms=total_time_ms,
        timings=meta.get("timings", {}),
        validation_report=final_state.get("validation_report")
    )

    return final_state
