"""
Tests for the Literature Agent — Phase 1 (LangChain + Ollama)
Run with: pytest tests/ -v
"""

import pytest
import json
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import Paper, GeneEntry, LiteratureAgentOutput
from agents import literature_agent


# ── Fixtures ──────────────────────────────────────────────────────────────────
SAMPLE_PAPERS = [
    Paper(
        pmid="12345",
        title="KRAS mutations in pancreatic cancer",
        abstract="KRAS is mutated in over 90% of pancreatic ductal adenocarcinoma cases. TP53 alterations are also common. Targeting KRAS G12C with small molecules shows promise.",
        authors=["Smith J", "Doe A"],
        year="2023",
    ),
    Paper(
        pmid="67890",
        title="TP53 tumor suppressor function in pancreatic cancer",
        abstract="TP53 loss-of-function mutations are found in ~70% of pancreatic cancers. SMAD4 is another frequently mutated gene in this cancer type.",
        authors=["Chen L"],
        year="2022",
    ),
]

SAMPLE_LLM_GENES = [
    {
        "name": "KRAS",
        "full_name": "Kirsten Rat Sarcoma Viral Proto-Oncogene",
        "relevance_score": 0.95,
        "reasoning": "KRAS is mutated in >90% of pancreatic cancers and is the primary oncogenic driver.",
    },
    {
        "name": "TP53",
        "full_name": "Tumor Protein P53",
        "relevance_score": 0.82,
        "reasoning": "TP53 mutations are present in ~70% of cases and are key to disease progression.",
    },
]


# ── Unit Tests ────────────────────────────────────────────────────────────────
class TestPaperModel:
    def test_paper_creation(self):
        paper = Paper(pmid="001", title="Test", abstract="Test abstract")
        assert paper.pmid == "001"
        assert paper.authors == []

    def test_paper_requires_pmid(self):
        with pytest.raises(Exception):
            Paper(title="No PMID", abstract="...")


class TestGeneEntry:
    def test_valid_gene_entry(self):
        gene = GeneEntry(name="KRAS", relevance_score=0.95)
        assert gene.name == "KRAS"
        assert gene.relevance_score == 0.95

    def test_relevance_score_bounds(self):
        with pytest.raises(Exception):
            GeneEntry(name="X", relevance_score=1.5)   # > 1.0 not allowed
        with pytest.raises(Exception):
            GeneEntry(name="X", relevance_score=-0.1)  # < 0.0 not allowed


class TestExtractGenesWithLLM:
    """Test LLM gene extraction step with mocked LangChain/Ollama calls."""

    @patch("agents.literature_agent.llm")
    def test_gene_extraction_returns_sorted_list(self, mock_llm):
        """Should return genes sorted by relevance_score descending."""
        mock_response = MagicMock()
        mock_response.content = json.dumps({"genes": SAMPLE_LLM_GENES})
        mock_llm.invoke.return_value = mock_response

        genes = literature_agent.extract_genes_with_llm("pancreatic cancer", SAMPLE_PAPERS)

        assert len(genes) == 2
        assert genes[0].name == "KRAS"
        assert genes[0].relevance_score > genes[1].relevance_score

    @patch("agents.literature_agent.llm")
    def test_gene_extraction_handles_bare_array(self, mock_llm):
        """LLM sometimes returns a bare JSON array instead of wrapped object."""
        mock_response = MagicMock()
        mock_response.content = json.dumps(SAMPLE_LLM_GENES)
        mock_llm.invoke.return_value = mock_response

        genes = literature_agent.extract_genes_with_llm("pancreatic cancer", SAMPLE_PAPERS)
        assert len(genes) == 2

    @patch("agents.literature_agent.llm")
    def test_gene_extraction_handles_bad_json(self, mock_llm):
        """Should return empty list if LLM returns invalid JSON."""
        mock_response = MagicMock()
        mock_response.content = "Sorry, I cannot help."
        mock_llm.invoke.return_value = mock_response

        genes = literature_agent.extract_genes_with_llm("some disease", SAMPLE_PAPERS)
        assert genes == []


class TestLiteratureAgentRun:
    """Integration-style tests for the full run() function."""

    @patch("agents.literature_agent.extract_genes_with_llm")
    @patch("agents.literature_agent.fetch_papers")
    def test_run_returns_output_model(self, mock_fetch, mock_extract):
        mock_fetch.return_value = SAMPLE_PAPERS
        mock_extract.return_value = [GeneEntry(name="KRAS", relevance_score=0.95)]

        result = literature_agent.run("pancreatic cancer")

        assert isinstance(result, LiteratureAgentOutput)
        assert result.disease == "pancreatic cancer"
        assert result.papers_fetched == 2
        assert result.genes[0].name == "KRAS"

    @patch("agents.literature_agent.fetch_papers")
    def test_run_handles_no_papers(self, mock_fetch):
        mock_fetch.return_value = []
        result = literature_agent.run("unknown disease xyz123")
        assert result.papers_fetched == 0
        assert result.genes == []
