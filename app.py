import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
# Load .env or .env.txt from project root before reading any configs
for env_name in ('.env', '.env.txt'):
    env_path = BASE_DIR / env_name
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path, override=True)


print("ENV FILE:", BASE_DIR / ".env")
print("ENV EXISTS:", (BASE_DIR / ".env").is_file())
print("MAIL USER:", os.getenv("MAIL_USERNAME"))
print("MAIL PASSWORD LOADED:", bool(os.getenv("MAIL_PASSWORD")))

from datetime import datetime
from flask import Flask, render_template, session, g, redirect, url_for
from config import Config
from models import db, User, Category, Skill, CareerPath, Resource, Bookmark

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Global user authentication hook before each request
    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')
        if user_id is None:
            g.user = None
        else:
            g.user = db.session.get(User, user_id)

    # Global template context processor
    @app.context_processor
    def inject_globals():
        return {
            'current_user': g.user,
            'now': datetime.utcnow(),
            'site_name': 'SkillMarket',
            'site_tagline': 'Discover Skills That Actually Pay.'
        }

    # Register Route Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.skills import skills_bp
    from routes.recommendations import recommendations_bp
    from routes.roadmap import roadmap_bp
    from routes.resources import resources_bp
    from routes.analytics import analytics_bp
    from routes.bookmarks import bookmarks_bp
    from routes.profile import profile_bp
    from routes.api import api_bp
    from routes.admin import admin_bp
    from routes.skill_gap import skill_gap_bp
    from routes.resume_analyzer import resume_analyzer_bp
    from routes.career_assistant import career_assistant_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(bookmarks_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(skill_gap_bp)
    app.register_blueprint(resume_analyzer_bp)
    app.register_blueprint(career_assistant_bp)

    # Public Landing Page Route
    @app.route('/')
    def index():
        trending_skills = Skill.query.filter_by(trending=True).limit(8).all()
        categories = Category.query.all()
        featured_roadmaps = CareerPath.query.filter_by(trending=True).limit(4).all()
        stats = {
            'skills_count': Skill.query.count(),
            'roadmaps_count': CareerPath.query.count(),
            'resources_count': Resource.query.count(),
            'categories_count': Category.query.count()
        }
        return render_template(
            'index.html',
            trending_skills=trending_skills,
            categories=categories,
            featured_roadmaps=featured_roadmaps,
            stats=stats
        )

    # Public About Page Route
    @app.route('/about')
    def about():
        return render_template('about.html')

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)
