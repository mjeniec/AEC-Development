import pymupdf
import numpy as np
import json

from pathlib import Path
from ollama import embed


PDF_PATH = Path(__file__).resolve().parent / "Approved Documents" / "Approved_Document_K.pdf"

INDEX_FOLDER = Path(__file__).resolve().parent / "index"
EMBEDDINGS_FILE = INDEX_FOLDER / "embeddings.npy"
PAGES_FILE = INDEX_FOLDER / "pages.json"


def load_pages():
    pages = []

    with pymupdf.open(PDF_PATH) as document:
        for index, page in enumerate(document):
            text = page.get_text(sort=True)

            if text.strip():
                pages.append({
                    "pdf_page": index + 1,
                    "text": text
                })

    return pages


def load_or_create_index():

    INDEX_FOLDER.mkdir(exist_ok=True)

    # If saved embeddings exist, load them
    if EMBEDDINGS_FILE.exists() and PAGES_FILE.exists():

        print("Loading saved document index...")

        embeddings = np.load(EMBEDDINGS_FILE)

        with open(PAGES_FILE, "r", encoding="utf-8") as file:
            pages = json.load(file)

    # Otherwise, create the embeddings and save them
    else:

        print("Creating document index...")

        pages = load_pages()

        texts = [page["text"] for page in pages]

        embeddings = np.array(
            embed(model="nomic-embed-text", input=texts).embeddings
        )

        np.save(EMBEDDINGS_FILE, embeddings)

        with open(PAGES_FILE, "w", encoding="utf-8") as file:
            json.dump(pages, file, indent=2)

        print("Document index saved.")

    return pages, embeddings


def find_relevant_pages(question, pages, embeddings, top_k=3):

    question_vector = np.array(
        embed(model="nomic-embed-text", input=question).embeddings[0]
    )

    similarities = embeddings @ question_vector / (
        np.linalg.norm(embeddings, axis=1)
        * np.linalg.norm(question_vector)
    )

    best_indices = np.argsort(similarities)[-top_k:][::-1]

    return [pages[i] for i in best_indices]