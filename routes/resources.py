from flask import Blueprint, render_template, request
from models import Resource, Skill, Category

resources_bp = Blueprint('resources', __name__)

@resources_bp.route('/resources')
def index():
    res_type = request.args.get('type', '').strip()
    is_free_param = request.args.get('free', '').strip()
    search_query = request.args.get('q', '').strip()

    query = Resource.query

    if res_type and res_type.lower() != 'all':
        query = query.filter(Resource.type.ilike(res_type))

    if is_free_param == 'true':
        query = query.filter_by(is_free=True)
    elif is_free_param == 'paid':
        query = query.filter_by(is_free=False)

    if search_query:
        query = query.filter(
            (Resource.title.ilike(f'%{search_query}%')) |
            (Resource.description.ilike(f'%{search_query}%')) |
            (Resource.provider.ilike(f'%{search_query}%'))
        )

    resources = query.all()
    categories = Category.query.all()

    return render_template(
        'resources/index.html',
        resources=resources,
        selected_type=res_type,
        selected_free=is_free_param,
        search_query=search_query,
        categories=categories,
        total_count=len(resources)
    )
