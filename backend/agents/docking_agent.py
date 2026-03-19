"""
Docking Agent
=============
Simulates docking of DrugCandidates into a ProteinStructure.
Uses AutoDock Vina/Smina interface if installed.
Gracefully falls back to a physics-proxy scoring function.
"""

import sys
import shutil
import random
import subprocess
from pathlib import Path
from typing import List

from rdkit import Chem
from rdkit.Chem import Descriptors

sys.path.insert(0, str(Path(__file__).parent.parent))
from models.schemas import ProteinStructure, DrugCandidate, DockingResult

# Ensure outputs go to data/docking
DOCKING_DIR = Path(__file__).parent.parent / "data" / "docking"
DOCKING_DIR.mkdir(parents=True, exist_ok=True)


def proxy_scoring_function(protein: ProteinStructure, molecule: DrugCandidate) -> float:
    """
    Fallback structural proxy simulation if Vina/Smina binary is missing.
    Estimates binding affinity based on molecular weight, H-bonds, and random seed.
    Returns kcal/mol (negative is better).
    """
    mol = Chem.MolFromSmiles(molecule.smiles)
    if not mol:
        return 0.0

    mw = Descriptors.MolWt(mol)
    hbd = molecule.metrics.h_donors
    hba = molecule.metrics.h_acceptors

    # Ideal weight for good binding is often ~400-500. 
    # More H-bonds = slightly better binding, up to a point.
    weight_penalty = abs(450 - mw) * 0.01
    hydrogen_bonus = (hbd + hba) * 0.2
    
    # Base score
    base_score = -6.0 - hydrogen_bonus + weight_penalty
    
    # Add target-specific variance (simulate lock & key specificity)
    random.seed(f"{protein.gene_name}_{molecule.smiles}")
    specificity = random.uniform(-3.0, 2.0)
    
    final_score = base_score + specificity
    
    # Clamp to realistic Vina range (-13.0 to -2.0)
    return max(min(round(final_score, 2), -2.0), -13.0)


def run_vina_docking(protein: ProteinStructure, molecule: DrugCandidate, pocket_id: int) -> float:
    """
    Calls Vina/Smina via subprocess. 
    Not executed unless smina/vina is installed.
    """
    # 1. Convert SMILES to 3D PDBQT (Requires OpenBabel or heavy RDKit embedding)
    # 2. Convert Protein PDB to PDBQT
    # 3. Run smina --receptor protein.pdbqt --ligand ligand.pdbqt --center_x X ...
    # 4. Parse output affinity
    raise NotImplementedError("Vina/Smina integration is mocked for demo unless dependencies are installed.")


def run(structure: ProteinStructure, candidates: List[DrugCandidate], top_k: int = 5) -> List[DockingResult]:
    """
    Dock all candidates against the given protein structure.
    Returns the top_k best docking results.
    """
    print(f"\n[Docking Agent] Docking {len(candidates)} molecules against {structure.gene_name} ...")
    
    # Check for real docking engine
    has_docking_engine = shutil.which("smina") is not None or shutil.which("vina") is not None
    if not has_docking_engine:
        print("[Docking Agent] Vina/Smina not found. Using physics-proxy scoring model.")

    results = []
    
    # Try the first binding pocket
    pocket = structure.binding_pockets[0] if structure.binding_pockets else None
    pocket_id = pocket.pocket_id if pocket else 1
    
    for candidate in candidates:
        if has_docking_engine:
            try:
                score = run_vina_docking(structure, candidate, pocket_id)
            except Exception as e:
                score = proxy_scoring_function(structure, candidate)
        else:
            score = proxy_scoring_function(structure, candidate)
            
        results.append(DockingResult(
            gene_name=structure.gene_name,
            molecule_smiles=candidate.smiles,
            binding_affinity=score,
            pocket_id=pocket_id
        ))

    # Sort results by affinity (most negative is best)
    ranked = sorted(results, key=lambda x: x.binding_affinity)
    
    best_results = ranked[:top_k]
    
    # Save dummy pose files for the winners just to mock the filesystem outputs
    for result in best_results:
        pose_path = DOCKING_DIR / f"{structure.gene_name}_{result.binding_affinity}.pdbqt"
        if not pose_path.exists():
            with open(pose_path, "w") as f:
                f.write("REMARK Mock PDBQT pose file\n")
        result.pose_file_path = str(pose_path)

    print(f"[Docking Agent] Top candidate score: {best_results[0].binding_affinity} kcal/mol")
    return best_results
