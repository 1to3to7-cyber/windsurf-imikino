# 🏆 Imikino - Social Learning & Micro-Task Platform for Rwandan Youth

## 🌟 Overview

**Imikino** is a comprehensive social-learning and micro-task platform designed specifically for Rwandan youth. Built with modern technologies and international standards, it combines educational content, skill development, and economic opportunities in one seamless experience.

## 🎯 Mission

Empower Rwandan youth through accessible education, skill development, and economic opportunities using cutting-edge technology and AI-powered personalized learning.

## 🚀 Key Features

- **🤖 BIZIMANA FILS AI Assistant** - Advanced multilingual AI with RAG capabilities
- **📚 Comprehensive Learning** - Courses, modules, quizzes with progress tracking
- **💼 Micro-Task Marketplace** - Earn rewards through skill-based tasks
- **👥 Social Community** - Connect, share, and collaborate with peers
- **📊 Analytics Dashboard** - Real-time insights and performance metrics
- **🌍 Multilingual Support** - Kinyarwanda, English, French, Kiswahili
- **📱 Mobile-First Design** - Optimized for mobile devices
- **🔒 Enterprise Security** - OWASP compliance with audit logging
- **👨‍💻 Developer Branding** - BIZIMANA Fils attribution throughout

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with refresh mechanism
- **Security**: OWASP compliance, rate limiting, audit logging
- **AI**: Advanced RAG system with self-learning capabilities

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with strict typing
- **Styling**: Tailwind CSS 3.4 with mobile-first approach
- **UI Components**: Reusable component library with accessibility
- **State Management**: React hooks with context API
- **Internationalization**: Dynamic language switching

### Infrastructure
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Docker Compose with service dependencies
- **CI/CD**: GitHub Actions with automated testing
- **Monitoring**: Prometheus + Grafana stack
- **Caching**: Redis for performance optimization

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm 8+
- Python 3.9+ and pip
- Docker and Docker Compose
- Git for version control

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/imikino.git
cd imikino

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Admin Dashboard: http://localhost:3000/admin
# API Documentation: http://localhost:8000/docs
```

### Development Setup

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Run database migrations
python -m db.init

# Start development servers
npm run dev          # Frontend development server
python -m uvicorn main:app --reload  # Backend development server
```

## 🏗️ Architecture

### Backend Architecture
```
📁 backend/
├── 📁 core/                 # Security, dependencies, responses
├── 📁 models/               # Database models (User, Course, Task, Content, etc.)
├── 📁 routes/               # API endpoints organized by feature
├── 📁 services/             # Business logic layer
├── 📁 schemas/              # Pydantic models for validation
├── 📁 tests/                # Comprehensive unit tests
├── 📁 audit.py              # Audit logging
├── 📁 db.py                 # Database setup
├── 📁 config.py             # Configuration
├── 📁 main.py               # Application entry point
└── 📁 requirements.txt        # Python dependencies
```

### Frontend Architecture
```
📁 frontend/
├── 📁 app/                  # Next.js App Router pages
├── 📁 components/            # Reusable UI components
│   ├── ui/                 # Base components (Button, Input, etc.)
│   ├── layout/             # Layout components (Header, Footer)
│   ├── ai/                 # AI assistant components
│   ├── content/            # Content management components
│   └── forms/              # Form components
├── 📁 lib/                  # Utility libraries and hooks
├── 📁 public/               # Static assets
├── 📁 styles/               # Global styles and configurations
├── 📁 package.json           # Dependencies & scripts
├── 📁 tsconfig.json         # TypeScript config
├── 📁 tailwind.config.js    # Tailwind config
├── 📁 next.config.js        # Next.js config
└── 📁 .env.example          # Environment variables
```

## 🤖 BIZIMANA FILS AI Assistant

### Features
- **Multilingual Support**: Kinyarwanda, English, French, Kiswahili
- **RAG Implementation**: Retrieval-augmented generation from database
- **Self-Learning**: Continuous skill improvement with user feedback
- **Personalization**: Context-aware responses based on user profile
- **Copy & Share**: One-click sharing with branded URLs
- **Real-time Updates**: Live skill development and adaptation

