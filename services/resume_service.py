import re
import io
from pypdf import PdfReader
from models import db, Skill, CareerPath, Category

# Comprehensive skill aliases mapped to canonical Skill names
SKILL_ALIASES = {
    'Python': [r'\bpython\b', r'\bpython3\b', r'\bdjango\b', r'\bfastapi\b'],
    'JavaScript': [r'\bjavascript\b', r'\bjs\b', r'\becmascript\b', r'\bes6\b'],
    'React': [r'\breact\b', r'\breactjs\b', r'\breact\.js\b', r'\bredux\b', r'\bnext\.js\b', r'\bnextjs\b'],
    'Node.js': [r'\bnode\.?js\b', r'\bnodejs\b', r'\bexpress\.?js\b', r'\bexpress\b'],
    'Java': [r'\bjava\b(?!script)', r'\bspring\s*boot\b', r'\bspringboot\b', r'\bj2ee\b'],
    'REST APIs': [r'\brest\s*apis?\b', r'\brestful\b', r'\bapi\s*design\b', r'\bjson\s*api\b'],
    'Flask': [r'\bflask\b', r'\bjinja2?\b'],
    'TypeScript': [r'\btypescript\b', r'\bts\b'],
    'SQL': [r'\bsql\b', r'\bpostgresql\b', r'\bpostgres\b', r'\bmysql\b', r'\bsqlite\b', r'\brdbms\b'],
    'Data Science': [r'\bdata\s*science\b', r'\bdata\s*scientist\b', r'\bexploratory\s*data\s*analysis\b', r'\beda\b'],
    'Machine Learning': [r'\bmachine\s*learning\b', r'\bml\b', r'\bscikit-learn\b', r'\bsklearn\b', r'\bclassification\b', r'\bregression\b'],
    'Deep Learning': [r'\bdeep\s*learning\b', r'\bpytorch\b', r'\btensorflow\b', r'\bkeras\b', r'\bneural\s*networks?\b', r'\btransformers?\b', r'\bllms?\b', r'\bnlp\b'],
    'Pandas & NumPy': [r'\bpandas\b', r'\bnumpy\b', r'\bdataframes?\b'],
    'Power BI & Tableau': [r'\bpower\s*bi\b', r'\btableau\b', r'\bdata\s*visualization\b', r'\bbi\s*dashboards?\b'],
    'Cloud Computing (AWS)': [r'\baws\b', r'\bamazon\s*web\s*services\b', r'\bec2\b', r'\bs3\b', r'\blambda\b', r'\bcloud\s*computing\b', r'\bazure\b', r'\bgcp\b'],
    'Docker': [r'\bdocker\b', r'\bcontainers?\b', r'\bcontainerization\b', r'\bdocker\s*compose\b'],
    'Kubernetes': [r'\bkubernetes\b', r'\bk8s\b', r'\bhelm\b'],
    'DevOps & CI/CD': [r'\bdevops\b', r'\bci\s*/\s*cd\b', r'\bcicd\b', r'\bgit\b', r'\bgithub\b', r'\bgitlab\b', r'\bjenkins\b', r'\bgithub\s*actions\b'],
    'Linux & Bash': [r'\blinux\b', r'\bbash\b', r'\bshell\s*scripting\b', r'\bunix\b', r'\bubuntu\b'],
    'Cybersecurity Fundamentals': [r'\bcybersecurity\b', r'\binformation\s*security\b', r'\binfosec\b', r'\bsecurity\s*audit\b'],
    'Ethical Hacking & Penetration Testing': [r'\bethical\s*hacking\b', r'\bpenetration\s*testing\b', r'\bpentesting\b', r'\bkali\s*linux\b', r'\bburp\s*suite\b', r'\bowasp\b'],
    'Network Security': [r'\bnetwork\s*security\b', r'\bwireshark\b', r'\bfirewalls?\b', r'\btcp\s*/\s*ip\b', r'\bvpn\b'],
    'UI/UX Design & Figma': [r'\bfigma\b', r'\bui\s*/\s*ux\b', r'\bux\s*design\b', r'\bui\s*design\b', r'\bwireframing\b', r'\buser\s*research\b'],
    'Design Systems & Prototyping': [r'\bdesign\s*systems?\b', r'\bprototyping\b', r'\binteractive\s*prototypes?\b', r'\bmockups?\b'],
    'Flutter & Dart': [r'\bflutter\b', r'\bdart\b'],
    'React Native': [r'\breact\s*native\b', r'\bexpo\b']
}

