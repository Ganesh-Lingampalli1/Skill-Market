from flask import Blueprint, render_template, request, redirect, url_for, flash, g, jsonify, abort
from routes.auth import login_required
from models import db, Skill, CareerPath, Category, UserSkill
from services.skill_gap_service import SkillGapService

skill_gap_bp = Blueprint('skill_gap', __name__)

@skill_gap_bp.route('/skill-gap')
@login_required
def index():
    user = g.user
    career_paths = CareerPath.query.order_by(CareerPath.trending.desc(), CareerPath.name.asc()).all()
    categories = Category.query.all()
    all_skills = Skill.query.order_by(Skill.name.asc()).all()

    # User's current skills
    user_skill_info = SkillGapService.get_user_skills(user.id)
    user_skill_ids = user_skill_info['skill_ids']

    # Recommended career path based on user interest
    default_career_path = None
    if user.career_interest:
        default_career_path = CareerPath.query.filter(
            CareerPath.name.ilike(f"%{user.career_interest}%")
        ).first()
    if not default_career_path and career_paths:
        default_career_path = career_paths[0]

    return render_template(
        'skill_gap/index.html',
        career_paths=career_paths,
        categories=categories,
        all_skills=all_skills,
        user_skill_ids=user_skill_ids,
        user_skills=user_skill_info['skills'],
        default_career_path=default_career_path
    )

@skill_gap_bp.route('/skill-gap/analyze', methods=['POST'])
@login_required
def run_analysis():
    user = g.user
    career_path_id = request.form.get('career_path_id')
    selected_skill_ids = request.form.getlist('selected_skills', type=int)

    if not career_path_id:
        flash('Please select a career path to analyze.', 'warning')
        return redirect(url_for('skill_gap.index'))

    career_path = db.session.get(CareerPath, int(career_path_id))
    if not career_path:
        flash('Career path not found.', 'danger')
        return redirect(url_for('skill_gap.index'))

    # If user selected skills, synchronize any newly checked skills to their profile
    if selected_skill_ids:
        for sid in selected_skill_ids:
            SkillGapService.add_user_skill(user.id, sid, source='manual')

    return redirect(url_for('skill_gap.result', slug=career_path.slug))

@skill_gap_bp.route('/skill-gap/result/<slug>')
@login_required
def result(slug):
    user = g.user
    career_path = CareerPath.query.filter_by(slug=slug).first_or_404()

    analysis = SkillGapService.analyze(user.id, career_path.slug)
    if not analysis:
        flash('Could not perform skill gap analysis.', 'danger')
        return redirect(url_for('skill_gap.index'))

    # Other career paths for quick switching
    other_paths = CareerPath.query.filter(CareerPath.id != career_path.id).limit(4).all()

    return render_template(
        'skill_gap/result.html',
        career_path=career_path,
        analysis=analysis,
        other_paths=other_paths
    )

@skill_gap_bp.route('/skill-gap/add-skill/<int:skill_id>', methods=['POST'])
@login_required
def add_skill(skill_id):
    user = g.user
    skill = db.session.get(Skill, skill_id)
    if not skill:
        abort(404)
    user_skill = SkillGapService.add_user_skill(user.id, skill.id, source='manual')

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f"Added '{skill.name}' to your acquired skills.",
            'skill_id': skill.id,
            'skill_name': skill.name
        })

    flash(f"Added '{skill.name}' to your skills profile.", 'success')
    return redirect(request.referrer or url_for('skill_gap.index'))

@skill_gap_bp.route('/skill-gap/remove-skill/<int:skill_id>', methods=['POST'])
@login_required
def remove_skill(skill_id):
    user = g.user
    skill = db.session.get(Skill, skill_id)
    if not skill:
        abort(404)
    SkillGapService.remove_user_skill(user.id, skill.id)

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f"Removed '{skill.name}' from your skills.",
            'skill_id': skill.id
        })

    flash(f"Removed '{skill.name}' from your skills profile.", 'info')
    return redirect(request.referrer or url_for('skill_gap.index'))

@skill_gap_bp.route('/api/skill-gap/preview/<slug>')
@login_required
def api_preview(slug):
    user = g.user
    analysis = SkillGapService.analyze(user.id, slug)
    if not analysis:
        return jsonify({'error': 'Career path not found'}), 404

    return jsonify({
        'career_path': {
            'id': analysis['career_path'].id,
            'name': analysis['career_path'].name,
            'slug': analysis['career_path'].slug,
            'average_salary': analysis['career_path'].average_salary,
            'estimated_duration': analysis['career_path'].estimated_duration
        },
        'readiness_score': analysis['readiness_score'],
        'readiness_level': analysis['readiness_level'],
        'matched_skills': [s.name for s in analysis['matched_skills']],
        'missing_skills': [s.name for s in analysis['missing_skills']],
        'next_priority_skill': analysis['next_priority_skill'].name if analysis['next_priority_skill'] else None,
        'estimated_weeks': analysis['estimated_weeks']
    })
