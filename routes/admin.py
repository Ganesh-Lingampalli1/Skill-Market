import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session, abort
from models import (
    db, User, Skill, Category, Resource, CareerPath,
    CareerPathSkill, RoadmapResource, Bookmark, UserProgress
)
from routes.auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user and g.user.is_admin:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()

        user = User.query.filter(
            (User.username.ilike(username)) & (User.email.ilike(email))
        ).first()

        if not user or not user.is_admin:
            flash("Invalid administrator credentials or not authorized.", "error")
            return render_template('admin/login.html', username=username, email=email)

        session.clear()
        session['user_id'] = user.id
        user.last_login = datetime.utcnow()
        db.session.commit()

        flash(f"Welcome to SkillMarket Administrator Console, {user.username}.", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'verified_users': User.query.filter_by(is_verified=True).count(),
        'total_skills': Skill.query.count(),
        'total_resources': Resource.query.count(),
        'total_roadmaps': CareerPath.query.count(),
        'total_bookmarks': Bookmark.query.count()
    }

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_skills = Skill.query.order_by(Skill.id.desc()).limit(5).all()
    categories = Category.query.all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_skills=recent_skills,
        categories=categories
    )

# --- SKILLS CRUD ---

@admin_bp.route('/skills', methods=['GET'])
@admin_required
def skills():
    q = request.args.get('q', '').strip()
    query = Skill.query
    if q:
        query = query.filter((Skill.name.ilike(f'%{q}%')) | (Skill.description.ilike(f'%{q}%')))
    skills_list = query.order_by(Skill.id.desc()).all()
    categories = Category.query.all()
    return render_template('admin/skills.html', skills=skills_list, categories=categories, q=q)

@admin_bp.route('/skills/add', methods=['POST'])
@admin_required
def add_skill():
    name = request.form.get('name', '').strip()
    category_id = request.form.get('category_id')
    description = request.form.get('description', '').strip()
    difficulty = request.form.get('difficulty', 'Beginner')
    demand_score = int(request.form.get('demand_score', 80))
    salary_min = int(request.form.get('salary_min', 4))
    salary_max = int(request.form.get('salary_max', 15))
    learning_duration = request.form.get('learning_duration', '6-8 weeks')
    market_demand = request.form.get('market_demand', 'High')
    trending = bool(request.form.get('trending'))

    if not name or not category_id:
        flash("Skill name and category are required.", "error")
        return redirect(url_for('admin.skills'))

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')

    skill = Skill(
        name=name,
        slug=slug,
        category_id=category_id,
        description=description,
        difficulty=difficulty,
        demand_score=demand_score,
        salary_min=salary_min,
        salary_max=salary_max,
        learning_duration=learning_duration,
        market_demand=market_demand,
        trending=trending
    )
    db.session.add(skill)
    db.session.commit()
    flash(f"Skill '{name}' added successfully.", "success")
    return redirect(url_for('admin.skills'))

@admin_bp.route('/skills/<int:id>/edit', methods=['POST'])
@admin_required
def edit_skill(id):
    skill = Skill.query.get_or_404(id)
    skill.name = request.form.get('name', skill.name).strip()
    skill.category_id = request.form.get('category_id', skill.category_id)
    skill.description = request.form.get('description', skill.description).strip()
    skill.difficulty = request.form.get('difficulty', skill.difficulty)
    skill.demand_score = int(request.form.get('demand_score', skill.demand_score))
    skill.salary_min = int(request.form.get('salary_min', skill.salary_min))
    skill.salary_max = int(request.form.get('salary_max', skill.salary_max))
    skill.learning_duration = request.form.get('learning_duration', skill.learning_duration)
    skill.market_demand = request.form.get('market_demand', skill.market_demand)
    skill.trending = bool(request.form.get('trending'))

    db.session.commit()
    flash(f"Skill '{skill.name}' updated successfully.", "success")
    return redirect(url_for('admin.skills'))

@admin_bp.route('/skills/<int:id>/delete', methods=['POST'])
@admin_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    name = skill.name
    db.session.delete(skill)
    db.session.commit()
    flash(f"Skill '{name}' deleted.", "info")
    return redirect(url_for('admin.skills'))

# --- RESOURCES CRUD ---

@admin_bp.route('/resources')
@admin_required
def resources():
    resources_list = Resource.query.order_by(Resource.id.desc()).all()
    skills = Skill.query.order_by(Skill.name).all()
    return render_template('admin/resources.html', resources=resources_list, skills=skills)

