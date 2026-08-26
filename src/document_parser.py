"""
Hierarchical Document Parsing and Chunking Engine for Banking Regulations.
Parses structured regulatory circulars into chunk nodes preserving:
- Document ID, Title, Classification/Sensitivity Tier
- Section and Clause Hierarchies
- Exact text blocks and regulatory formulas
"""

import os
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class RegulatoryChunk:
    chunk_id: str
    doc_id: str
    doc_title: str
    classification: str
    section: str
    clause: str
    content: str
    token_estimate: int


class RegulatoryDocumentParser:
    def __init__(self):
        pass

    def parse_markdown_file(self, file_path: str) -> List[RegulatoryChunk]:
        """
        Parses a banking regulatory markdown document into semantic clause-level chunks.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Extract frontmatter / header metadata
        doc_id_match = re.search(r"\*\*Document ID\*\*:\s*`([^`]+)`", raw_text)
        doc_id = doc_id_match.group(1) if doc_id_match else os.path.basename(file_path).replace(".md", "").upper()

        classification_match = re.search(r"\*\*Classification\*\*:\s*`([^`]+)`", raw_text)
        classification = classification_match.group(1) if classification_match else "INTERNAL_BANK_POLICY"

        title_match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
        doc_title = title_match.group(1).strip() if title_match else "Regulatory Standard"

        # Split into sections and clauses
        chunks = []
        sections = re.split(r"(?=^##\s+)", raw_text, flags=re.MULTILINE)

        chunk_idx = 1
        for sec in sections:
            if not sec.strip() or sec.startswith("# "):
                continue

            sec_title_match = re.search(r"^##\s+(.+)$", sec, re.MULTILINE)
            sec_title = sec_title_match.group(1).strip() if sec_title_match else "General Section"

            clauses = re.split(r"(?=^###\s+)", sec, flags=re.MULTILINE)
            for cl in clauses:
                if not cl.strip() or cl.startswith("## "):
                    continue

                cl_title_match = re.search(r"^###\s+(.+)$", cl, re.MULTILINE)
                cl_title = cl_title_match.group(1).strip() if cl_title_match else "Clause"

                clean_content = cl.strip()
                chunks.append(RegulatoryChunk(
                    chunk_id=f"{doc_id}_CHK_{chunk_idx:03d}",
                    doc_id=doc_id,
                    doc_title=doc_title,
                    classification=classification,
                    section=sec_title,
                    clause=cl_title,
                    content=clean_content,
                    token_estimate=len(clean_content.split())
                ))
                chunk_idx += 1

        return chunks

    def parse_directory(self, dir_path: str) -> List[RegulatoryChunk]:
        all_chunks = []
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    all_chunks.extend(self.parse_markdown_file(full_path))
        return all_chunks
