from models import db, Skill, CareerPath, CareerPathSkill, UserSkill, UserProgress, Resource, Bookmark

class SkillGapService:
    @staticmethod
    def get_user_skills(user_id):
        """
        Retrieves all skills acquired by the user:
        1. Explicitly recorded skills from UserSkill (manual or resume-extracted)
        2. Completed roadmap steps from UserProgress linked to a Skill
        Returns a dict: {
            'skill_ids': set of skill IDs,
            'skills': list of Skill objects,
            'user_skills': list of UserSkill objects
        }
        """
        user_skills_records = UserSkill.query.filter_by(user_id=user_id).all()
        acquired_skill_ids = {us.skill_id for us in user_skills_records}

        # Also include completed roadmap step skills
        completed_progress = UserProgress.query.filter_by(user_id=user_id, completed=True).all()
        for prog in completed_progress:
            if prog.step and prog.step.skill_id:
                acquired_skill_ids.add(prog.step.skill_id)

        # Retrieve Skill instances
        skills = Skill.query.filter(Skill.id.in_(acquired_skill_ids)).all() if acquired_skill_ids else []

        return {
            'skill_ids': acquired_skill_ids,
            'skills': skills,
            'user_skills': user_skills_records
        }

    @staticmethod
    def add_user_skill(user_id, skill_id, source='manual'):
        """
        Adds a skill to the user's acquired skills if not already present.
        """
        existing = UserSkill.query.filter_by(user_id=user_id, skill_id=skill_id).first()
        if not existing:
            user_skill = UserSkill(user_id=user_id, skill_id=skill_id, source=source)
            db.session.add(user_skill)
            db.session.commit()
            return user_skill
        return existing

    @staticmethod
    def remove_user_skill(user_id, skill_id):
        """
        Removes a skill from the user's acquired skills.
        """
        existing = UserSkill.query.filter_by(user_id=user_id, skill_id=skill_id).first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
            return True
        return False

    @staticmethod
    def analyze(user_id, career_path_id_or_slug, explicit_skill_ids=None):
        """
        Performs comprehensive skill gap analysis between a user's skills and a target career path.
        """
        # Find CareerPath by ID or slug
        if isinstance(career_path_id_or_slug, int) or (isinstance(career_path_id_or_slug, str) and str(career_path_id_or_slug).isdigit()):
            career_path = db.session.get(CareerPath, int(career_path_id_or_slug))
        else:
            career_path = CareerPath.query.filter_by(slug=str(career_path_id_or_slug)).first()

        if not career_path:
            return None

        # Fetch career path steps ordered by sequence
        steps = CareerPathSkill.query.filter_by(career_path_id=career_path.id)\
            .order_by(CareerPathSkill.sequence_order.asc()).all()

        # Build ordered list of required skills with step metadata
        required_skills = []
        required_skill_ids = set()
        skill_step_meta = {}

        for step in steps:
            if step.skill and step.skill.id not in required_skill_ids:
                required_skill_ids.add(step.skill.id)
                required_skills.append(step.skill)
                skill_step_meta[step.skill.id] = {
                    'step_title': step.step_title,
                    'sequence_order': step.sequence_order,
                    'step_description': step.step_description
                }

        # Fallback if no steps have linked skills: use category skills
        if not required_skills and career_path.category_id:
            category_skills = Skill.query.filter_by(category_id=career_path.category_id).limit(6).all()
            for idx, sk in enumerate(category_skills, 1):
                required_skills.append(sk)
                required_skill_ids.add(sk.id)
                skill_step_meta[sk.id] = {
                    'step_title': f"Core {sk.name}",
                    'sequence_order': idx,
                    'step_description': sk.description
                }

        # Determine user skills
        if explicit_skill_ids is not None:
            user_skill_ids = set(explicit_skill_ids)
        else:
            user_skill_info = SkillGapService.get_user_skills(user_id) if user_id else {'skill_ids': set(), 'skills': []}
            user_skill_ids = user_skill_info['skill_ids']

        # Partition required skills into matched vs missing
        matched_skills = []
        missing_skills = []

        for skill in required_skills:
            if skill.id in user_skill_ids:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)

        total_required = len(required_skills)
        matched_count = len(matched_skills)

        if total_required > 0:
            readiness_score = round((matched_count / total_required) * 100)
        else:
            readiness_score = 0

        # Readiness categorization
        if readiness_score >= 80:
            readiness_level = "Job Ready"
            readiness_color = "success"
            readiness_desc = "You have the vast majority of core competencies required for this career path."
        elif readiness_score >= 50:
            readiness_level = "Intermediate Readiness"
            readiness_color = "primary"
            readiness_desc = "Solid foundational base. You only need a few key skills to become job-market competitive."
        elif readiness_score >= 25:
            readiness_level = "Developing"
            readiness_color = "warning"
            readiness_desc = "Good start on the fundamentals, with substantial runway to build job-ready skills."
        else:
            readiness_level = "Early Stage"
            readiness_color = "info"
            readiness_desc = "Starting fresh in this discipline. Follow the recommended learning path below."

        # Learning order: missing skills ordered by sequence_order
        recommended_learning_order = sorted(
            missing_skills,
            key=lambda s: skill_step_meta.get(s.id, {}).get('sequence_order', 99)
        )

        next_priority_skill = recommended_learning_order[0] if recommended_learning_order else None

        # Fetch curated learning resources for missing skills
        resources_by_skill = {}
        missing_ids = [s.id for s in missing_skills]
        if missing_ids:
            all_resources = Resource.query.filter(Resource.skill_id.in_(missing_ids)).all()
            for res in all_resources:
                if res.skill_id not in resources_by_skill:
                    resources_by_skill[res.skill_id] = []
                if len(resources_by_skill[res.skill_id]) < 3:
                    resources_by_skill[res.skill_id].append(res)

        # Estimate time to bridge gap (approx 3-4 weeks per missing skill)
        estimated_weeks = max(len(missing_skills) * 3, 2) if missing_skills else 0

        # Fetch user's all known skills for context
        user_skills_list = Skill.query.filter(Skill.id.in_(user_skill_ids)).all() if user_skill_ids else []

        return {
            'career_path': career_path,
            'required_skills': required_skills,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'total_required': total_required,
            'matched_count': matched_count,
            'missing_count': len(missing_skills),
            'readiness_score': readiness_score,
            'readiness_level': readiness_level,
            'readiness_color': readiness_color,
            'readiness_desc': readiness_desc,
            'recommended_learning_order': recommended_learning_order,
            'next_priority_skill': next_priority_skill,
            'skill_step_meta': skill_step_meta,
            'resources_by_skill': resources_by_skill,
            'estimated_weeks': estimated_weeks,
            'user_skills_list': user_skills_list
        }