@admin_bp.route('/resources/add', methods=['POST'])
@admin_required
def add_resource():
    title = request.form.get('title', '').strip()
    skill_id = request.form.get('skill_id')
    res_type = request.form.get('type', 'Documentation')
    provider = request.form.get('provider', 'Official Docs').strip()
    url = request.form.get('url', '').strip()
    description = request.form.get('description', '').strip()
    is_free = bool(request.form.get('is_free'))

    if not title or not url:
        flash("Resource title and URL are required.", "error")
        return redirect(url_for('admin.resources'))

    res = Resource(
        title=title,
        skill_id=skill_id if skill_id else None,
        type=res_type,
        provider=provider,
        url=url,
        description=description,
        is_free=is_free
    )
    db.session.add(res)
    db.session.commit()
    flash(f"Resource '{title}' created successfully.", "success")
    return redirect(url_for('admin.resources'))

@admin_bp.route('/resources/<int:id>/delete', methods=['POST'])
@admin_required
def delete_resource(id):
    res = Resource.query.get_or_404(id)
    title = res.title
    db.session.delete(res)
    db.session.commit()
    flash(f"Resource '{title}' removed.", "info")
    return redirect(url_for('admin.resources'))

# --- ROADMAPS CRUD ---

@admin_bp.route('/roadmaps')
@admin_required
def roadmaps():
    roadmaps_list = CareerPath.query.order_by(CareerPath.id.desc()).all()
    categories = Category.query.all()
    skills = Skill.query.order_by(Skill.name).all()
    return render_template('admin/roadmaps.html', roadmaps=roadmaps_list, categories=categories, skills=skills)

@admin_bp.route('/roadmaps/add', methods=['POST'])
@admin_required
def add_roadmap():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category_id = request.form.get('category_id')
    difficulty = request.form.get('difficulty', 'Beginner → Advanced')
    demand_level = request.form.get('demand_level', 'High Demand')
    estimated_duration = request.form.get('estimated_duration', '6 months')
    average_salary = request.form.get('average_salary', '₹6L – ₹18L+')
    trending = bool(request.form.get('trending'))

    if not name:
        flash("Career Path / Roadmap name is required.", "error")
        return redirect(url_for('admin.roadmaps'))

    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')

    cp = CareerPath(
        name=name,
        slug=slug,
        description=description,
        category_id=category_id if category_id else None,
        difficulty=difficulty,
        demand_level=demand_level,
        estimated_duration=estimated_duration,
        average_salary=average_salary,
        trending=trending
    )
    db.session.add(cp)
    db.session.commit()
    flash(f"Roadmap '{name}' created successfully.", "success")
    return redirect(url_for('admin.roadmaps'))

@admin_bp.route('/roadmaps/<int:id>/delete', methods=['POST'])
@admin_required
def delete_roadmap(id):
    cp = CareerPath.query.get_or_404(id)
    name = cp.name
    db.session.delete(cp)
    db.session.commit()
    flash(f"Roadmap '{name}' deleted.", "info")
    return redirect(url_for('admin.roadmaps'))

@admin_bp.route('/roadmaps/<int:id>/steps/add', methods=['POST'])
@admin_required
def add_step(id):
    cp = CareerPath.query.get_or_404(id)
    step_title = request.form.get('step_title', '').strip()
    step_description = request.form.get('step_description', '').strip()
    skill_id = request.form.get('skill_id')

    if not step_title:
        flash("Step title is required.", "error")
        return redirect(url_for('admin.roadmaps'))

    next_order = len(cp.steps) + 1
    step = CareerPathSkill(
        career_path_id=cp.id,
        skill_id=skill_id if skill_id else None,
        step_title=step_title,
        step_description=step_description,
        sequence_order=next_order
    )
    db.session.add(step)
    db.session.commit()
    flash(f"Step '{step_title}' added to {cp.name}.", "success")
    return redirect(url_for('admin.roadmaps'))

@admin_bp.route('/roadmaps/steps/<int:step_id>/delete', methods=['POST'])
@admin_required
def delete_step(step_id):
    step = CareerPathSkill.query.get_or_404(step_id)
    db.session.delete(step)
    db.session.commit()
    flash("Step deleted.", "info")
    return redirect(url_for('admin.roadmaps'))

# --- USERS MANAGEMENT ---

@admin_bp.route('/users')
@admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)

@admin_bp.route('/users/<int:id>/toggle-verify', methods=['POST'])
@admin_required
def toggle_verify(id):
    user = User.query.get_or_404(id)
    user.is_verified = not user.is_verified
    db.session.commit()
    flash(f"User {user.username} verification updated to {user.is_verified}.", "success")
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(id):
    user = User.query.get_or_404(id)
    if user.id == g.user.id:
        flash("Cannot remove your own administrator status.", "error")
        return redirect(url_for('admin.users'))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"User {user.username} admin status set to {user.is_admin}.", "success")
    return redirect(url_for('admin.users'))
