from flask import Blueprint, render_template, request, g
from models import Skill, Bookmark
from services.recommendation_service import RecommendationService

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations', methods=['GET', 'POST'])
def index():
    # Pre-populate defaults from user profile if logged in
    default_interest = g.user.career_interest if (g.user and g.user.career_interest) else 'Web Development'
    default_experience = g.user.experience_level if (g.user and g.user.experience_level) else 'Beginner'

    selected_interest = request.form.get('career_interest', default_interest) if request.method == 'POST' else request.args.get('interest', default_interest)
    selected_experience = request.form.get('experience_level', default_experience) if request.method == 'POST' else request.args.get('experience', default_experience)
    
    if request.method == 'POST':
        selected_skills = request.form.getlist('current_skills')
    else:
        selected_skills = request.args.getlist('current_skills')

    # Fetch recommendations
    recommendations = RecommendationService.get_recommendations(
        career_interest=selected_interest,
        experience_level=selected_experience,
        current_skills=selected_skills,
        limit=8
    )

    all_common_skills = Skill.query.order_by(Skill.demand_score.desc()).limit(16).all()

    # User bookmarked skills
    bookmarked_skill_ids = set()
    if g.user:
        bookmarked_skill_ids = set(
            b.skill_id for b in Bookmark.query.filter_by(user_id=g.user.id).all()
        )

    return render_template(
        'recommendations/index.html',
        recommendations=recommendations,
        selected_interest=selected_interest,
        selected_experience=selected_experience,
        selected_skills=selected_skills,
        all_common_skills=all_common_skills,
        bookmarked_skill_ids=bookmarked_skill_ids,
        has_submitted=(request.method == 'POST' or bool(request.args.get('interest')))
    )
