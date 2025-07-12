# Ajout d'un blueprint Flask pour l'upload et la gestion des PDF (upload et listing).

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app, send_from_directory
import os
from werkzeug.utils import secure_filename
from models import db, PDFDocument, FAQ
import fitz  # PyMuPDF pour l'extraction de texte
from functools import wraps
from utils.ollama_rag import OllamaRAGService
from utils.task_manager import task_manager
import threading

# Création d'un blueprint Flask pour la gestion des PDF
pdf_bp = Blueprint('pdf', __name__)
# Définition du dossier où seront stockés les fichiers uploadés
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../uploads')
# Définition des extensions autorisées (ici uniquement PDF)
ALLOWED_EXTENSIONS = {'pdf'}

# Fonction utilitaire pour vérifier l'extension du fichier
def allowed_file(filename):
    # Vérifie que le nom contient un point et que l'extension est dans la liste autorisée
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route pour uploader un fichier PDF
@pdf_bp.route('/api/pdf/upload', methods=['POST'])
def upload_pdf():
    # Vérifie qu'un fichier a bien été envoyé dans la requête
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier envoyé.'}), 400
    file = request.files['file']
    # Vérifie que le nom du fichier n'est pas vide
    if file.filename == '':
        return jsonify({'error': 'Nom de fichier vide.'}), 400
    # Vérifie que le fichier existe et que son extension est autorisée
    if file and allowed_file(file.filename):
        # Sécurise le nom du fichier pour éviter les problèmes de chemin
        filename = secure_filename(file.filename)
        # Sauvegarde le fichier dans le dossier UPLOAD_FOLDER
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # Récupère une éventuelle description envoyée dans le formulaire
        description = request.form.get('description', '')
        # Crée une nouvelle entrée PDFDocument en base de données
        pdf_doc = PDFDocument(filename=filename, description=description)
        # Ajoute l'entrée en base de données et valide la transaction
        db.session.add(pdf_doc)
        db.session.commit()
        # Retourne une réponse JSON avec un message de succès et l'id du document
        return jsonify({'message': 'Fichier uploadé.', 'id': pdf_doc.id, 'filename': filename}), 201
    else:
        # Si le fichier n'est pas autorisé, retourne une erreur
        return jsonify({'error': 'Format de fichier non autorisé.'}), 400

# Route pour lister les PDF uploadés
@pdf_bp.route('/api/pdf', methods=['GET'])
def list_pdfs():
    # Récupère tous les documents PDF enregistrés en base
    pdfs = PDFDocument.query.all()
    # Retourne la liste des PDF sous forme de JSON
    return jsonify([
        {
            'id': pdf.id,
            'filename': pdf.filename,
            'upload_date': str(pdf.upload_date) if pdf.upload_date else None,
            'description': pdf.description
        } for pdf in pdfs
    ])

# Route pour extraire le texte d'un PDF par son id
@pdf_bp.route('/api/pdf/extract/<int:pdf_id>', methods=['GET'])
def extract_pdf_text(pdf_id):
    # Recherche le document PDF en base
    pdf_doc = PDFDocument.query.get_or_404(pdf_id)
    # Construit le chemin complet du fichier PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_doc.filename)
    # Vérifie que le fichier existe bien sur le disque
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'Fichier PDF introuvable sur le serveur.'}), 404
    # Ouvre le PDF et extrait le texte de chaque page
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    # Retourne le texte extrait sous forme de JSON
    return jsonify({'id': pdf_id, 'filename': pdf_doc.filename, 'text': text})

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect('/login')  # URL directe au lieu de url_for
        return f(*args, **kwargs)
    return decorated_function

