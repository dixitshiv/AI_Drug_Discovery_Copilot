import { Network, Server, Database, Microscope, Cpu, ArrowRight } from "lucide-react";

export default function ArchitecturePage() {
  return (
    <div className="space-y-16 animate-in fade-in slide-in-from-bottom-8 duration-1000 max-w-5xl mx-auto relative pt-4">
      {/* Background glow specific to architecture page */}
      <div className="fixed top-[20%] right-[10%] w-96 h-96 bg-purple-900/20 blur-[150px] rounded-full pointer-events-none z-0"></div>

      <div className="text-center space-y-6 relative z-10">
        <div className="inline-flex items-center justify-center p-5 bg-white/5 border border-white/10 rounded-3xl shadow-[0_0_30px_rgba(255,255,255,0.05)] mb-4">
          <Network size={48} className="text-blue-400" />
        </div>
        <h1 className="text-5xl md:text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-tight drop-shadow-sm">
          System Architecture
        </h1>
        <p className="text-slate-400 text-xl max-w-2xl mx-auto font-medium leading-relaxed">
          Deep dive into the LangGraph multi-agent orchestration dynamically powering the autonomous target discovery pipeline.
        </p>
      </div>

      {/* Main Flow Diagram */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[3rem] p-8 md:p-16 shadow-2xl relative overflow-hidden group">
        
        {/* Glows */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl -z-10 transform translate-x-1/2 -translate-y-1/2 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -z-10 transform -translate-x-1/2 translate-y-1/2 pointer-events-none"></div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 items-center relative z-10 text-center">
          
          {/* Node 1 */}
          <div className="md:col-span-1 flex flex-col items-center">
            <div className="w-28 h-28 bg-[#030712]/80 backdrop-blur-md border border-white/10 rounded-3xl shadow-[0_0_20px_rgba(59,130,246,0.2)] flex items-center justify-center text-blue-400 mb-6 z-10 hover:shadow-[0_0_30px_rgba(59,130,246,0.4)] hover:-translate-y-2 transition-all duration-300">
              <Server size={40} />
            </div>
            <h3 className="font-black text-white text-lg tracking-wide">LiteratureMiner</h3>
            <p className="text-sm text-slate-400 mt-3 font-medium px-2 leading-relaxed">Parallel scraping of PubMed & arXiv. RAG via vector DB.</p>
          </div>

          <div className="hidden md:flex justify-center text-slate-600">
             <ArrowRight size={32} className="animate-pulse" />
          </div>

          {/* Node 2 */}
          <div className="md:col-span-1 flex flex-col items-center">
            <div className="w-28 h-28 bg-[#030712]/80 backdrop-blur-md border border-white/10 rounded-3xl shadow-[0_0_20px_rgba(245,158,11,0.15)] flex items-center justify-center text-amber-400 mb-6 z-10 hover:shadow-[0_0_30px_rgba(245,158,11,0.3)] hover:-translate-y-2 transition-all duration-300">
              <Database size={40} />
            </div>
            <h3 className="font-black text-white text-lg tracking-wide">TargetValidator</h3>
            <p className="text-sm text-slate-400 mt-3 font-medium px-2 leading-relaxed">Cross-references UniProt API & assesses clinical druggability.</p>
          </div>

          <div className="hidden md:flex justify-center text-slate-600">
             <ArrowRight size={32} className="animate-pulse" />
          </div>

          {/* Node 3 */}
          <div className="md:col-span-1 flex flex-col items-center">
            <div className="w-28 h-28 bg-[#030712]/80 backdrop-blur-md border border-white/10 rounded-3xl shadow-[0_0_20px_rgba(168,85,247,0.2)] flex items-center justify-center text-purple-400 mb-6 z-10 hover:shadow-[0_0_30px_rgba(168,85,247,0.4)] hover:-translate-y-2 transition-all duration-300">
              <Microscope size={40} />
            </div>
            <h3 className="font-black text-white text-lg tracking-wide">StructuralBio</h3>
            <p className="text-sm text-slate-400 mt-3 font-medium px-2 leading-relaxed">PDB data ingestion & generative ESMFold sequencing.</p>
          </div>

        </div>

        {/* Second Row node */}
        <div className="mt-16 pt-16 border-t border-dashed border-white/10 grid grid-cols-1 md:grid-cols-3 gap-8 items-center relative z-10">
          <div className="md:col-span-3 flex flex-col items-center relative">
            {/* Connecting line vertical */}
            <div className="hidden md:block absolute w-0.5 h-16 bg-gradient-to-b from-slate-600 to-emerald-500/50 -top-16"></div>
            
            <div className="w-32 h-32 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-[2rem] shadow-[0_0_40px_rgba(16,185,129,0.3)] flex items-center justify-center text-white mb-8 z-10 hover:scale-105 hover:shadow-[0_0_60px_rgba(16,185,129,0.5)] transition-all duration-500 border border-emerald-400/50">
              <Cpu size={48} />
            </div>
            <h3 className="text-3xl font-black text-white tracking-tight">Cheminformatics Agent</h3>
            <p className="text-base text-slate-400 mt-4 max-w-2xl text-center font-medium leading-relaxed px-4">
              Utilizes stable generative diffusion models to synthesize 100+ hit candidate SMILES strings, followed by highly parallelized AutoDock Vina instances simulating binding affinities against active pocket sites.
            </p>
          </div>
        </div>

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-8">
        
        {/* Tech Stack Card */}
        <div className="bg-[#030712]/80 backdrop-blur-xl rounded-[2.5rem] p-12 text-slate-300 shadow-2xl border border-white/10 group hover:border-white/20 transition-all duration-500 relative overflow-hidden">
           <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none group-hover:bg-blue-500/20 transition-all duration-500"></div>
           <h3 className="text-2xl font-black text-white mb-8 tracking-wide">Technology Stack</h3>
           <ul className="space-y-6">
             <li className="flex items-center gap-4 border-b border-white/5 pb-4">
               <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center shadow-inner">
                 <span className="w-3 h-3 rounded-full bg-blue-400 shadow-[0_0_10px_rgba(96,165,250,0.8)]"></span>
               </div>
               <div>
                 <span className="block text-xs uppercase tracking-widest font-black text-slate-500 mb-1">Frontend Layer</span>
                 <strong className="text-lg font-bold text-white tracking-wide">React 18, TailwindCSS, 3Dmol</strong>
               </div>
             </li>
             <li className="flex items-center gap-4 border-b border-white/5 pb-4">
               <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shadow-inner">
                 <span className="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.8)]"></span>
               </div>
               <div>
                 <span className="block text-xs uppercase tracking-widest font-black text-slate-500 mb-1">Compute Backend</span>
                 <strong className="text-lg font-bold text-white tracking-wide">FastAPI, Python 3.11</strong>
               </div>
             </li>
             <li className="flex items-center gap-4 border-b border-white/5 pb-4">
               <div className="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center shadow-inner">
                 <span className="w-3 h-3 rounded-full bg-purple-400 shadow-[0_0_10px_rgba(192,132,252,0.8)]"></span>
               </div>
               <div>
                 <span className="block text-xs uppercase tracking-widest font-black text-slate-500 mb-1">Agent Orchestration</span>
                 <strong className="text-lg font-bold text-white tracking-wide">LangGraph, OpenAI Models</strong>
               </div>
             </li>
             <li className="flex items-center gap-4">
               <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shadow-inner">
                 <span className="w-3 h-3 rounded-full bg-amber-400 shadow-[0_0_10px_rgba(251,191,36,0.8)]"></span>
               </div>
               <div>
                 <span className="block text-xs uppercase tracking-widest font-black text-slate-500 mb-1">Bio/Chem Simulations</span>
                 <strong className="text-lg font-bold text-white tracking-wide">AutoDock Vina, Open Babel</strong>
               </div>
             </li>
           </ul>
        </div>
        
        {/* Schema Card */}
        <div className="bg-white/5 backdrop-blur-xl rounded-[2.5rem] p-12 text-slate-300 shadow-2xl border border-white/10 group hover:border-white/20 transition-all duration-500 relative overflow-hidden flex flex-col">
           <div className="absolute -top-24 -left-24 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none group-hover:bg-indigo-500/20 transition-all duration-500"></div>
           <h3 className="text-2xl font-black text-white mb-6 tracking-wide">Agent State Schema</h3>
           <p className="text-base leading-relaxed mb-8 font-medium text-slate-400">
             The immutable graph state passed sequentially between nodes in the LangGraph flow, strictly validated by Pydantic serializers:
           </p>
           <div className="flex-1 bg-[#010308] p-8 rounded-3xl border border-white/5 shadow-inner overflow-hidden relative group/code">
             <div className="absolute top-0 right-0 p-4 opacity-50"><Server size={18}/></div>
             <pre className="font-mono text-sm leading-8 text-blue-300 overflow-x-auto">
{`class GraphState(TypedDict):
    disease_query: str
    target_genes: List[str]
    validated_targets: List[TargetModel]
    pdb_structures: List[ProteinBlob]
    docked_candidates: List[SMILES_Score]
    current_agent: str
    errors: List[str]`}
             </pre>
           </div>
        </div>

      </div>
    </div>
  );
}
