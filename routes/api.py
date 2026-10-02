from flask import Blueprint, request, jsonify, g
from models import db, Skill, CareerPath, User

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/theme', methods=['POST'])
def update_theme():
    data = request.get_json(silent=True) or request.form
    theme = data.get('theme', '').strip().lower()

    if theme not in ['light', 'dark']:
        return jsonify({'success': False, 'message': 'Invalid theme value'}), 400

    if g.user:
        g.user.theme_preference = theme
        db.session.commit()
        return jsonify({'success': True, 'theme': theme, 'synced_to_user': True})

    return jsonify({'success': True, 'theme': theme, 'synced_to_user': False})

@api_bp.route('/search')
def live_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'skills': [], 'roadmaps': []})

    skills = Skill.query.filter(
        (Skill.name.ilike(f'%{q}%')) | (Skill.description.ilike(f'%{q}%'))
    ).limit(5).all()

    roadmaps = CareerPath.query.filter(
        (CareerPath.name.ilike(f'%{q}%')) | (CareerPath.description.ilike(f'%{q}%'))
    ).limit(4).all()

    return jsonify({
        'skills': [{
            'name': s.name,
            'slug': s.slug,
            'category': s.category.name if s.category else '',
            'salary': s.salary_formatted,
            'url': f'/skills/{s.slug}'
        } for s in skills],
        'roadmaps': [{
            'name': r.name,
            'slug': r.slug,
            'duration': r.estimated_duration,
            'url': f'/roadmaps/{r.slug}'
        } for r in roadmaps]
    })
