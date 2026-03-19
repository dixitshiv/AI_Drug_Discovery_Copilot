"""
Literature Agent
================
Fetches biomedical papers from PubMed and uses LangChain + Ollama (local LLM)
to extract gene/protein candidates relevant to a given disease query.
"""

import sys
import json
from typing import List
from pathlib import Path

from Bio import Entrez
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ENTREZ_EMAIL, ENTREZ_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL, MAX_PAPERS, MAX_GENES
from models.schemas import Paper, GeneEntry, LiteratureAgentOutput


# ── Setup ─────────────────────────────────────────────────────────────────────
Entrez.email = ENTREZ_EMAIL
if ENTREZ_API_KEY:
    Entrez.api_key = ENTREZ_API_KEY

# LangChain Ollama LLM (runs fully locally — no API key required)
llm = ChatOllama(
    base_url=OLLAMA_BASE_URL,
    model=OLLAMA_MODEL,
    temperature=0.1,
    format="json",          # ask Ollama to return JSON directly
)


# ── Step 1: Fetch papers from PubMed ─────────────────────────────────────────
def fetch_papers(disease: str, max_results: int = MAX_PAPERS) -> List[Paper]:
    """
    Search PubMed for papers related to the disease and return a list of Paper objects.
    """
    print(f"[Literature Agent] Searching PubMed for: '{disease}' ...")
    query = f"{disease}[Title/Abstract] AND (gene OR protein OR target OR mutation)[Title/Abstract]"

    handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results, sort="relevance")
    record = Entrez.read(handle)
    handle.close()

    pmids = record["IdList"]
    if not pmids:
        print("[Literature Agent] No papers found.")
        return []

    print(f"[Literature Agent] Found {len(pmids)} papers. Fetching abstracts ...")

    handle = Entrez.efetch(
        db="pubmed",
        id=",".join(pmids),
        rettype="abstract",
        retmode="xml"
    )
    records = Entrez.read(handle)
    handle.close()

    papers = []
    for article in records.get("PubmedArticle", []):
        try:
            medline = article["MedlineCitation"]
            art = medline["Article"]
            pmid = str(medline["PMID"])
            title = str(art.get("ArticleTitle", ""))

            abstract_obj = art.get("Abstract", {})
            abstract_text = abstract_obj.get("AbstractText", [""])
            if isinstance(abstract_text, list):
                abstract = " ".join(str(t) for t in abstract_text)
            else:
                abstract = str(abstract_text)

            author_list = art.get("AuthorList", [])
            authors = []
            for author in author_list:
                last = author.get("LastName", "")
                fore = author.get("ForeName", "")
                authors.append(f"{last} {fore}".strip())

            pub_date = art.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
            year = str(pub_date.get("Year", pub_date.get("MedlineDate", "")[:4] if "MedlineDate" in pub_date else ""))

            if title and abstract:
                papers.append(Paper(
                    pmid=pmid,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    year=year,
                ))
        except Exception as e:
            print(f"[Literature Agent] Warning: skipped a paper due to parse error: {e}")
            continue

    print(f"[Literature Agent] Successfully parsed {len(papers)} papers.")
    return papers


# ── Step 2: Extract genes via LangChain + Ollama ──────────────────────────────
def extract_genes_with_llm(disease: str, papers: List[Paper], max_genes: int = MAX_GENES) -> List[GeneEntry]:
    """
    Send paper abstracts to a local Ollama LLM via LangChain and extract gene/protein candidates.
    Returns a ranked list of GeneEntry objects.
    """
    # Build condensed corpus from abstracts
    corpus_parts = []
    for i, paper in enumerate(papers):
        corpus_parts.append(f"Paper {i+1} ({paper.year}): {paper.title}\n{paper.abstract[:500]}")
    corpus = "\n\n---\n\n".join(corpus_parts)

    system_prompt = """You are a biomedical AI assistant specializing in drug target identification.
Analyze research paper abstracts about a disease and extract the most relevant gene and protein targets.

For each gene/protein return a JSON object with these exact keys:
- name: gene symbol (e.g. KRAS, TP53, EGFR)
- full_name: full gene/protein name
- relevance_score: float between 0.0 and 1.0
- reasoning: 1-2 sentence explanation

Return ONLY a valid JSON object in this exact format:
{"genes": [ { "name": "...", "full_name": "...", "relevance_score": 0.0, "reasoning": "..." }, ... ]}"""

    user_prompt = f"""Disease: {disease}

Analyze these {len(papers)} paper abstracts and extract the top {max_genes} gene/protein drug targets, sorted by relevance_score descending.

{corpus}"""

    print(f"[Literature Agent] Sending {len(papers)} abstracts to Ollama ({OLLAMA_MODEL}) for gene extraction ...")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip markdown block formatting if present (common with Gemma/Mistral)
    if raw.startswith("```json"):
        raw = raw[7:]
    elif raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()

    # Parse JSON response
    try:
        parsed = json.loads(raw)
        # Handle both {"genes": [...]} and bare [...] formats
        if isinstance(parsed, dict):
            gene_list = parsed.get("genes", next(iter(parsed.values()), []))
        else:
            gene_list = parsed
    except json.JSONDecodeError as e:
        print(f"[Literature Agent] LLM returned invalid JSON: {e}")
        print(f"Raw response preview: {raw[:300]}")
        return []

    gene_entries = []
    for item in gene_list[:max_genes]:
        try:
            entry = GeneEntry(
                name=item["name"],
                full_name=item.get("full_name"),
                relevance_score=float(item.get("relevance_score", 0.5)),
                mentioned_in_papers=item.get("mentioned_in_papers", 1),
                reasoning=item.get("reasoning"),
            )
            gene_entries.append(entry)
        except Exception as e:
            print(f"[Literature Agent] Warning: skipped gene entry due to error: {e}")

    return sorted(gene_entries, key=lambda g: g.relevance_score, reverse=True)


# ── Main agent function ───────────────────────────────────────────────────────
def run(disease: str) -> LiteratureAgentOutput:
    """
    Run the full Literature Agent pipeline for a given disease.
    Returns a LiteratureAgentOutput with ranked gene candidates.
    """
    papers = fetch_papers(disease)
    if not papers:
        return LiteratureAgentOutput(disease=disease, papers_fetched=0, genes=[])

    genes = extract_genes_with_llm(disease, papers)
    return LiteratureAgentOutput(disease=disease, papers_fetched=len(papers), genes=genes)