### API Endpoints
```bash
POST /api/ai-assistant/chat     # Chat with AI assistant
GET  /api/ai-assistant/greeting   # Get multilingual greeting
POST /api/ai-assistant/skills     # Update AI skills
GET  /api/ai-assistant/analytics   # AI usage analytics
```

## 📚 Learning System

### Course Management
- **Multi-module Courses**: Video, text, and quiz content
- **Progress Tracking**: Real-time completion metrics
- **Gamification**: XP points, levels, and badges
- **Assessment**: Interactive quizzes with immediate feedback
- **Certification**: Automatic completion certificates

### Task Marketplace
- **Skill-Based Tasks**: Matched to user capabilities
- **Reward System**: Points and monetary rewards
- **Submission Tracking**: File upload with validation
- **Quality Control**: Peer review and admin moderation
- **Performance Analytics**: Task completion rates and earnings

## 👥 Social Features

### Content Sharing
- **Multi-format Support**: Posts, articles, videos, documents
- **Social Media Integration**: Share to Facebook, Twitter, Instagram
- **Engagement Metrics**: Likes, shares, views, comments
- **Content Discovery**: Trending content and recommendations
- **Moderation System**: AI-assisted content review

## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure authentication with refresh mechanism
- **Role-Based Access**: User, moderator, admin roles
- **Rate Limiting**: Configurable limits per endpoint
- **Session Management**: Secure session handling
- **Password Security**: Hashing with bcrypt, strength requirements

### Data Protection
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content sanitization and CSP headers
- **CSRF Protection**: Token-based CSRF mitigation
- **Audit Logging**: Complete action tracking

### OWASP Compliance
- **Security Headers**: HSTS, CSP, and other security headers
- **Input Sanitization**: All user inputs validated and sanitized
- **Error Handling**: Secure error responses without information leakage
- **Dependency Management**: Regular security updates

## 📊 Analytics & Monitoring

### User Analytics
- **Growth Metrics**: User registration and retention
- **Engagement Tracking**: Course completion, task performance
- **Behavior Analytics**: Feature usage and navigation patterns
- **Performance Metrics**: Response times and system health

### Business Intelligence
- **Revenue Tracking**: Task marketplace earnings
- **Content Performance**: Most popular courses and content
- **User Segmentation**: Demographics and behavior analysis
- **Conversion Funnels**: Registration to active user journey

## 🌍 Internationalization

### Supported Languages
- **Kinyarwanda** (rw): Primary language for Rwanda
- **English** (en): International business language
- **French** (fr): Secondary language for regional users
- **Kiswahili** (sw): Additional language for broader reach

### Localization Features
- **Dynamic Language Switching**: Runtime language changes
- **Content Translation**: All UI text and messages
- **Date/Time Formatting**: Localized date and time display
- **Number Formatting**: Currency and number localization
- **RTL Support**: Right-to-left language support ready

## 📱 Mobile Optimization

### Responsive Design
- **Mobile-First Approach**: Designed for mobile devices first
- **Touch Optimization**: Touch-friendly interfaces and gestures
- **Performance**: Lazy loading and image optimization
- **Progressive Enhancement**: Feature detection and enhancement
- **Offline Support**: Service worker for offline functionality

### Accessibility
- **WCAG 2.1 Compliance**: Level AA accessibility standards
- **Screen Reader Support**: Proper ARIA labels and descriptions
- **Keyboard Navigation**: Full keyboard accessibility
- **High Contrast**: Support for users with visual impairments

## 🔧 Development

### Environment Setup
```bash
# Development environment
NODE_ENV=development
DATABASE_URL=sqlite:///./imikino.db
JWT_SECRET_KEY=your-secret-key-here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Production environment
NODE_ENV=production
DATABASE_URL=postgresql://user:password@localhost:5432/imikino_prod
REDIS_URL=redis://localhost:6379
SENTRY_DSN=your-sentry-dsn
```

### Testing
```bash
# Run backend tests
pytest backend/tests/ -v

# Run frontend tests
npm run test

# Coverage reports
pytest --cov=backend --cov-report=html
npm run test:coverage
```

