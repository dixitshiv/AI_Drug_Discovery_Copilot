"""
Tests for Phase 3 — Molecule Agent & Docking Agent
Run with: pytest tests/ -v
"""

import pytest
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import DrugCandidate, ProteinStructure, BindingPocket, LipinskiMetrics
from agents import molecule_agent, docking_agent

# ── Fixtures ──────────────────────────────────────────────────────────────────
VALID_SMILES = "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5" # Imatinib
INVALID_SMILES = "INVALID_SMILES_STRING"

MOCK_PROTEIN = ProteinStructure(
    gene_name="KRAS",
    pdb_id="6GOD",
    binding_pockets=[BindingPocket(pocket_id=1, volume=100.0)]
)

MOCK_CANDIDATE = DrugCandidate(
    smiles=VALID_SMILES,
    metrics=LipinskiMetrics(mol_weight=493.6, logp=3.8, h_donors=2, h_acceptors=7, violations=0),
    is_druggable=True
)


# ── Molecule Agent Tests ──────────────────────────────────────────────────────
class TestMoleculeAgent:

    def test_calculate_lipinski_valid(self):
        metrics = molecule_agent.calculate_lipinski(VALID_SMILES)
        assert metrics.mol_weight > 0
        assert metrics.logp is not None
        assert metrics.h_donors >= 0
        assert metrics.h_acceptors >= 0
        assert metrics.violations == 0

    def test_calculate_lipinski_invalid_smiles(self):
        with pytest.raises(ValueError):
            molecule_agent.calculate_lipinski(INVALID_SMILES)

    def test_generate_library(self):
        smiles_list = molecule_agent.generate_library(5)
        assert len(smiles_list) <= 5
        assert len(smiles_list) > 0

    def test_run_molecule_agent(self):
        candidates = molecule_agent.run(num_molecules=5)
        # Should return a list of DrugCandidate models
        assert all(isinstance(c, DrugCandidate) for c in candidates)
        # All returned candidates should be druggable
        assert all(c.is_druggable for c in candidates)


# ── Docking Agent Tests ───────────────────────────────────────────────────────
class TestDockingAgent:

    def test_proxy_scoring_function(self):
        """Proxy should return a negative kcal/mol score within bounds."""
        score = docking_agent.proxy_scoring_function(MOCK_PROTEIN, MOCK_CANDIDATE)
        assert isinstance(score, float)
        assert -13.0 <= score <= -2.0

    def test_run_docking_agent(self):
        """Should return ranked DockingResult list."""
        candidates = [
            MOCK_CANDIDATE,
            DrugCandidate(
                smiles="CC1=CN=C(C(=N1)O)C2=CC=CC=C2", 
                metrics=LipinskiMetrics(mol_weight=200, logp=2, h_donors=1, h_acceptors=2, violations=0),
                is_druggable=True
            )
        ]
        
        results = docking_agent.run(MOCK_PROTEIN, candidates, top_k=2)
        assert len(results) == 2
        # First result should have a more negative (better) or equal affinity
        assert results[0].binding_affinity <= results[1].binding_affinity
        
        # Verify pose file path was assigned
        assert results[0].pose_file_path is not None
        assert "6GOD" not in results[0].pose_file_path  # Should use gene_name, not PDB ID
        assert "KRAS" in results[0].pose_file_path
