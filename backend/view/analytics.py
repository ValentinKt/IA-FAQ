"""
Blueprint pour les analytics et prédictions des visites
"""

from flask import Blueprint, render_template, jsonify, session, redirect, flash
from functools import wraps
from models import db
from utils.analytics_service import VisitAnalyticsService
import logging

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or not session.get('is_admin'):
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/admin/analytics')
@admin_required
def admin_analytics_dashboard():
    """Dashboard principal d'analytics"""
    try:
        analytics_service = VisitAnalyticsService()

        # Récupérer les statistiques
        stats = analytics_service.get_visit_stats(db.session)

        # Entraîner le modèle et obtenir les prédictions
        training_result = analytics_service.train_prediction_model(db.session)
        predictions = []
        insights = []

        if training_result.get('success'):
            predictions = analytics_service.predict_future_visits(7)
            insights = analytics_service.generate_insights(stats)

        return render_template('admin_analytics.html',
                             stats=stats,
                             predictions=predictions,
                             insights=insights,
                             training_result=training_result)

    except Exception as e:
        logger.error(f"Erreur dans le dashboard analytics: {e}")
        flash(f"Erreur lors du chargement des analytics: {str(e)}", "danger")
        return render_template('admin_analytics.html',
                             stats={},
                             predictions=[],
                             insights=[],
                             training_result={'success': False})

@analytics_bp.route('/api/analytics/stats')
@admin_required
def api_analytics_stats():
    """API pour récupérer les statistiques en JSON"""
    try:
        analytics_service = VisitAnalyticsService()
        stats = analytics_service.get_visit_stats(db.session)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erreur API analytics: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/predictions')
@admin_required
def api_analytics_predictions():
    """API pour récupérer les prédictions en JSON"""
    try:
        analytics_service = VisitAnalyticsService()

        # Entraîner le modèle
        training_result = analytics_service.train_prediction_model(db.session)

        if not training_result.get('success'):
            return jsonify({'error': training_result.get('message')}), 400

        predictions = analytics_service.predict_future_visits(7)

        return jsonify({
            'predictions': predictions,
            'training_result': training_result
        })

    except Exception as e:
        logger.error(f"Erreur API prédictions: {e}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/analytics/retrain', methods=['POST'])
@admin_required
def api_retrain_model():
    """API pour ré-entraîner le modèle de prédiction"""
    try:
        analytics_service = VisitAnalyticsService()
        result = analytics_service.train_prediction_model(db.session)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erreur ré-entraînement: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