@pdf_bp.route('/admin/pdfs')
@admin_required
def admin_pdf_list():
    try:
        pdfs = PDFDocument.query.order_by(PDFDocument.upload_date.desc()).all()
        print(f"DEBUG: Nombre de PDFs trouvés: {len(pdfs)}")  # Pour debug
        return render_template('admin_pdf_list.html', pdfs=pdfs)
    except Exception as e:
        print(f"DEBUG: Erreur dans admin_pdf_list: {e}")
        flash(f"Erreur lors du chargement des PDF: {str(e)}", "danger")
        return render_template('admin_pdf_list.html', pdfs=[])

@pdf_bp.route('/admin/pdfs/upload', methods=['GET', 'POST'])
@admin_required
def admin_pdf_upload():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            flash('Aucun fichier sélectionné.', 'danger')
            return render_template('admin_pdf_upload.html')

        file = request.files['pdf_file']
        if file.filename == '':
            flash('Aucun fichier sélectionné.', 'danger')
            return render_template('admin_pdf_upload.html')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Créer le dossier uploads s'il n'existe pas
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            description = request.form.get('description', '')
            pdf_doc = PDFDocument(filename=filename, description=description)
            db.session.add(pdf_doc)
            db.session.commit()

            flash('PDF uploadé avec succès.', 'success')
            return redirect(url_for('pdf.admin_pdf_list'))
        else:
            flash('Format de fichier non autorisé. Seuls les PDF sont acceptés.', 'danger')

    return render_template('admin_pdf_upload.html')

@pdf_bp.route('/admin/pdfs/delete/<int:pdf_id>', methods=['POST'])
@admin_required
def admin_delete_pdf(pdf_id):
    pdf_doc = PDFDocument.query.get_or_404(pdf_id)
    # Supprimer le fichier physique
    filepath = os.path.join(UPLOAD_FOLDER, pdf_doc.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    # Supprimer l'entrée en base
    db.session.delete(pdf_doc)
    db.session.commit()
    flash('PDF supprimé avec succès.', 'success')
    return redirect(url_for('pdf.admin_pdf_list'))

@pdf_bp.route('/admin/ia/generation')
@admin_required
def admin_ia_generation():
    """Interface de génération de FAQ par IA"""
    # Vérifier le statut d'Ollama
    rag_service = OllamaRAGService()
    ollama_status = rag_service.check_ollama_connection()
    current_model = rag_service.model if ollama_status else "Non disponible"

    # Récupérer les PDF disponibles
    pdfs = PDFDocument.query.order_by(PDFDocument.upload_date.desc()).all()

    # Récupérer les FAQ générées en attente (on pourrait ajouter un champ status plus tard)
    pending_faqs = []  # Pour l'instant, on peut utiliser les FAQ avec source='ia' récentes

    return render_template('admin_ia_generation.html',
                         ollama_status=ollama_status,
                         current_model=current_model,
                         pdfs=pdfs,
                         pending_faqs=pending_faqs)

# Fonction pour exécuter la génération en arrière-plan
def _generate_faq_background(task_id: str, pdf_path: str, pdf_filename: str):
    """Fonction pour générer les FAQ en arrière-plan"""
    from app import app  # Import local pour éviter les imports circulaires

    try:
        with app.app_context():  # Créer un contexte d'application Flask
            # Démarrer la tâche
            task_manager.start_task(task_id)
            task_manager.update_task(task_id, progress=10, message="Initialisation du service IA...")

            current_app.logger.info(f"Début génération background pour tâche {task_id}")

            # Initialiser le service RAG
            rag_service = OllamaRAGService()

            if not rag_service.check_ollama_connection():
                current_app.logger.error("Ollama non disponible")
                task_manager.fail_task(task_id, "Service IA non disponible")
                return

            task_manager.update_task(task_id, progress=20, message="Analyse du document PDF...")
            current_app.logger.info(f"Analyse du PDF: {pdf_path}")

            # Générer les FAQ
            generated_faqs = rag_service.process_pdf_to_faq(pdf_path)

            if not generated_faqs:
                current_app.logger.warning("Aucune FAQ générée")
                task_manager.fail_task(task_id, "Aucune FAQ générée à partir du document")
                return

            task_manager.update_task(task_id, progress=80, message="Sauvegarde des FAQ...")
            current_app.logger.info(f"Sauvegarde de {len(generated_faqs)} FAQ")

            # Sauvegarder les FAQ
            saved_count = 0
            for faq_data in generated_faqs:
                if faq_data.get('question') and faq_data.get('answer'):
                    faq = FAQ(
                        question=faq_data['question'],
                        answer=faq_data['answer'],
                        source='ia'
                    )
                    db.session.add(faq)
                    saved_count += 1

            db.session.commit()
            current_app.logger.info(f"FAQ sauvegardées avec succès: {saved_count}")

            # Terminer la tâche
            task_manager.complete_task(task_id, {
                'saved_count': saved_count,
                'pdf_filename': pdf_filename,
                'message': f'{saved_count} FAQ générées avec succès'
            })

    except Exception as e:
        current_app.logger.error(f"Erreur dans génération background: {e}", exc_info=True)
        task_manager.fail_task(task_id, str(e))

# Route API pour lancer la génération asynchrone
@pdf_bp.route('/api/ia/start-generation', methods=['POST'])
@admin_required
def api_start_generation():
    """Lance une génération de FAQ en arrière-plan"""
    try:
        pdf_id = request.json.get('pdf_id')
        if not pdf_id:
            return jsonify({'success': False, 'message': 'PDF ID manquant'}), 400

        pdf_doc = PDFDocument.query.get_or_404(pdf_id)
        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_doc.filename)

        if not os.path.exists(pdf_path):
            return jsonify({'success': False, 'message': 'Fichier PDF introuvable'}), 404

        # Créer une tâche
        task_id = task_manager.create_task(
            'generate_faq',
            pdf_id=pdf_id,
            pdf_filename=pdf_doc.filename
        )

        # Lancer la génération en arrière-plan
        thread = threading.Thread(
            target=_generate_faq_background,
            args=(task_id, pdf_path, pdf_doc.filename)
        )
        thread.daemon = True
        thread.start()

        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Génération lancée en arrière-plan'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Route API pour vérifier le statut d'une tâche
