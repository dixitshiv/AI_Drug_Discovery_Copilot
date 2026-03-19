"""
UniProt Agent
=============
Queries the UniProt REST API to validate and enrich gene/protein targets:
- Confirms the gene exists in humans
- Gets protein function, recommended name, and known druggability signals
"""

import sys
import requests
from typing import Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.schemas import GeneEntry, ProteinTarget

UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"


def _search_uniprot(gene_name: str) -> Optional[dict]:
    """
    Search UniProt for a human protein by gene name.
    Returns the top hit's JSON entry or None if not found.
    """
    params = {
        "query": f"gene:{gene_name} AND organism_id:9606 AND reviewed:true",
        "format": "json",
        "size": 1,
        "fields": "accession,gene_names,protein_name,organism_name,cc_function,keyword",
    }
    try:
        r = requests.get(f"{UNIPROT_BASE}/search", params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])
        return results[0] if results else None
    except requests.RequestException as e:
        print(f"[UniProt Agent] Warning: API error for '{gene_name}': {e}")
        return None


def _extract_druggability(entry: dict) -> bool:
    """
    Check UniProt keywords for druggability signals:
    disease involvement, pharmaceutical use, or enzyme activity.
    """
    keywords = [kw.get("name", "") for kw in entry.get("keywords", [])]
    druggable_signals = {
        "Disease variant", "Pharmaceutical", "Enzyme", "Kinase",
        "Protease", "Drug target", "Proto-oncogene",
    }
    return bool(druggable_signals.intersection(set(keywords)))


def _druggability_score(entry: dict) -> float:
    """
    Heuristic score (0–1) based on UniProt keywords.
    Each signal adds weight; capped at 1.0.
    """
    keywords = {kw.get("name", "") for kw in entry.get("keywords", [])}
    score = 0.0
    weights = {
        "Proto-oncogene": 0.35,
        "Disease variant": 0.25,
        "Pharmaceutical": 0.30,
        "Enzyme": 0.15,
        "Kinase": 0.20,
        "Protease": 0.15,
        "Drug target": 0.35,
    }
    for kw, w in weights.items():
        if kw in keywords:
            score += w
    return min(round(score, 2), 1.0)


def enrich_target(gene: GeneEntry) -> ProteinTarget:
    """
    Look up a gene in UniProt and return a ProteinTarget with enriched metadata.
    Falls back gracefully if the gene is not found or is not a valid human protein.
    """
    entry = _search_uniprot(gene.name)

    if entry is None:
        # Not found in UniProt — mark as low confidence
        return ProteinTarget(
            gene_name=gene.name,
            full_name=gene.full_name,
            is_druggable=False,
            druggability_score=0.0,
            literature_score=gene.relevance_score,
            combined_score=round(gene.relevance_score * 0.4, 2),  # penalise unknown genes
        )

    # Extract fields
    accession = entry.get("primaryAccession", "")
    protein_desc = entry.get("proteinDescription", {})
    recommended = protein_desc.get("recommendedName", {})
    full_name = recommended.get("fullName", {}).get("value", gene.full_name or gene.name)
    organism = entry.get("organism", {}).get("scientificName", "Homo sapiens")

    # Function comment
    comments = entry.get("comments", [])
    function_text = None
    for c in comments:
        if c.get("commentType") == "FUNCTION":
            texts = c.get("texts", [])
            if texts:
                function_text = texts[0].get("value", "")[:300]
                break

    druggable = _extract_druggability(entry)
    d_score = _druggability_score(entry)
    lit_score = gene.relevance_score

    # Combined score: 60% literature relevance + 40% druggability
    combined = round(0.6 * lit_score + 0.4 * d_score, 2)

    return ProteinTarget(
        gene_name=gene.name,
        uniprot_id=accession,
        full_name=full_name,
        organism=organism,
        function=function_text,
        is_druggable=druggable,
        druggability_score=d_score,
        literature_score=lit_score,
        combined_score=combined,
    )


def run(genes: list[GeneEntry], top_k: int = 5) -> list[ProteinTarget]:
    """
    Enrich all gene entries via UniProt, then return the top_k ranked targets
    by combined_score. Also de-duplicates KRAS variant entries (G12D, G12V, etc.)
    back to the parent gene.
    """
    print(f"[UniProt Agent] Enriching {len(genes)} gene candidates ...")

    # Normalise KRAS mutation variants (G12D, G12V, G12R, etc.) → KRAS
    normalised = []
    seen_names = set()
    for gene in genes:
        name = gene.name.upper()
        if name in {"G12D", "G12V", "G12R", "G12C", "G12S", "G13D"}:
            gene = gene.model_copy(update={"name": "KRAS"})
        if gene.name.upper() not in seen_names:
            seen_names.add(gene.name.upper())
            normalised.append(gene)

    # Enrich via UniProt
    targets = []
    for gene in normalised:
        print(f"[UniProt Agent] Looking up: {gene.name}")
        target = enrich_target(gene)
        targets.append(target)

    # Rank by combined score and return top_k
    ranked = sorted(targets, key=lambda t: t.combined_score, reverse=True)[:top_k]
    print(f"[UniProt Agent] Top {len(ranked)} targets selected.")
    return ranked
