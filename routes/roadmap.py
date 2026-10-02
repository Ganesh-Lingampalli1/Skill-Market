from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, g, abort, redirect, url_for, flash
from models import db, CareerPath, CareerPathSkill, Resource, UserProgress, Bookmark, Category
from routes.auth import login_required

roadmap_bp = Blueprint('roadmap', __name__)

@roadmap_bp.route('/roadmaps')
def list_roadmaps():
    category_slug = request.args.get('category', '').strip()
    query = CareerPath.query

    selected_category = None
    if category_slug:
        selected_category = Category.query.filter_by(slug=category_slug).first()
        if selected_category:
            query = query.filter_by(category_id=selected_category.id)

    roadmaps = query.all()
    categories = Category.query.all()

    # Calculate user progress per roadmap if logged in
    user_progress_map = {}
    if g.user:
        for r in roadmaps:
            total_steps = len(r.steps)
            if total_steps > 0:
                completed = UserProgress.query.filter_by(
                    user_id=g.user.id, career_path_id=r.id, completed=True
                ).count()
                pct = int((completed / total_steps) * 100)
                user_progress_map[r.id] = {
                    'completed': completed,
                    'total': total_steps,
                    'percentage': pct
                }

    return render_template(
        'roadmap/list.html',
        roadmaps=roadmaps,
        categories=categories,
        selected_category=selected_category,
        user_progress_map=user_progress_map
    )

@roadmap_bp.route('/roadmaps/<slug>')
def detail(slug):
    career_path = CareerPath.query.filter_by(slug=slug).first_or_404()

    # Steps in sequence
    steps = CareerPathSkill.query.filter_by(career_path_id=career_path.id)\
        .order_by(CareerPathSkill.sequence_order.asc()).all()

    total_steps = len(steps)
    completed_step_ids = set()

    if g.user:
        completed_records = UserProgress.query.filter_by(
            user_id=g.user.id, career_path_id=career_path.id, completed=True
        ).all()
        completed_step_ids = set(r.career_path_skill_id for r in completed_records)

    completed_count = len(completed_step_ids)
    progress_percentage = int((completed_count / total_steps * 100)) if total_steps > 0 else 0

    return render_template(
        'roadmap/detail.html',
        career_path=career_path,
        steps=steps,
        total_steps=total_steps,
        completed_count=completed_count,
        completed_step_ids=completed_step_ids,
        progress_percentage=progress_percentage
    )

@roadmap_bp.route('/roadmaps/<int:career_path_id>/step/<int:step_id>/toggle', methods=['POST'])
@login_required
def toggle_step(career_path_id, step_id):
    career_path = CareerPath.query.get_or_404(career_path_id)
    step = CareerPathSkill.query.get_or_404(step_id)

    if step.career_path_id != career_path.id:
        return jsonify({'success': False, 'message': 'Invalid step for roadmap'}), 400

    progress_record = UserProgress.query.filter_by(
        user_id=g.user.id,
        career_path_id=career_path_id,
        career_path_skill_id=step_id
    ).first()

    if not progress_record:
        progress_record = UserProgress(
            user_id=g.user.id,
            career_path_id=career_path_id,
            career_path_skill_id=step_id,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress_record)
        completed = True
    else:
        progress_record.completed = not progress_record.completed
        progress_record.completed_at = datetime.utcnow() if progress_record.completed else None
        completed = progress_record.completed

    db.session.commit()

    # Recalculate progress
    total_steps = CareerPathSkill.query.filter_by(career_path_id=career_path_id).count()
    completed_count = UserProgress.query.filter_by(
        user_id=g.user.id, career_path_id=career_path_id, completed=True
    ).count()

    progress_pct = int((completed_count / total_steps * 100)) if total_steps > 0 else 0

    return jsonify({
        'success': True,
        'completed': completed,
        'completed_count': completed_count,
        'total_steps': total_steps,
        'progress_percentage': progress_pct,
        'message': f"Step '{step.step_title}' marked as {'completed' if completed else 'incomplete'}."
    })
