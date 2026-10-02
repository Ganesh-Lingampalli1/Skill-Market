from models import Skill, Category

class RecommendationService:
    # Synergy mapping: if you know key skill, these adjacent skills are great companions
    SYNERGY_MAP = {
        'python': ['SQL', 'Flask', 'Django', 'Docker', 'REST APIs', 'FastAPI', 'Pandas', 'NumPy'],
        'javascript': ['React', 'Node.js', 'TypeScript', 'Next.js', 'HTML/CSS', 'GraphQL', 'Tailwind CSS'],
        'react': ['TypeScript', 'Next.js', 'Tailwind CSS', 'Redux', 'Node.js', 'GraphQL'],
        'sql': ['Python', 'PostgreSQL', 'Data Warehousing', 'Power BI', 'Tableau', 'DBT'],
        'docker': ['Kubernetes', 'Linux', 'AWS', 'CI/CD', 'Terraform', 'Microservices'],
        'aws': ['Docker', 'Terraform', 'Kubernetes', 'Linux', 'Serverless', 'Cloud Security'],
        'linux': ['Bash Scripting', 'Git', 'Docker', 'DevOps', 'Networking', 'Cybersecurity'],
        'html': ['CSS', 'JavaScript', 'Tailwind CSS', 'React', 'UI/UX Design'],
        'css': ['JavaScript', 'Tailwind CSS', 'React', 'Figma', 'UI/UX Design']
    }

    # Core required skills per career path interest
    INTEREST_CORE_SKILLS = {
        'Web Development': ['JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'REST APIs', 'HTML/CSS', 'Git', 'Docker'],
        'Data Science': ['Python', 'SQL', 'Pandas', 'NumPy', 'Machine Learning', 'Data Visualization', 'Statistics', 'Power BI'],
        'AI/ML': ['Python', 'Machine Learning', 'Deep Learning', 'PyTorch', 'TensorFlow', 'NLP', 'Computer Vision', 'Mathematics'],
        'Cloud & DevOps': ['Linux', 'Docker', 'Kubernetes', 'AWS', 'Terraform', 'CI/CD', 'Git', 'Python'],
        'Cybersecurity': ['Linux', 'Networking', 'Ethical Hacking', 'Cryptography', 'SIEM', 'Python', 'Web Security'],
        'UI/UX Design': ['Figma', 'User Research', 'Wireframing', 'Prototyping', 'Design Systems', 'HTML/CSS'],
        'Mobile Development': ['Flutter', 'React Native', 'Swift', 'Kotlin', 'REST APIs', 'Firebase']
    }

    @classmethod
    def get_recommendations(cls, career_interest: str = None, experience_level: str = 'Beginner', current_skills: list = None, limit: int = 8):
        """
        Generates personalized skill recommendations with match percentages and explanations.
        """
        current_skills = [s.strip().lower() for s in (current_skills or []) if s]
        all_skills = Skill.query.all()
        scored_skills = []

        target_interest = career_interest or 'Web Development'
        core_skill_names = [s.lower() for s in cls.INTEREST_CORE_SKILLS.get(target_interest, [])]

        for skill in all_skills:
            skill_lower = skill.name.lower()

            # If user already possesses this skill, skip or lower rank
            already_knows = skill_lower in current_skills
            
            # Base match starts at demand score
            base_score = skill.demand_score * 0.6  # up to 60 pts

            # Category / Career interest relevance
            interest_bonus = 0
            reasons = []

            if skill_lower in core_skill_names:
                interest_bonus += 25
                reasons.append(f"Essential core competency for {target_interest}")
            elif skill.category and target_interest.lower() in skill.category.name.lower():
                interest_bonus += 20
                reasons.append(f"Highly relevant to {target_interest} field")

            # Synergy with current skills
            synergy_bonus = 0
            synergy_matches = []
            for cur in current_skills:
                for key, adjacent_list in cls.SYNERGY_MAP.items():
                    if key in cur and any(skill_lower in adj.lower() for adj in adjacent_list):
                        synergy_matches.append(cur.title())

            if synergy_matches:
                unique_synergies = list(set(synergy_matches))[:2]
                synergy_bonus += min(15, len(unique_synergies) * 8)
                reasons.append(f"Pairs exceptionally well with your knowledge of {', '.join(unique_synergies)}")

            # Experience level matching
            difficulty_bonus = 0
            if experience_level == 'Beginner':
                if skill.difficulty == 'Beginner':
                    difficulty_bonus = 10
                    reasons.append("Beginner-friendly starting point")
                elif skill.difficulty == 'Intermediate':
                    difficulty_bonus = 5
            elif experience_level == 'Intermediate':
                if skill.difficulty in ['Intermediate', 'Beginner']:
                    difficulty_bonus = 10
                    reasons.append("Matches your intermediate technical capability")
            elif experience_level == 'Advanced':
                if skill.difficulty in ['Advanced', 'Intermediate']:
                    difficulty_bonus = 10
                    reasons.append("High-yield specialization for advanced practitioners")

            # High market demand bonus
            if skill.market_demand in ['Very High', 'High']:
                reasons.append(f"Strong market hiring demand (Score: {skill.demand_score}/100)")

            total_score = base_score + interest_bonus + synergy_bonus + difficulty_bonus

            # Scale to 70% - 98% range for realistic top recommendations
            match_percentage = min(98, max(72, int(total_score)))

            # If already knows, penalize so they discover new skills
            if already_knows:
                match_percentage = max(50, match_percentage - 30)
                reasons = ["You already marked this skill, consider advanced certification or deep-dive."]

            if not reasons:
                reasons.append(f"Growing market adoption and strong salary potential ({skill.salary_formatted})")

            scored_skills.append({
                'skill': skill,
                'match_percentage': match_percentage,
                'reasons': reasons[:2],
                'is_already_known': already_knows
            })

        # Sort descending by match percentage
        scored_skills.sort(key=lambda x: (not x['is_already_known'], x['match_percentage']), reverse=True)
        return scored_skills[:limit]
