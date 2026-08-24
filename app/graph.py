"""LangGraph orchestration pipeline connecting Module 1 and Module 2."""

from langgraph.graph import StateGraph, START, END
from app.state import BlueprintState
from app.agents.requirement_agent import requirement_agent_node
from app.agents.planning_agent import planning_agent_node


def build_blueprint_graph():
    """Build and compile the LangGraph workflow for Blueprint AI.
    
    Graph Topology:
    START -> requirement_agent -> planning_agent -> END
    """
    workflow = StateGraph(BlueprintState)

    # Add agent nodes
    workflow.add_node("requirement_agent", requirement_agent_node)
    workflow.add_node("planning_agent", planning_agent_node)

    # Add linear transitions
    workflow.add_edge(START, "requirement_agent")
    workflow.add_edge("requirement_agent", "planning_agent")
    workflow.add_edge("planning_agent", END)

    # Compile executable graph
    return workflow.compile()


# Global compiled workflow instance
blueprint_graph = build_blueprint_graph()


def run_blueprint_generation(project_idea: str) -> BlueprintState:
    """Execute the full blueprint generation workflow for a project idea."""
    initial_state: BlueprintState = {
        "project_idea": project_idea,
        "requirements": None,
        "project_plan": None,
        "errors": []
    }
    
    final_state = blueprint_graph.invoke(initial_state)
    return final_state
