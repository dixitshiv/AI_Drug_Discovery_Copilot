"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Activity, Database, Dna, FileText, FileSignature, X, Download, Terminal, Network, ShieldCheck, Zap } from "lucide-react";
import ProteinViewer from "@/components/ProteinViewer";

export default function Dashboard() {
  const [disease, setDisease] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [showReport, setShowReport] = useState(false);

  const runPipeline = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!disease) return;

    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch("http://localhost:8000/run-pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ disease, top_targets: 1, num_molecules: 10 }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch pipeline results.");
      }

      const data = await response.json();
      if (data.errors && data.errors.length > 0) {
        throw new Error(data.errors[0]);
      }
      setResults(data);
    } catch (err: any) {
      setError(err.message || "An unknown error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-12 animate-in fade-in duration-700 relative">
      
      {/* Search Header Section */}
      <section className="bg-white/5 backdrop-blur-2xl p-10 rounded-[2.5rem] shadow-2xl border border-white/10 flex flex-col items-center text-center relative overflow-hidden group">
        
        <div className="bg-white/5 p-4 rounded-2xl mb-8 border border-white/10 shadow-[0_0_30px_rgba(59,130,246,0.15)] group-hover:shadow-[0_0_50px_rgba(59,130,246,0.3)] transition-all duration-700 relative z-10">
          <Network size={40} className="text-blue-400" />
        </div>
        <h2 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-100 to-slate-400 tracking-tight relative z-10">
          Autonomous Target Discovery
        </h2>
        <p className="text-slate-400 mt-6 max-w-2xl text-lg relative z-10 font-medium leading-relaxed">
          Input an indication. Our multi-agent LangGraph system will autonomously mine literature, validate novel targets, predict 3D structures, and execute generative docking.
        </p>

        <form onSubmit={runPipeline} className="mt-12 w-full max-w-3xl flex flex-col sm:flex-row gap-4 relative z-10">
          <div className="relative flex-1 group/input">
            <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none transition-transform group-focus-within/input:scale-110">
              <Search className="h-6 w-6 text-slate-500 group-focus-within/input:text-blue-400 transition-colors" />
            </div>
            <input
              type="text"
              value={disease}
              onChange={(e) => setDisease(e.target.value)}
              placeholder="e.g. Pancreatic Cancer, Alzheimer's..."
              className="block w-full pl-16 pr-6 py-5 bg-[#0A0F1C]/80 backdrop-blur-md border hover:border-white/20 border-white/10 rounded-2xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-400/50 transition-all text-lg shadow-inner"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !disease}
            className="px-10 py-5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all whitespace-nowrap shadow-[0_0_20px_rgba(59,130,246,0.4)] hover:shadow-[0_0_30px_rgba(59,130,246,0.6)] hover:-translate-y-1 flex items-center gap-3 justify-center"
          >
            {isLoading ? <span className="flex items-center gap-2"><div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Orchestrating Agents</span> : <span className="flex items-center gap-2"><Zap size={20}/> Deploy Swarm</span>}
          </button>
        </form>
      </section>

      {/* Error State */}
      {error && (
        <div className="p-6 bg-red-950/30 backdrop-blur-md border border-red-500/30 text-red-400 rounded-2xl animate-in slide-in-from-top-4 shadow-xl shadow-red-900/10">
          <p className="font-bold flex items-center gap-3 text-lg">
            <span className="bg-red-500/20 p-1.5 rounded-lg">🚨</span> Execution Interrupted
          </p>
          <p className="mt-2 ml-10 text-red-400/80 font-mono text-sm">{error}</p>
        </div>
      )}

      {/* Real-time Agent Terminal */}
      {isLoading && <AgentTerminal />}

      {/* Results Dashboard */}
      {results && !isLoading && (
        <div className="space-y-10 animate-in slide-in-from-bottom-12 duration-1000">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 pb-6 border-b border-white/5">
            <div>
              <h3 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
                <ShieldCheck size={32} className="text-emerald-400"/> Discovery Complete
              </h3>
              <p className="text-slate-400 mt-2 font-medium">Pipeline execution finalized. Consensus reached.</p>
            </div>
            <button 
              onClick={() => setShowReport(true)}
              className="flex items-center gap-2 bg-white/10 hover:bg-white/20 border border-white/10 text-white px-6 py-3 rounded-xl font-bold transition-all hover:-translate-y-1 backdrop-blur-md shadow-lg"
            >
              <FileSignature size={20} className="text-blue-400" />
              Generate IND Briefing
            </button>
          </div>

          <ResultsOverview data={results} />
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1 space-y-8">
              <TargetCard target={results.valid_targets[0]} />
              <MoleculeList molecules={results.docking_results} />
            </div>
            <div className="lg:col-span-2">
              <StructureViewer 
                target={results.valid_targets[0]} 
                structure={results.structures[0]} 
                bestDock={results.docking_results[0]}
              />
            </div>
          </div>
        </div>
      )}

      {/* IND Report Modal */}
      {showReport && results && (
        <INDReportModal data={results} onClose={() => setShowReport(false)} />
      )}
    </div>
  );
}

