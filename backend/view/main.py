"""
Blueprint pour les pages principales
"""
from flask import Blueprint, render_template, request
from models import FAQ

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil qui affiche l'interface FAQ"""
    faqs = FAQ.query.order_by(FAQ.created_at.desc()).all()
    return render_template('faq_list.html', faqs=faqs)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Page de contact"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        return render_template('contact.html', success=True, name=name)
    return render_template('contact.html')
