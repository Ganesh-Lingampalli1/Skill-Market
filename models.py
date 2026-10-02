from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    theme_preference = db.Column(db.String(10), default='light', nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    career_interest = db.Column(db.String(100), default='Web Development', nullable=True)
    experience_level = db.Column(db.String(50), default='Beginner', nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    bookmarks = db.relationship('Bookmark', backref='user', cascade='all, delete-orphan', lazy=True)
    progress_items = db.relationship('UserProgress', backref='user', cascade='all, delete-orphan', lazy=True)
    user_skills = db.relationship('UserSkill', backref='user', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_verified': self.is_verified,
            'theme_preference': self.theme_preference,
            'career_interest': self.career_interest,
            'experience_level': self.experience_level,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class EmailVerification(db.Model):
    __tablename__ = 'email_verification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    username = db.Column(db.String(64), nullable=True)
    otp_hash = db.Column(db.String(128), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='folder', nullable=False)

    # Relationships
    skills = db.relationship('Skill', backref='category', lazy=True, cascade='all, delete-orphan')
    career_paths = db.relationship('CareerPath', backref='category', lazy=True)


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(30), default='Beginner', nullable=False)  # Beginner, Intermediate, Advanced
    demand_score = db.Column(db.Integer, default=85, nullable=False)           # 1 - 100
    salary_min = db.Column(db.Integer, default=4, nullable=False)              # ₹ in Lakhs (LPA)
    salary_max = db.Column(db.Integer, default=15, nullable=False)             # ₹ in Lakhs (LPA)
    learning_duration = db.Column(db.String(50), default='6-8 weeks', nullable=False)
    icon = db.Column(db.String(50), default='code-2', nullable=False)
    market_demand = db.Column(db.String(30), default='High', nullable=False)   # High, Very High, Steady, Growing
    trending = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    resources = db.relationship('Resource', backref='skill', cascade='all, delete-orphan', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='skill', cascade='all, delete-orphan', lazy=True)
    roadmap_steps = db.relationship('CareerPathSkill', backref='skill', lazy=True)

    @property
    def salary_formatted(self):
        return f"₹{self.salary_min}L – ₹{self.salary_max}L+"


class Resource(db.Model):
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), default='Documentation', nullable=False)  # Documentation, Video Course, Practice, Course, Book
    provider = db.Column(db.String(100), default='Official Docs', nullable=False)
    is_free = db.Column(db.Boolean, default=True, nullable=False)

    roadmap_links = db.relationship('RoadmapResource', backref='resource', cascade='all, delete-orphan', lazy=True)


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill_bookmark'),
    )


class CareerPath(db.Model):
    __tablename__ = 'career_paths'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    difficulty = db.Column(db.String(50), default='Beginner → Advanced', nullable=False)
    demand_level = db.Column(db.String(50), default='High Demand', nullable=False)
    estimated_duration = db.Column(db.String(50), default='6 months', nullable=False)
    average_salary = db.Column(db.String(50), default='₹6L – ₹18L+', nullable=False)
    icon = db.Column(db.String(50), default='briefcase', nullable=False)
    trending = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    steps = db.relationship(
        'CareerPathSkill',
        backref='career_path',
        cascade='all, delete-orphan',
        lazy=True,
        order_by='CareerPathSkill.sequence_order'
    )
    user_progress = db.relationship('UserProgress', backref='career_path', cascade='all, delete-orphan', lazy=True)


class CareerPathSkill(db.Model):
    __tablename__ = 'career_path_skills'

    id = db.Column(db.Integer, primary_key=True)
    career_path_id = db.Column(db.Integer, db.ForeignKey('career_paths.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='SET NULL'), nullable=True)
    step_title = db.Column(db.String(150), nullable=False)
    step_description = db.Column(db.Text, nullable=True)
    sequence_order = db.Column(db.Integer, nullable=False)

    # Relationships
    step_resources = db.relationship('RoadmapResource', backref='step', cascade='all, delete-orphan', lazy=True)
    progress_records = db.relationship('UserProgress', backref='step', cascade='all, delete-orphan', lazy=True)


class RoadmapResource(db.Model):
    __tablename__ = 'roadmap_resources'

    id = db.Column(db.Integer, primary_key=True)
    career_path_skill_id = db.Column(db.Integer, db.ForeignKey('career_path_skills.id', ondelete='CASCADE'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id', ondelete='CASCADE'), nullable=False)


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    career_path_id = db.Column(db.Integer, db.ForeignKey('career_paths.id', ondelete='CASCADE'), nullable=False)
    career_path_skill_id = db.Column(db.Integer, db.ForeignKey('career_path_skills.id', ondelete='CASCADE'), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'career_path_id', 'career_path_skill_id', name='uq_user_path_step'),
    )


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    source = db.Column(db.String(50), default='manual', nullable=False)  # manual, resume, roadmap
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),
    )

    skill = db.relationship('Skill', backref=db.backref('user_skills', cascade='all, delete-orphan', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_id': self.skill_id,
            'source': self.source,
            'skill_name': self.skill.name if self.skill else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
