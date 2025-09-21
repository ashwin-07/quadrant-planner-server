# 🚀 Quadrant Planner Server

Backend API for Quadrant Planner - A philosophy-driven productivity application implementing Stephen Covey's Time Management Matrix.

## 🏗️ Tech Stack

- **Framework:** FastAPI (Python 3.9+)
- **Database:** Supabase (PostgreSQL)
- **Deployment:** Vercel (Serverless Functions)
- **Authentication:** JWT Bearer Token (Google OAuth tokens from frontend)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Poetry (dependency management)
- Supabase account and project

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd quadrant-planner-server
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase credentials
   ```

4. **Run the development server:**
   ```bash
   poetry run python -m api.main
   ```

   Or using uvicorn directly:
   ```bash
   poetry run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/api/docs
   - Health Check: http://localhost:8000/api/health

## 🔐 Authentication

The API uses JWT Bearer token authentication. The frontend handles Google OAuth and sends the resulting JWT token in the `Authorization` header.

### JWT Token Structure
The API expects Google OAuth JWT tokens with the following structure:
```json
{
  "iss": "https://accounts.google.com",
  "aud": "your-client-id",
  "sub": "user-id",
  "email": "user@example.com",
  "name": "User Name",
  "iat": 1234567890,
  "exp": 1234567890
}
```

### Making Authenticated Requests
```bash
curl -H "Authorization: Bearer <jwt-token>" \
     "http://localhost:8000/api/v1/goals"
```

### Frontend Integration
```javascript
fetch('http://localhost:8000/api/v1/goals', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
})
```

## 📊 API Endpoints

### Core Endpoints
- `GET /` - API health check
- `GET /api` - API information
- `GET /api/health` - Health check

### Goals API ✅
- `GET /api/v1/goals` - List goals (JWT auth required)
- `POST /api/v1/goals` - Create goal (JWT auth required)
- `GET /api/v1/goals/{goalId}` - Get specific goal (JWT auth required)
- `PUT /api/v1/goals/{goalId}` - Update goal (JWT auth required)
- `DELETE /api/v1/goals/{goalId}` - Delete goal (JWT auth required)

### Tasks API ✅
- `GET /api/v1/tasks` - List tasks (JWT auth required)
- `POST /api/v1/tasks` - Create task (JWT auth required)
- `GET /api/v1/tasks/{taskId}` - Get specific task (JWT auth required)
- `PUT /api/v1/tasks/{taskId}` - Update task (JWT auth required)
- `DELETE /api/v1/tasks/{taskId}` - Delete task (JWT auth required)

### Analytics API (Coming Soon)
- `GET /api/v1/analytics/dashboard` - Analytics dashboard
- `GET /api/v1/analytics/goals/{goalId}` - Goal analytics

## 🗄️ Database Setup

### Supabase Configuration

1. Create a new Supabase project
2. Set up the database tables using the schema in `database/models.py`
3. Configure Row Level Security (RLS) policies
4. Add your Supabase credentials to `.env`

### Environment Variables

```bash
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
ENVIRONMENT=development
LOG_LEVEL=info
```

## 🧪 Testing

Run tests with:
```bash
poetry run pytest
```

Run tests with coverage:
```bash
poetry run pytest --cov=api --cov-report=html
```

## 🚀 Deployment

### Vercel Deployment

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

3. Set environment variables in Vercel dashboard

### Environment Variables for Production

Set these in your Vercel dashboard:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_KEY`
- `ENVIRONMENT=production`

## 📁 Project Structure

```
quadrant-planner-server/
├── api/
│   ├── main.py              # FastAPI app entry point
│   ├── dependencies.py     # Shared dependencies
│   ├── auth/
│   │   └── jwt_handler.py  # JWT authentication handler
│   ├── shared/
│   │   ├── responses.py    # Response models
│   │   ├── exceptions.py   # Custom exceptions
│   │   └── validation.py   # Input validation
│   ├── goals/              # Goals API ✅
│   │   ├── models.py       # Goal Pydantic models
│   │   ├── service.py      # Goal business logic
│   │   └── routes.py       # Goal API endpoints
│   ├── tasks/              # Tasks API ✅
│   │   ├── models.py       # Task Pydantic models
│   │   ├── service.py      # Task business logic
│   │   └── routes.py       # Task API endpoints
│   └── analytics/          # Analytics API (coming soon)
├── database/
│   ├── connection.py       # Supabase client
│   ├── models.py          # Database models
│   └── migrations/        # SQL migration files
├── tests/                 # Test suite
├── vercel.json            # Vercel configuration
├── pyproject.toml         # Poetry configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Development

### Code Quality

The project uses:
- **Black** for code formatting
- **mypy** for type checking
- **pytest** for testing

Run code quality checks:
```bash
poetry run black api/
poetry run mypy api/
poetry run pytest
```

### Pre-commit Hooks

Install pre-commit hooks:
```bash
poetry run pre-commit install
```

## 📚 Documentation

- [Planning Document](planning.md) - Implementation roadmap
- [API Design](API_DESIGN.md) - Detailed API specifications
- [Requirements](requirements.md) - Product requirements

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For questions or support, please refer to the documentation or create an issue.

---

**Current Status:** ✅ Core APIs Implemented

- ✅ **Goals API**: Full CRUD operations with JWT authentication
- ✅ **Tasks API**: Full CRUD operations with JWT authentication  
- ✅ **JWT Authentication**: Google OAuth token integration
- ✅ **Database Integration**: Supabase with RLS policies
- ✅ **CORS Configuration**: Frontend integration ready
- 🚧 **Analytics API**: Coming soon
- 🚧 **Deployment**: Vercel configuration ready
