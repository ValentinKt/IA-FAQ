import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import fitz  # PyMuPDF
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np
from models.pdf_embedding import PDFEmbedding
from models import db

def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extrait le texte de chaque page d'un PDF et retourne une liste de textes (un par page).
    """
    texts = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            texts.append(page.get_text())
    return texts

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Découpe un texte en chunks de taille fixe avec un chevauchement.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks

def generate_embeddings(chunks: list[str]) -> list[np.ndarray]:
    """
    Génère les embeddings pour une liste de chunks de texte.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model.encode(chunks, show_progress_bar=True)

def save_embeddings_to_db(pdf_id: int, chunks: list[str], embeddings: list[np.ndarray], page_number: int):
    """
    Sauvegarde chaque chunk et son embedding dans la table PDFEmbedding.
    """
    for chunk, embedding in zip(chunks, embeddings):
        pdf_embedding = PDFEmbedding(
            pdf_id=pdf_id,
            chunk_text=chunk,
            embedding=embedding,
            page_number=page_number
        )
        db.session.add(pdf_embedding)
    db.session.commit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Indexation PDF : extraction, chunk, embeddings, sauvegarde en base")
    parser.add_argument('--pdf', type=str, required=True, help='Chemin du fichier PDF à indexer')
    parser.add_argument('--pdf_id', type=int, required=False, help="ID du PDF dans la base (optionnel)")
    parser.add_argument('--description', type=str, required=False, help="Description du PDF (optionnel)")
    args = parser.parse_args()

    pdf_path = args.pdf
    pdf_id = args.pdf_id
    description = args.description or ""

    if not os.path.exists(pdf_path):
        print(f"Fichier introuvable : {pdf_path}")
    else:
        from app import app  # Import local pour éviter le circular import
        from models.pdf_document import PDFDocument
        with app.app_context():
            if pdf_id is not None:
                pdf_doc = PDFDocument.query.get(pdf_id)
                if not pdf_doc:
                    pdf_doc = PDFDocument(id=pdf_id, filename=os.path.basename(pdf_path), description=description)
                    db.session.add(pdf_doc)
                    db.session.commit()
            else:
                pdf_doc = PDFDocument(filename=os.path.basename(pdf_path), description=description)
                db.session.add(pdf_doc)
                db.session.commit()
                pdf_id = pdf_doc.id
                print(f"Nouveau PDFDocument créé avec id={pdf_id}")
            pages = extract_text_from_pdf(pdf_path)
            for i, text in enumerate(pages):
                chunks = chunk_text(text)
                embeddings = generate_embeddings(chunks)
                save_embeddings_to_db(pdf_id, chunks, embeddings, i)
            print("Sauvegarde en base terminée.")
