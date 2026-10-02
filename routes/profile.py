from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from models import db, User, Bookmark, UserProgress, CareerPath, Skill
from routes.auth import login_required

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def index():
    user = g.user
    bookmarks = Bookmark.query.filter_by(user_id=user.id).all()
    bookmarked_skills = [b.skill for b in bookmarks if b.skill]

    # Roadmap progress summary
    progress_records = UserProgress.query.filter_by(user_id=user.id, completed=True).all()
    completed_steps_count = len(progress_records)

    # Started career paths
    started_path_ids = set(p.career_path_id for p in progress_records)
    started_paths = CareerPath.query.filter(CareerPath.id.in_(started_path_ids)).all() if started_path_ids else []

    roadmaps_summary = []
    for cp in started_paths:
        total = len(cp.steps)
        done = sum(1 for p in progress_records if p.career_path_id == cp.id)
        pct = int((done / total * 100)) if total > 0 else 0
        roadmaps_summary.append({
            'career_path': cp,
            'done': done,
            'total': total,
            'percentage': pct
        })

    return render_template(
        'profile/index.html',
        user=user,
        bookmarked_skills=bookmarked_skills,
        completed_steps_count=completed_steps_count,
        roadmaps_summary=roadmaps_summary
    )

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user = g.user

    if request.method == 'POST':
        # Update preferences
        career_interest = request.form.get('career_interest', user.career_interest).strip()
        experience_level = request.form.get('experience_level', user.experience_level).strip()
        theme_preference = request.form.get('theme_preference', user.theme_preference).strip()

        if theme_preference in ['light', 'dark']:
            user.theme_preference = theme_preference

        user.career_interest = career_interest
        user.experience_level = experience_level

        db.session.commit()
        flash("Settings saved successfully!", "success")
        return redirect(url_for('profile.settings'))

    return render_template('profile/settings.html', user=user)
