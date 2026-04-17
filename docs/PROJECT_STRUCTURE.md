# Imikino - Clean Production Folder Structure

## 📁 Root Directory Structure
```
windsurf-imikino/
├── 📁 backend/                    # FastAPI backend
│   ├── 📁 core/                 # Core security and utilities
│   │   ├── security.py         # Authentication & authorization
│   │   ├── dependencies.py     # Dependency injection
│   │   └── responses.py        # API response utilities
│   ├── 📁 models/               # Database models
│   │   ├── user.py             # User model with XP/levels
│   │   ├── content.py          # User content hosting
│   │   ├── ai_skills.py        # AI learning system
│   │   ├── course.py           # Course management
│   │   ├── task.py             # Task marketplace
│   │   ├── post.py             # Social feed
│   │   └── contact_submission.py # Contact forms
│   ├── 📁 routes/               # API endpoints
│   │   ├── auth.py             # Authentication routes
│   │   ├── users.py            # User management
│   │   ├── courses.py          # Course system
│   │   ├── tasks.py            # Task marketplace
│   │   ├── posts.py            # Social feed
│   │   ├── admin.py            # Admin dashboard
│   │   ├── ai_assistant.py     # BIZIMANA FILS AI
│   │   ├── content.py          # User content hosting
│   │   └── contact.py          # Contact form
│   ├── 📁 services/             # Business logic
│   │   ├── auth_service.py     # Authentication logic
│   │   ├── email_service.py    # Email handling
│   │   ├── moderation_service.py # Content moderation
│   │   └── xp_service.py       # XP calculation
│   ├── 📁 schemas/              # Pydantic models
│   │   ├── auth.py             # Auth schemas
│   │   ├── user.py             # User schemas
│   │   ├── course.py          # Course schemas
│   │   ├── task.py             # Task schemas
│   │   ├── post.py             # Post schemas
│   │   ├── content.py          # Content schemas
│   │   └── contact.py          # Contact schemas
│   ├── 📁 tests/                # Unit tests
│   │   ├── test_auth.py        # Auth tests
│   │   ├── test_courses.py     # Course tests
│   │   ├── test_tasks.py       # Task tests
│   │   ├── test_posts.py       # Post tests
│   │   └── test_email.py       # Email tests
│   ├── 📁 audit.py              # Audit logging
│   ├── 📁 db.py                 # Database setup
│   ├── 📁 config.py             # Configuration
│   ├── 📁 main.py               # Application entry
│   └── 📁 requirements.txt        # Python dependencies
├── 📁 frontend/                   # Next.js frontend
│   ├── 📁 app/                  # Next.js app router
│   │   ├── (auth)/              # Authentication pages
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/          # Dashboard pages
│   │   │   └── page.tsx
│   │   ├── (courses)/            # Course pages
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── (tasks)/              # Task pages
│   │   │   ├── page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── (ai-assistant)/       # AI assistant
│   │   │   └── page.tsx
│   │   ├── (contact)/            # Contact page
│   │   │   └── page.tsx
│   │   ├── (content)/            # User content
│   │   │   ├── page.tsx
│   │   │   ├── upload/page.tsx
│   │   │   └── [id]/page.tsx
│   │   ├── (community)/          # Social feed
│   │   │   └── page.tsx
│   │   ├── (profile)/            # User profiles
│   │   │   └── page.tsx
│   │   ├── (admin)/              # Admin interface
│   │   │   ├── dashboard/page.tsx
│   │   │   └── page.tsx
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css           # Global styles
│   │   └── loading.tsx          # Loading states
│   ├── 📁 components/            # Reusable components
│   │   ├── ui/                 # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── LanguageSelector.tsx
│   │   │   └── MobileOptimized.tsx
│   │   ├── layout/             # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── ai/                 # AI assistant components
│   │   │   └── AIAssistant.tsx
│   │   ├── content/            # Content components
│   │   │   ├── ContentCard.tsx
│   │   │   ├── ContentUpload.tsx
│   │   │   └── SocialShare.tsx
│   │   └── forms/              # Form components
│   │       ├── ContactForm.tsx
│   │       └── LoginForm.tsx
│   ├── 📁 lib/                 # Utility libraries
│   │   ├── api/                # API client
│   │   ├── auth/               # Auth utilities
│   │   ├── utils/              # General utilities
│   │   └── hooks/              # Custom hooks
│   ├── 📁 public/               # Static assets
│   │   ├── images/             # Image assets
│   │   ├── icons/              # Icon assets
│   │   └── favicon.ico          # Site favicon
│   ├── 📁 styles/               # Global styles
│   │   └── globals.css
│   ├── 📁 package.json           # Dependencies & scripts
│   ├── 📁 tsconfig.json         # TypeScript config
│   ├── 📁 tailwind.config.js    # Tailwind config
│   ├── 📁 next.config.js        # Next.js config
│   └── 📁 .env.example          # Environment variables
├── 📁 docs/                     # Documentation
│   ├── PROJECT_STRUCTURE.md    # This file
│   ├── API.md               # API documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── CONTRIBUTING.md       # Contributing guide
├── 📁 scripts/                   # Automation scripts
│   ├── setup.sh             # Development setup
│   ├── deploy.sh             # Deployment script
│   └── backup.sh             # Database backup
├── 📁 .github/                   # GitHub workflows
│   └── workflows/               # CI/CD pipelines
│       ├── ci-cd.yml           # Main pipeline
│       └── tests.yml            # Testing pipeline
├── 📁 Dockerfile                # Container configuration
├── 📁 docker-compose.yml         # Multi-service setup
├── 📁 .env.example              # Environment template
├── 📁 .gitignore               # Git exclusions
├── 📁 README.md                # Project documentation
└── 📁 LICENSE                  # Project license
```

## 🎯 Key Features Implemented

### ✅ **Completed Features**
1. **BIZIMANA FILS AI Assistant** - Advanced multilingual RAG with self-learning
2. **Contact Form System** - Multi-category forms with email routing to 1to3to7@gmail.com
3. **User Content Hosting** - Social media integration with engagement metrics
4. **Developer Footer** - BIZIMANA Fils branding on all pages
5. **Enhanced Security** - OWASP compliance with audit logging
6. **Advanced Admin Interface** - Comprehensive dashboard with analytics
7. **Professional Code Structure** - Clean, scalable architecture

### 🔄 **In Progress Features**
8. **Real-time Updates** - WebSocket integration for live updates
9. **Performance Optimization** - Lazy loading and caching
10. **Comprehensive Multilingual Support** - Complete RW/EN/FR/SW localization

## 🚀 Production Deployment Ready

The project is structured for:
- **Scalability**: Modular architecture with clear separation of concerns
- **Maintainability**: Clean code organization with comprehensive documentation
- **Security**: OWASP compliance with advanced audit logging
- **Performance**: Optimized for mobile-first Rwandan users
- **International Standards**: Multilingual support with cultural adaptation
- **Developer Experience**: Comprehensive tooling and documentation