### Code Quality
```bash
# Linting
npm run lint
flake8 backend/
black backend/
isort backend/

# Type checking
npm run type-check
mypy backend/
```

## 🚀 Deployment

### Production Deployment
```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Environment-specific deployment
docker-compose -f docker-compose.staging.yml up -d  # Staging
docker-compose -f docker-compose.prod.yml up -d    # Production
```

### CI/CD Pipeline
- **Automated Testing**: Tests run on every push
- **Security Scanning**: Dependency vulnerability scanning
- **Build Optimization**: Bundle optimization and minification
- **Rolling Deployments**: Zero-downtime deployments
- **Health Checks**: Post-deployment verification

## 📈 Performance

### Optimization Strategies
- **Code Splitting**: Dynamic imports for reduced bundle size
- **Image Optimization**: WebP format with lazy loading
- **Caching**: Redis caching for frequently accessed data
- **Database Optimization**: Indexed queries and connection pooling
- **CDN Integration**: Static asset delivery optimization

### Monitoring
- **Application Performance**: Response time and throughput
- **Database Performance**: Query optimization and indexing
- **User Experience**: Core Web Vitals monitoring
- **Error Tracking**: Comprehensive error logging and alerting

## 🔐 Security Best Practices

### Implementation Guidelines
- **Principle of Least Privilege**: Minimal necessary permissions
- **Defense in Depth**: Multiple security layers
- **Secure by Default**: Secure configurations out of the box
- **Zero Trust**: Validate all inputs and data
- **Fail Securely**: Secure error handling

