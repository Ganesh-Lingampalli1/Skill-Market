import os
import json
import urllib.request
import urllib.error
from flask import current_app
from models import Skill, CareerPath, Category, Resource, UserSkill, UserProgress
from services.skill_gap_service import SkillGapService

class CareerAssistantService:
    @staticmethod
    def get_system_prompt(user, page_context=None):
        """
        Builds a rich context prompt containing user profile and live platform data.
        """
        context_lines = [
            "You are the SkillMarket AI Career Assistant, a knowledgeable, encouraging, and highly practical career coach and tech advisor.",
            "Your mission is to help students, developers, and tech professionals discover high-paying skills, understand market demand, optimize resumes, bridge skill gaps, and accelerate their careers.",
            "Format your answers with clean, readable Markdown (bullet points, bold highlights, concise sections). Keep your tone professional, motivating, and actionable."
        ]

        if user:
            user_skills = SkillGapService.get_user_skills(user.id)
            skill_names = [s.name for s in user_skills['skills']]
            context_lines.append(f"\nUser Profile:")
            context_lines.append(f"- Name: {user.username}")
            context_lines.append(f"- Career Target: {user.career_interest or 'Software Engineering'}")
            context_lines.append(f"- Experience Level: {user.experience_level or 'Beginner'}")
            context_lines.append(f"- Current Verified Skills: {', '.join(skill_names) if skill_names else 'None recorded yet'}")

        if page_context:
            context_lines.append(f"\nUser's Current Page Context:")
            context_lines.append(f"- URL: {page_context.get('url', '/')}")
            context_lines.append(f"- Page Title: {page_context.get('title', 'SkillMarket')}")
            if page_context.get('role'):
                context_lines.append(f"- Active Role in View: {page_context.get('role')}")
            if page_context.get('score') is not None:
                context_lines.append(f"- Latest Readiness Score: {page_context.get('score')}%")
            if page_context.get('missing'):
                context_lines.append(f"- Identified Skill Gaps: {page_context.get('missing')}")

        return "\n".join(context_lines)

    @classmethod
    def ask(cls, user, user_message, page_context=None, conversation_history=None):
        """
        Dual-mode dispatcher:
        Tries external AI API first if configured; falls back cleanly to local rule engine.
        """
        api_key = current_app.config.get('AI_API_KEY', '').strip()
        model_name = current_app.config.get('AI_MODEL', 'gemini-1.5-flash').strip()

        if api_key:
            try:
                response_text = cls._call_gemini_api(api_key, model_name, user, user_message, page_context, conversation_history)
                if response_text:
                    return {
                        'reply': response_text,
                        'source': 'ai_api',
                        'model': model_name
                    }
            except Exception as e:
                # Log error and fall through to internal rule engine
                current_app.logger.warning(f"External AI call failed ({e}), falling back to SkillMarket Rule Engine.")

        # Fallback to local rule engine
        fallback_reply = cls._generate_rule_based_response(user, user_message, page_context)
        return {
            'reply': fallback_reply,
            'source': 'rule_engine',
            'model': 'SkillMarket Career Intelligence Engine'
        }

    @classmethod
    def _call_gemini_api(cls, api_key, model_name, user, user_message, page_context, conversation_history):
        """
        Calls Google Gemini API using urllib (standard library, zero external dependencies).
        """
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        system_prompt = cls.get_system_prompt(user, page_context)

        contents = []
        # Add system instruction as first user exchange
        contents.append({
            "role": "user",
            "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\nPlease acknowledge and assist the user."}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Understood. I am the SkillMarket AI Career Assistant, ready to provide personalized, actionable career guidance."}]
        })

        # Add recent conversation history (last 6 messages)
        if conversation_history:
            for item in conversation_history[-6:]:
                role = "user" if item.get('sender') == 'user' else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": item.get('text', '')}]
                })

        # Add current user message
        contents.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000
            }
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=12) as response:
            result = json.loads(response.read().decode('utf-8'))
            candidates = result.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    return parts[0].get('text', '')

        return None

    @classmethod
    def _generate_rule_based_response(cls, user, user_message, page_context=None):
        """
        SkillMarket Rule Engine: Generates intelligent, contextual, and accurate career advice
        when external AI API is offline or unconfigured.
        """
        msg_lower = user_message.lower()
        username = user.username if user else "there"
        target_role = (user.career_interest if user and user.career_interest else "Software Engineering")
        user_skills_info = SkillGapService.get_user_skills(user.id) if user else {'skills': [], 'skill_ids': set()}
        user_skills = [s.name for s in user_skills_info['skills']]

        # 1. Skill Gap / Readiness Queries
        if any(w in msg_lower for w in ['gap', 'readiness', 'missing', 'score', 'evaluate']):
            # Look up career path
            path = CareerPath.query.filter(CareerPath.name.ilike(f"%{target_role}%")).first()
            if not path:
                path = CareerPath.query.first()

            if path:
                analysis = SkillGapService.analyze(user.id if user else None, path.slug)
                missing_names = [s.name for s in analysis['missing_skills']]
                matched_names = [s.name for s in analysis['matched_skills']]
                next_skill = analysis['next_priority_skill'].name if analysis['next_priority_skill'] else 'Advanced System Design'

                return (
                    f"### 🎯 Skill Gap Assessment for **{path.name}**\n\n"
                    f"Hello **{username}**! Based on your verified profile, here is your readiness breakdown:\n\n"
                    f"- **Current Readiness Score:** `{analysis['readiness_score']}%` ({analysis['readiness_level']})\n"
                    f"- **Verified Competencies ({len(matched_names)}):** {', '.join(matched_names) if matched_names else 'None registered yet'}\n"
                    f"- **Identified Gaps ({len(missing_names)}):** {', '.join(missing_names) if missing_names else 'Zero gaps! You are fully qualified.'}\n\n"
                    f"#### ⚡ Immediate Next Step:\n"
                    f"Prioritize mastering **{next_skill}**. Completing this milestone will bridge your most critical knowledge gap for {path.name}.\n\n"
                    f"💡 *Action Tip:* Visit the [Skill Gap Analyzer](/skill-gap) to inspect curated resources and track your milestones."
                )

        # 2. Resume Improvement / Review Queries
        if any(w in msg_lower for w in ['resume', 'cv', 'ats', 'bullet point']):
            return (
                f"### 📄 Resume Optimization Strategy for **{target_role}**\n\n"
                f"Hi **{username}**! To make your resume stand out to hiring managers and pass ATS screeners:\n\n"
                f"1. **Lead with Technical Competencies:** Group skills logically into *Languages*, *Frameworks*, *Cloud & DevOps*, and *Databases* right below your summary.\n"
                f"2. **Use Google's XYZ Formula:** Structure your bullet points as *\"Accomplished [X], as measured by [Y], by doing [Z]\"*.\n"
                f"   - *Example:* \"Reduced backend API response latency by 35% by implementing Redis caching and SQL indexing in Flask.\"\n"
                f"3. **Incorporate Target Role Keywords:** Align with job postings for {target_role} by highlighting your core tools: {', '.join(user_skills[:4]) if user_skills else 'Python, SQL, REST APIs, Git'}.\n"
                f"4. **Quantify Results:** Include measurable outcomes (e.g., test coverage %, query execution times, concurrent users handled).\n\n"
                f"🚀 *Next Step:* Upload your PDF into our [Resume Skill Analyzer](/resume-analyzer) to benchmark your exact coverage against top job profiles!"
            )

        # 3. Salary & Market Demand Queries
        if any(w in msg_lower for w in ['salary', 'pay', 'lpa', 'compensation', 'market demand', 'highest']):
            top_skills = Skill.query.order_by(Skill.salary_max.desc()).limit(4).all()
            skills_bullets = "\n".join([f"- **{s.name}**: ₹{s.salary_min}L – ₹{s.salary_max}L+ LPA (Demand Score: `{s.demand_score}%`)" for s in top_skills])

            return (
                f"### 💼 Market Compensation & High-Demand Skills\n\n"
                f"Here are the most lucrative skills currently tracked on SkillMarket:\n\n"
                f"{skills_bullets}\n\n"
                f"💡 **Career Advice for {username}:**\n"
                f"Specializing in Cloud infrastructure (AWS/Docker) and AI/ML currently provides the strongest salary multiplier over general development roles.\n\n"
                f"Explore our [Market Insights](/analytics) dashboard for live industry trends and regional benchmarks."
            )

        # 4. Roadmap / What to Learn Next Queries
        if any(w in msg_lower for w in ['learn next', 'roadmap', 'study', 'schedule', 'priority', 'what to learn']):
            path = CareerPath.query.filter(CareerPath.name.ilike(f"%{target_role}%")).first() or CareerPath.query.first()
            if path:
                analysis = SkillGapService.analyze(user.id if user else None, path.slug)
                next_skill = analysis['next_priority_skill']
                next_name = next_skill.name if next_skill else 'System Design'
                est_weeks = analysis['estimated_weeks']

                return (
                    f"### 🚀 Your Personalized Learning Blueprint\n\n"
                    f"To reach job readiness for **{path.name}** in approximately **{est_weeks} weeks**:\n\n"
                    f"1. **Immediate Focus: {next_name}**\n"
                    f"   - Dedicate 5–8 hours/week mastering core concepts.\n"
                    f"   - Build a mini-project showcasing real-world implementation.\n"
                    f"2. **Follow the Role Sequence:**\n"
                    f"   - Follow the step-by-step roadmap under [Career Paths](/roadmaps/{path.slug}).\n"
                    f"3. **Proof of Work:**\n"
                    f"   - Commit your code to GitHub with comprehensive README documentation.\n\n"
                    f"Would you like recommended project ideas or interview questions for **{next_name}**?"
                )

        # 5. Interview Preparation Queries
        if any(w in msg_lower for w in ['interview', 'questions', 'prepare', 'coding interview', 'system design']):
            return (
                f"### 🎤 Technical Interview Prep for **{target_role}**\n\n"
                f"Here is how to prepare effectively for your upcoming technical interviews:\n\n"
                f"1. **Core Fundamentals:** Review data structures, relational database indexing, and REST API conventions.\n"
                f"2. **Common Questions:**\n"
                f"   - *How do transactions work in relational databases (ACID properties)?*\n"
                f"   - *Explain the difference between horizontal and vertical scaling.*\n"
                f"   - *How would you diagnose and resolve a slow API endpoint in production?*\n"
                f"3. **Behavioral STAR Technique:** Prepare 2-3 stories detailing a complex technical challenge you solved, a bug you investigated, and how you collaborated with teammates.\n\n"
                f"Feel free to ask me to drill you on specific topics like SQL queries, Docker containers, or Python OOP!"
            )

        # Default Helpful Career Assistant Response
        return (
            f"### 👋 Hello {username}! I'm your SkillMarket Career Assistant.\n\n"
            f"I can help you accelerate your journey toward becoming a top-tier **{target_role}**:\n\n"
            f"- 🎯 **Skill Gap Analysis:** Check your readiness percentage and missing competencies.\n"
            f"- 📄 **Resume Evaluation:** ATS formatting tips and technical impact phrases.\n"
            f"- 💼 **Salary Insights:** Discover highest-paying skill combinations.\n"
            f"- 🗺️ **Learning Roadmaps:** Step-by-step guidance for your target roles.\n\n"
            f"What would you like to explore today? You can try asking:\n"
            f"- *\"What is my skill gap for {target_role}?\"*\n"
            f"- *\"How can I improve my resume for ATS screeners?\"*\n"
            f"- *\"Which skills pay the highest right now?\"*"
        )