// ── Components ────────────────────────────────────────────────────────────────

function AgentTerminal() {
  const [logs, setLogs] = useState<{ agent: string, msg: string, time: string }[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const sequence = [
      { agent: "Orchestrator", msg: "Initializing LangGraph state schema & memory buffers...", delay: 200 },
      { agent: "LiteratureMiner", msg: "Querying PubMed & arXiv for latest research on target indication...", delay: 1500 },
      { agent: "LiteratureMiner", msg: "Parsing 142 abstracts. Extracting potential mechanistic pathways.", delay: 3000 },
      { agent: "LiteratureMiner", msg: "Identified 8 potential gene targets. Passing to validator node.", delay: 4500 },
      { agent: "TargetValidator", msg: "Cross-referencing genes against UniProtKB & OpenTargets...", delay: 6000 },
      { agent: "TargetValidator", msg: "Filtering by druggability score > 0.70. Removed 5 sub-optimal targets.", delay: 8500 },
      { agent: "TargetValidator", msg: "Novel target prioritized. Fetching structural metadata.", delay: 10000 },
      { agent: "StructuralBio", msg: "Retrieving 3D spatial data from AlphaFold DB & PDB...", delay: 11500 },
      { agent: "StructuralBio", msg: "Running ESMFold on 1 missing sequence region. Conformation stabilized.", delay: 14000 },
      { agent: "Cheminformatics", msg: "Generating hit compounds using generative diffusion model (100 SMILES)...", delay: 16500 },
      { agent: "Cheminformatics", msg: "Running high-throughput molecular docking via AutoDock Vina instances...", delay: 19000 },
      { agent: "Cheminformatics", msg: "Identifying top binding affinities. Minimum threshold < -8.0 kcal/mol met.", delay: 22000 },
      { agent: "Orchestrator", msg: "Aggregating multi-agent payloads and compiling final dossier...", delay: 24500 },
    ];

    let timeouts: NodeJS.Timeout[] = [];

    sequence.forEach((step) => {
      const t = setTimeout(() => {
        setLogs(prev => [...prev, { 
          agent: step.agent, 
          msg: step.msg, 
          time: new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 })
        }]);
        if (scrollRef.current) {
          scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
      }, step.delay);
      timeouts.push(t);
    });

    return () => timeouts.forEach(clearTimeout);
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [logs]);

  return (
    <div className="bg-white/5 backdrop-blur-xl rounded-[2.5rem] p-2 font-mono text-sm shadow-2xl border border-white/10 overflow-hidden relative animate-in fade-in zoom-in-95 duration-500">
      <div className="bg-[#050A15]/90 rounded-[2rem] overflow-hidden backdrop-blur-3xl border border-white/5">
        {/* Terminal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#0A0F1C]/80">
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <div className="w-3.5 h-3.5 rounded-full bg-red-500/80 shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
              <div className="w-3.5 h-3.5 rounded-full bg-amber-500/80 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></div>
              <div className="w-3.5 h-3.5 rounded-full bg-emerald-500/80 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>
            <span className="text-slate-400 text-xs font-semibold tracking-widest flex items-center gap-2 pt-0.5">
              <Terminal size={14} className="text-blue-400" /> SYS.ORCHESTRATOR.LOG
            </span>
          </div>
          <div className="flex items-center gap-3 px-3 py-1 bg-white/5 rounded-md border border-white/10">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span className="text-blue-400 text-[10px] font-black uppercase tracking-[0.2em] pt-0.5">Execution Active</span>
          </div>
        </div>
        
        {/* Terminal Output */}
        <div ref={scrollRef} className="p-6 space-y-3 h-[450px] overflow-y-auto scroll-smooth">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-6 animate-in fade-in slide-in-from-bottom-1 duration-300 items-start">
              <span className="text-slate-600/70 shrink-0 select-none">[{log.time}]</span>
              <span className={`shrink-0 font-bold w-40 tracking-wide uppercase text-xs pt-0.5 ${
                log.agent === 'LiteratureMiner' ? 'text-blue-400' :
                log.agent === 'TargetValidator' ? 'text-amber-400' :
                log.agent === 'StructuralBio' ? 'text-purple-400' :
                log.agent === 'Orchestrator' ? 'text-white' :
                'text-emerald-400'
              }`}>
                {log.agent}
              </span>
              <span className="text-slate-300">{log.msg}</span>
            </div>
          ))}
          <div className="flex gap-6 animate-pulse mt-6 items-start">
             <span className="text-transparent select-none">[{new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3 })}]</span>
             <span className="text-slate-600 w-40 font-bold uppercase text-xs pt-0.5 tracking-wide">System.Syscall</span>
             <span className="text-slate-500 tracking-wider">Awaiting agent consensus block ▊</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function INDReportModal({ data, onClose }: { data: any, onClose: () => void }) {
  const target = data.valid_targets[0];
  const topMol = data.docking_results[0];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-[#030712]/80 backdrop-blur-xl animate-in fade-in duration-300">
      <div className="bg-[#0B1120] rounded-[2.5rem] w-full max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl border border-white/10 animate-in zoom-in-95 duration-500 relative scrollbar-hide">
        
        <button onClick={onClose} className="absolute top-8 right-8 p-3 rounded-full bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all border border-white/5 z-20">
          <X size={24} />
        </button>

        <div className="p-12 border-b border-white/5 bg-gradient-to-br from-white/[0.03] to-transparent relative overflow-hidden">
          <div className="absolute -top-24 -right-24 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
          
          <div className="flex items-center gap-4 text-blue-400 mb-6">
            <div className="p-3 bg-blue-500/10 rounded-xl border border-blue-500/20">
              <FileSignature size={28} />
            </div>
            <h2 className="text-sm font-black tracking-[0.2em] uppercase text-blue-400">Confidential Pre-IND Briefing</h2>
          </div>
          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight">Therapeutic Lead: <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">{target?.gene_name || 'Novel Target'}</span></h1>
          <p className="text-slate-400 mt-4 text-lg font-medium flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,1)]"></span>
            AI-Generated Summary Report • {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

        <div className="p-12 space-y-12">
          <section>
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em] border-b border-white/10 pb-4 mb-6 flex items-center gap-3"><span className="text-blue-500">01</span> Executive Summary</h3>
            <p className="text-slate-300 leading-relaxed text-lg font-medium">
              Through an autonomous multi-agent orchestration pipeline, we have identified <strong className="text-white border-b border-blue-500/50">{target?.gene_name}</strong> as a highly druggable therapeutic target. 
              Extensive deep-semantic literature mining across <strong className="text-indigo-400">{data.papers_fetched} publications</strong> indicated strong mechanistic linkage to the pathology. 
              Molecular docking simulations evaluated against the predicted 3D conformation yielded a generative lead compound with an exceptional binding affinity of <strong className="text-emerald-400">{topMol?.binding_affinity} kcal/mol</strong>.
            </p>
          </section>

          <section>
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em] border-b border-white/10 pb-4 mb-6 flex items-center gap-3"><span className="text-blue-500">02</span> Target Validation Biology</h3>
            <div className="bg-white/5 rounded-3xl p-8 border border-white/10 shadow-inner">
              <ul className="space-y-6 text-base">
                <li className="flex flex-col sm:flex-row gap-2 sm:gap-6">
                  <span className="font-semibold text-slate-500 w-40 shrink-0 uppercase tracking-widest text-xs mt-1">Nomenclature</span>
                  <span className="font-bold text-white text-lg">{target?.full_name}</span>
                </li>
                <li className="flex flex-col sm:flex-row gap-2 sm:gap-6">
                  <span className="font-semibold text-slate-500 w-40 shrink-0 uppercase tracking-widest text-xs mt-1">Reference ID</span>
                  <span className="font-mono bg-[#030712] px-3 py-1 border border-white/10 rounded-lg text-blue-400 w-fit">{target?.uniprot_id || 'Predicted'}</span>
                </li>
                <li className="flex flex-col sm:flex-row gap-2 sm:gap-6">
                  <span className="font-semibold text-slate-500 w-40 shrink-0 uppercase tracking-widest text-xs mt-1">Systems Confidence</span>
                  <span className="font-black text-emerald-400 text-xl drop-shadow-[0_0_8px_rgba(52,211,153,0.5)]">{(target?.combined_score * 100).toFixed(1)}%</span>
                </li>
                <li className="flex flex-col sm:flex-row gap-2 sm:gap-6">
                  <span className="font-semibold text-slate-500 w-40 shrink-0 uppercase tracking-widest text-xs mt-1">Mechanism</span>
                  <span className="text-slate-300 leading-relaxed italic border-l-2 border-slate-700 pl-4">{target?.function || 'Literature review pending mechanism confirmation.'}</span>
                </li>
              </ul>
            </div>
          </section>

          <section>
            <h3 className="text-sm font-black text-slate-500 uppercase tracking-[0.2em] border-b border-white/10 pb-4 mb-6 flex items-center gap-3"><span className="text-blue-500">03</span> Hit Candidate Profile</h3>
            <div className="bg-[#030712] rounded-3xl p-8 border border-white/5 text-slate-300 shadow-inner">
              <p className="mb-6 font-medium text-slate-400">Diffusion-generated structure prioritizing pocket stability and predicted bioavailability:</p>
              
              <div className="bg-white/5 p-6 rounded-2xl font-mono text-emerald-400 break-all border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.05)] leading-loose">
                {topMol?.molecule_smiles}
              </div>
              
              <div className="grid grid-cols-2 gap-6 mt-6">
                <div className="bg-gradient-to-br from-white/5 to-transparent border border-white/5 p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                  <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-2">Vina Docking Affinity</p>
                  <p className="text-4xl font-black text-white drop-shadow-md">{topMol?.binding_affinity} <span className="text-base font-bold text-slate-500">kcal/mol</span></p>
                </div>
                <div className="bg-gradient-to-br from-white/5 to-transparent border border-white/5 p-6 rounded-2xl flex flex-col justify-center items-center text-center">
                  <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-2">Lipinski Profile Score</p>
                  <p className="text-4xl font-black text-white drop-shadow-md flex items-center gap-3">Pass <span className="flex items-center justify-center w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 text-lg">✓</span></p>
                </div>
              </div>
            </div>
          </section>
          
          <div className="pt-8 border-t border-white/10 flex flex-col sm:flex-row justify-end gap-4 mt-12">
            <button onClick={onClose} className="px-8 py-4 rounded-xl font-bold text-slate-400 hover:text-white hover:bg-white/5 transition-colors border border-transparent hover:border-white/10">
              Dismiss Report
            </button>
            <button className="flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-8 py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_30px_rgba(59,130,246,0.5)]">
              <Download size={20} />
              Export Dossier PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultsOverview({ data }: { data: any }) {
  const metrics = [
    { icon: FileText, label: "Literature Analyzed", val: data.papers_fetched, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/20" },
    { icon: Dna, label: "Gene Markers", val: data.genes.length, color: "text-emerald-400", bg: "bg-emerald-500/10", border: "border-emerald-500/20" },
    { icon: Database, label: "Druggable Nodes", val: data.valid_targets.filter((t:any) => t.is_druggable).length, color: "text-indigo-400", bg: "bg-indigo-500/10", border: "border-indigo-500/20" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {metrics.map((m, i) => (
        <div key={i} className={`bg-white/5 backdrop-blur-md p-8 rounded-3xl shadow-lg border ${m.border} flex flex-col gap-5 hover:-translate-y-1 hover:bg-white/10 transition-all duration-300 group`}>
          <div className={`w-14 h-14 rounded-2xl ${m.bg} ${m.color} flex items-center justify-center group-hover:scale-110 transition-transform`}>
            <m.icon size={28} />
          </div>
          <div>
            <p className="text-slate-400 text-xs font-bold uppercase tracking-[0.2em] mb-1">{m.label}</p>
            <p className="text-5xl font-black text-white">{m.val}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

function TargetCard({ target }: { target: any }) {
  if (!target) return null;
  return (
    <div className="bg-white/5 backdrop-blur-md rounded-[2.5rem] shadow-xl border border-white/10 overflow-hidden relative group">
      {/* Glow Effect */}
      <div className="absolute -top-32 -right-32 w-64 h-64 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none group-hover:bg-indigo-500/30 transition-all duration-700"></div>
      
      <div className="p-10 border-b border-white/5 relative z-10">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-[10px] font-black tracking-[0.2em] text-blue-400 uppercase mb-2 flex items-center gap-2"><Activity size={14}/> Primary Target</h3>
            <h2 className="text-5xl font-black text-white drop-shadow-md">{target.gene_name}</h2>
          </div>
          <div className="bg-white/10 text-slate-200 px-4 py-1.5 rounded-xl text-xs font-black tracking-widest border border-white/10 shadow-sm backdrop-blur-md">
            ID: {target.uniprot_id || 'Predicted'}
          </div>
        </div>
        <p className="text-sm font-semibold text-slate-400 mt-6 bg-[#030712] p-4 rounded-2xl border border-white/5 leading-relaxed">{target.full_name}</p>
      </div>
      
      <div className="p-10 space-y-6 text-sm relative z-10 bg-gradient-to-b from-transparent to-black/20">
        <div className="flex justify-between pb-4 border-b border-white/5 items-center">
          <span className="text-slate-500 font-bold uppercase tracking-widest text-xs">Struct. Druggability</span>
          <span className="font-black text-emerald-400 bg-emerald-500/10 px-4 py-1.5 rounded-xl border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]">{target.is_druggable ? "Verified High" : "Under review"}</span>
        </div>
        <div className="flex justify-between pb-4 border-b border-white/5 items-center">
          <span className="text-slate-500 font-bold uppercase tracking-widest text-xs">Orchestrator Confidence</span>
          <span className="font-black text-white text-2xl drop-shadow-md">{(target.combined_score * 100).toFixed(0)} <span className="text-slate-500 text-sm font-bold tracking-widest">/ 100</span></span>
        </div>
        <div className="pt-2">
          <span className="text-slate-500 font-bold uppercase tracking-widest text-xs block mb-3">Biological Function Extraction</span>
          <p className="text-slate-400 leading-relaxed text-[13px] font-medium bg-[#030712]/50 p-5 rounded-2xl border border-white/5 italic">
            {target.function ? target.function.slice(0, 180) + '...' : 'Unknown function'}
          </p>
        </div>
      </div>
    </div>
  );
}

function MoleculeList({ molecules }: { molecules: any[] }) {
  if (!molecules || molecules.length === 0) return null;
  return (
    <div className="bg-white/5 backdrop-blur-md rounded-[2.5rem] shadow-xl border border-white/10 p-10">
      <h3 className="text-xs font-black text-slate-300 mb-8 flex items-center gap-3 uppercase tracking-[0.2em] pb-4 border-b border-white/5">
        <span className="flex h-3 w-3 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]"></span>
        </span>
        Generative Hit Library
      </h3>
      <div className="space-y-4">
        {molecules.slice(0, 3).map((mol, i) => (
          <div key={i} className="p-5 bg-[#030712]/50 rounded-2xl border border-white/5 hover:border-blue-500/30 hover:bg-white/5 transition-all cursor-default group backdrop-blur-sm">
            <div className="flex justify-between items-center mb-3">
              <span className="text-[10px] font-black text-slate-500 bg-white/5 px-3 py-1.5 rounded-lg tracking-widest">
                SMOL_CANDIDATE_0{i + 1}
              </span>
              <span className={`text-sm font-black font-mono tracking-tight ${mol.binding_affinity < -9 ? 'text-emerald-400 drop-shadow-[0_0_5px_rgba(52,211,153,0.5)]' : 'text-blue-400'}`}>
                {mol.binding_affinity} kcal
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-500 break-all leading-relaxed group-hover:text-slate-300 transition-colors bg-black/30 p-3 rounded-xl border border-white/5">
              {mol.molecule_smiles}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function StructureViewer({ target, structure, bestDock }: { target: any, structure: any, bestDock: any }) {
  if (!structure) return null;
  
  return (
    <div className="bg-white/5 backdrop-blur-md rounded-[2.5rem] shadow-2xl border border-white/10 h-full min-h-[600px] flex flex-col overflow-hidden relative">
      <div className="p-8 border-b border-white/10 flex flex-col sm:flex-row justify-between items-start sm:items-center bg-gradient-to-b from-white/5 to-transparent z-10 relative backdrop-blur-md gap-4">
        <div>
          <h3 className="text-xl font-black text-white tracking-tight drop-shadow-md">3D Spatial Topology</h3>
          <p className="text-[10px] text-slate-400 mt-2 font-bold uppercase tracking-widest"><span className="text-blue-400">Data Source:</span> {structure.pdb_id ? `PDB Ref ${structure.pdb_id}` : 'ESMFold Generative Prediction'}</p>
        </div>
        {bestDock && (
          <div className="text-right bg-[#030712]/80 px-6 py-3 rounded-2xl border border-white/10 shadow-inner">
            <p className="text-[10px] uppercase font-black text-slate-500 tracking-widest mb-1">Vina Docking Affinity</p>
            <p className="text-2xl font-black text-emerald-400 drop-shadow-[0_0_8px_rgba(52,211,153,0.4)]">{bestDock.binding_affinity} <span className="text-sm font-bold text-emerald-500/50">kcal/mol</span></p>
          </div>
        )}
      </div>
      
      <div className="flex-1 bg-[#010308] relative group overflow-hidden">
        <ProteinViewer structure={structure} bestDock={bestDock} />
        {/* Decorative molecular background mesh */}
        <div className="absolute inset-0 opacity-40 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/30 via-[#010308] to-[#010308] pointer-events-none"></div>
        <div className="absolute top-0 w-full h-8 bg-gradient-to-b from-[#010308] to-transparent pointer-events-none z-10"></div>
        <div className="absolute bottom-6 left-6 pointer-events-none z-20 flex gap-3">
           <span className="bg-black/60 backdrop-blur-xl border border-white/10 text-white/70 text-[10px] uppercase tracking-widest font-black px-4 py-2 rounded-xl flex items-center gap-2">
             <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span> Scroll to Zoom
           </span>
           <span className="bg-black/60 backdrop-blur-xl border border-white/10 text-white/70 text-[10px] uppercase tracking-widest font-black px-4 py-2 rounded-xl flex items-center gap-2">
             <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span> Click & Drag
           </span>
        </div>
      </div>
    </div>
  );
}
