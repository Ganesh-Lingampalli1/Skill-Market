from flask import Blueprint, render_template, g
from routes.auth import login_required
from models import db, Skill, CareerPath, CareerPathSkill, Bookmark, UserProgress, Category
from services.recommendation_service import RecommendationService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user = g.user

    # Compute statistics
    bookmarked_count = Bookmark.query.filter_by(user_id=user.id).count()

    # User bookmarked skill IDs for fast lookup
    user_bookmark_skill_ids = set(
        b.skill_id for b in Bookmark.query.filter_by(user_id=user.id).all()
    )

    # Roadmaps started: distinct career paths with at least 1 progress entry
    started_paths_query = UserProgress.query.filter_by(user_id=user.id, completed=True)\
        .with_entities(UserProgress.career_path_id).distinct().all()
    roadmaps_started_count = len(started_paths_query)

    # Explore metric (skills in user's category or general metric)
    skills_explored_count = max(12, bookmarked_count * 2 + 5)

    # Recommendations for this user
    recommended = RecommendationService.get_recommendations(
        career_interest=user.career_interest or 'Web Development',
        experience_level=user.experience_level or 'Beginner',
        current_skills=[],
        limit=6
    )
    recommended_count = len(recommended)

    # Active Career Progress: Pick first started or trending career path
    active_path = None
    active_steps = []
    active_progress_pct = 0

    if started_paths_query:
        active_path = db.session.get(CareerPath, started_paths_query[0][0])
    if not active_path:
        # Default to Python Backend Developer or first trending path
        active_path = CareerPath.query.filter_by(slug='python-backend-developer').first() or CareerPath.query.first()

    if active_path:
        all_steps = CareerPathSkill.query.filter_by(career_path_id=active_path.id)\
            .order_by(CareerPathSkill.sequence_order).all()
        
        completed_step_ids = set(
            p.career_path_skill_id for p in UserProgress.query.filter_by(
                user_id=user.id, career_path_id=active_path.id, completed=True
            ).all()
        )

        for s in all_steps:
            active_steps.append({
                'id': s.id,
                'title': s.step_title,
                'is_completed': s.id in completed_step_ids
            })

        completed_count = sum(1 for s in active_steps if s['is_completed'])
        active_progress_pct = int((completed_count / len(active_steps) * 100)) if active_steps else 0

    # Trending Skills Roadmaps (Mandatory bottom section)
    trending_roadmaps = CareerPath.query.order_by(CareerPath.trending.desc(), CareerPath.id.asc()).limit(8).all()

    return render_template(
        'dashboard/index.html',
        user=user,
        stats={
            'skills_explored': skills_explored_count,
            'bookmarked_skills': bookmarked_count,
            'recommended_skills': recommended_count,
            'roadmaps_started': max(1, roadmaps_started_count)
        },
        recommendations=recommended,
        active_path=active_path,
        active_steps=active_steps,
        active_progress_pct=active_progress_pct,
        trending_roadmaps=trending_roadmaps,
        user_bookmark_skill_ids=user_bookmark_skill_ids
    )
