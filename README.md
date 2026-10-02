# SkillMarket – Discover Skills That Actually Pay

**SkillMarket** is a modern, production-grade career and skill discovery platform designed for students, fresh graduates, and career switchers. The platform eliminates career guesswork by marrying industry compensation figures with real-time employer demand scores, curated learning resources, and structured interactive roadmaps.

---

## Key Features

1. **Light / Dark Mode**:
   - High-contrast, polished modern SaaS design system with zero neon clutter.
   - Real-time instant toggle with persistent storage in `localStorage` and automatic synchronization to the user's database record.
2. **OTP Email Authentication Flow**:
   - Secure registration using `username` + `email`.
   - Cryptographically random 6-digit OTP generation, SHA-256 salted hashing, 10-minute expiration, and strict rate limiting.
   - Professional HTML verification emails sent via SMTP with fallback dev preview mode for local environments.
   - Login verifies user existence and verified status.
3. **Interactive User Dashboard**:
   - Top-right profile menu with avatar dropdown (Profile, Dashboard, Bookmarks, Roadmap, Settings, Logout).
   - Real-time statistics counters (Skills Explored, Bookmarked Skills, Recommended Skills, Roadmaps Started).
   - Dynamic recommendation cards with % match and synergy explanations.
   - Active career progress tracker with completion percentage and milestone checkpoints.
   - **Mandatory bottom section**: Trending Skills Roadmaps with difficulty, duration, and step counts.
4. **Skill Discovery & Detail Pages**:
   - Multi-parameter filtering (Category, Difficulty, Market Demand) and sorting (Popular, Highest Demand, Highest Salary, Beginner Friendly).
   - Skill detail pages with compensation gauges, market demand score (out of 100), related career roles, and curated resources.
5. **Interactive Roadmaps & Progress Tracking**:
   - Visual step-by-step career timelines (`01`, `02`, `03`... checkpoints).
   - Clickable milestones revealing vetted Documentation, Video Courses, and Practice Labs.
   - Asynchronous "Mark as Complete" toggle that saves to the database in real-time and recalculates the progress bar.
6. **Market Analytics Dashboard**:
   - Professional Chart.js visualizations for top-paying skills, demand scores, and domain distribution.
   - Prominent salary estimation disclaimer.
7. **Personalized Skill Matcher**:
   - Interactive questionnaire factoring in interest domain, experience level, and existing skill synergies.
8. **Admin Control Console**:
   - Protected admin gateway (`/admin`).
   - Platform metrics overview.
   - Full CRUD operations for Skills, Resources, Roadmaps, Sequential Steps, and User Management.

---

## Project Structure

```
skillmarket/
├── app.py                      # Flask Application Factory & route registration
├── config.py                   # App configuration & environment variables
├── models.py                   # Relational SQLAlchemy database models (10 tables)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── README.md                   # Documentation and run instructions
│
├── routes/
│   ├── auth.py                 # Login, Register, OTP verification & resend
│   ├── dashboard.py            # User dashboard, statistics & trending roadmaps
│   ├── skills.py               # Explore skills, multi-criteria filters & details
│   ├── recommendations.py      # Personalized skill matching engine
│   ├── roadmap.py              # Career roadmaps & interactive progress tracking
│   ├── resources.py            # Curated learning resources directory
│   ├── analytics.py            # Market analytics & Chart.js API
│   ├── bookmarks.py            # Async bookmarking and library view
│   ├── profile.py              # User profile and settings
│   ├── api.py                  # Theme sync & live typeahead search
│   └── admin.py                # Admin dashboard & complete CRUD
│
├── services/
│   ├── otp_service.py          # Secure OTP generator & validator
│   ├── email_service.py        # SMTP email dispatcher with dev preview fallback
│   ├── recommendation_service.py # Rule-based synergy matching engine
│   └── analytics_service.py    # Salary metrics & chart aggregations
│
├── templates/                  # Modular Jinja2 templates (Base, Auth, Dashboard, Roadmaps, Admin)
├── static/                     # CSS design system, Lucide icons, Chart.js & theme logic
└── database/
    └── seed.py                 # Seed script with 25+ skills, 6 categories, 10 roadmaps, 50+ resources
```

---

## Quickstart Setup & Run

### 1. Prerequisites
- Python 3.10+ installed
- Pip package manager

### 2. Install Dependencies
```bash
cd skillmarket
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Populates 25+ skills, 6 categories, 10 complete roadmaps, 50+ learning resources, and default demo accounts:
```bash
python database/seed.py
```

### 4. Run Development Server
```bash
python app.py
```
Open your browser at: `http://127.0.0.1:5000`

---

## Pre-Configured Demo Accounts

| Account | Username | Email | Role / Notes |
| :--- | :--- | :--- | :--- |
| **Demo User** | `bharat` | `bharat@example.com` | Verified user with bookmarks & active progress |
| **Admin User** | `admin` | `admin@skillmarket.com` | Full administrative console access |

---

## SMTP Email Configuration (Optional)

To send real verification emails via SMTP (e.g. Gmail App Password or SendGrid), copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER="SkillMarket Team <noreply@skillmarket.com>"
```

*Note: In development mode, if SMTP is not configured, the verification OTP is logged to the console and displayed in a developer banner on the verification page for zero-friction testing.*
