"""
Blueprint pour l'administration
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from models import User, FAQ, PDFDocument, VisitLog, AdminActionLog, db
from datetime import datetime, timedelta
from sqlalchemy import func
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Tableau de bord administrateur"""
    # Statistiques générales
    stats = {
        'total_faqs': FAQ.query.count(),
        'total_pdfs': PDFDocument.query.count(),
        'total_users': User.query.count(),
        'total_visits': VisitLog.query.count(),
        'manual_faqs': FAQ.query.filter_by(source='manuel').count(),
        'ia_faqs': FAQ.query.filter_by(source='ia').count()
    }

    # Statistiques des visites par période
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    stats['visits_today'] = VisitLog.query.filter(VisitLog.timestamp >= today).count()
    stats['visits_week'] = VisitLog.query.filter(VisitLog.timestamp >= week_ago).count()
    stats['visits_month'] = VisitLog.query.filter(VisitLog.timestamp >= month_ago).count()

    # Pages les plus visitées
    top_pages = db.session.query(
        VisitLog.url,
        func.count(VisitLog.id).label('count')
    ).group_by(VisitLog.url).order_by(func.count(VisitLog.id).desc()).limit(10).all()

    # Activité récente
    recent_faqs = FAQ.query.order_by(FAQ.created_at.desc()).limit(5).all()
    recent_pdfs = PDFDocument.query.order_by(PDFDocument.upload_date.desc()).limit(5).all()

    return render_template('admin_dashboard.html',
                         stats=stats,
                         top_pages=top_pages,
                         recent_faqs=recent_faqs,
                         recent_pdfs=recent_pdfs)

@admin_bp.route('/users')
@admin_required
def admin_users():
    """Liste des utilisateurs"""
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    """Ajouter un utilisateur"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin'))

        if not username or not password:
            flash("Nom d'utilisateur et mot de passe requis.", "danger")
            return render_template('admin_user_form.html')

        if User.query.filter_by(username=username).first():
            flash("Nom d'utilisateur déjà utilisé.", "danger")
            return render_template('admin_user_form.html')

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        flash("Utilisateur ajouté avec succès.", "success")
        return redirect(url_for('admin.admin_users'))

    return render_template('admin_user_form.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Modifier un utilisateur"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form.get('username')
        is_admin = bool(request.form.get('is_admin'))

        if not username:
            flash("Nom d'utilisateur requis.", "danger")
            return render_template('admin_user_form.html', user=user, edit=True)

        if User.query.filter(User.username == username, User.id != user.id).first():
            flash("Nom d'utilisateur déjà utilisé.", "danger")
            return render_template('admin_user_form.html', user=user, edit=True)

        user.username = username
        user.is_admin = is_admin

        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)

        db.session.commit()
        flash("Utilisateur modifié avec succès.", "success")
        return redirect(url_for('admin.admin_users'))

    return render_template('admin_user_form.html', user=user, edit=True)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Supprimer un utilisateur"""
    user = User.query.get_or_404(user_id)

    if user.id == session.get('user_id'):
        flash("Vous ne pouvez pas supprimer votre propre compte.", "danger")
        return redirect(url_for('admin.admin_users'))

    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé avec succès.", "success")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/logs')
@admin_required
def admin_logs():
    """Logs d'administration"""
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 50  # 50 visites par page

    # Statistiques
    total_visits = VisitLog.query.count()
    yesterday = datetime.utcnow() - timedelta(days=1)
    visits_today = VisitLog.query.filter(VisitLog.timestamp >= yesterday).count()

    # Récupération des logs avec pagination
    pagination = VisitLog.query.order_by(VisitLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    visits = pagination.items

    return render_template('admin_logs.html',
                         visits=visits,
                         pagination=pagination,
                         total_visits=total_visits,
                         visits_today=visits_today)
