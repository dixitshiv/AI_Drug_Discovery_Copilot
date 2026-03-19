"""
main.py — CLI entry point for the AI Drug Discovery Copilot
------------------------------------------------------------
Usage:
    python main.py --disease "pancreatic cancer"
    python main.py --disease "lung cancer" --output results.json --top-targets 5
"""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from workflow import execute_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="AI Drug Discovery Copilot (Powered by LangGraph)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --disease "pancreatic cancer"
  python main.py --disease "lung cancer" --top-targets 5 --output results.json
        """,
    )
    parser.add_argument("--disease", required=True, help='Disease to search for')
    parser.add_argument("--top-targets", type=int, default=3, help="Number of top targets (default: 3)")
    parser.add_argument("--num-molecules", type=int, default=20, help="Number of virtual molecules to generate (default: 20)")
    parser.add_argument("--output", default=None, help="Save results to JSON file")

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  AI Drug Discovery Copilot 🕸️ (LangGraph)")
    print(f"  Disease: {args.disease}")
    print(f"{'='*60}\n")

    # Run the LangGraph orchestration
    state = execute_pipeline(args.disease, args.top_targets, args.num_molecules)

    # Print final summary state
    print(f"\n{'='*60}")
    print("  Pipeline Execution Complete")
    print(f"{'='*60}\n")

    if state.get("errors"):
        print("⚠️ Pipeline finished with errors:")
        for error in state["errors"]:
            print(f"  - {error}")
        return

    # Print target summary
    targets = state.get("valid_targets", [])
    if targets:
        print(f"🏆 Top Target: {targets[0].gene_name} (Score: {targets[0].combined_score:.2f})")
    
    # Print structures
    structures = state.get("structures", [])
    if structures:
        tag = f"PDB: {structures[0].pdb_id}" if structures[0].pdb_id else "ESMFold Prediction"
        print(f"🧬 Structure : {tag}")
        
    # Print molecules
    molecules = state.get("raw_molecules", [])
    print(f"💊 Molecules : {len(molecules)} valid Lipinski-filtered candidates generated")

    # Print docking results
    results = state.get("docking_results", [])
    if results:
        print(f"\n🔗 Top Docked Candidate:")
        print(f"   SMILES  : {results[0].molecule_smiles}")
        print(f"   Affinity: {results[0].binding_affinity:.2f} kcal/mol")
        print(f"   Pose    : {results[0].pose_file_path}")

    # Save to JSON
    if args.output:
        # Convert Pydantic models to dicts for JSON serialization
        output_state = {
            "disease": state["disease"],
            "papers_fetched": state["papers_fetched"],
            "genes": [g.model_dump() for g in state["genes"]],
            "valid_targets": [t.model_dump() for t in state.get("valid_targets", [])],
            "structures": [s.model_dump() for s in state.get("structures", [])],
            "docking_results": [r.model_dump() for r in state.get("docking_results", [])]
        }
        with open(args.output, "w") as f:
            json.dump(output_state, f, indent=2)
        print(f"\nResults saved to: {args.output}\n")


if __name__ == "__main__":
    main()
