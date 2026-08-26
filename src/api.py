"""
FastAPI Server for Enterprise Regulatory & Compliance RAG Copilot.
Provides endpoints for:
- Role-filtered query answering with strict citations
- Automated benchmark evaluation runs
- Document catalog inspection
- Health and guardrail telemetry
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field

from document_parser import RegulatoryDocumentParser
from vector_store import HybridRegulatoryStore
from rag_pipeline import GroundedRegulatoryRAGPipeline
from evaluator import run_rag_benchmark


app = FastAPI(
    title="Enterprise Regulatory Compliance RAG Copilot API",
    description="Role-aware, citation-grounded RAG assistant for banking policies, Basel III, DFAST, AML, and credit underwriting.",
    version="1.0.0"
)

# Global pipeline instance
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample_regulations")
parser = RegulatoryDocumentParser()
chunks = parser.parse_directory(DATA_DIR)
vector_store = HybridRegulatoryStore()
vector_store.index_chunks(chunks)
pipeline = GroundedRegulatoryRAGPipeline(vector_store)


class QueryRequest(BaseModel):
    query: str = Field(..., example="What is the minimum CET1 ratio under Basel III?")
    user_role: str = Field("JUNIOR_ANALYST", example="JUNIOR_ANALYST")
    top_k: int = Field(3, example=3)


class CitationItem(BaseModel):
    doc_id: str
    doc_title: str
    section: str
    clause: str
    classification: str
    citation_tag: str


class QueryResponse(BaseModel):
    query: str
    user_role: str
    answer: str
    groundedness_score: float
    status: str
    citations: List[CitationItem]
    pii_redacted: List[str]
    latency_ms: float


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "regulatory-copilot-rag-api",
        "indexed_chunks_count": len(vector_store.chunks),
        "supported_roles": list(vector_store.rbac_engine.permissions.keys())
    }


@app.post("/query", response_model=QueryResponse, tags=["RAG Inference"])
def ask_regulatory_question(req: QueryRequest):
    res = pipeline.query(req.query, user_role=req.user_role, top_k=req.top_k)
    return QueryResponse(
        query=req.query,
        user_role=req.user_role,
        answer=res["answer"],
        groundedness_score=res["groundedness_score"],
        status=res["status"],
        citations=res["citations"],
        pii_redacted=res.get("pii_redacted", []),
        latency_ms=res["latency_ms"]
    )


@app.post("/eval/benchmark", tags=["Evaluation"])
def execute_eval():
    eval_file = os.path.join(os.path.dirname(__file__), "..", "data", "eval_questions.json")
    results = run_rag_benchmark(eval_file, DATA_DIR)
    return results
