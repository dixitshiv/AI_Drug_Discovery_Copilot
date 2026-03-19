from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ── Phase 1 models ────────────────────────────────────────────────────────────
class Paper(BaseModel):
    """A single PubMed paper."""
    pmid: str
    title: str
    abstract: str
    authors: List[str] = []
    year: Optional[str] = None


class GeneEntry(BaseModel):
    """A gene/protein candidate extracted from literature."""
    name: str = Field(..., description="Gene symbol, e.g. 'KRAS'")
    full_name: Optional[str] = None
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    mentioned_in_papers: int = 1
    reasoning: Optional[str] = None


class LiteratureAgentOutput(BaseModel):
    """Full output from the Literature Agent."""
    disease: str
    papers_fetched: int
    genes: List[GeneEntry]


# ── Phase 2 models ────────────────────────────────────────────────────────────
class ProteinTarget(BaseModel):
    """A validated protein target with metadata from UniProt."""
    gene_name: str = Field(..., description="Gene symbol, e.g. 'KRAS'")
    uniprot_id: Optional[str] = None
    full_name: Optional[str] = None
    organism: Optional[str] = None
    function: Optional[str] = None
    is_druggable: bool = False
    druggability_score: float = Field(default=0.0, ge=0.0, le=1.0)
    combined_score: float = Field(default=0.0, ge=0.0, le=1.0,
                                  description="Weighted combo of literature + druggability score")
    literature_score: float = Field(default=0.0, ge=0.0, le=1.0)


class BindingPocket(BaseModel):
    """A binding pocket on a protein structure."""
    pocket_id: int = 1
    center_x: Optional[float] = None
    center_y: Optional[float] = None
    center_z: Optional[float] = None
    volume: Optional[float] = None       # Å³
    druggability_score: Optional[float] = None


class ProteinStructure(BaseModel):
    """3D structure info for a protein target."""
    gene_name: str
    pdb_id: Optional[str] = None
    pdb_file_path: Optional[str] = None
    source: str = Field(default="pdb", description="'pdb' or 'esmfold'")
    resolution: Optional[float] = None   # Å (lower is better; PDB structures only)
    binding_pockets: List[BindingPocket] = []


class TargetRankerOutput(BaseModel):
    """Full output from Phase 2 (Target Ranker + Structure Module)."""
    disease: str
    targets: List[ProteinTarget]
    structures: List[ProteinStructure]


# ── Phase 3 models ────────────────────────────────────────────────────────────
class LipinskiMetrics(BaseModel):
    """Lipinski's Rule of 5 parameters."""
    mol_weight: float
    logp: float
    h_donors: int
    h_acceptors: int
    violations: int


class DrugCandidate(BaseModel):
    """A generated molecule candidate."""
    smiles: str
    metrics: LipinskiMetrics
    is_druggable: bool


class DockingResult(BaseModel):
    """Result of docking a DrugCandidate into a ProteinTarget."""
    gene_name: str
    molecule_smiles: str
    binding_affinity: float = Field(..., description="Docking score in kcal/mol (more negative = better)")
    pocket_id: int
    pose_file_path: Optional[str] = None


class DockingPipelineOutput(BaseModel):
    """Full output tying everything together."""
    disease: str
    target: ProteinTarget
    structure: ProteinStructure
    top_candidates: List[DockingResult]
