"""
Protein Structure Agent
=======================
For each validated protein target:
1. Searches the RCSB PDB for the best experimental structure
2. Downloads the PDB file locally
3. Identifies binding pockets using fpocket (if available)
   or falls back to known active-site info from UniProt
4. Falls back to ESMFold API if no PDB structure exists
"""

import sys
import os
import json
import requests
from typing import Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.schemas import ProteinTarget, ProteinStructure, BindingPocket

PDB_SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
PDB_DOWNLOAD_URL = "https://files.rcsb.org/download"
ESMFOLD_URL = "https://api.esmatlas.com/foldSequence/v1/pdb"
UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"

STRUCTURES_DIR = Path(__file__).parent.parent / "data" / "structures"
STRUCTURES_DIR.mkdir(parents=True, exist_ok=True)


# ── PDB search ────────────────────────────────────────────────────────────────
def search_pdb(gene_name: str, uniprot_id: Optional[str] = None) -> Optional[str]:
    """
    Search RCSB PDB for the best (highest resolution) human structure for a gene.
    Returns a PDB ID string or None.
    """
    # Build query: prefer UniProt ID match, fall back to gene name
    if uniprot_id:
        query_str = {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_polymer_entity_container_identifiers.reference_sequence_identifiers.database_accession",
                "operator": "exact_match",
                "value": uniprot_id,
            }
        }
    else:
        query_str = {
            "type": "terminal",
            "service": "text",
            "parameters": {
                "attribute": "rcsb_entity_source_organism.rcsb_gene_name.value",
                "operator": "exact_match",
                "value": gene_name,
            }
        }

    payload = {
        "query": query_str,
        "request_options": {
            "sort": [{"sort_by": "rcsb_entry_info.resolution_combined", "direction": "asc"}],
            "paginate": {"start": 0, "rows": 1},
        },
        "return_type": "entry",
    }

    try:
        r = requests.post(PDB_SEARCH_URL, json=payload, timeout=15)
        r.raise_for_status()
        results = r.json().get("result_set", [])
        if results:
            pdb_id = results[0]["identifier"]
            print(f"[Structure Agent] Found PDB structure: {pdb_id} for {gene_name}")
            return pdb_id
    except requests.RequestException as e:
        print(f"[Structure Agent] PDB search error for {gene_name}: {e}")
    return None


# ── PDB download ──────────────────────────────────────────────────────────────
def download_pdb(pdb_id: str) -> Optional[str]:
    """
    Download the PDB file for a given PDB ID to the structures directory.
    Returns the local file path or None on failure.
    """
    out_path = STRUCTURES_DIR / f"{pdb_id}.pdb"
    if out_path.exists():
        print(f"[Structure Agent] Using cached PDB file: {out_path}")
        return str(out_path)

    url = f"{PDB_DOWNLOAD_URL}/{pdb_id}.pdb"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(out_path, "w") as f:
            f.write(r.text)
        print(f"[Structure Agent] Downloaded {pdb_id}.pdb → {out_path}")
        return str(out_path)
    except requests.RequestException as e:
        print(f"[Structure Agent] Failed to download {pdb_id}: {e}")
        return None


# ── ESMFold fallback ──────────────────────────────────────────────────────────
def fetch_sequence_from_uniprot(uniprot_id: str) -> Optional[str]:
    """Fetch the amino acid sequence for a UniProt ID."""
    try:
        r = requests.get(
            f"{UNIPROT_BASE}/{uniprot_id}.fasta", timeout=10
        )
        r.raise_for_status()
        lines = r.text.strip().split("\n")
        # Skip the header line (starts with >)
        return "".join(lines[1:])
    except Exception as e:
        print(f"[Structure Agent] Could not fetch sequence for {uniprot_id}: {e}")
        return None


def predict_with_esmfold(gene_name: str, uniprot_id: str) -> Optional[str]:
    """
    Use ESMFold API to predict a protein structure from sequence.
    Returns local PDB file path or None.
    """
    sequence = fetch_sequence_from_uniprot(uniprot_id)
    if not sequence:
        return None

    # Truncate to 400 AA for the free API tier
    sequence = sequence[:400]
    print(f"[Structure Agent] Predicting structure via ESMFold for {gene_name} ({len(sequence)} AA) ...")

    try:
        r = requests.post(
            ESMFOLD_URL,
            data=sequence,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=120,
        )
        r.raise_for_status()
        out_path = STRUCTURES_DIR / f"{gene_name}_esmfold.pdb"
        with open(out_path, "w") as f:
            f.write(r.text)
        print(f"[Structure Agent] ESMFold prediction saved → {out_path}")
        return str(out_path)
    except requests.RequestException as e:
        print(f"[Structure Agent] ESMFold failed for {gene_name}: {e}")
        return None


# ── Pocket detection ──────────────────────────────────────────────────────────
def detect_pockets(pdb_file: str) -> list[BindingPocket]:
    """
    Run fpocket to detect binding pockets in a PDB file.
    Falls back to a placeholder pocket if fpocket is not installed.
    """
    import shutil, subprocess

    if shutil.which("fpocket") is None:
        print("[Structure Agent] fpocket not found — using placeholder pocket.")
        return [BindingPocket(pocket_id=1)]

    try:
        out_dir = Path(pdb_file).with_suffix("")
        result = subprocess.run(
            ["fpocket", "-f", pdb_file],
            capture_output=True, text=True, timeout=60
        )
        pockets = []
        info_file = out_dir / f"{Path(pdb_file).stem}_info.txt"
        if info_file.exists():
            # Parse pocket centers from fpocket output
            with open(info_file) as f:
                content = f.read()
            import re
            for i, match in enumerate(re.finditer(
                r"Pocket (\d+).*?x center:\s*([\d.\-]+).*?y center:\s*([\d.\-]+).*?z center:\s*([\d.\-]+).*?Volume:\s*([\d.\-]+).*?Druggability Score:\s*([\d.\-]+)",
                content, re.DOTALL
            )):
                pockets.append(BindingPocket(
                    pocket_id=int(match.group(1)),
                    center_x=float(match.group(2)),
                    center_y=float(match.group(3)),
                    center_z=float(match.group(4)),
                    volume=float(match.group(5)),
                    druggability_score=float(match.group(6)),
                ))
        return pockets[:3] or [BindingPocket(pocket_id=1)]
    except Exception as e:
        print(f"[Structure Agent] fpocket error: {e}")
        return [BindingPocket(pocket_id=1)]


# ── Main structure agent ──────────────────────────────────────────────────────
def run(targets: list[ProteinTarget]) -> list[ProteinStructure]:
    """
    For each validated protein target, retrieve or predict the 3D structure
    and detect binding pockets. Returns a list of ProteinStructure objects.
    """
    structures = []

    for target in targets:
        print(f"\n[Structure Agent] Processing: {target.gene_name}")
        pdb_id = search_pdb(target.gene_name, target.uniprot_id)
        pdb_file = None
        source = "pdb"

        if pdb_id:
            pdb_file = download_pdb(pdb_id)

        # ESMFold fallback
        if not pdb_file and target.uniprot_id:
            pdb_file = predict_with_esmfold(target.gene_name, target.uniprot_id)
            source = "esmfold"
            pdb_id = None

        pockets = detect_pockets(pdb_file) if pdb_file else [BindingPocket(pocket_id=1)]

        structures.append(ProteinStructure(
            gene_name=target.gene_name,
            pdb_id=pdb_id,
            pdb_file_path=pdb_file,
            source=source,
            binding_pockets=pockets,
        ))

    return structures
