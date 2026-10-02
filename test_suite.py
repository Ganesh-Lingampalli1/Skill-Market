import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from app import create_app
import io
from models import db, User, Skill, Category, CareerPath, CareerPathSkill, Bookmark, UserProgress, EmailVerification, UserSkill
from services.otp_service import OTPService
from services.email_service import EmailService
from services.skill_gap_service import SkillGapService
from services.resume_service import ResumeService
from services.career_assistant_service import CareerAssistantService

class SkillMarketTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_01_landing_page(self):
        """Test public landing page loads with hero, stats, and trending skills"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Discover Skills That", html)
        self.assertIn("Actually Pay", html)
        self.assertIn("Trending High-Yield Skills", html)
        self.assertIn("How SkillMarket Works", html)

    def test_02_registration_secure_otp_flow(self):
        """Test complete registration, OTP generation, 5-min expiry, no URL leakage, and verification"""
        with self.app.app_context():
            User.query.filter_by(username='alextech').delete()
            EmailVerification.query.filter_by(email='alex@example.com').delete()
            db.session.commit()

        # Step 1: Mock EmailService to simulate successful real SMTP dispatch
        with patch.object(EmailService, 'send_verification_otp', return_value=(True, "Verification code sent to alex@example.com")):
            reg_response = self.client.post('/register', data={
                'username': 'alextech',
                'email': 'alex@example.com'
            }, follow_redirects=False)

            # Assert redirected to /verify-otp?email=alex@example.com&username=alextech
            self.assertEqual(reg_response.status_code, 302)
            location = reg_response.headers.get('Location')
            # Critical Security Check: Assert OTP is NOT in URL query params
            from urllib.parse import urlparse, parse_qs
            query_params = parse_qs(urlparse(location).query)
            self.assertNotIn('otp', query_params)
            self.assertNotIn('dev_otp', query_params)

            # Follow redirect to verify page
            verify_page = self.client.get(location)
            page_html = verify_page.get_data(as_text=True)
            self.assertIn("Verify Your Email", page_html)
            self.assertIn("alex@example.com", page_html)
            self.assertIn("5 minutes", page_html)
            # Critical Security Check: Assert OTP is NOT in page HTML
            self.assertNotIn('dev-otp-display', page_html)

        # Step 2: Retrieve hashed record from database & verify 5-minute expiration
        with self.app.app_context():
            entry = EmailVerification.query.filter_by(email='alex@example.com').first()
            self.assertIsNotNone(entry)
            self.assertFalse(entry.verified)
            # Assert expiry is set to ~5 minutes
            time_diff = (entry.expires_at - entry.created_at).total_seconds()
            self.assertAlmostEqual(time_diff, 300, delta=10)

        # Step 3: Test incorrect OTP
        wrong_response = self.client.post('/verify-otp', data={
            'email': 'alex@example.com',
            'username': 'alextech',
            'otp': '000000'
        }, follow_redirects=True)
        self.assertIn("Invalid OTP. Please try again.", wrong_response.get_data(as_text=True))

        # Step 4: Test Expired OTP (>5 mins)
        with self.app.app_context():
            entry = EmailVerification.query.filter_by(email='alex@example.com').first()
            entry.expires_at = datetime.utcnow() - timedelta(minutes=1)
            db.session.commit()

        expired_response = self.client.post('/verify-otp', data={
            'email': 'alex@example.com',
            'username': 'alextech',
            'otp': '123456'
        }, follow_redirects=True)
        self.assertIn("OTP expired. Please request a new OTP.", expired_response.get_data(as_text=True))

        # Step 5: Test Resend OTP invalidates the old record and creates fresh 5-min OTP
        with patch.object(EmailService, 'send_verification_otp', return_value=(True, "A new 6-digit verification code has been sent")):
            with self.app.app_context():
                # Allow resend by resetting created_at past cooldown
                entry = EmailVerification.query.filter_by(email='alex@example.com').first()
                entry.created_at = datetime.utcnow() - timedelta(seconds=70)
                db.session.commit()

            resend_res = self.client.post('/resend-otp', data={'email': 'alex@example.com'})
            self.assertEqual(resend_res.status_code, 200)
            resend_data = resend_res.get_json()
            self.assertTrue(resend_data['success'])
            # Critical Security Check: Assert OTP is NOT in JSON response
            self.assertNotIn('otp', resend_data)
            self.assertNotIn('dev_otp', resend_data)

        # Step 6: Verify with correct OTP generated by service
        with self.app.app_context():
            fresh_otp = "849201"
            entry = EmailVerification.query.filter_by(email='alex@example.com', verified=False).first()
            entry.otp_hash = OTPService._hash_otp(fresh_otp)
            db.session.commit()

        valid_response = self.client.post('/verify-otp', data={
            'email': 'alex@example.com',
            'username': 'alextech',
            'otp': fresh_otp
        }, follow_redirects=True)
        self.assertEqual(valid_response.status_code, 200)
        self.assertIn("Email verified successfully", valid_response.get_data(as_text=True))

        # Verify user in database is now marked verified
        with self.app.app_context():
            created_user = User.query.filter_by(username='alextech').first()
            self.assertIsNotNone(created_user)
            self.assertTrue(created_user.is_verified)

    def test_02b_unconfigured_smtp_fails_cleanly(self):
        """Test that missing SMTP credentials warns without revealing OTP or demo code"""
        with self.app.app_context():
            # Temporarily clear mail credentials
            orig_user = self.app.config.get('MAIL_USERNAME')
            orig_pass = self.app.config.get('MAIL_PASSWORD')
            self.app.config['MAIL_USERNAME'] = ''
            self.app.config['MAIL_PASSWORD'] = ''

        res = self.client.post('/register', data={
            'username': 'newtester',
            'email': 'newtester@example.com'
        }, follow_redirects=True)

        html = res.get_data(as_text=True)
        # Should show configuration warning
        self.assertIn("Email delivery is not configured", html)
        # MUST NOT leak OTP or demo code
        self.assertNotIn("Dev/Demo", html)
        self.assertNotIn("dev-otp", html)

        with self.app.app_context():
            self.app.config['MAIL_USERNAME'] = orig_user
            self.app.config['MAIL_PASSWORD'] = orig_pass

    def test_03_login_and_authentication(self):
        """Test login with verified credentials and error states"""
        # Test nonexistent account
        res = self.client.post('/login', data={
            'username': 'ghostuser',
            'email': 'ghost@example.com'
        }, follow_redirects=True)
        self.assertIn("Account not found", res.get_data(as_text=True))

        # Test valid login with verified user (alextech)
        login_res = self.client.post('/login', data={
            'username': 'alextech',
            'email': 'alex@example.com'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn("Welcome back, alextech", login_res.get_data(as_text=True))

    def test_04_user_dashboard(self):
        """Test authenticated user dashboard has stats, roadmaps, and recommendations"""
        self.client.post('/login', data={'username': 'alextech', 'email': 'alex@example.com'})
        
        dash_res = self.client.get('/dashboard')
        self.assertEqual(dash_res.status_code, 200)
        html = dash_res.get_data(as_text=True)
        self.assertIn("Ready to build your next career skill?", html)
        self.assertIn("Recommended For You", html)
        self.assertIn("Active Career Roadmap", html)
        self.assertIn("Trending Skills Roadmaps", html)
        self.assertIn("Quick Actions", html)

    def test_05_skills_explore_and_filters(self):
        """Test skills discovery, search, and category filtering"""
        res = self.client.get('/skills')
        self.assertEqual(res.status_code, 200)
        self.assertIn("Python", res.get_data(as_text=True))

        search_res = self.client.get('/skills?q=Docker')
        self.assertEqual(search_res.status_code, 200)
        self.assertIn("Docker", search_res.get_data(as_text=True))

        cat_res = self.client.get('/skills?category=data-and-ai')
        self.assertEqual(cat_res.status_code, 200)
        self.assertIn("Data Science", cat_res.get_data(as_text=True))

        detail_res = self.client.get('/skills/python')
        self.assertEqual(detail_res.status_code, 200)
        html = detail_res.get_data(as_text=True)
        self.assertIn("Market Insights & Compensation", html)
        self.assertIn("Verified Learning Resources", html)

    def test_06_bookmarks_async_toggle(self):
        """Test bookmarking skill and persistence"""
        self.client.post('/login', data={'username': 'alextech', 'email': 'alex@example.com'})
        
        with self.app.app_context():
            user = User.query.filter_by(username='alextech').first()
            skill = Skill.query.first()
            Bookmark.query.filter_by(user_id=user.id, skill_id=skill.id).delete()
            db.session.commit()
            skill_id = skill.id

        res = self.client.post(f'/bookmarks/toggle/{skill_id}', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['bookmarked'])

        res2 = self.client.post(f'/bookmarks/toggle/{skill_id}', headers={'X-Requested-With': 'XMLHttpRequest'})
        data2 = res2.get_json()
        self.assertFalse(data2['bookmarked'])

    def test_07_roadmap_progress_toggle(self):
        """Test interactive roadmap step completion toggle and percentage calculation"""
        self.client.post('/login', data={'username': 'alextech', 'email': 'alex@example.com'})

        with self.app.app_context():
            path = CareerPath.query.first()
            step = path.steps[0]
            path_id = path.id
            step_id = step.id

        res = self.client.post(f'/roadmaps/{path_id}/step/{step_id}/toggle', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('progress_percentage', data)

    def test_08_theme_persistence_api(self):
        """Test persistent theme updates saved to database"""
        self.client.post('/login', data={'username': 'alextech', 'email': 'alex@example.com'})

        res = self.client.post('/api/theme', json={'theme': 'dark'})
        self.assertEqual(res.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(username='alextech').first()
            self.assertEqual(user.theme_preference, 'dark')

        res2 = self.client.post('/api/theme', json={'theme': 'light'})
        self.assertEqual(res2.status_code, 200)
        with self.app.app_context():
            user = User.query.filter_by(username='alextech').first()
            self.assertEqual(user.theme_preference, 'light')

    def test_09_analytics_and_charts_api(self):
        """Test analytics page and Chart.js data API endpoint"""
        res = self.client.get('/analytics')
        self.assertEqual(res.status_code, 200)
        self.assertIn("Salary & Market Analytics", res.get_data(as_text=True))

        api_res = self.client.get('/api/analytics/charts')
        self.assertEqual(api_res.status_code, 200)
        data = api_res.get_json()
        self.assertIn('salary_chart', data)
        self.assertIn('demand_chart', data)
        self.assertIn('category_chart', data)

    def test_10_admin_operations(self):
        """Test admin authentication, authorization protection, and CRUD operations"""
        self.client.post('/login', data={'username': 'alextech', 'email': 'alex@example.com'})
        blocked_res = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn("Access denied", blocked_res.get_data(as_text=True))

        with self.app.app_context():
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                admin_user = User(username='testadmin', email='admin@skillmarket.com', is_admin=True, is_verified=True)
                db.session.add(admin_user)
                db.session.commit()
            admin_username = admin_user.username
            admin_email = admin_user.email

        admin_login = self.client.post('/admin/login', data={
            'username': admin_username,
            'email': admin_email
        }, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)
        self.assertIn("System Overview", admin_login.get_data(as_text=True))

        with self.app.app_context():
            cat = Category.query.first()
            cat_id = cat.id

        add_res = self.client.post('/admin/skills/add', data={
            'name': 'Golang Microservices',
            'category_id': cat_id,
            'description': 'High-performance cloud-native backend services written in Go.',
            'difficulty': 'Intermediate',
            'demand_score': '91',
            'salary_min': '8',
            'salary_max': '24',
            'learning_duration': '6-8 weeks',
            'trending': '1'
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn("added successfully", add_res.get_data(as_text=True))

        with self.app.app_context():
            new_skill = Skill.query.filter_by(name='Golang Microservices').first()
            self.assertIsNotNone(new_skill)
            skill_id = new_skill.id

        del_res = self.client.post(f'/admin/skills/{skill_id}/delete', follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)

        with self.app.app_context():
            self.assertIsNone(db.session.get(Skill, skill_id))

    def test_11_skill_gap_analyzer(self):
        """Test Skill Gap Analyzer: auth protection, role selection, gap calculation, readiness %, learning order, and API"""
        # 1. Unauthenticated access redirects to login
        self.client.get('/logout')
        anon_res = self.client.get('/skill-gap')
        self.assertEqual(anon_res.status_code, 302)
        self.assertIn('/login', anon_res.headers.get('Location'))

        # 2. Authenticated access
        with self.app.app_context():
            user = User.query.filter_by(username='bharat777').first()
            user_id = user.id
            career_path = CareerPath.query.filter_by(slug='python-backend-developer').first()
            path_id = career_path.id
            path_slug = career_path.slug

            # Clean previous user skills for a deterministic baseline
            UserSkill.query.filter_by(user_id=user_id).delete()
            db.session.commit()

        # Login user
        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id

        # GET /skill-gap
        res_page = self.client.get('/skill-gap')
        self.assertEqual(res_page.status_code, 200)
        self.assertIn("Skill Gap Analyzer", res_page.get_data(as_text=True))

        # 3. Calculation with 0 skills
        with self.app.app_context():
            analysis_zero = SkillGapService.analyze(user_id, path_slug)
            self.assertEqual(analysis_zero['readiness_score'], 0)
            self.assertEqual(len(analysis_zero['matched_skills']), 0)
            self.assertGreater(len(analysis_zero['missing_skills']), 0)
            total_req = analysis_zero['total_required']

            # Add 2 skills (Python and SQL)
            python_skill = Skill.query.filter_by(name='Python').first()
            sql_skill = Skill.query.filter_by(name='SQL').first()
            SkillGapService.add_user_skill(user_id, python_skill.id, source='manual')
            SkillGapService.add_user_skill(user_id, sql_skill.id, source='manual')

            # 4. Calculation with matched skills
            analysis_partial = SkillGapService.analyze(user_id, path_slug)
            expected_score = round((2 / total_req) * 100)
            self.assertEqual(analysis_partial['readiness_score'], expected_score)
            self.assertEqual(len(analysis_partial['matched_skills']), 2)
            self.assertIn(python_skill, analysis_partial['matched_skills'])
            self.assertIn(sql_skill, analysis_partial['matched_skills'])

            # Recommendation sequence & next priority
            self.assertIsNotNone(analysis_partial['next_priority_skill'])
            self.assertEqual(analysis_partial['next_priority_skill'], analysis_partial['recommended_learning_order'][0])

        # 5. Form POST /skill-gap/analyze redirects to result
        post_res = self.client.post('/skill-gap/analyze', data={
            'career_path_id': path_id
        }, follow_redirects=False)
        self.assertEqual(post_res.status_code, 302)
        self.assertIn(f'/skill-gap/result/{path_slug}', post_res.headers.get('Location'))

        # GET /skill-gap/result/<slug>
        result_page = self.client.get(f'/skill-gap/result/{path_slug}')
        self.assertEqual(result_page.status_code, 200)
        self.assertIn("Skill Gap:", result_page.get_data(as_text=True))
        self.assertIn(f"{expected_score}%", result_page.get_data(as_text=True))

        # 6. Test JSON preview API
        api_res = self.client.get(f'/api/skill-gap/preview/{path_slug}')
        self.assertEqual(api_res.status_code, 200)
        api_data = api_res.get_json()
        self.assertEqual(api_data['readiness_score'], expected_score)
        self.assertIn('Python', api_data['matched_skills'])

        # Clean up
        with self.app.app_context():
            UserSkill.query.filter_by(user_id=user_id).delete()
            db.session.commit()

    def test_12_resume_skill_analyzer(self):
        """Test Resume Skill Analyzer: file format validation, size limits, alias matching, role comparison, review and confirmation"""
        with self.app.app_context():
            user = User.query.filter_by(username='bharat777').first()
            user_id = user.id

        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id

        # 1. GET /resume-analyzer page
        page_res = self.client.get('/resume-analyzer')
        self.assertEqual(page_res.status_code, 200)
        self.assertIn("Resume Skill Analyzer", page_res.get_data(as_text=True))

        # 2. Reject non-PDF file
        txt_file = (io.BytesIO(b"Hello world"), 'resume.txt')
        bad_format_res = self.client.post('/resume-analyzer/upload', data={
            'resume_file': txt_file
        }, follow_redirects=True)
        self.assertIn("Invalid file format", bad_format_res.get_data(as_text=True))

        # 3. Reject oversized payload (> 5MB)
        large_bytes = io.BytesIO(b"x" * (6 * 1024 * 1024))
        large_file = (large_bytes, 'large_resume.pdf')
        oversized_res = self.client.post('/resume-analyzer/upload', data={
            'resume_file': large_file
        }, follow_redirects=True)
        self.assertIn("exceeds the 5MB limit", oversized_res.get_data(as_text=True))

        # 4. Text skill extraction and alias matching verification
        sample_text = """
        Technical Expertise:
        Languages & Frameworks: Python, Flask, Django, JS, React, Node.js.
        Databases & Cloud: PostgreSQL, AWS EC2, S3, Docker, Kubernetes.
        Practices: CI/CD, Git, Linux scripting, Ethical Hacking, Figma design.
        """
        with self.app.app_context():
            extracted = ResumeService.extract_skills_from_text(sample_text)
            detected_names = {s.name for s in extracted['detected_skills']}

            self.assertIn('Python', detected_names)
            self.assertIn('Flask', detected_names)
            self.assertIn('JavaScript', detected_names)  # Mapped from 'JS'
            self.assertIn('SQL', detected_names)         # Mapped from 'PostgreSQL'
            self.assertIn('Cloud Computing (AWS)', detected_names) # Mapped from 'AWS'
            self.assertIn('Docker', detected_names)
            self.assertIn('DevOps & CI/CD', detected_names) # Mapped from 'CI/CD' / 'Git'

            # 5. Target career comparison
            career_path = CareerPath.query.filter_by(slug='python-backend-developer').first()
            comparison = ResumeService.compare_with_career_path(extracted['detected_skill_ids'], career_path.id)
            self.assertIsNotNone(comparison)
            self.assertGreater(comparison['match_score'], 0)
            self.assertGreater(len(comparison['matched_skills']), 0)

        # 6. Session-based review and confirmation flow (no auto-update)
        with self.app.app_context():
            python_skill = Skill.query.filter_by(name='Python').first()
            docker_skill = Skill.query.filter_by(name='Docker').first()
            python_id = python_skill.id
            docker_id = docker_skill.id
            UserSkill.query.filter_by(user_id=user_id).delete()
            db.session.commit()

        # Populate review session
        with self.client.session_transaction() as sess:
            sess['resume_analysis'] = {
                'filename': 'my_resume.pdf',
                'detected_skill_ids': [python_id, docker_id],
                'total_detected': 2,
                'word_count': 180,
                'target_path_id': 1
            }

        result_page = self.client.get('/resume-analyzer/result')
        self.assertEqual(result_page.status_code, 200)
        self.assertIn("Identified 2 Technical Skills", result_page.get_data(as_text=True))
        self.assertIn("Review & Confirm Skills to Sync", result_page.get_data(as_text=True))

        # Explicit user confirmation: only select python_id
        save_res = self.client.post('/resume-analyzer/save-skills', data={
            'confirmed_skills': [python_id],
            'target_path_id': 1
        }, follow_redirects=True)
        self.assertEqual(save_res.status_code, 200)

        # Assert only explicitly confirmed skill is saved
        with self.app.app_context():
            saved_python = UserSkill.query.filter_by(user_id=user_id, skill_id=python_id).first()
            saved_docker = UserSkill.query.filter_by(user_id=user_id, skill_id=docker_id).first()
            self.assertIsNotNone(saved_python)
            self.assertEqual(saved_python.source, 'resume')
            self.assertIsNone(saved_docker)  # Unselected skill was not added

            # Cleanup
            UserSkill.query.filter_by(user_id=user_id).delete()
            db.session.commit()

    def test_13_ai_career_assistant(self):
        """Test AI Career Assistant: chat endpoint, validation, dual-mode fallback, context awareness, and error handling"""
        with self.app.app_context():
            user = User.query.filter_by(username='bharat777').first()
            user_id = user.id

        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id

        # 1. Validation: empty message rejected with 400
        empty_res = self.client.post('/api/ai/chat', json={'message': '   '})
        self.assertEqual(empty_res.status_code, 400)

        # 2. Context retrieval endpoint
        ctx_res = self.client.get('/api/ai/context')
        self.assertEqual(ctx_res.status_code, 200)
        ctx_data = ctx_res.get_json()
        self.assertEqual(ctx_data['user']['username'], 'bharat777')
        self.assertGreater(len(ctx_data['default_suggestions']), 0)

        # 3. Dual-mode fallback: with no AI_API_KEY, fallback to local rule engine
        chat_res = self.client.post('/api/ai/chat', json={
            'message': 'What are my skill gaps for Python Backend Developer?',
            'page_context': {
                'url': '/skill-gap/result/python-backend-developer',
                'title': 'Skill Gap: Python Backend Developer',
                'role': 'Python Backend Developer',
                'score': 45,
                'missing': 'Docker, Kubernetes'
            }
        })
        self.assertEqual(chat_res.status_code, 200)
        chat_data = chat_res.get_json()
        self.assertEqual(chat_data['source'], 'rule_engine')
        self.assertIn('Skill Gap Assessment', chat_data['reply'])
        self.assertGreater(len(chat_data['suggestions']), 0)

        # 4. External API failure simulation: verify graceful fallback to rule engine
        with patch.object(CareerAssistantService, '_call_gemini_api', side_effect=Exception("Connection timeout")):
            with patch.dict(self.app.config, {'AI_API_KEY': 'dummy_key'}):
                safe_res = self.client.post('/api/ai/chat', json={
                    'message': 'How can I optimize my resume bullet points?'
                })
                self.assertEqual(safe_res.status_code, 200)
                safe_data = safe_res.get_json()
                self.assertEqual(safe_data['source'], 'rule_engine')
                self.assertIn('Resume Optimization Strategy', safe_data['reply'])

if __name__ == '__main__':
    unittest.main()
