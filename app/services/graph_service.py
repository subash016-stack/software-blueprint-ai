"""Multi-tier Traceability Graph management using NetworkX."""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from app.schemas import (
    RequirementAnalysis,
    ProjectPlan,
    ArchitectureBlueprint,
    ImpactLevel
)

logger = logging.getLogger("software-blueprint-ai.graph")


class TraceabilityGraphService:
    """Constructs and queries the multi-tier engineering traceability graph."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(
        self,
        requirements: RequirementAnalysis,
        project_plan: ProjectPlan,
        architecture: ArchitectureBlueprint
    ) -> nx.DiGraph:
        """Construct the complete multi-tier directed traceability graph."""
        G = nx.DiGraph()

        # 1. Stakeholders -> FRs
        for st in requirements.stakeholders:
            G.add_node(st.id, type="Stakeholder", label=st.name, data=st.model_dump())

        for fr in requirements.functional_requirements:
            G.add_node(fr.id, type="Requirement", label=fr.title, priority=fr.priority.value, data=fr.model_dump())
            for st_id in fr.stakeholders:
                if G.has_node(st_id):
                    G.add_edge(st_id, fr.id, relation="staked_by")

        # 2. FRs -> Modules
        for m in project_plan.modules:
            G.add_node(m.id, type="Module", label=m.name, data=m.model_dump())
            for r_id in m.requirement_ids:
                if G.has_node(r_id):
                    G.add_edge(r_id, m.id, relation="grouped_in")

        # 3. FRs -> Tasks & Task Dependencies
        for t in project_plan.tasks:
            G.add_node(t.id, type="Task", label=t.title, effort=t.estimated_hours, data=t.model_dump())
            for r_id in t.requirement_ids:
                if G.has_node(r_id):
                    G.add_edge(r_id, t.id, relation="implements")
            for dep in t.dependencies:
                if G.has_node(dep):
                    G.add_edge(dep, t.id, relation="depends_on")

        # 4. Tasks -> Milestones
        for ms in project_plan.milestones:
            G.add_node(ms.id, type="Milestone", label=ms.name, data=ms.model_dump())
            for t_id in ms.task_ids:
                if G.has_node(t_id):
                    G.add_edge(t_id, ms.id, relation="delivers")

        # 5. FRs -> Architecture Components
        for comp in architecture.components:
            G.add_node(comp.id, type="Component", label=comp.name, data=comp.model_dump())
            for r_id in comp.requirement_ids:
                if G.has_node(r_id):
                    G.add_edge(r_id, comp.id, relation="architects")
            if comp.module_id and G.has_node(comp.module_id):
                G.add_edge(comp.module_id, comp.id, relation="belongs_to")

        # 6. Components -> APIs
        for api in architecture.apis:
            G.add_node(api.id, type="API", label=f"{api.method} {api.endpoint}", data=api.model_dump())
            if G.has_node(api.component_id):
                G.add_edge(api.component_id, api.id, relation="exposes")
            for r_id in api.requirement_ids:
                if G.has_node(r_id):
                    G.add_edge(r_id, api.id, relation="satisfies")

        # 7. Components -> Databases
        for db in architecture.databases:
            G.add_node(db.id, type="Database", label=db.name, engine=db.engine, data=db.model_dump())
            for c_id in db.component_ids:
                if G.has_node(c_id):
                    G.add_edge(c_id, db.id, relation="persists_to")

        self.graph = G
        return G

    def analyze_downstream_impact(self, changed_fr_id: str) -> Dict[str, Any]:
        """Traverse downstream directed graph to find all affected entities."""
        if not self.graph.has_node(changed_fr_id):
            return {
                "impact_level": ImpactLevel.LOW,
                "affected_modules": [],
                "affected_tasks": [],
                "affected_components": [],
                "affected_apis": [],
                "affected_milestones": [],
                "affected_requirements": [changed_fr_id],
                "effort_hours_delta": 4.0
            }

        # BFS downstream reachable nodes
        downstream_nodes = nx.descendants(self.graph, changed_fr_id)
        affected_all = downstream_nodes | {changed_fr_id}

        affected_modules = []
        affected_tasks = []
        affected_components = []
        affected_apis = []
        affected_milestones = []
        affected_reqs = [changed_fr_id]
        effort_delta = 0.0

        for node_id in affected_all:
            node_data = self.graph.nodes[node_id]
            node_type = node_data.get("type", "")

            if node_type == "Module":
                affected_modules.append(node_id)
            elif node_type == "Task":
                affected_tasks.append(node_id)
                effort_delta += float(node_data.get("effort", 4.0))
            elif node_type == "Component":
                affected_components.append(node_id)
            elif node_type == "API":
                affected_apis.append(node_id)
            elif node_type == "Milestone":
                affected_milestones.append(node_id)
            elif node_type == "Requirement" and node_id != changed_fr_id:
                affected_reqs.append(node_id)

        # Categorize Impact Level
        total_affected = len(affected_tasks) + len(affected_components) + len(affected_apis)
        if total_affected >= 7 or len(affected_milestones) >= 2:
            impact_level = ImpactLevel.CRITICAL
        elif total_affected >= 4:
            impact_level = ImpactLevel.HIGH
        elif total_affected >= 2:
            impact_level = ImpactLevel.MEDIUM
        else:
            impact_level = ImpactLevel.LOW

        return {
            "impact_level": impact_level,
            "affected_requirements": sorted(affected_reqs),
            "affected_modules": sorted(affected_modules),
            "affected_tasks": sorted(affected_tasks),
            "affected_components": sorted(affected_components),
            "affected_apis": sorted(affected_apis),
            "affected_milestones": sorted(affected_milestones),
            "effort_hours_delta": round(effort_delta, 1)
        }

    def to_react_flow_graph(self, highlight_nodes: Optional[Set[str]] = None) -> Dict[str, Any]:
        """Convert entire traceability graph to layered React Flow nodes and edges."""
        nodes = []
        edges = []
        highlight_set = highlight_nodes or set()

        # Layout columns by tier
        tier_x = {
            "Stakeholder": 50,
            "Requirement": 280,
            "Module": 520,
            "Task": 760,
            "Component": 1000,
            "API": 1240,
            "Database": 1240,
            "Milestone": 1000
        }

        tier_counts = {}

        for node_id, data in self.graph.nodes(data=True):
            n_type = data.get("type", "Requirement")
            idx = tier_counts.get(n_type, 0)
            tier_counts[n_type] = idx + 1

            x = tier_x.get(n_type, 400)
            y = 50 + idx * 110

            is_highlighted = node_id in highlight_set

            nodes.append({
                "id": node_id,
                "type": "traceNode",
                "position": {"x": x, "y": y},
                "data": {
                    "id": node_id,
                    "label": f"{node_id}: {data.get('label', '')[:22]}",
                    "entityType": n_type,
                    "isHighlighted": is_highlighted,
                    "raw": data.get("data", {})
                }
            })

        for u, v, edata in self.graph.edges(data=True):
            is_edge_highlighted = u in highlight_set and v in highlight_set
            edges.append({
                "id": f"e-{u}-{v}",
                "source": u,
                "target": v,
                "label": edata.get("relation", ""),
                "animated": is_edge_highlighted,
                "style": {"stroke": "#f43f5e" if is_edge_highlighted else "#475569"}
            })

        return {"nodes": nodes, "edges": edges}


# Global singleton instance
traceability_service = TraceabilityGraphService()
