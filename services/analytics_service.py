from sqlalchemy import func
from models import db, Skill, Category, CareerPath, Resource, Bookmark, User

class AnalyticsService:
    @classmethod
    def get_market_overview(cls):
        """
        Gathers key statistical indicators for the analytics dashboard and Chart.js views.
        """
        # Highest Paying Skills (sorted by salary_max desc)
        highest_paying = Skill.query.order_by(Skill.salary_max.desc(), Skill.demand_score.desc()).limit(8).all()
        
        # Most In-Demand Skills (sorted by demand_score desc)
        most_in_demand = Skill.query.order_by(Skill.demand_score.desc()).limit(8).all()

        # Category distribution
        categories = Category.query.all()
        cat_labels = []
        cat_counts = []
        for cat in categories:
            count = Skill.query.filter_by(category_id=cat.id).count()
            if count > 0:
                cat_labels.append(cat.name)
                cat_counts.append(count)

        # Average salaries by difficulty / experience level
        difficulty_levels = ['Beginner', 'Intermediate', 'Advanced']
        salary_by_difficulty = {}
        for diff in difficulty_levels:
            skills = Skill.query.filter_by(difficulty=diff).all()
            if skills:
                avg_min = sum(s.salary_min for s in skills) / len(skills)
                avg_max = sum(s.salary_max for s in skills) / len(skills)
                salary_by_difficulty[diff] = {
                    'avg_min': round(avg_min, 1),
                    'avg_max': round(avg_max, 1),
                    'count': len(skills)
                }
            else:
                salary_by_difficulty[diff] = {'avg_min': 4, 'avg_max': 12, 'count': 0}

        # Trending skills
        trending = Skill.query.filter_by(trending=True).limit(6).all()
        if not trending:
            trending = Skill.query.order_by(Skill.demand_score.desc()).limit(6).all()

        return {
            'highest_paying': highest_paying,
            'most_in_demand': most_in_demand,
            'trending': trending,
            'category_distribution': {
                'labels': cat_labels,
                'counts': cat_counts
            },
            'salary_by_difficulty': salary_by_difficulty,
            'total_skills': Skill.query.count(),
            'total_categories': Category.query.count(),
            'total_roadmaps': CareerPath.query.count(),
            'total_resources': Resource.query.count()
        }

    @classmethod
    def get_chart_data(cls):
        """
        Returns ready-to-consume JSON structures for Chart.js charts.
        """
        highest_paying = Skill.query.order_by(Skill.salary_max.desc()).limit(7).all()
        most_demand = Skill.query.order_by(Skill.demand_score.desc()).limit(7).all()
        categories = Category.query.all()

        return {
            'salary_chart': {
                'labels': [s.name for s in highest_paying],
                'min_salaries': [s.salary_min for s in highest_paying],
                'max_salaries': [s.salary_max for s in highest_paying]
            },
            'demand_chart': {
                'labels': [s.name for s in most_demand],
                'scores': [s.demand_score for s in most_demand]
            },
            'category_chart': {
                'labels': [c.name for c in categories if len(c.skills) > 0],
                'counts': [len(c.skills) for c in categories if len(c.skills) > 0]
            }
        }
