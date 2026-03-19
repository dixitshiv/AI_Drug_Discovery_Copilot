"""
FastAPI Server for AI Drug Discovery Copilot
============================================
Exposes the LangGraph workflow via a REST API for the Next.js frontend.

Run with:
    fastapi dev api.py
    # or
    uvicorn api:app --reload --port 8000
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from workflow import execute_pipeline
from models.schemas import (
    GeneEntry, ProteinTarget, ProteinStructure, 
    DrugCandidate, DockingResult
)

app = FastAPI(title="AI Drug Discovery API")

# Allow Requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PipelineRequest(BaseModel):
    disease: str
    top_targets: int = 1
    num_molecules: int = 5


class PipelineResponse(BaseModel):
    disease: str
    papers_fetched: int
    genes: List[GeneEntry]
    valid_targets: List[ProteinTarget]
    structures: List[ProteinStructure]
    docking_results: List[DockingResult]
    errors: List[str] = []


@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Drug Discovery Copilot API is running."}


@app.post("/run-pipeline", response_model=PipelineResponse)
def run_pipeline(request: PipelineRequest):
    """
    Executes the full requested pipeline (Literature -> UniProt -> Structure -> Docking).
    This is a long-running synchronous request.
    """
    try:
        # Run the LangGraph state machine
        state = execute_pipeline(
            disease=request.disease,
            top_targets=request.top_targets,
            num_molecules=request.num_molecules
        )
        
        return PipelineResponse(
            disease=state["disease"],
            papers_fetched=state.get("papers_fetched", 0),
            genes=state.get("genes", []),
            valid_targets=state.get("valid_targets", []),
            structures=state.get("structures", []),
            docking_results=state.get("docking_results", []),
            errors=state.get("errors", [])
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{filename}")
def get_file(filename: str):
    """Serve PDB and PDBQT files from the data directory for the frontend viewer."""
    # Prevent path traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    # Check structures dir
    struct_path = Path(__file__).parent / "data" / "structures" / filename
    if struct_path.exists() and struct_path.is_file():
        return FileResponse(struct_path)
        
    # Check docking dir
    docking_path = Path(__file__).parent / "data" / "docking" / filename
    if docking_path.exists() and docking_path.is_file():
        return FileResponse(docking_path)
        
    raise HTTPException(status_code=404, detail="File not found")