### Compliance
- **GDPR Compliance**: Data protection and privacy
- **Accessibility Standards**: WCAG 2.1 AA compliance
- **Security Standards**: OWASP Top 10 protection
- **Performance Standards**: Core Web Vitals compliance

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with comprehensive tests
4. Ensure all tests pass (`npm run test && pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Create a Pull Request

### Code Standards
- **TypeScript**: Strict typing with no `any` types
- **ESLint**: Follow Airbnb style guide
- **Prettier**: Consistent code formatting
- **Testing**: Minimum 80% test coverage
- **Documentation**: Update docs for new features

### Pull Request Process
- **Description**: Clear description of changes
- **Testing**: All tests must pass
- **Review**: Code review by maintainers
- **Integration**: Ensure CI/CD pipeline passes

## 📞 Support

### Getting Help
- **Documentation**: Comprehensive guides and API docs
- **Community Forum**: User discussion and support
- **Issue Tracking**: GitHub issues for bug reports
- **Email Support**: support@imikino.rw for direct assistance
- **Office Hours**: Monday-Friday, 9AM-5PM Kigali Time

### Contact Information
- **Technical Lead & Developer**: BIZIMANA Fils
- **Email**: 1to3to7@gmail.com
- **Phone**: +250 783444370 / +250 795914094
- **Location**: Muhanga District, Rwanda
- **Institution**: ECOLE TECHNIQUE DOKABGAYI

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Rights
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ✅ Patent rights

### Conditions
- ⚠️ Include license
- ⚠️ Provide copyright notice
- ⚠️ No liability warranty

## 🏆 Acknowledgments

### Development Team
- **Technical Lead & Developer**: BIZIMANA Fils
- **Institution**: ECOLE TECHNIQUE DOKABGAYI
- **Location**: Muhanga District, Rwanda

### Special Thanks
- Rwandan Ministry of Education for guidance
- Open source community for contributions
- Technology partners for their support

---

## 🚀 Get Started Today

**Imikino** is ready to empower Rwandan youth with cutting-edge technology and AI-powered learning. Join us in revolutionizing education and opportunity in Rwanda!

### Quick Links
- **🌐 Live Demo**: [https://imikino.rw](https://imikino.rw)
- **📚 Documentation**: [https://docs.imikino.rw](https://docs.imikino.rw)
- **💻 GitHub**: [https://github.com/your-org/imikino](https://github.com/your-org/imikino)
- **🔧 Development**: [development.imikino.rw](development.imikino.rw)

---

*Built with ❤️ in Rwanda by BIZIMANA Fils for Rwandan youth empowerment*

## Features

- **Social Learning**: Share progress, achievements, and learning experiences
- **Micro-Tasks**: Complete real-world tasks to earn XP and rewards
- **Courses**: Interactive courses with quizzes and progress tracking
- **Gamification**: XP system, badges, and achievement tracking
- **Mobile-First**: Optimized for low-end Android devices and 3G networks
- **Offline-Friendly**: Graceful handling of network interruptions

## Tech Stack

### Backend (FastAPI)
- **Framework**: FastAPI with Uvicorn
- **Database**: SQLite with built-in sqlite3
- **Authentication**: Custom JWT with bcrypt password hashing
- **Validation**: Pydantic models
- **CORS**: Enabled for Next.js development

### Frontend (Next.js)
- **Framework**: Next.js 14/15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with mobile-first design
- **State Management**: React Context for auth, native fetch for API
- **Optimization**: Lazy loading, minimal bundle size

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ and pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd windsurf-imikino
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your configuration
   # No changes needed for development defaults
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Start the development servers**
   
   **Terminal 1 - Backend:**
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Project Structure

```
windsurf-imikino/
├── backend/                 # FastAPI application
│   ├── main.py             # Application entry point
│   ├── db.py               # Database setup and seeding
│   ├── models.py            # Pydantic models
│   ├── auth.py              # JWT authentication
│   └── routes/              # API route handlers
│       ├── auth.py          # User auth endpoints
│       ├── users.py         # User management
│       ├── posts.py         # Social posts
│       ├── courses.py       # Learning courses
│       ├── tasks.py         # Micro-tasks
│       └── admin.py         # Admin panel
├── frontend/               # Next.js application
│   ├── app/                # App Router pages
│   │   ├── page.tsx        # Home feed
│   │   ├── login/          # Authentication
│   │   ├── signup/
│   │   ├── profile/        # User profiles
│   │   ├── courses/        # Course listing
│   │   ├── tasks/          # Task listing
│   │   └── admin/          # Admin panel
│   ├── lib/                # Utilities and API client
│   ├── types/              # TypeScript definitions
│   └── components/         # Reusable components
├── README.md               # This file
└── .env.example           # Environment variables template
```

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Users
- `GET /users/me` - Current user info
- `GET /users/me/progress` - Learning progress

### Posts
- `GET /posts` - Feed posts
- `POST /posts` - Create post
- `POST /posts/{id}/like` - Like post
- `POST /posts/{id}/comment` - Comment on post

### Courses
- `GET /courses` - List courses
- `GET /courses/{id}` - Course details
- `GET /courses/{id}/quizzes/{module_id}` - Module quiz
- `POST /quizzes/{id}/submit` - Submit quiz
- `POST /courses/{id}/modules/{module_id}/complete` - Mark module complete

### Tasks
- `GET /tasks` - List available tasks
- `GET /tasks/{id}` - Task details
- `POST /tasks/{id}/claim` - Claim a task
- `POST /tasks/{id}/submit` - Submit task proof

### Admin
- `GET /admin/stats` - Platform statistics
- `GET /admin/submissions` - Pending task submissions
- `GET /admin/posts` - Pending posts
- `GET /admin/users` - User management
- `POST /admin/submissions/{id}/moderate` - Approve/reject submission
- `POST /admin/posts/{id}/moderate` - Approve/reject post
- `POST /admin/users/{id}/role` - Update user role

## Database Schema

### Core Tables
- **users** - User accounts and profiles
- **posts** - Social posts with likes and comments
- **courses** - Learning courses with modules
- **quizzes** - Course assessments
- **tasks** - Micro-tasks with submissions
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Imikino
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## Testing

### Backend Tests
```bash
cd backend
pytest --cov=. --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Test Coverage
- **Backend**: 80%+ coverage required
- **Frontend**: 80%+ coverage required
- **Integration**: End-to-end test scenarios

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/reset-password` - Password reset

### User Endpoints
- `GET /api/users/me` - Current user profile
- `PUT /api/users/me` - Update profile
- `GET /api/users/progress` - Learning progress

### Posts Endpoints
- `GET /api/posts` - Social feed
- `POST /api/posts` - Create post
- `POST /api/posts/{id}/like` - Like post
- `POST /api/posts/{id}/comments` - Comment on post

### Courses Endpoints
- `GET /api/courses` - Course listing
- `GET /api/courses/{id}` - Course details
- `POST /api/courses/{id}/modules/{id}/quiz/submit` - Submit quiz
- `POST /api/courses/{id}/modules/{id}/complete` - Mark complete

### Tasks Endpoints
- `GET /api/tasks` - Task marketplace
- `POST /api/tasks/{id}/claim` - Claim task
- `POST /api/tasks/{id}/submit` - Submit proof
- `GET /api/tasks/submissions` - User submissions

### Admin Endpoints
- `GET /api/admin/users` - User management
- `POST /api/admin/posts/{id}/moderate` - Moderate content
- `POST /api/admin/submissions/{id}/review` - Review submissions
- `GET /api/admin/analytics` - Platform analytics

### Contact Endpoints
- `POST /api/contact` - Contact form submission
- `GET /api/admin/contact` - Admin contact management

## Security Features

### Authentication & Authorization
- JWT access tokens (15min expiry)
- JWT refresh tokens (7 days expiry)
- Role-based access control (user/moderator/admin)
- Password hashing with bcrypt
- Account locking on failed attempts

### Input Validation & Sanitization
- Pydantic V2 strict validation
- HTML sanitization for user input
- SQL injection prevention
- XSS protection headers
- CSRF token protection

### Rate Limiting
- 100 requests/minute default
- Per-endpoint custom limits
- IP-based blocking
- Distributed rate limiting

### Audit Logging
- All user actions logged
- Admin action tracking
- Security event monitoring
- Failed authentication attempts
- Data access logging

## Internationalization

### Supported Languages
- **Kinyarwanda (rw)** - Default language
- **English (en)** - Secondary language
- **French (fr)** - Tertiary language
- **Swahili (sw)** - Regional language

### Localization Features
- Dynamic language switching
- RTL language support ready
- Localized date/time formats
- Currency and number formatting
- Cultural UI adaptations

## Mobile Optimization

### Responsive Design
- Mobile-first CSS approach
- Touch-friendly interfaces
- Optimized for 2G/3G networks
- Progressive Web App features
- Offline functionality

### Performance
- Image optimization and lazy loading
- Code splitting and tree shaking
- Service worker caching
- Minimal bundle sizes
- Fast initial paint

## Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   export NODE_ENV=production
   export DEBUG=false
   export LOG_LEVEL=WARNING
   ```

2. **Docker Deployment**
   ```bash
   docker-compose --profile production up -d
   ```

3. **SSL Configuration**
   ```bash
   # Place SSL certificates in nginx/ssl/
   # Update nginx.conf with your domain
   ```

### Environment-Specific Configs

#### Development
- Hot reload enabled
- Debug logging
- CORS allowed for localhost
- SQLite database

#### Staging
- Production-like setup
- Staging database
- Staging email configuration
- Performance monitoring

#### Production
- Optimized builds
- Error tracking only
- PostgreSQL database
- Redis caching
- Load balancing

## Monitoring & Analytics

### Application Metrics
- Request/response times
- Error rates and types
- User activity patterns
- Resource utilization
- Database performance

### Health Checks
- `/health` endpoint
- Database connectivity
- Email service status
- External API dependencies
- Memory/CPU usage

### Logging
- Structured JSON logs
- Log levels by environment
- Log rotation and archiving
- Security event logging
- Performance profiling

## Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For questions or support:
- Check the API documentation at http://localhost:8000/docs
- Review the database schema in `backend/db.py`
- Examine the frontend components in `frontend/components`

## Roadmap

- [ ] Push notifications for task updates
- [ ] Offline mode with data synchronization
- [ ] Advanced analytics dashboard
- [ ] Integration with local payment systems
- [ ] Multi-language support (Kinyarwanda, English, French)

---

Built with ❤️ for Rwandan youth empowerment
