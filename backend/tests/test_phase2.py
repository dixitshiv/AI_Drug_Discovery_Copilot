"""
Tests for Phase 2 — UniProt Agent & Protein Structure Agent
Run with: pytest tests/ -v
"""

import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import GeneEntry, ProteinTarget, ProteinStructure, BindingPocket
from agents import uniprot_agent, structure_agent


# ── Fixtures ──────────────────────────────────────────────────────────────────
SAMPLE_GENES = [
    GeneEntry(name="KRAS", relevance_score=0.90),
    GeneEntry(name="TP53", relevance_score=0.80),
    GeneEntry(name="G12D", relevance_score=0.70),   # KRAS variant — should be normalised
    GeneEntry(name="RMC-7977", relevance_score=0.10), # drug compound — should fail UniProt
]

MOCK_UNIPROT_ENTRY = {
    "primaryAccession": "P01116",
    "proteinDescription": {
        "recommendedName": {"fullName": {"value": "GTPase KRas"}}
    },
    "organism": {"scientificName": "Homo sapiens"},
    "comments": [
        {"commentType": "FUNCTION", "texts": [{"value": "Plays a role in regulating cell division."}]}
    ],
    "keywords": [
        {"name": "Proto-oncogene"},
        {"name": "Disease variant"},
    ],
}

SAMPLE_TARGETS = [
    ProteinTarget(gene_name="KRAS", uniprot_id="P01116", combined_score=0.89, literature_score=0.90, druggability_score=0.60, is_druggable=True),
    ProteinTarget(gene_name="TP53", uniprot_id="P04637", combined_score=0.70, literature_score=0.80, druggability_score=0.50, is_druggable=True),
]


# ── UniProt Agent Tests ────────────────────────────────────────────────────────
class TestUniProtAgent:

    @patch("agents.uniprot_agent._search_uniprot")
    def test_kras_variant_normalised(self, mock_search):
        """G12D should be normalised to KRAS before UniProt lookup."""
        mock_search.return_value = MOCK_UNIPROT_ENTRY

        result = uniprot_agent.run(SAMPLE_GENES, top_k=5)
        names = [t.gene_name for t in result]
        # G12D should NOT appear as a separate entry
        assert "G12D" not in names
        assert "KRAS" in names

    @patch("agents.uniprot_agent._search_uniprot")
    def test_druggability_scored_correctly(self, mock_search):
        """Proto-oncogene + Disease variant keywords → high druggability."""
        mock_search.return_value = MOCK_UNIPROT_ENTRY
        genes = [GeneEntry(name="KRAS", relevance_score=0.9)]
        targets = uniprot_agent.run(genes, top_k=1)

        assert targets[0].is_druggable is True
        assert targets[0].druggability_score >= 0.5

    @patch("agents.uniprot_agent._search_uniprot")
    def test_unknown_gene_gets_penalised(self, mock_search):
        """Genes not found in UniProt should have a low combined score."""
        mock_search.return_value = None
        genes = [GeneEntry(name="RMC-7977", relevance_score=0.10)]
        targets = uniprot_agent.run(genes, top_k=1)

        assert targets[0].combined_score < 0.2
        assert targets[0].is_druggable is False

    @patch("agents.uniprot_agent._search_uniprot")
    def test_combined_score_formula(self, mock_search):
        """Combined score = 0.6 * lit_score + 0.4 * druggability_score."""
        mock_search.return_value = MOCK_UNIPROT_ENTRY
        genes = [GeneEntry(name="KRAS", relevance_score=1.0)]
        targets = uniprot_agent.run(genes, top_k=1)

        expected = round(0.6 * 1.0 + 0.4 * targets[0].druggability_score, 2)
        assert abs(targets[0].combined_score - expected) < 0.01

    @patch("agents.uniprot_agent._search_uniprot")
    def test_deduplication(self, mock_search):
        """Multiple KRAS variants should collapse to one KRAS entry."""
        mock_search.return_value = MOCK_UNIPROT_ENTRY
        genes = [
            GeneEntry(name="KRAS",  relevance_score=0.9),
            GeneEntry(name="G12D",  relevance_score=0.7),
            GeneEntry(name="G12V",  relevance_score=0.6),
        ]
        targets = uniprot_agent.run(genes, top_k=5)
        kras_entries = [t for t in targets if t.gene_name == "KRAS"]
        assert len(kras_entries) == 1


# ── Structure Agent Tests ─────────────────────────────────────────────────────
class TestStructureAgent:

    @patch("agents.structure_agent.detect_pockets")
    @patch("agents.structure_agent.download_pdb")
    @patch("agents.structure_agent.search_pdb")
    def test_returns_structure_for_each_target(self, mock_search, mock_download, mock_pockets):
        mock_search.return_value = "6GOD"
        mock_download.return_value = "/tmp/6GOD.pdb"
        mock_pockets.return_value = [BindingPocket(pocket_id=1)]

        structures = structure_agent.run(SAMPLE_TARGETS)
        assert len(structures) == 2
        assert all(isinstance(s, ProteinStructure) for s in structures)

    @patch("agents.structure_agent.detect_pockets")
    @patch("agents.structure_agent.predict_with_esmfold")
    @patch("agents.structure_agent.download_pdb")
    @patch("agents.structure_agent.search_pdb")
    def test_esmfold_fallback_when_no_pdb(self, mock_search, mock_download, mock_esmfold, mock_pockets):
        """When PDB returns None, should fall back to ESMFold."""
        mock_search.return_value = None
        mock_download.return_value = None
        mock_esmfold.return_value = "/tmp/KRAS_esmfold.pdb"
        mock_pockets.return_value = [BindingPocket(pocket_id=1)]

        targets = [SAMPLE_TARGETS[0]]
        structures = structure_agent.run(targets)
        assert structures[0].source == "esmfold"
        assert structures[0].pdb_id is None

    @patch("agents.structure_agent.detect_pockets")
    @patch("agents.structure_agent.download_pdb")
    @patch("agents.structure_agent.search_pdb")
    def test_pdb_id_stored_correctly(self, mock_search, mock_download, mock_pockets):
        mock_search.return_value = "6GOD"
        mock_download.return_value = "/tmp/6GOD.pdb"
        mock_pockets.return_value = [BindingPocket(pocket_id=1)]

        structures = structure_agent.run([SAMPLE_TARGETS[0]])
        assert structures[0].pdb_id == "6GOD"
        assert structures[0].source == "pdb"
