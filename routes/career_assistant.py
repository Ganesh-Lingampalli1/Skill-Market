from flask import Blueprint, request, jsonify, g, session
from services.career_assistant_service import CareerAssistantService
from services.skill_gap_service import SkillGapService
from models import CareerPath

career_assistant_bp = Blueprint('career_assistant', __name__)

@career_assistant_bp.route('/api/ai/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    page_context = data.get('page_context', {})
    history = data.get('history', [])

    response_data = CareerAssistantService.ask(
        user=g.user,
        user_message=message,
        page_context=page_context,
        conversation_history=history
    )

    # Dynamic follow-up chips based on context
    msg_lower = message.lower()
    suggestions = []
    if 'gap' in msg_lower or 'readiness' in msg_lower:
        suggestions = ["How do I learn the first missing skill?", "What portfolio project should I build?", "Show salary potential"]
    elif 'resume' in msg_lower or 'cv' in msg_lower:
        suggestions = ["Give me an XYZ bullet point example", "What skills should I highlight?", "How to beat ATS screeners?"]
    elif 'salary' in msg_lower:
        suggestions = ["Which cloud skills pay best?", "How to negotiate higher compensation?", "View Market Insights"]
    else:
        suggestions = ["What are my skill gaps?", "How to optimize my resume?", "What should I study next?"]

    return jsonify({
        'reply': response_data['reply'],
        'source': response_data['source'],
        'model': response_data['model'],
        'suggestions': suggestions
    })

@career_assistant_bp.route('/api/ai/context', methods=['GET'])
def get_context():
    user_info = None
    if g.user:
        user_skills = SkillGapService.get_user_skills(g.user.id)
        user_info = {
            'username': g.user.username,
            'career_interest': g.user.career_interest,
            'experience_level': g.user.experience_level,
            'skills_count': len(user_skills['skills'])
        }

    return jsonify({
        'user': user_info,
        'default_suggestions': [
            "What should I learn next for my role?",
            "How can I bridge my skill gaps?",
            "How do I improve my resume for recruiters?",
            "Which tech skills offer the highest salaries?"
        ]
    })
