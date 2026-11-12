# Building Regulations Assistant

### Local AI Assistant Using Retrieval-Augmented Generation (RAG)

**Project:** AEC Development — Building Regulations Assistant  
**Language:** Python  
**Status:** Prototype — Version 0.1  
**Initial Document:** Approved Document K (England)

---

## 1. Project Overview

Building Regulations Assistant is a Python application that uses Retrieval-Augmented Generation (RAG) to answer questions about Building Regulations Approved Documents.

The assistant uses locally hosted AI models to search regulatory guidance, identify relevant passages and generate answers with source page references.

The application runs locally using Ollama, without requiring external AI API calls.

The initial prototype uses Approved Document K to demonstrate the principles of RAG, semantic search, local LLM integration and modular software architecture.

### Long-Term Objective

### BIM Integration and Building Regulations Compliance Management

Develop the Building Regulations Assistant into an AI-assisted compliance management tool integrated with Revit.

The application should support two complementary workflows:

**1. Automated Model Assessment**

- Query Revit model information through the Revit API and/or MCP.
- Identify elements and design conditions relevant to Building Regulations requirements.
- Retrieve applicable regulatory guidance using RAG.
- Undertake automated checks where requirements can be evaluated using model geometry and parameters.
- Highlight potential compliance issues within the Revit model.
- Provide relevant regulatory references and recommendations for further investigation.

**2. Project-Specific Compliance Assessment and Recording**

- Allow architects to ask Building Regulations questions relating to a particular project.
- Retrieve relevant guidance, including document editions and paragraph references.
- Support the investigation and resolution of identified compliance issues.
- Allow users to record compliance strategies and supporting design evidence.
- Link issues to relevant Revit elements, drawings, specifications and regulatory references.
- Maintain a project-specific Building Regulations Compliance Register.
- Track issues through identification, investigation, resolution and professional verification.
- Export the register as an Excel or PDF schedule.

The objective is to support the Building Regulations Principal Designer in coordinating, monitoring and documenting the design team's approach to regulatory compliance.

The system should maintain an auditable record of identified issues, design decisions, supporting evidence and professional review.

AI-generated assessments must remain advisory, with compliance decisions subject to verification by appropriately competent professionals.

---

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application development and workflow coordination |
| PyMuPDF | Extracting text from PDF documents |
| Ollama | Running and managing local AI models |
| Qwen 2.5 3B | Generating natural-language answers |
| nomic-embed-text | Generating semantic embeddings |
| NumPy | Storing vectors and calculating similarity |
| JSON | Storing extracted document text and page information |

All AI inference is performed locally.

---

## 3. System Architecture

The application has two main processes:

1. Document indexing
2. Question answering

### A. Document Indexing

Documents are processed and converted into searchable information.

```text
Approved Document K
        |
        v
PyMuPDF
Extracts PDF text
        |
        v
Document Pages
Text + Page Number
        |
        v
nomic-embed-text
Generates embeddings
        |
        v
Saved Index
embeddings.npy + pages.json
```

Each PDF page is currently treated as one searchable passage.

The embedding model converts page text into numerical vectors representing semantic information.

These vectors are saved locally, alongside the corresponding page text and references.

The index is created once and reused for subsequent questions.

### B. Question Answering

```text
User Question
      |
      v
nomic-embed-text
Question embedding
      |
      v
NumPy
Cosine similarity search
      |
      v
Top 3 Relevant Pages
      |
      v
Context + Question
      |
      v
Ollama API
      |
      v
Qwen 2.5
      |
      v
Generated Answer
+
Source Page References
```

The question is converted into an embedding using the same model used to index the documents.

The application compares the question vector against the saved document vectors using cosine similarity.

The three highest-ranking pages are retrieved and supplied to Qwen as context.

Qwen generates an answer using the supplied document information.

---

## 4. Python Application Structure

```text
BR_Assistant/
│
├── main.py
├── retrieval.py
├── README.md
├── .gitignore
│
├── Approved Documents/
│   └── Approved_Document_K.pdf
│
└── index/
    ├── embeddings.npy
    └── pages.json
```

The `Approved Documents` and `index` folders are excluded from GitHub through `.gitignore`.

### main.py

The main application controls the workflow.

Responsibilities:

1. Load the existing document index or create it if necessary.
2. Define the user's question.
3. Call the retrieval function.
4. Combine retrieved text into a context string.
5. Send the context and question to Qwen using Ollama's API.
6. Display the generated answer and source pages.

### retrieval.py

Contains three principal functions.

**`load_pages()`**

Opens Approved Document K using PyMuPDF.

Extracts the text from each page and stores it in dictionaries containing:

- PDF page number
- Extracted page text

Returns a list of page dictionaries.

**`load_or_create_index()`**

Checks whether saved index files exist.

If they exist, the function loads the saved page information and embeddings.

Otherwise, it:

1. Calls `load_pages()`.
2. Generates embeddings for the extracted pages.
3. Saves the embeddings using NumPy.
4. Saves page information using JSON.