@pdf_bp.route('/api/ia/task-status/<task_id>', methods=['GET'])
@admin_required
def api_task_status(task_id):
    """Récupère le statut d'une tâche"""
    task = task_manager.get_task(task_id)

    if not task:
        return jsonify({'success': False, 'message': 'Tâche introuvable'}), 404

    return jsonify({
        'success': True,
        'task': {
            'id': task['id'],
            'status': task['status'],
            'progress': task['progress'],
            'message': task['message'],
            'result': task['result'],
            'error': task['error']
        }
    })

# Remplacer les anciennes routes par les nouvelles
@pdf_bp.route('/api/ia/generate-faq', methods=['POST'])
@admin_required
def api_generate_faq():
    """Redirection vers la nouvelle API asynchrone"""
    return api_start_generation()

@pdf_bp.route('/api/ia/process-faq', methods=['POST'])
@admin_required
def api_process_faq():
    """Route dépréciée - redirection vers le système de tâches"""
    return jsonify({
        'success': False,
        'message': 'Cette route est dépréciée. Utilisez /api/ia/start-generation'
    }), 410

# Route pour servir les fichiers PDF uploadés
@pdf_bp.route('/uploads/<filename>')
def serve_pdf(filename):
    """Servir les fichiers PDF uploadés"""
    try:
        # Vérifier que le fichier existe en base de données
        pdf_doc = PDFDocument.query.filter_by(filename=filename).first()
        if not pdf_doc:
            return "Fichier non trouvé", 404

        # Servir le fichier depuis le dossier uploads
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)
    except Exception as e:
        current_app.logger.error(f"Erreur lors du service du PDF {filename}: {e}")
        return "Erreur lors du chargement du fichier", 500
