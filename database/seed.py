import os
import sys
from datetime import datetime

# Add root directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import (
    db, User, Category, Skill, Resource, CareerPath,
    CareerPathSkill, RoadmapResource, Bookmark, UserProgress
)

app = create_app()

def seed_database():
    with app.app_context():
        print("Ensuring database tables exist...")
        db.create_all()

        print("Checking Demo Users...")
        if not User.query.filter_by(username='bharat').first():
            user_bharat = User(
                username='bharat',
                email='bharat@example.com',
                is_verified=True,
                theme_preference='dark',
                career_interest='Web Development',
                experience_level='Intermediate',
                is_admin=False,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.session.add(user_bharat)

        if not User.query.filter_by(username='admin').first():
            user_admin = User(
                username='admin',
                email='admin@skillmarket.com',
                is_verified=True,
                theme_preference='dark',
                career_interest='Cloud & DevOps',
                experience_level='Advanced',
                is_admin=True,
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            db.session.add(user_admin)
        db.session.commit()

        print("Seeding Categories...")
        categories_data = [
            {
                'name': 'Software Development',
                'slug': 'software-development',
                'description': 'Frontend, backend, full-stack, and enterprise software engineering.',
                'icon': 'code-2'
            },
            {
                'name': 'Data & AI',
                'slug': 'data-and-ai',
                'description': 'Data analytics, engineering, machine learning, and generative artificial intelligence.',
                'icon': 'brain'
            },
            {
                'name': 'Cloud & DevOps',
                'slug': 'cloud-and-devops',
                'description': 'Cloud architecture, infrastructure as code, CI/CD, and system operations.',
                'icon': 'cloud'
            },
            {
                'name': 'Cybersecurity',
                'slug': 'cybersecurity',
                'description': 'Information security, ethical hacking, network defense, and compliance.',
                'icon': 'shield-check'
            },
            {
                'name': 'UI/UX Design',
                'slug': 'ui-ux-design',
                'description': 'User experience design, visual design, design systems, and rapid prototyping.',
                'icon': 'palette'
            },
            {
                'name': 'Mobile Development',
                'slug': 'mobile-development',
                'description': 'Native and cross-platform mobile apps for iOS and Android ecosystems.',
                'icon': 'smartphone'
            }
        ]

        cat_objs = {}
        for cat in categories_data:
            c = Category(**cat)
            db.session.add(c)
            cat_objs[cat['slug']] = c
        db.session.commit()

        print("Seeding Skills...")
        skills_data = [
            # Software Development
            {
                'name': 'Python',
                'slug': 'python',
                'category_id': cat_objs['software-development'].id,
                'description': 'A versatile, high-level programming language used extensively across web development, backend automation, and artificial intelligence.',
                'difficulty': 'Beginner',
                'demand_score': 95,
                'salary_min': 5,
                'salary_max': 18,
                'learning_duration': '6-8 weeks',
                'icon': 'file-code',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'JavaScript',
                'slug': 'javascript',
                'category_id': cat_objs['software-development'].id,
                'description': 'The standard scripting language of the web that powers client-side interfaces and scalable backend services with Node.js.',
                'difficulty': 'Beginner',
                'demand_score': 94,
                'salary_min': 5,
                'salary_max': 16,
                'learning_duration': '6-8 weeks',
                'icon': 'code',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'React',
                'slug': 'react',
                'category_id': cat_objs['software-development'].id,
                'description': 'A popular declarative JavaScript library for building responsive and interactive user interfaces with reusable component state.',
                'difficulty': 'Intermediate',
                'demand_score': 92,
                'salary_min': 6,
                'salary_max': 20,
                'learning_duration': '8-10 weeks',
                'icon': 'atom',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Node.js',
                'slug': 'nodejs',
                'category_id': cat_objs['software-development'].id,
                'description': 'Asynchronous event-driven JavaScript runtime designed to build scalable network applications and RESTful APIs.',
                'difficulty': 'Intermediate',
                'demand_score': 88,
                'salary_min': 6,
                'salary_max': 18,
                'learning_duration': '6-8 weeks',
                'icon': 'server',
                'market_demand': 'High',
                'trending': False
            },
            {
                'name': 'Java',
                'slug': 'java',
                'category_id': cat_objs['software-development'].id,
                'description': 'Robust, object-oriented language dominating enterprise backends, high-throughput architectures, and Android development.',
                'difficulty': 'Intermediate',
                'demand_score': 89,
                'salary_min': 6,
                'salary_max': 22,
                'learning_duration': '10-12 weeks',
                'icon': 'coffee',
                'market_demand': 'High',
                'trending': False
            },
            {
                'name': 'REST APIs',
                'slug': 'rest-apis',
                'category_id': cat_objs['software-development'].id,
                'description': 'Representational State Transfer architectural pattern enabling seamless HTTP-based client-server communications.',
                'difficulty': 'Beginner',
                'demand_score': 91,
                'salary_min': 5,
                'salary_max': 16,
                'learning_duration': '3-4 weeks',
                'icon': 'network',
                'market_demand': 'Very High',
                'trending': False
            },
            {
                'name': 'Flask',
                'slug': 'flask',
                'category_id': cat_objs['software-development'].id,
                'description': 'Lightweight WSGI Python micro-framework for rapidly engineering extensible web applications and microservice APIs.',
                'difficulty': 'Beginner',
                'demand_score': 82,
                'salary_min': 5,
                'salary_max': 14,
                'learning_duration': '4-6 weeks',
                'icon': 'terminal',
                'market_demand': 'High',
                'trending': False
            },
            {
                'name': 'TypeScript',
                'slug': 'typescript',
                'category_id': cat_objs['software-development'].id,
                'description': 'Typed superset of JavaScript that compiles to plain JavaScript, greatly increasing code reliability and refactor confidence.',
                'difficulty': 'Intermediate',
                'demand_score': 90,
                'salary_min': 7,
                'salary_max': 22,
                'learning_duration': '4-6 weeks',
                'icon': 'file-type',
                'market_demand': 'Very High',
                'trending': True
            },

            # Data & AI
            {
                'name': 'SQL',
                'slug': 'sql',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Standard language for storing, querying, and managing relational databases, indispensable across every technical discipline.',
                'difficulty': 'Beginner',
                'demand_score': 96,
                'salary_min': 5,
                'salary_max': 17,
                'learning_duration': '4-5 weeks',
                'icon': 'database',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Data Science',
                'slug': 'data-science',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Multidisciplinary domain combining scientific computing, exploratory data analysis, statistics, and business insight extraction.',
                'difficulty': 'Intermediate',
                'demand_score': 93,
                'salary_min': 7,
                'salary_max': 24,
                'learning_duration': '12-16 weeks',
                'icon': 'line-chart',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Machine Learning',
                'slug': 'machine-learning',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Algorithms and statistical models that computer systems use to perform tasks without explicit step-by-step instructions.',
                'difficulty': 'Advanced',
                'demand_score': 94,
                'salary_min': 8,
                'salary_max': 28,
                'learning_duration': '14-18 weeks',
                'icon': 'cpu',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Deep Learning',
                'slug': 'deep-learning',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Subset of machine learning based on multi-layered artificial neural networks powering computer vision, speech, and LLMs.',
                'difficulty': 'Advanced',
                'demand_score': 91,
                'salary_min': 10,
                'salary_max': 32,
                'learning_duration': '16-20 weeks',
                'icon': 'layers',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Pandas & NumPy',
                'slug': 'pandas-numpy',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Core numerical computing and dataframe manipulation libraries for Python scientific workflows.',
                'difficulty': 'Beginner',
                'demand_score': 87,
                'salary_min': 5,
                'salary_max': 16,
                'learning_duration': '4-6 weeks',
                'icon': 'table',
                'market_demand': 'High',
                'trending': False
            },
            {
                'name': 'Power BI & Tableau',
                'slug': 'powerbi-tableau',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Business intelligence and interactive data visualization suites used by corporate stakeholders to drive decisions.',
                'difficulty': 'Beginner',
                'demand_score': 86,
                'salary_min': 5,
                'salary_max': 15,
                'learning_duration': '4-6 weeks',
                'icon': 'pie-chart',
                'market_demand': 'High',
                'trending': False
            },

            # Cloud & DevOps
            {
                'name': 'Cloud Computing (AWS)',
                'slug': 'cloud-computing-aws',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'Architecting resilient, secure, and scalable cloud solutions using Amazon Web Services core infrastructure.',
                'difficulty': 'Intermediate',
                'demand_score': 93,
                'salary_min': 7,
                'salary_max': 25,
                'learning_duration': '8-12 weeks',
                'icon': 'cloud-rain',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Docker',
                'slug': 'docker',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'OS-level virtualization platform to package applications and their dependencies into lightweight, portable containers.',
                'difficulty': 'Intermediate',
                'demand_score': 91,
                'salary_min': 6,
                'salary_max': 20,
                'learning_duration': '4-6 weeks',
                'icon': 'container',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Kubernetes',
                'slug': 'kubernetes',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'Open-source container orchestration system for automating application deployment, scaling, and operational management.',
                'difficulty': 'Advanced',
                'demand_score': 90,
                'salary_min': 9,
                'salary_max': 30,
                'learning_duration': '8-12 weeks',
                'icon': 'boxes',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'DevOps & CI/CD',
                'slug': 'devops-cicd',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'Methodologies and pipeline tooling (GitHub Actions, Jenkins) bridging software development with automated system operations.',
                'difficulty': 'Intermediate',
                'demand_score': 92,
                'salary_min': 7,
                'salary_max': 24,
                'learning_duration': '8-10 weeks',
                'icon': 'git-merge',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Linux & Bash',
                'slug': 'linux-bash',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'Command-line administration, process scheduling, shell automation, and operating system internals.',
                'difficulty': 'Beginner',
                'demand_score': 89,
                'salary_min': 5,
                'salary_max': 16,
                'learning_duration': '4-6 weeks',
                'icon': 'terminal',
                'market_demand': 'High',
                'trending': False
            },

            # Cybersecurity
            {
                'name': 'Cybersecurity Fundamentals',
                'slug': 'cybersecurity-fundamentals',
                'category_id': cat_objs['cybersecurity'].id,
                'description': 'Core principles of information security, threat vectors, cryptography fundamentals, and defense-in-depth strategies.',
                'difficulty': 'Beginner',
                'demand_score': 88,
                'salary_min': 6,
                'salary_max': 19,
                'learning_duration': '6-8 weeks',
                'icon': 'shield',
                'market_demand': 'High',
                'trending': True
            },
            {
                'name': 'Ethical Hacking & Penetration Testing',
                'slug': 'ethical-hacking',
                'category_id': cat_objs['cybersecurity'].id,
                'description': 'Authoritative penetration testing methodologies, vulnerability assessments, and exploitation tooling (Burp Suite, Metasploit).',
                'difficulty': 'Advanced',
                'demand_score': 89,
                'salary_min': 8,
                'salary_max': 26,
                'learning_duration': '12-16 weeks',
                'icon': 'key',
                'market_demand': 'Very High',
                'trending': True
            },
            {
                'name': 'Network Security',
                'slug': 'network-security',
                'category_id': cat_objs['cybersecurity'].id,
                'description': 'Protocols, firewalls, intrusion detection systems (IDS/IPS), VPNs, and packet analysis using Wireshark.',
                'difficulty': 'Intermediate',
                'demand_score': 85,
                'salary_min': 6,
                'salary_max': 18,
                'learning_duration': '6-8 weeks',
                'icon': 'wifi',
                'market_demand': 'High',
                'trending': False
            },

            # UI/UX Design
            {
                'name': 'UI/UX Design & Figma',
                'slug': 'ui-ux-design-figma',
                'category_id': cat_objs['ui-ux-design'].id,
                'description': 'User experience research, wireframing, high-fidelity UI design systems, and clickable interactive prototypes in Figma.',
                'difficulty': 'Beginner',
                'demand_score': 87,
                'salary_min': 5,
                'salary_max': 17,
                'learning_duration': '6-8 weeks',
                'icon': 'figma',
                'market_demand': 'High',
                'trending': True
            },
            {
                'name': 'Design Systems & Prototyping',
                'slug': 'design-systems',
                'category_id': cat_objs['ui-ux-design'].id,
                'description': 'Building atomic component libraries, tokenized design architectures, and accessible interactive workflows.',
                'difficulty': 'Intermediate',
                'demand_score': 84,
                'salary_min': 6,
                'salary_max': 18,
                'learning_duration': '4-6 weeks',
                'icon': 'component',
                'market_demand': 'High',
                'trending': False
            },

            # Mobile Development
            {
                'name': 'Flutter & Dart',
                'slug': 'flutter-dart',
                'category_id': cat_objs['mobile-development'].id,
                'description': 'Google UI toolkit for natively compiling cross-platform mobile, web, and desktop applications from a single codebase.',
                'difficulty': 'Intermediate',
                'demand_score': 86,
                'salary_min': 6,
                'salary_max': 19,
                'learning_duration': '8-10 weeks',
                'icon': 'smartphone',
                'market_demand': 'High',
                'trending': False
            },
            {
                'name': 'React Native',
                'slug': 'react-native',
                'category_id': cat_objs['mobile-development'].id,
                'description': 'Cross-platform mobile framework allowing React developers to craft fluid native iOS and Android experiences with JavaScript.',
                'difficulty': 'Intermediate',
                'demand_score': 88,
                'salary_min': 6,
                'salary_max': 21,
                'learning_duration': '8-10 weeks',
                'icon': 'tablet',
                'market_demand': 'High',
                'trending': True
            }
        ]

        skill_objs = {}
        for sdata in skills_data:
            s = Skill(**sdata)
            db.session.add(s)
            skill_objs[sdata['slug']] = s
        db.session.commit()

        print("Seeding Learning Resources...")
        resources_data = [
            # Python
            {
                'skill_id': skill_objs['python'].id,
                'title': 'Official Python 3 Documentation',
                'description': 'Comprehensive language reference, tutorials, and standard library guides directly from Python.org.',
                'url': 'https://docs.python.org/3/',
                'type': 'Documentation',
                'provider': 'Python Software Foundation',
                'is_free': True
            },
            {
                'skill_id': skill_objs['python'].id,
                'title': 'Python for Beginners (Full Course)',
                'description': 'Comprehensive 4-hour crash course covering variables, collections, loops, and OOP fundamentals.',
                'url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',
                'type': 'Video Course',
                'provider': 'freeCodeCamp',
                'is_free': True
            },
            {
                'skill_id': skill_objs['python'].id,
                'title': 'Exercism Python Track',
                'description': '140+ hands-on coding exercises with automated testing and community mentor feedback.',
                'url': 'https://exercism.org/tracks/python',
                'type': 'Practice',
                'provider': 'Exercism',
                'is_free': True
            },
            {
                'skill_id': skill_objs['python'].id,
                'title': 'Python for Everybody Specialization',
                'description': 'Top-rated introductory academic specialization teaching foundational programming with Python.',
                'url': 'https://www.coursera.org/specializations/python',
                'type': 'Course',
                'provider': 'University of Michigan / Coursera',
                'is_free': False
            },

            # JavaScript
            {
                'skill_id': skill_objs['javascript'].id,
                'title': 'MDN Web Docs - JavaScript Guide',
                'description': 'The industry gold standard guide to modern ES6+ JavaScript, syntax, and Web APIs.',
                'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript',
                'type': 'Documentation',
                'provider': 'Mozilla Developer Network',
                'is_free': True
            },
            {
                'skill_id': skill_objs['javascript'].id,
                'title': 'JavaScript Algorithms and Data Structures',
                'description': 'Interactive curriculum mastering fundamentals, regular expressions, and algorithmic scripting.',
                'url': 'https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/',
                'type': 'Practice',
                'provider': 'freeCodeCamp',
                'is_free': True
            },

            # React
            {
                'skill_id': skill_objs['react'].id,
                'title': 'React Official Documentation (react.dev)',
                'description': 'Interactive docs teaching state, props, effect hooks, and modern React best practices.',
                'url': 'https://react.dev',
                'type': 'Documentation',
                'provider': 'Meta Open Source',
                'is_free': True
            },
            {
                'skill_id': skill_objs['react'].id,
                'title': 'Epic React Workshop Series',
                'description': 'Deep architectural dive into React hooks, performance optimization, and application patterns.',
                'url': 'https://epicreact.dev',
                'type': 'Course',
                'provider': 'Kent C. Dodds',
                'is_free': False
            },

            # SQL
            {
                'skill_id': skill_objs['sql'].id,
                'title': 'PostgreSQL Official Documentation',
                'description': 'Complete manual for the worlds most advanced open-source relational database.',
                'url': 'https://www.postgresql.org/docs/',
                'type': 'Documentation',
                'provider': 'PostgreSQL Global Development Group',
                'is_free': True
            },
            {
                'skill_id': skill_objs['sql'].id,
                'title': 'SQLBolt - Interactive SQL Lessons',
                'description': 'Series of interactive lessons and queries that run directly in your browser.',
                'url': 'https://sqlbolt.com/',
                'type': 'Practice',
                'provider': 'SQLBolt',
                'is_free': True
            },
            {
                'skill_id': skill_objs['sql'].id,
                'title': 'LeetCode SQL Study Plan',
                'description': 'Curated collection of 50 essential SQL interview problems from top tech firms.',
                'url': 'https://leetcode.com/studyplan/top-sql-50/',
                'type': 'Practice',
                'provider': 'LeetCode',
                'is_free': True
            },

            # Docker
            {
                'skill_id': skill_objs['docker'].id,
                'title': 'Docker Official Documentation & Guides',
                'description': 'Step-by-step guides for Dockerfiles, images, containers, networks, and compose.',
                'url': 'https://docs.docker.com/',
                'type': 'Documentation',
                'provider': 'Docker Inc.',
                'is_free': True
            },
            {
                'skill_id': skill_objs['docker'].id,
                'title': 'Docker Tutorial for Beginners',
                'description': 'Full hands-on video covering containerization, volume mounting, and microservice setups.',
                'url': 'https://www.youtube.com/watch?v=3c-iBn73dDE',
                'type': 'Video Course',
                'provider': 'TechWorld with Nana',
                'is_free': True
            },

            # AWS
            {
                'skill_id': skill_objs['cloud-computing-aws'].id,
                'title': 'AWS Skill Builder Training',
                'description': 'Official cloud learning library by Amazon Web Services for certification and architecture.',
                'url': 'https://explore.skillbuilder.aws/',
                'type': 'Course',
                'provider': 'Amazon Web Services',
                'is_free': True
            },
            {
                'skill_id': skill_objs['cloud-computing-aws'].id,
                'title': 'AWS Certified Cloud Practitioner Training',
                'description': 'Complete 13-hour video course covering EC2, S3, RDS, IAM, VPC, and serverless compute.',
                'url': 'https://www.youtube.com/watch?v=SOTamWNgDKc',
                'type': 'Video Course',
                'provider': 'freeCodeCamp',
                'is_free': True
            },

            # Machine Learning
            {
                'skill_id': skill_objs['machine-learning'].id,
                'title': 'Scikit-Learn User Guide',
                'description': 'Exhaustive documentation for regression, classification, clustering, and model evaluation.',
                'url': 'https://scikit-learn.org/stable/user_guide.html',
                'type': 'Documentation',
                'provider': 'Scikit-Learn Community',
                'is_free': True
            },
            {
                'skill_id': skill_objs['machine-learning'].id,
                'title': 'Machine Learning Specialization',
                'description': 'Foundational AI course taught by Andrew Ng covering supervised and unsupervised learning.',
                'url': 'https://www.coursera.org/specializations/machine-learning-introduction',
                'type': 'Course',
                'provider': 'DeepLearning.AI / Stanford',
                'is_free': False
            },

            # Kubernetes
            {
                'skill_id': skill_objs['kubernetes'].id,
                'title': 'Kubernetes Basics Interactive Tutorials',
                'description': 'Official interactive walkthrough of pods, deployments, services, and rolling updates.',
                'url': 'https://kubernetes.io/docs/tutorials/kubernetes-basics/',
                'type': 'Documentation',
                'provider': 'Cloud Native Computing Foundation',
                'is_free': True
            },

            # Cybersecurity
            {
                'skill_id': skill_objs['cybersecurity-fundamentals'].id,
                'title': 'TryHackMe - Pre-Security Path',
                'description': 'Hands-on browser-based labs covering networking fundamentals, web basics, and Linux.',
                'url': 'https://tryhackme.com/path/outline/presecurity',
                'type': 'Practice',
                'provider': 'TryHackMe',
                'is_free': True
            },

            # UI/UX Figma
            {
                'skill_id': skill_objs['ui-ux-design-figma'].id,
                'title': 'Figma Design Handbook & Tutorials',
                'description': 'Learn autolayout, components, variants, variables, and interactive prototyping.',
                'url': 'https://help.figma.com/hc/en-us',
                'type': 'Documentation',
                'provider': 'Figma',
                'is_free': True
            },

            # REST APIs
            {
                'skill_id': skill_objs['rest-apis'].id,
                'title': 'Postman API Fundamentals Student Expert',
                'description': 'Hands-on certification learning REST request anatomy, auth, tests, and mock servers.',
                'url': 'https://academy.postman.com/',
                'type': 'Practice',
                'provider': 'Postman',
                'is_free': True
            },

            # Flask
            {
                'skill_id': skill_objs['flask'].id,
                'title': 'Flask Quickstart and Pattern Guide',
                'description': 'The official Pallets project documentation for routing, blueprints, templates, and sessions.',
                'url': 'https://flask.palletsprojects.com/',
                'type': 'Documentation',
                'provider': 'Pallets Projects',
                'is_free': True
            }
        ]

        resource_objs = []
        for rdata in resources_data:
            r = Resource(**rdata)
            db.session.add(r)
            resource_objs.append(r)
        db.session.commit()

        print("Seeding Career Paths & Roadmaps...")
        career_paths_data = [
            {
                'name': 'Python Backend Developer',
                'slug': 'python-backend-developer',
                'category_id': cat_objs['software-development'].id,
                'description': 'Master modern server-side engineering, database modeling, RESTful API architecture, containerization, and cloud deployment.',
                'difficulty': 'Beginner → Advanced',
                'demand_level': 'High Demand',
                'estimated_duration': '6 months',
                'average_salary': '₹6L – ₹20L+',
                'icon': 'server',
                'trending': True,
                'steps': [
                    {'title': 'Python Fundamentals', 'desc': 'Syntax, control flow, functions, error handling, and file I/O.', 'skill': 'python'},
                    {'title': 'Object-Oriented Programming', 'desc': 'Classes, inheritance, polymorphism, encapsulation, and design patterns.', 'skill': 'python'},
                    {'title': 'SQL & Relational Databases', 'desc': 'Schema design, normalization, complex joins, indexing, and transactions.', 'skill': 'sql'},
                    {'title': 'Git & Version Control', 'desc': 'Branching strategies, pull requests, merge conflict resolution, and GitHub.', 'skill': 'devops-cicd'},
                    {'title': 'Flask & Web Frameworks', 'desc': 'Routing, request handling, Jinja templates, ORMs, and application factory pattern.', 'skill': 'flask'},
                    {'title': 'REST APIs & Authentication', 'desc': 'API contracts, JSON serialization, JWT tokens, session security, and rate limiting.', 'skill': 'rest-apis'},
                    {'title': 'Docker Containerization', 'desc': 'Multi-stage Dockerfiles, Docker Compose, environment management, and volumes.', 'skill': 'docker'},
                    {'title': 'AWS Cloud Deployment', 'desc': 'EC2, RDS PostgreSQL, S3 asset storage, domain configuration, and basic CI/CD.', 'skill': 'cloud-computing-aws'}
                ]
            },
            {
                'name': 'Data Scientist',
                'slug': 'data-scientist',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Transform raw complex data into actionable predictive insights using Python, statistics, predictive modeling, and business intuition.',
                'difficulty': 'Intermediate → Advanced',
                'demand_level': 'Very High Demand',
                'estimated_duration': '8 months',
                'average_salary': '₹8L – ₹26L+',
                'icon': 'line-chart',
                'trending': True,
                'steps': [
                    {'title': 'Python for Data Analysis', 'desc': 'NumPy vectors, Pandas dataframes, data cleaning, and feature engineering.', 'skill': 'pandas-numpy'},
                    {'title': 'SQL for Analytics', 'desc': 'Aggregations, window functions, CTEs, and reporting data extraction.', 'skill': 'sql'},
                    {'title': 'Exploratory Data Analysis', 'desc': 'Matplotlib, Seaborn visualizations, correlation analysis, and distributions.', 'skill': 'data-science'},
                    {'title': 'Applied Statistics & Probability', 'desc': 'Hypothesis testing, p-values, regression analysis, and confidence intervals.', 'skill': 'data-science'},
                    {'title': 'Machine Learning Algorithms', 'desc': 'Scikit-learn classifiers, regressors, cross-validation, and hyperparameter tuning.', 'skill': 'machine-learning'},
                    {'title': 'Model Evaluation & Deployment', 'desc': 'ROC-AUC, precision-recall tradeoffs, FastAPI model serving, and Streamlit dashboards.', 'skill': 'machine-learning'}
                ]
            },
            {
                'name': 'Machine Learning Engineer',
                'slug': 'machine-learning-engineer',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Bridge data science and software engineering to construct production-ready, low-latency AI and deep learning systems.',
                'difficulty': 'Advanced',
                'demand_level': 'Very High Demand',
                'estimated_duration': '9 months',
                'average_salary': '₹10L – ₹32L+',
                'icon': 'cpu',
                'trending': True,
                'steps': [
                    {'title': 'Python & Math Foundations', 'desc': 'Linear algebra, calculus, matrix multiplication, and vectorization.', 'skill': 'python'},
                    {'title': 'Supervised & Unsupervised ML', 'desc': 'Tree ensembles, XGBoost, clustering, and dimensionality reduction.', 'skill': 'machine-learning'},
                    {'title': 'Deep Learning with PyTorch', 'desc': 'Tensors, autograd, multilayer perceptrons, convolutional & recurrent networks.', 'skill': 'deep-learning'},
                    {'title': 'Transformer Architectures & NLP', 'desc': 'Attention mechanisms, tokenization, Hugging Face models, and fine-tuning.', 'skill': 'deep-learning'},
                    {'title': 'MLOps & Containerization', 'desc': 'Packaging models in Docker, tracking experiments with MLflow, and model registries.', 'skill': 'docker'},
                    {'title': 'Scalable Cloud Serving', 'desc': 'Serving endpoints on AWS/GCP, batch inference pipelines, and GPU optimization.', 'skill': 'cloud-computing-aws'}
                ]
            },
            {
                'name': 'Full Stack Developer',
                'slug': 'full-stack-developer',
                'category_id': cat_objs['software-development'].id,
                'description': 'Build complete end-to-end web applications combining dynamic React frontends with robust Node/Python backend architectures.',
                'difficulty': 'Beginner → Advanced',
                'demand_level': 'Very High Demand',
                'estimated_duration': '7 months',
                'average_salary': '₹6L – ₹22L+',
                'icon': 'layers',
                'trending': True,
                'steps': [
                    {'title': 'HTML5, Modern CSS & Responsive Design', 'desc': 'Semantic markup, Flexbox, Grid, media queries, and accessibility standards.', 'skill': 'javascript'},
                    {'title': 'JavaScript (ES6+) Core', 'desc': 'Async/await, DOM manipulation, closures, promises, and fetch API.', 'skill': 'javascript'},
                    {'title': 'React Component Engineering', 'desc': 'State management, custom hooks, component composition, and virtual DOM.', 'skill': 'react'},
                    {'title': 'Backend APIs with Node.js or Python', 'desc': 'Server routing, middleware, controllers, and JSON responses.', 'skill': 'nodejs'},
                    {'title': 'Database Integration & ORMs', 'desc': 'Relational modeling with SQL/PostgreSQL and indexing performance.', 'skill': 'sql'},
                    {'title': 'Deployment & Cloud Hosting', 'desc': 'CI/CD deployment to Vercel/Render, SSL, and monitoring.', 'skill': 'docker'}
                ]
            },
            {
                'name': 'Cloud Engineer',
                'slug': 'cloud-engineer',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'Design, provision, and maintain enterprise cloud infrastructure prioritizing high availability, disaster recovery, and cost efficiency.',
                'difficulty': 'Intermediate → Advanced',
                'demand_level': 'Very High Demand',
                'estimated_duration': '6 months',
                'average_salary': '₹8L – ₹25L+',
                'icon': 'cloud',
                'trending': True,
                'steps': [
                    {'title': 'Linux System Administration', 'desc': 'File system permissions, systemd services, SSH keys, and bash scripts.', 'skill': 'linux-bash'},
                    {'title': 'Networking Foundations', 'desc': 'TCP/IP, DNS, subnetting, CIDR notation, load balancers, and gateways.', 'skill': 'linux-bash'},
                    {'title': 'AWS Core Services', 'desc': 'EC2 compute, S3 storage, VPC isolation, IAM policies, and RDS databases.', 'skill': 'cloud-computing-aws'},
                    {'title': 'Infrastructure as Code (IaC)', 'desc': 'Declarative infrastructure provisioning using Terraform and CloudFormation.', 'skill': 'cloud-computing-aws'},
                    {'title': 'Containerized Workloads', 'desc': 'ECS, EKS, and container registries for scalable microservices.', 'skill': 'docker'},
                    {'title': 'Cloud Security & Compliance', 'desc': 'KMS encryption, security groups, audit logs, and IAM least privilege.', 'skill': 'cybersecurity-fundamentals'}
                ]
            },
            {
                'name': 'DevOps Engineer',
                'slug': 'devops-engineer',
                'category_id': cat_objs['cloud-and-devops'].id,
                'description': 'Automate software delivery pipelines, maintain continuous integration, and orchestrate containerized microservices at scale.',
                'difficulty': 'Intermediate → Advanced',
                'demand_level': 'High Demand',
                'estimated_duration': '7 months',
                'average_salary': '₹8L – ₹26L+',
                'icon': 'git-merge',
                'trending': True,
                'steps': [
                    {'title': 'Version Control & GitOps', 'desc': 'Advanced Git branching, webhooks, pull request automation.', 'skill': 'devops-cicd'},
                    {'title': 'Docker Container Packaging', 'desc': 'Standardizing dev and prod runtime environments inside images.', 'skill': 'docker'},
                    {'title': 'CI/CD Pipeline Automation', 'desc': 'GitHub Actions workflows, testing stages, artifact publishing, and rollbacks.', 'skill': 'devops-cicd'},
                    {'title': 'Kubernetes Cluster Management', 'desc': 'Deployments, ingresses, ConfigMaps, Secrets, and Helm package charts.', 'skill': 'kubernetes'},
                    {'title': 'Monitoring & Observability', 'desc': 'Prometheus metrics scraping, Grafana dashboards, log aggregation, and alerting.', 'skill': 'linux-bash'}
                ]
            },
            {
                'name': 'Cybersecurity Specialist',
                'slug': 'cybersecurity-specialist',
                'category_id': cat_objs['cybersecurity'].id,
                'description': 'Protect organizational digital assets through vulnerability assessments, incident response, network monitoring, and security controls.',
                'difficulty': 'Beginner → Advanced',
                'demand_level': 'High Demand',
                'estimated_duration': '7 months',
                'average_salary': '₹7L – ₹22L+',
                'icon': 'shield-check',
                'trending': True,
                'steps': [
                    {'title': 'Security Fundamentals & Threat Landscape', 'desc': 'CIA triad, malware types, social engineering, and attack vectors.', 'skill': 'cybersecurity-fundamentals'},
                    {'title': 'Computer Networking & Protocols', 'desc': 'Packet inspection, Wireshark, OSI model, firewalls, and proxy servers.', 'skill': 'network-security'},
                    {'title': 'Linux & Operating System Hardening', 'desc': 'User privilege separation, auditing services, and firewall rules.', 'skill': 'linux-bash'},
                    {'title': 'Vulnerability Scanning & Penetration Testing', 'desc': 'Nmap port scans, OWASP Top 10 vulnerabilities, and Metasploit basics.', 'skill': 'ethical-hacking'},
                    {'title': 'Security Operations & Incident Response', 'desc': 'SIEM log monitoring, threat hunting, forensic triage, and incident playbooks.', 'skill': 'cybersecurity-fundamentals'}
                ]
            },
            {
                'name': 'Data Analyst',
                'slug': 'data-analyst',
                'category_id': cat_objs['data-and-ai'].id,
                'description': 'Extract meaningful trends from business data, author dashboards, and communicate metrics to executive leaders.',
                'difficulty': 'Beginner → Intermediate',
                'demand_level': 'High Demand',
                'estimated_duration': '5 months',
                'average_salary': '₹5L – ₹14L+',
                'icon': 'pie-chart',
                'trending': True,
                'steps': [
                    {'title': 'Advanced Excel & Spreadsheets', 'desc': 'VLOOKUP, INDEX/MATCH, Pivot Tables, conditional logic, and charting.', 'skill': 'powerbi-tableau'},
                    {'title': 'SQL Data Extraction', 'desc': 'Filtering, grouping, aggregating, joins, and database queries.', 'skill': 'sql'},
                    {'title': 'Business Intelligence Dashboards', 'desc': 'Building interactive KPI reports in Power BI or Tableau.', 'skill': 'powerbi-tableau'},
                    {'title': 'Python for Data Cleaning', 'desc': 'Automating data transformation and cleansing with Pandas.', 'skill': 'pandas-numpy'},
                    {'title': 'Data Storytelling & Reporting', 'desc': 'Translating complex statistical metrics into executive presentations.', 'skill': 'data-science'}
                ]
            },
            {
                'name': 'UI/UX Product Designer',
                'slug': 'ui-ux-designer',
                'category_id': cat_objs['ui-ux-design'].id,
                'description': 'Design frictionless digital customer journeys, user interfaces, design systems, and delightful interactive prototypes.',
                'difficulty': 'Beginner → Intermediate',
                'demand_level': 'High Demand',
                'estimated_duration': '5 months',
                'average_salary': '₹5L – ₹18L+',
                'icon': 'palette',
                'trending': False,
                'steps': [
                    {'title': 'User Research & Personas', 'desc': 'User interviews, competitive analysis, customer journeys, and empathy mapping.', 'skill': 'ui-ux-design-figma'},
                    {'title': 'Information Architecture & Wireframing', 'desc': 'Sitemaps, user flows, low-fidelity paper and digital wireframes.', 'skill': 'ui-ux-design-figma'},
                    {'title': 'Visual Design & Figma Mastery', 'desc': 'Color theory, typography, spacing grids, autolayout, and components.', 'skill': 'ui-ux-design-figma'},
                    {'title': 'Design Systems & Tokens', 'desc': 'Reusable component libraries, state variants, and developer handoff.', 'skill': 'design-systems'},
                    {'title': 'Usability Testing & Iteration', 'desc': 'Prototype testing with real users, tracking friction points, and metric iterations.', 'skill': 'ui-ux-design-figma'}
                ]
            },
            {
                'name': 'Mobile App Developer',
                'slug': 'mobile-developer',
                'category_id': cat_objs['mobile-development'].id,
                'description': 'Develop fluid, high-performance cross-platform mobile apps for iOS and Android with React Native and Flutter.',
                'difficulty': 'Intermediate',
                'demand_level': 'High Demand',
                'estimated_duration': '6 months',
                'average_salary': '₹6L – ₹20L+',
                'icon': 'smartphone',
                'trending': False,
                'steps': [
                    {'title': 'Programming Fundamentals', 'desc': 'JavaScript ES6+ or Dart programming language foundations.', 'skill': 'javascript'},
                    {'title': 'Mobile Framework Components', 'desc': 'Mobile view layouts, scroll views, touch gestures, and navigation stacks.', 'skill': 'react-native'},
                    {'title': 'State Management & Storage', 'desc': 'Managing mobile application state and offline local storage caching.', 'skill': 'react'},
                    {'title': 'API Integration & Push Notifications', 'desc': 'Connecting to REST endpoints, Firebase authentication, and push alerts.', 'skill': 'rest-apis'},
                    {'title': 'App Store & Play Store Deployment', 'desc': 'Signing certificates, release builds, guidelines compliance, and distribution.', 'skill': 'react-native'}
                ]
            }
        ]

        career_path_objs = {}
        for cp_data in career_paths_data:
            steps_info = cp_data.pop('steps')
            cp = CareerPath(**cp_data)
            db.session.add(cp)
            db.session.flush() # get cp.id
            career_path_objs[cp.slug] = cp

            for idx, step_info in enumerate(steps_info, start=1):
                skill_ref = skill_objs.get(step_info.get('skill'))
                cps = CareerPathSkill(
                    career_path_id=cp.id,
                    skill_id=skill_ref.id if skill_ref else None,
                    step_title=step_info['title'],
                    step_description=step_info['desc'],
                    sequence_order=idx
                )
                db.session.add(cps)
                db.session.flush()

                # Link existing skill resources if available
                if skill_ref and skill_ref.resources:
                    for res in skill_ref.resources:
                        rr = RoadmapResource(
                            career_path_skill_id=cps.id,
                            resource_id=res.id
                        )
                        db.session.add(rr)

        db.session.commit()

        user_bharat = User.query.filter_by(username='bharat').first()
        if user_bharat:
            print("Seeding Bookmarks & Active Progress for Demo User (Bharat)...")
            saved_skill_slugs = ['python', 'sql', 'docker', 'machine-learning', 'react']
            for slug in saved_skill_slugs:
                if slug in skill_objs and not Bookmark.query.filter_by(user_id=user_bharat.id, skill_id=skill_objs[slug].id).first():
                    bm = Bookmark(user_id=user_bharat.id, skill_id=skill_objs[slug].id)
                    db.session.add(bm)

            # Bharat Active Progress in Python Backend Developer
            python_path = career_path_objs.get('python-backend-developer')
            if python_path:
                steps = CareerPathSkill.query.filter_by(career_path_id=python_path.id).order_by(CareerPathSkill.sequence_order).all()
                for i in range(min(3, len(steps))):
                    if not UserProgress.query.filter_by(user_id=user_bharat.id, career_path_id=python_path.id, career_path_skill_id=steps[i].id).first():
                        up = UserProgress(
                            user_id=user_bharat.id,
                            career_path_id=python_path.id,
                            career_path_skill_id=steps[i].id,
                            completed=True,
                            completed_at=datetime.utcnow()
                        )
                        db.session.add(up)

        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
