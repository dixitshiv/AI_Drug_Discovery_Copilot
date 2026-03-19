# AI Drug Discovery Co Pilot 🧬

An advanced, multi-agent pipeline orchestrated with LangGraph that autonomously executes early-stage drug discovery. By inputting a disease indication, the system dynamically mines biomedical literature, statistically validates novel target proteins, predicts 3D spatial structures, and executes generative molecular docking.

**Built with:** Python · LangGraph · OpenAI Models · Biopython · RDKit · FastAPI · Next.js 14 · TailwindCSS

---

## ✨ Features & Architecture

* **Autonomous Multi-Agent Swarm (LangGraph):** Sequential orchestration of specialized agents (LiteratureMiner, TargetValidator, StructuralBio, Cheminformatics).
* **Real-Time Agent Execution Terminal:** A beautiful Next.js interactive dashboard that streams the internal "thought process" and system calls of the agents.
* **Automated IND Briefing Generator:** Compiles multi-agent outputs into a professional, exportable Pre-IND (Investigational New Drug) dossier.
* **Architecture Visualization:** Interactive architectural topology maps showing state schema validation (via Pydantic) and data flow.
* **Dark Mode Glassmorphism UI:** Premium, enterprise-grade frontend designed exactly like modern Biotech AI startups.

---

## 📸 Demo & Screenshots

*(Replace these placeholders with your actual screenshots and video links!)*

**[ Insert Demo Video GIF Here ]**

* 🖥️ **[Insert Screenshot 1: The Dark Mode Agent Terminal running a pipeline]**
* 📊 **[Insert Screenshot 2: The Generated IND Briefing Modal with data]**
* 🧭 **[Insert Screenshot 3: The System Architecture Flowchart]**

---

## 🚀 Local Environment Setup

Since the project is divided into a LangGraph/FastAPI backend and a Next.js frontend, you need to run two terminal windows.

### 1. Start the Backend (FastAPI / LangGraph)

**Important:** Before starting, copy the `.env.example` file to create your own `.env` file. You must add your personal email address to `ENTREZ_EMAIL` inside the `.env` so the NCBI Entrez API grants the system access to biomedical literature.

```bash
cd backend
cp .env.example .env
# Edit .env and set ENTREZ_EMAIL=your.actual.email@example.com
```

Next, open a terminal and start the Python environment:

```bash
source venv/bin/activate
# If using Windows: venv\Scripts\activate

uvicorn api:app --reload --port 8000
```
*The backend API will now be listening on `http://localhost:8000` for requests from the frontend.*

### 2. Start the Frontend (Next.js Dashboard)

Open a **new** terminal window and navigate to the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

*The Next.js interactive UI will now be running on `http://localhost:3000`.*

**You're all set!** Open your browser to [http://localhost:3000](http://localhost:3000), enter a disease like "pancreatic cancer", and hit **Deploy Swarm**.

---

## 📂 Project Structure

```
project1/
├── backend/
│   ├── agents/                   # LangGraph node functions (Literature, UniProt, Docking etc.)
│   ├── models/                   # Pydantic data schemas
│   ├── data/                     # Downloaded structures & generated molecules
│   ├── api.py                    # FastAPI server
│   ├── workflow.py               # LangGraph compiled StateGraph
│   ├── config.py                 # Settings & API key loading
│   └── requirements.txt
├── frontend/
│   ├── src/app/                  # Next.js App Router (Dashboard & Architecture)
│   ├── src/components/           # StructuralBio 3DMol Viewers
│   ├── tailwind.config.ts        # Glassmorphism styling system
│   └── package.json
└── README.md                     # Setup instructions
```

---

## 📈 Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| **1 — Literature Agent** | ✅ Complete | PubMed search + LLM gene extraction |
| **2 — Target Ranking & Structures** | ✅ Complete | UniProt + PDB integration |
| **3 — Molecule Generation & Docking** | ✅ Complete | RDKit + Proxied Docking Score |
| **4 — LangGraph Orchestration** | ✅ Complete | Autonomous agent graph execution |
| **5 — Next.js Dashboard** | ✅ Complete | Interactive web UI with 3Dmol.js viewer |
| **6 — Portfolio Polish** | ✅ Complete | Real-time terminal, IND report modal, advanced Architecture mapping |

---

## 🧬 Key Concepts Tracker

Not from a biology background? Read [`biotech_primer.md`](./biotech_primer.md) for a plain-English explanation of the biochemical concepts and AI architectures used in this project.
