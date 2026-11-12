# Building Regulations Assistant — Development Test Log

---

# Commit 001

## Git Commit #

001

---

## Commit Message

Implement local RAG assistant with semantic document retrieval and persistent embeddings

---

## Change Made

Developed the first working prototype of the Building Regulations Assistant using Retrieval-Augmented Generation (RAG).

The application now:

- Extracts text from Approved Document K using PyMuPDF.
- Generates document embeddings using `nomic-embed-text`.
- Stores embeddings locally using NumPy and page information using JSON.
- Converts user questions into embeddings and identifies the three most relevant pages using cosine similarity.
- Passes retrieved passages to a locally running Qwen 2.5 language model through Ollama.
- Generates answers with PDF page references.
- Reuses saved embeddings rather than regenerating them for every question.

The application is divided into two modules:

- `main.py` — Coordinates retrieval and answer generation.
- `retrieval.py` — Handles document extraction, indexing and semantic searching.

---

## Reason for Change

To develop an understanding of how AI applications are built using existing models, libraries and APIs.

The project demonstrates how RAG enables a language model to answer questions using external documents without retraining.

It forms the foundation for a future Revit-integrated Building Regulations compliance assistant, with automated model checking and a project-specific compliance register to support Building Regulations Principal Designer duties.

---

# Test Results

## Local LLM Integration

[x] PASS

Qwen 2.5 successfully runs locally through Ollama and responds to questions sent from Python using the Ollama API.

---

## Document Retrieval

[x] PASS

Approved Document K was successfully extracted and converted into searchable embeddings.

Test question:

*What is the minimum headroom required above stairs?*

The retrieval function identified:

- PDF page 17 — General stair headroom requirements.
- PDF page 18 — Reduced headroom for loft conversions.
- PDF page 15 — Related stair design guidance.

The most relevant page was correctly ranked first.

---

## Answer Generation

[~] PARTIAL PASS

Qwen successfully generated answers using the retrieved document information and identified the general 2m headroom guidance.

However, some answers incorrectly combined requirements from different paragraphs or included irrelevant information.

This demonstrates that successful retrieval does not guarantee accurate interpretation.

---

## Persistent Index

[x] PASS

The application successfully generates and saves document embeddings on the first run.

Subsequent runs load the existing index, avoiding repeated processing of unchanged documents.

---

## Overall Result

**First functional RAG prototype successfully completed.**

The application demonstrates the complete workflow:

```text
Approved Document K
        ↓
PDF Text Extraction
        ↓
Embedding Generation
        ↓
Saved Search Index
        ↓
Semantic Retrieval
        ↓
Local LLM (Qwen)
        ↓
Answer + Source References
```

The system operates locally without external AI API calls.

---

## Current Limitations

- Only Approved Document K is included.
- Documents are indexed by page rather than paragraph.
- Diagrams and complex tables may not be interpreted correctly.
- References use PDF page numbers rather than regulatory paragraph references.
- Generated answers are not always accurate.
- No automatic index updating or document version management.
- No interactive user interface.
- Compliance assessments require independent professional verification.

---

## Next Change / Hypothesis

Expand the assistant into a project-specific Building Regulations compliance tool.

Future development should introduce:

- All relevant Approved Documents, managed through a database.
- Improved document parsing and paragraph-level references.
- More reliable retrieval and answer verification.
- A project-specific compliance register recording issues, proposed solutions, regulatory references and review status.
- Integration with Revit through the Revit API/MCP.
- Automated identification of potential compliance issues using model information.

The longer-term objective is to support Building Regulations Principal Designer duties through structured compliance assessment, coordination and record-keeping.