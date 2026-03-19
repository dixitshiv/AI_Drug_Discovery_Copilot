"use client";

import { useEffect, useRef } from "react";

export default function ProteinViewer({ 
  structure, 
  bestDock 
}: { 
  structure: any; 
  bestDock: any;
}) {
  const viewerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // We must safely load 3Dmol since it requires the window/DOM
    const initViewer = async () => {
      if (typeof window === "undefined" || !viewerRef.current) return;
      
      // Grab the statically injected 3Dmol script from the window object
      // (avoiding Next.js Turbopack compiler bugs with the npm package)
      const $3Dmol = (window as any).$3Dmol;
      if (!$3Dmol) {
        console.error("3Dmol is not loaded on window.");
        return;
      }

      // Clear previous viewer
      viewerRef.current.innerHTML = "";
      
      const config = { backgroundColor: "#0f172a" }; // Match slate-900 
      const viewer = $3Dmol.createViewer(viewerRef.current, config);
      
      try {
        // 1. Fetch & Load Protein (PDB)
        const pdbFilename = structure.pdb_file_path.split("/").pop();
        const pdbRes = await fetch(`http://localhost:8000/files/${pdbFilename}`);
        if (pdbRes.ok) {
          const pdbData = await pdbRes.text();
          viewer.addModel(pdbData, "pdb");
          
          // Style protein: cartoon representation, blue-slate tint
          viewer.setStyle(
            {}, 
            { cartoon: { color: "spectrum", style: "oval", thickness: 0.2 } }
          );
        }

        // 2. Fetch & Load Docked Ligand (PDBQT)
        if (bestDock && bestDock.pose_file_path) {
          const ligandFilename = bestDock.pose_file_path.split("/").pop();
          const ligRes = await fetch(`http://localhost:8000/files/${ligandFilename}`);
          if (ligRes.ok) {
            const ligData = await ligRes.text();
            viewer.addModel(ligData, "pdbqt");
            
            // Style ligand: stick representation, bright emerald color for visibility
            viewer.setStyle(
              { model: 1 }, 
              { stick: { colorscheme: "greenCarbon", radius: 0.2 } }
            );
          }
        }

        // Center, zoom, and render
        viewer.zoomTo();
        viewer.render();
        
      } catch (err) {
        console.error("Error loading models into 3D viewer:", err);
      }
    };

    initViewer();
  }, [structure, bestDock]);

  return (
    <div 
      ref={viewerRef} 
      className="absolute inset-0 w-full h-full"
      style={{ position: "absolute" }}
    />
  );
}
