from flask import Blueprint, render_template, jsonify
from services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def index():
    overview = AnalyticsService.get_market_overview()
    chart_data = AnalyticsService.get_chart_data()
    return render_template('analytics/index.html', overview=overview, chart_data=chart_data)

@analytics_bp.route('/api/analytics/charts')
def chart_data_api():
    return jsonify(AnalyticsService.get_chart_data())