class ResumeService:
    @staticmethod
    def extract_text_from_pdf(file_stream, max_pages=15):
        """
        Reads a PDF file in-memory using pypdf and extracts plain text.
        Validates structure and rejects encrypted or corrupt files.
        """
        try:
            reader = PdfReader(file_stream)
            if reader.is_encrypted:
                return None, "This PDF is password-protected or encrypted. Please upload an unprotected PDF."

            total_pages = len(reader.pages)
            if total_pages == 0:
                return None, "The uploaded PDF appears to be empty or contains no pages."

            text_chunks = []
            for i in range(min(total_pages, max_pages)):
                page = reader.pages[i]
                extracted = page.extract_text() or ''
                text_chunks.append(extracted)

            combined_text = "\n".join(text_chunks).strip()
            if not combined_text:
                return None, "No selectable text could be extracted from this PDF. Scanned images without OCR are not supported."

            return combined_text, None
        except Exception as e:
            return None, f"Unable to parse PDF: {str(e)}"

    @staticmethod
    def extract_skills_from_text(text):
        """
        Analyzes plain text, matching against Skill names and regex aliases.
        Returns a dictionary with:
        - detected_skills: list of Skill objects
        - detected_skill_ids: set of integer IDs
        - skill_matches: dict of skill_id -> matched token
        - categorized_skills: dict of category_name -> list of Skill objects
        """
        all_skills = Skill.query.all()
        skills_by_name = {s.name: s for s in all_skills}

        detected_skills = []
        detected_skill_ids = set()
        matched_terms = {}

        # Search against compiled alias regexes
        text_lower = text.lower()

        for canonical_name, patterns in SKILL_ALIASES.items():
            skill_obj = skills_by_name.get(canonical_name)
            if not skill_obj:
                continue

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if skill_obj.id not in detected_skill_ids:
                        detected_skill_ids.add(skill_obj.id)
                        detected_skills.append(skill_obj)
                        matched_terms[skill_obj.id] = match.group(0)
                    break

        # Also search directly for any skill name not covered by aliases
        for s in all_skills:
            if s.id not in detected_skill_ids:
                escaped_name = re.escape(s.name.lower())
                pattern = rf'\b{escaped_name}\b'
                if re.search(pattern, text_lower):
                    detected_skill_ids.add(s.id)
                    detected_skills.append(s)
                    matched_terms[s.id] = s.name

        # Group detected skills by category
        categorized_skills = {}
        for skill in detected_skills:
            cat_name = skill.category.name if skill.category else 'General'
            if cat_name not in categorized_skills:
                categorized_skills[cat_name] = []
            categorized_skills[cat_name].append(skill)

        # Basic word count for metadata
        word_count = len(re.findall(r'\b\w+\b', text))

        return {
            'detected_skills': detected_skills,
            'detected_skill_ids': detected_skill_ids,
            'matched_terms': matched_terms,
            'categorized_skills': categorized_skills,
            'total_detected': len(detected_skills),
            'word_count': word_count
        }

    @staticmethod
    def compare_with_career_path(detected_skill_ids, career_path_id_or_slug):
        """
        Compares extracted skills against a target career path's required steps.
        """
        if isinstance(career_path_id_or_slug, int) or (isinstance(career_path_id_or_slug, str) and str(career_path_id_or_slug).isdigit()):
            career_path = db.session.get(CareerPath, int(career_path_id_or_slug))
        else:
            career_path = CareerPath.query.filter_by(slug=str(career_path_id_or_slug)).first()

        if not career_path:
            return None

        # Required skills for this career path
        required_skills = []
        required_skill_ids = set()

        for step in career_path.steps:
            if step.skill and step.skill.id not in required_skill_ids:
                required_skill_ids.add(step.skill.id)
                required_skills.append(step.skill)

        matched_skills = [s for s in required_skills if s.id in detected_skill_ids]
        missing_skills = [s for s in required_skills if s.id not in detected_skill_ids]

        total_req = len(required_skills)
        match_score = round((len(matched_skills) / total_req) * 100) if total_req > 0 else 0

        # Skills detected on resume that are not strictly required for this path (bonus skills)
        bonus_skills = [s for s in Skill.query.filter(Skill.id.in_(detected_skill_ids)).all() if s.id not in required_skill_ids]

        return {
            'career_path': career_path,
            'required_skills': required_skills,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_score': match_score,
            'bonus_skills': bonus_skills,
            'total_required': total_req
        }
