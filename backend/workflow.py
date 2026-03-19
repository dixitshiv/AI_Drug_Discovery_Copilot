"""
LangGraph Orchestration Pipeline
================================
Defines the state and flow of the agents in the drug discovery pipeline 
using LangGraph.
"""

import sys
from pathlib import Path
from typing import TypedDict, List, Optional, Annotated
import operator

sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, START, END

from models.schemas import (
    GeneEntry, ProteinTarget, ProteinStructure, 
    DrugCandidate, DockingResult
)
from agents import literature_agent, uniprot_agent, structure_agent, molecule_agent, docking_agent


# ── 1. Define Graph State ─────────────────────────────────────────────────────
class AgentState(TypedDict):
    """The shared data state that passes between agents."""
    disease: str
    top_targets_count: int
    num_molecules: int
    
    # Accumulated data
    papers_fetched: int
    genes: List[GeneEntry]
    valid_targets: List[ProteinTarget]
    structures: List[ProteinStructure]
    raw_molecules: List[DrugCandidate]
    docking_results: List[DockingResult]
    
    # Error tracking
    errors: List[str]


# ── 2. Define Nodes (Agent Wrappers) ──────────────────────────────────────────

def run_literature_agent(state: AgentState):
    print("\n[LangGraph] ── Node: Literature Agent ──")
    try:
        result = literature_agent.run(state["disease"])
        return {
            "papers_fetched": result.papers_fetched,
            "genes": result.genes
        }
    except Exception as e:
        return {"errors": [f"LiteratureAgent failed: {e}"]}


def run_uniprot_agent(state: AgentState):
    print("\n[LangGraph] ── Node: UniProt Target Ranker ──")
    genes = state.get("genes", [])
    if not genes:
        return {"errors": ["No genes provided to UniProt agent"]}
        
    try:
        targets = uniprot_agent.run(genes, top_k=state.get("top_targets_count", 3))
        return {"valid_targets": targets}
    except Exception as e:
        return {"errors": [f"UniProtAgent failed: {e}"]}


def run_structure_agent(state: AgentState):
    print("\n[LangGraph] ── Node: Protein Structure Retrieval ──")
    targets = state.get("valid_targets", [])
    if not targets:
        return {"errors": ["No valid targets for Structure agent"]}
        
    try:
        # We only pass the top 1 target for structure+docking in this demo config
        structures = structure_agent.run([targets[0]])
        return {"structures": structures}
    except Exception as e:
        return {"errors": [f"StructureAgent failed: {e}"]}


def run_molecule_agent(state: AgentState):
    print("\n[LangGraph] ── Node: Molecule Generator ──")
    try:
        candidates = molecule_agent.run(num_molecules=state.get("num_molecules", 20))
        return {"raw_molecules": candidates}
    except Exception as e:
        return {"errors": [f"MoleculeAgent failed: {e}"]}


def run_docking_agent(state: AgentState):
    print("\n[LangGraph] ── Node: Docking Simulation ──")
    structures = state.get("structures", [])
    candidates = state.get("raw_molecules", [])
    
    if not structures or not candidates:
        return {"errors": ["Missing structures or candidates for Docking"]}
        
    try:
        results = docking_agent.run(structures[0], candidates, top_k=5)
        return {"docking_results": results}
    except Exception as e:
        return {"errors": [f"DockingAgent failed: {e}"]}


# ── 3. Build & Compile Graph ──────────────────────────────────────────────────

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("literature", run_literature_agent)
workflow.add_node("uniprot", run_uniprot_agent)
workflow.add_node("structure", run_structure_agent)
workflow.add_node("molecule", run_molecule_agent)
workflow.add_node("docking", run_docking_agent)

# Define edges (linear path)
workflow.add_edge(START, "literature")
workflow.add_edge("literature", "uniprot")
workflow.add_edge("uniprot", "structure")
workflow.add_edge("structure", "molecule")
workflow.add_edge("molecule", "docking")
workflow.add_edge("docking", END)

# Compile
app = workflow.compile()


def execute_pipeline(disease: str, top_targets: int = 3, num_molecules: int = 20) -> AgentState:
    """Helper function to run the compiled LangGraph pipeline."""
    
    initial_state = {
        "disease": disease,
        "top_targets_count": top_targets,
        "num_molecules": num_molecules,
        "papers_fetched": 0,
        "genes": [],
        "valid_targets": [],
        "structures": [],
        "raw_molecules": [],
        "docking_results": [],
        "errors": []
    }
    
    # Run the graph
    final_state = app.invoke(initial_state)
    return final_state
