import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session, current_app, abort
from routes.auth import login_required
from models import db, Skill, CareerPath, Category, UserSkill
from services.resume_service import ResumeService
from services.skill_gap_service import SkillGapService

resume_analyzer_bp = Blueprint('resume_analyzer', __name__)

@resume_analyzer_bp.route('/resume-analyzer')
@login_required
def index():
    user = g.user
    career_paths = CareerPath.query.order_by(CareerPath.trending.desc(), CareerPath.name.asc()).all()
    
    default_path_id = None
    if user.career_interest:
        match = CareerPath.query.filter(CareerPath.name.ilike(f"%{user.career_interest}%")).first()
        if match:
            default_path_id = match.id
    if not default_path_id and career_paths:
        default_path_id = career_paths[0].id

    return render_template(
        'resume_analyzer/index.html',
        career_paths=career_paths,
        default_path_id=default_path_id,
        max_size_mb=current_app.config.get('MAX_RESUME_SIZE_MB', 5)
    )

@resume_analyzer_bp.route('/resume-analyzer/upload', methods=['POST'])
@login_required
def upload():
    user = g.user
    if 'resume_file' not in request.files:
        flash('No file was uploaded. Please choose a PDF resume.', 'warning')
        return redirect(url_for('resume_analyzer.index'))

    file = request.files['resume_file']
    if file.filename == '':
        flash('Please select a PDF file to upload.', 'warning')
        return redirect(url_for('resume_analyzer.index'))

    if not file.filename.lower().endswith('.pdf'):
        flash('Invalid file format. Only PDF documents (.pdf) are supported.', 'danger')
        return redirect(url_for('resume_analyzer.index'))

    # Check file size limit in-memory
    max_mb = current_app.config.get('MAX_RESUME_SIZE_MB', 5)
    file_bytes = file.read()
    if len(file_bytes) > max_mb * 1024 * 1024:
        flash(f'File size exceeds the {max_mb}MB limit. Please upload a smaller PDF.', 'danger')
        return redirect(url_for('resume_analyzer.index'))

    # Extract text in-memory
    stream = io.BytesIO(file_bytes)
    extracted_text, error = ResumeService.extract_text_from_pdf(stream)
    if error:
        flash(error, 'danger')
        return redirect(url_for('resume_analyzer.index'))

    # Extract skills
    analysis = ResumeService.extract_skills_from_text(extracted_text)
    detected_ids = list(analysis['detected_skill_ids'])

    if not detected_ids:
        flash("No known technical skills were identified in this resume. You can still manually select your skills in the Skill Gap Analyzer.", 'warning')

    # Compare with target career path if specified
    target_path_id = request.form.get('target_path_id')
    comparison = None
    if target_path_id and target_path_id.isdigit():
        comparison = ResumeService.compare_with_career_path(analysis['detected_skill_ids'], int(target_path_id))

    # Store analysis session data for user review (strictly in session, no file on disk)
    session['resume_analysis'] = {
        'filename': file.filename,
        'detected_skill_ids': detected_ids,
        'total_detected': analysis['total_detected'],
        'word_count': analysis['word_count'],
        'target_path_id': int(target_path_id) if target_path_id and target_path_id.isdigit() else None
    }

    return redirect(url_for('resume_analyzer.result'))

@resume_analyzer_bp.route('/resume-analyzer/result')
@login_required
def result():
    user = g.user
    resume_data = session.get('resume_analysis')
    if not resume_data:
        flash('Please upload your resume to view the analysis.', 'info')
        return redirect(url_for('resume_analyzer.index'))

    detected_ids = set(resume_data.get('detected_skill_ids', []))
    detected_skills = Skill.query.filter(Skill.id.in_(detected_ids)).all() if detected_ids else []

    # Group by category
    categorized_skills = {}
    for skill in detected_skills:
        cat_name = skill.category.name if skill.category else 'Other'
        if cat_name not in categorized_skills:
            categorized_skills[cat_name] = []
        categorized_skills[cat_name].append(skill)

    # User's existing skills to show what's already saved
    user_skill_info = SkillGapService.get_user_skills(user.id)
    user_skill_ids = user_skill_info['skill_ids']

    # Target path comparison
    target_path = None
    comparison = None
    target_path_id = resume_data.get('target_path_id')
    if target_path_id:
        target_path = db.session.get(CareerPath, target_path_id)
        if target_path:
            comparison = ResumeService.compare_with_career_path(detected_ids, target_path.id)

    # All career paths for selector
    career_paths = CareerPath.query.order_by(CareerPath.name.asc()).all()

    return render_template(
        'resume_analyzer/result.html',
        resume_data=resume_data,
        detected_skills=detected_skills,
        categorized_skills=categorized_skills,
        user_skill_ids=user_skill_ids,
        target_path=target_path,
        comparison=comparison,
        career_paths=career_paths
    )

@resume_analyzer_bp.route('/resume-analyzer/save-skills', methods=['POST'])
@login_required
def save_skills():
    user = g.user
    selected_skill_ids = request.form.getlist('confirmed_skills', type=int)

    if not selected_skill_ids:
        flash('No skills were selected to add to your profile.', 'info')
        return redirect(url_for('resume_analyzer.result'))

    added_count = 0
    for sid in selected_skill_ids:
        skill = db.session.get(Skill, sid)
        if skill:
            user_skill = SkillGapService.add_user_skill(user.id, skill.id, source='resume')
            if user_skill:
                added_count += 1

    flash(f"Successfully confirmed and saved {added_count} skills to your SkillMarket profile!", 'success')
    
    # Check if target role was selected to redirect to skill-gap result
    target_path_id = request.form.get('target_path_id')
    if target_path_id and target_path_id.isdigit():
        target_path = db.session.get(CareerPath, int(target_path_id))
        if target_path:
            return redirect(url_for('skill_gap.result', slug=target_path.slug))

    return redirect(url_for('dashboard.index'))
