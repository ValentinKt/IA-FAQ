from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for, flash
from models import db, FAQ
from functools import wraps

faq_bp = Blueprint('faq', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes pour l'interface web (Jinja2)
@faq_bp.route('/', methods=['GET'])
@faq_bp.route('/faqs', methods=['GET'])
def faq_list():
    """Affiche la liste des FAQs avec une interface web moderne"""
    faqs = FAQ.query.order_by(FAQ.created_at.desc()).all()
    return render_template('faq_list.html', faqs=faqs)

@faq_bp.route('/faq/<int:faq_id>', methods=['GET'])
def faq_detail(faq_id):
    """Affiche les détails d'une FAQ spécifique"""
    faq = FAQ.query.get_or_404(faq_id)
    return render_template('faq_detail.html', faq=faq)

@faq_bp.route('/api/faq', methods=['GET'])
def get_faqs():
    faqs = FAQ.query.all()
    return jsonify([
        {
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'source': faq.source,
            'created_at': str(faq.created_at) if faq.created_at else None,
            'updated_at': str(faq.updated_at) if faq.updated_at else None
        } for faq in faqs
    ])

@faq_bp.route('/api/faq', methods=['POST'])
def create_faq():
    data = request.get_json()
    faq = FAQ(
        question=data.get('question'),
        answer=data.get('answer'),
        source=data.get('source', 'manuel')
    )
    db.session.add(faq)
    db.session.commit()
    return jsonify({
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'source': faq.source,
        'created_at': str(faq.created_at) if faq.created_at else None,
        'updated_at': str(faq.updated_at) if faq.updated_at else None
    }), 201

@faq_bp.route('/api/faq/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    return jsonify({
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'source': faq.source,
        'created_at': str(faq.created_at) if faq.created_at else None,
        'updated_at': str(faq.updated_at) if faq.updated_at else None
    })

@faq_bp.route('/api/faq/<int:faq_id>', methods=['PUT', 'PATCH'])
def update_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    data = request.get_json()
    if 'question' in data:
        faq.question = data['question']
    if 'answer' in data:
        faq.answer = data['answer']
    if 'source' in data:
        faq.source = data['source']
    db.session.commit()
    return jsonify({
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'source': faq.source,
        'created_at': str(faq.created_at) if faq.created_at else None,
        'updated_at': str(faq.updated_at) if faq.updated_at else None
    })

@faq_bp.route('/api/faq/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    return jsonify({'message': 'FAQ supprimée.'}), 204

@faq_bp.route('/admin/faqs', methods=['GET'])
@admin_required
def admin_faq_list():
    faqs = FAQ.query.order_by(FAQ.created_at.desc()).all()
    return render_template('admin_faq_list.html', faqs=faqs)

@faq_bp.route('/admin/faqs/add', methods=['GET', 'POST'])
@admin_required
def admin_add_faq():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        source = request.form.get('source', 'manuel')
        if not question or not answer:
            flash("Question et réponse requises.", "danger")
            return render_template('admin_faq_form.html')
        faq = FAQ(question=question, answer=answer, source=source)
        db.session.add(faq)
        db.session.commit()
        flash("Question ajoutée avec succès.", "success")
        return redirect(url_for('faq.admin_faq_list'))
    return render_template('admin_faq_form.html')

@faq_bp.route('/admin/faqs/edit/<int:faq_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        source = request.form.get('source', 'manuel')
        if not question or not answer:
            flash("Question et réponse requises.", "danger")
            return render_template('admin_faq_form.html', faq=faq, edit=True)
        faq.question = question
        faq.answer = answer
        faq.source = source
        db.session.commit()
        flash("Question modifiée avec succès.", "success")
        return redirect(url_for('faq.admin_faq_list'))
    return render_template('admin_faq_form.html', faq=faq, edit=True)

@faq_bp.route('/admin/faqs/delete/<int:faq_id>', methods=['POST'])
@admin_required
def admin_delete_faq(faq_id):
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash("Question supprimée avec succès.", "success")
    return redirect(url_for('faq.admin_faq_list'))
