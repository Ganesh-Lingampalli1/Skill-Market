from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, g, flash, redirect, url_for
from models import db, Bookmark, Skill
from routes.auth import login_required

bookmarks_bp = Blueprint('bookmarks', __name__)

@bookmarks_bp.route('/bookmarks')
@login_required
def index():
    bookmarks = Bookmark.query.filter_by(user_id=g.user.id)\
        .order_by(Bookmark.created_at.desc()).all()
    bookmarked_skills = [b.skill for b in bookmarks if b.skill]

    return render_template(
        'bookmarks/index.html',
        skills=bookmarked_skills,
        total_count=len(bookmarked_skills)
    )

@bookmarks_bp.route('/bookmarks/toggle/<int:skill_id>', methods=['POST'])
@login_required
def toggle(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    bookmark = Bookmark.query.filter_by(user_id=g.user.id, skill_id=skill.id).first()

    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        bookmarked = False
        message = f"Removed {skill.name} from your bookmarks."
    else:
        new_bm = Bookmark(user_id=g.user.id, skill_id=skill.id, created_at=datetime.utcnow())
        db.session.add(new_bm)
        db.session.commit()
        bookmarked = True
        message = f"Added {skill.name} to your bookmarks."

    total_bookmarks = Bookmark.query.filter_by(user_id=g.user.id).count()

    # Support both JSON requests and form fallback
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'bookmarked': bookmarked,
            'skill_id': skill.id,
            'skill_name': skill.name,
            'total_bookmarks': total_bookmarks,
            'message': message
        })

    flash(message, 'success' if bookmarked else 'info')
    return redirect(request.referrer or url_for('bookmarks.index'))
