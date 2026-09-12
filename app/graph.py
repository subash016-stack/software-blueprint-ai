"""Stateful LangGraph orchestration pipeline connecting Modules 1 through 5."""

import logging
from langgraph.graph import StateGraph, START, END
from app.state import BlueprintState
from app.agents.requirement_agent import requirement_agent_node
from app.agents.planning_agent import planning_agent_node
from app.agents.architecture_agent import architecture_agent_node
from app.agents.rag_agent import rag_agent_node
from app.agents.validation_agent import validation_agent_node

logger = logging.getLogger("software-blueprint-ai.graph")


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

    # 1. Add Agent Nodes
    workflow.add_node("requirement_agent", requirement_agent_node)
    workflow.add_node("planning_agent", planning_agent_node)
    workflow.add_node("architecture_agent", architecture_agent_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("validation_agent", validation_agent_node)

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
    """Execute the complete multi-agent blueprint generation pipeline."""
    initial_state: BlueprintState = {
        "project_id": project_id,
        "project_idea": project_idea,
        "requirements": None,
        "project_plan": None,
        "architecture": None,
        "rag_recommendations": [],
        "validation_report": None,
        "version": 1,
        "errors": []
    }
    
    final_state = blueprint_graph.invoke(initial_state)
    return final_state
