import requests
import json
import logging
from typing import List, Dict, Optional
import fitz  # PyMuPDF
import os

class OllamaRAGService:
    """Service pour l'intégration Ollama et le système RAG"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self.base_url = base_url
        self.model = model
        self.logger = logging.getLogger(__name__)

        # Vérifier si le modèle existe, sinon utiliser un modèle de fallback
        self._select_available_model()

    def _select_available_model(self):
        """Sélectionne un modèle disponible"""
        available_models = self.get_available_models()
        if self.model not in available_models:
            self.logger.warning(f"Modèle {self.model} non disponible")
            # Essayer des modèles plus petits (ordre de préférence par taille de RAM)
            fallback_models = ["gemma:2b", "phi3:mini", "llama3.2:1b", "llama3.1", "llama3", "phi"]
            for fallback in fallback_models:
                if fallback in available_models:
                    self.model = fallback
                    self.logger.info(f"Utilisation du modèle de fallback: {fallback}")
                    break
            else:
                self.logger.error("Aucun modèle compatible trouvé")
                # Utiliser le premier modèle disponible s'il y en a un
                if available_models:
                    self.model = available_models[0]
                    self.logger.info(f"Utilisation du premier modèle disponible: {self.model}")

    def check_ollama_connection(self) -> bool:
        """Vérifie si Ollama est accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Erreur de connexion à Ollama: {e}")
            return False

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        try:
            text = ""
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text() + "\n"
            return text.strip()
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du PDF {pdf_path}: {e}")
            return ""

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divise le texte en chunks pour le traitement"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Essayer de couper à la fin d'une phrase
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                cut_point = max(last_period, last_newline)
                if cut_point > start + chunk_size // 2:
                    chunk = text[start:cut_point + 1]
                    end = cut_point + 1

            chunks.append(chunk.strip())
            start = end - overlap if end < len(text) else end

        return chunks

    def generate_faq_from_text(self, text: str) -> List[Dict[str, str]]:
        """Génère des questions/réponses à partir d'un texte via Ollama"""
        if not self.check_ollama_connection():
            raise Exception("Ollama n'est pas accessible")

        # Prompt en français pour générer des FAQ en français
        prompt = f"""Génère 3 questions-réponses de FAQ à partir de ce texte sur des formations.

IMPORTANT: Réponds UNIQUEMENT en français.

Texte: {text[:1500]}

Formate ta réponse comme un tableau JSON en français:
[
  {{"question": "Qu'est-ce que...?", "answer": "Il s'agit de..."}},
  {{"question": "Comment faire pour...?", "answer": "Vous pouvez..."}}
]

Retourne seulement du JSON valide, aucun autre texte. Les questions et réponses doivent être en français."""

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "num_predict": 800
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')

                self.logger.info(f"Texte généré par Ollama: {generated_text[:200]}...")

                # Tenter de parser le JSON généré
                try:
                    # Nettoyer le texte généré
                    cleaned_text = generated_text.strip()

                    # Extraire le JSON du texte
                    start_idx = cleaned_text.find('[')
                    end_idx = cleaned_text.rfind(']')

                    if start_idx != -1 and end_idx != -1:
                        json_text = cleaned_text[start_idx:end_idx+1]
                        faq_list = json.loads(json_text)

                        # Valider que c'est bien une liste de dictionnaires
                        if isinstance(faq_list, list) and all(
                            isinstance(item, dict) and 'question' in item and 'answer' in item
                            for item in faq_list
                        ):
                            return faq_list

                    # Si parsing échoue, créer une FAQ par défaut
                    return [{
                        "question": "Quelles sont les informations importantes dans ce document ?",
                        "answer": generated_text[:500] + "..."
                    }]

                except json.JSONDecodeError as e:
                    self.logger.error(f"Erreur de parsing JSON: {e}")
                    self.logger.error(f"Texte généré: {generated_text}")

                    # Retourner une FAQ par défaut si parsing échoue
                    return [{
                        "question": "Contenu du document",
                        "answer": generated_text[:500] + "..." if generated_text else "Contenu non disponible"
                    }]
            else:
                self.logger.error(f"Erreur Ollama: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            self.logger.error(f"Erreur lors de la génération FAQ: {e}")
            return []

    def process_pdf_to_faq(self, pdf_path: str) -> List[Dict[str, str]]:
        """Pipeline complet : PDF -> Texte -> Chunks -> FAQ"""
        # Extraire le texte
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return []

        # Diviser en chunks plus petits pour économiser la mémoire
        chunks = self.chunk_text(text, chunk_size=1000)  # Réduire la taille des chunks

        all_faqs = []
        # Limiter à 2 chunks pour éviter les timeouts et économiser la mémoire
        max_chunks = min(2, len(chunks))

        for i, chunk in enumerate(chunks[:max_chunks]):
            self.logger.info(f"Traitement du chunk {i+1}/{max_chunks}")
            try:
                faqs = self.generate_faq_from_text(chunk)
                all_faqs.extend(faqs)

                # Libérer la mémoire après chaque chunk
                import gc
                gc.collect()

            except Exception as e:
                self.logger.error(f"Erreur sur le chunk {i+1}: {e}")
                continue

        return all_faqs

    def get_available_models(self) -> List[str]:
        """Récupère la liste des modèles disponibles dans Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
