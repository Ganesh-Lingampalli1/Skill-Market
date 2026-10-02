from flask import Blueprint, render_template, request, g, abort
from models import Skill, Category, CareerPath, Bookmark, Resource

skills_bp = Blueprint('skills', __name__)

@skills_bp.route('/skills')
def explore():
    search_query = request.args.get('q', '').strip()
    category_slug = request.args.get('category', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    demand = request.args.get('demand', '').strip()
    sort_by = request.args.get('sort', 'popular').strip()

    query = Skill.query

    # Search filter
    if search_query:
        query = query.filter(
            (Skill.name.ilike(f'%{search_query}%')) |
            (Skill.description.ilike(f'%{search_query}%'))
        )

    # Category filter
    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    # Difficulty filter
    if difficulty and difficulty.lower() != 'all':
        query = query.filter(Skill.difficulty.ilike(difficulty))

    # Demand filter
    if demand and demand.lower() != 'all':
        query = query.filter(Skill.market_demand.ilike(f'%{demand}%'))

    # Sorting
    if sort_by == 'highest-demand' or sort_by == 'demand':
        query = query.order_by(Skill.demand_score.desc())
    elif sort_by == 'highest-salary' or sort_by == 'salary':
        query = query.order_by(Skill.salary_max.desc(), Skill.salary_min.desc())
    elif sort_by == 'beginner-friendly' or sort_by == 'beginner':
        # Custom ordering to put Beginner first
        query = query.order_by(
            db_case_difficulty(),
            Skill.demand_score.desc()
        )
    else: # popular / default
        query = query.order_by(Skill.trending.desc(), Skill.demand_score.desc())

    skills = query.all()
    categories = Category.query.all()

    # User bookmark IDs
    bookmarked_skill_ids = set()
    if g.user:
        bookmarked_skill_ids = set(
            b.skill_id for b in Bookmark.query.filter_by(user_id=g.user.id).all()
        )

    return render_template(
        'skills/explore.html',
        skills=skills,
        categories=categories,
        selected_category=selected_category,
        search_query=search_query,
        selected_difficulty=difficulty,
        selected_demand=demand,
        selected_sort=sort_by,
        bookmarked_skill_ids=bookmarked_skill_ids,
        total_count=len(skills)
    )

def db_case_difficulty():
    from sqlalchemy import case
    return case(
        (Skill.difficulty == 'Beginner', 1),
        (Skill.difficulty == 'Intermediate', 2),
        (Skill.difficulty == 'Advanced', 3),
        else_=4
    )

@skills_bp.route('/skills/<slug>')
def detail(slug):
    skill = Skill.query.filter_by(slug=slug).first_or_404()

    # Related skills in same category
    related_skills = Skill.query.filter(
        Skill.category_id == skill.category_id,
        Skill.id != skill.id
    ).limit(6).all()

    # Related career paths
    related_careers = CareerPath.query.filter(
        (CareerPath.category_id == skill.category_id) |
        (CareerPath.description.ilike(f'%{skill.name}%'))
    ).limit(4).all()

    # Learning resources categorized
    resources = Resource.query.filter_by(skill_id=skill.id).all()

    # User bookmark status
    is_bookmarked = False
    if g.user:
        is_bookmarked = Bookmark.query.filter_by(user_id=g.user.id, skill_id=skill.id).first() is not None

    return render_template(
        'skills/detail.html',
        skill=skill,
        related_skills=related_skills,
        related_careers=related_careers,
        resources=resources,
        is_bookmarked=is_bookmarked
    )