Returns the pages and embeddings.

**`find_relevant_pages()`**

Receives:

- The user's question.
- The document pages.
- The saved document embeddings.

It generates an embedding for the question, calculates cosine similarity against the document embeddings and returns the three most relevant pages.

The number of retrieved pages is controlled by the `top_k` parameter.

---

## 5. Local AI Models

Two different AI models are used.

### Embedding Model — nomic-embed-text

Converts document text and user questions into numerical vectors.

Text with similar meanings tends to produce vectors with similar directions.

This enables semantic search rather than relying solely on exact keyword matches.

### Language Model — Qwen 2.5 3B

Receives the relevant document passages and the user's question.

Generates a natural-language answer based on the supplied context.

The language model is not trained or fine-tuned on the Building Regulations documents.

Instead, it receives the relevant information when answering each question.

This is the fundamental principle of Retrieval-Augmented Generation.

---

## 6. API Integration

Python communicates with Ollama through its local API.

The Ollama Python library provides the `chat()` and `embed()` functions.

These functions allow the application to request:

- Embeddings from `nomic-embed-text`.
- Generated answers from `qwen2.5:3b`.

Ollama runs the models locally and returns their outputs to Python.

The application uses a generation temperature of `0` to reduce variation between responses, although identical outputs are not guaranteed.

---

## 7. Running the Application

### Requirements

- Python
- Ollama
- PyMuPDF
- NumPy
- Ollama Python library

Install the required Python packages:

```powershell
python -m pip install pymupdf numpy ollama
```

Download the models:

```powershell
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Ensure Ollama is running.

Navigate to the project directory:

```powershell
cd "D:\WORK\AEC TECH\AEC Development\BR_Assistant"
```

Run:

```powershell
python main.py
```

On the first run, the application creates the document index.

Subsequent runs load the saved index rather than regenerating document embeddings.

The current question is defined directly in `main.py`.

---

## 8. Key Development Concepts

### Retrieval-Augmented Generation

RAG allows a language model to answer questions using retrieved external information without retraining the model.

### Embeddings

Embeddings are numerical vector representations of text used to compare semantic similarity.

### Indexing vs Querying

Indexing prepares source information for retrieval.

Querying searches the prepared index to identify relevant information.

Separating these processes avoids repeatedly processing unchanged documents.

### Modular Software Architecture

The application separates retrieval functionality from application coordination and answer generation.

This allows individual components to be improved or replaced independently.

### API Integration

The application uses Ollama's Python interface to communicate with locally running AI models.

### Model Evaluation

Retrieving the correct information does not guarantee that a language model will interpret it correctly.

Both retrieval quality and answer accuracy require testing.

---

## 9. Current Limitations

The initial prototype has several limitations.

**Document coverage**

Only Approved Document K is currently indexed.

**Document processing**

Each PDF page is treated as a single searchable passage.

Complex tables, diagrams and layouts may not be extracted accurately.

**References**

The assistant currently provides PDF page numbers rather than verified printed page and paragraph references.

**Answer accuracy**

The language model may incorrectly interpret regulatory requirements or combine information from unrelated paragraphs.

**Index management**

Changes to source documents or the embedding model do not automatically trigger index regeneration.

**User interface**

Questions are currently defined directly in Python rather than entered through a dedicated interface.

**Document versions**

The application does not yet manage different editions or amendments of Approved Documents.

**Validation**

No comprehensive automated accuracy evaluation has been implemented.

The prototype must not be relied upon for regulatory compliance decisions without independent verification.

---

## 10. Future Development

### Version 0.2 — Expanded Document Library

- Add all relevant Approved Documents for England.
- Introduce a database for document text, metadata and embeddings.
- Record document editions and amendments.
- Improve document chunking and paragraph identification.
- Introduce more reliable source references.

### Version 0.3 — Retrieval and Answer Quality

- Improve semantic retrieval.
- Investigate hybrid keyword and vector search.
- Evaluate alternative language models.
- Improve handling of diagrams and tables.
- Develop a test dataset of verified regulatory questions.
- Introduce automated evaluation of answer accuracy.

### Version 0.4 — Application Interface

- Introduce an interactive question-and-answer interface.
- Allow selection of documents and search scope.
- Display retrieved passages alongside generated answers.
- Provide direct links to relevant PDF pages.

### Version 0.5 — Revit Integration

- Integrate the assistant into the CRiT pyRevit extension.
- Allow users to search regulatory guidance directly from Revit.
- Investigate linking regulatory information to model elements.
- Explore future model-checking functionality.

---

## 11. Project Purpose

This project forms part of an ongoing programme of AEC technology development.

Its initial purpose is to develop a practical understanding of:

- AI application architecture
- Retrieval-Augmented Generation
- Semantic search and embeddings
- Local language models
- API integration
- Modular Python development
- Data storage and retrieval
- AI reliability and evaluation

The long-term objective is to apply these principles to digital delivery, BIM automation and the development of intelligent tools for architectural practice.