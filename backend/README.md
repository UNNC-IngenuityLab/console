# IngenuityLab Console - FastAPI Backend

Backend API for the IngenuityLab Mini Program Management Console.

## Features

- JWT-based authentication
- User management with point adjustments
- Activity and sub-activity CRUD operations
- Announcement management
- Configurable level system
- Dynamic UI configuration
- System settings management
- Analytics and statistics
- Admin operation logging
- QR code generation for check-ins

## Tech Stack

- Python 3.11+
- FastAPI
- aiomysql (async MySQL)
- Pydantic (validation)
- python-jose (JWT)
- passlib (password hashing)
- qrcode (QR code generation)

## Getting Started

### Installation

```bash
# Install dependencies
pip install -e .

# Or using uv
uv pip install -e .
```

### Configuration

Configuration is done via **system environment variables only** (no .env files).

**Required environment variables:**

```bash
# Database
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ingenuity_lab
export DB_USER=root
export DB_PASSWORD=your_password_here

# JWT
export JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

**Optional environment variables (with defaults):**

```bash
# Database (defaults shown)
export DB_PORT=3306

# JWT (defaults shown)
export JWT_ALGORITHM=HS256
export JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Server (defaults shown)
export API_HOST=0.0.0.0
export API_PORT=8000
export API_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment (defaults shown)
export ENVIRONMENT=development
export DEBUG=true
```

### Quick Start

```bash
# Set required environment variables
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=ingenuity_lab
export DB_USER=root
export DB_PASSWORD=your_password
export JWT_SECRET_KEY=your-secret-key

# Run the server
uvicorn app.main:app --reload --port 8000
```

### Database Setup

```bash
# Run the database schema
mysql -u root -p < ../db_migration/schema.sql
```

### Running the Server

```bash
# Development with auto-reload
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using PM2
pm2 start ecosystem.config.js
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Project Structure

```
console/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management (env vars only)
│   ├── dependencies.py      # Dependency injection
│   ├── core/                # Core functionality
│   │   ├── security.py      # JWT, password hashing
│   │   └── exceptions.py    # Custom exceptions
│   ├── db/                  # Database layer
│   │   ├── pool.py          # Connection pool
│   │   ├── queries/         # SQL query definitions
│   │   └── repositories/    # Data access layer
│   ├── models/              # Pydantic models
│   └── api/v1/              # API routes
│       ├── auth.py          # Authentication
│       ├── users.py         # User management
│       ├── activities.py    # Activity management
│       ├── announcements.py # Announcement management
│       ├── levels.py        # Level configuration
│       ├── config.py        # UI configuration
│       ├── settings.py      # System settings
│       ├── analytics.py     # Analytics
│       └── admin_logs.py    # Admin logs
├── tests/                   # Tests
├── pyproject.toml           # Python dependencies
├── Dockerfile               # Container deployment
└── README.md                # This file
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Admin login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List users (paginated)
- `GET /api/v1/users/{id}` - Get user details
- `PUT /api/v1/users/{id}/points` - Update user points
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Activities
- `GET /api/v1/activities/` - List activities
- `GET /api/v1/activities/{id}` - Get activity details
- `POST /api/v1/activities/` - Create activity
- `PUT /api/v1/activities/{id}` - Update activity
- `DELETE /api/v1/activities/{id}` - Delete activity
- `POST /api/v1/activities/{id}/qrcode` - Generate QR code

### Sub-activities
- `POST /api/v1/activities/{id}/sub-activities` - Create sub-activity
- `PUT /api/v1/activities/sub-activities/{id}` - Update sub-activity
- `DELETE /api/v1/activities/sub-activities/{id}` - Delete sub-activity

### Announcements
- `GET /api/v1/announcements/` - List announcements
- `GET /api/v1/announcements/{id}` - Get announcement
- `POST /api/v1/announcements/` - Create announcement
- `PUT /api/v1/announcements/{id}` - Update announcement
- `DELETE /api/v1/announcements/{id}` - Delete announcement

### Level Configuration
- `GET /api/v1/levels/` - List all level configs
- `GET /api/v1/levels/export` - Export levels as JSON
- `GET /api/v1/levels/{id}` - Get level config
- `POST /api/v1/levels/` - Create level config
- `PUT /api/v1/levels/{id}` - Update level config
- `DELETE /api/v1/levels/{id}` - Delete level config
- `PUT /api/v1/levels/reorder` - Reorder levels

### UI Configuration
- `GET /api/v1/config/ui` - Get all UI configs
- `GET /api/v1/config/ui/category/{category}` - Get configs by category
- `GET /api/v1/config/ui/key/{key}` - Get single config
- `PUT /api/v1/config/ui/{key}` - Update single config
- `PUT /api/v1/config/ui/batch` - Batch update configs

### System Settings
- `GET /api/v1/settings/` - Get system settings
- `PUT /api/v1/settings/` - Update system settings

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard statistics
- `GET /api/v1/analytics/activity-stats` - Activity completion stats
- `GET /api/v1/analytics/trend` - User activity trends
- `GET /api/v1/analytics/leaderboard` - Leaderboard data
- `GET /api/v1/analytics/level-distribution` - Level distribution

### Admin Logs
- `GET /api/v1/admin-logs/` - List operation logs
- `GET /api/v1/admin-logs/export` - Export logs as CSV

## Response Format

All API responses follow this format:

```json
{
  "code": 0,           // 0 for success, non-zero for errors
  "message": "success",
  "data": { ... }      // Response data (can be null)
}
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

### Code Quality

```bash
# Format code
ruff format app/

# Lint code
ruff check app/

# Type check
mypy app/
```

## Production Deployment

### PM2 Configuration

Create `ecosystem.config.js`:

```javascript
module.exports = {
  apps: [{
    name: 'ingenuitylab-console',
    script: 'uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000',
    cwd: __dirname,
    interpreter: 'python3',
    instances: 1,
    exec_mode: 'fork',
    autorestart: true,
    env: {
      DB_HOST: process.env.DB_HOST,
      DB_PORT: process.env.DB_PORT || 3306,
      DB_NAME: process.env.DB_NAME || 'ingenuity_lab',
      DB_USER: process.env.DB_USER,
      DB_PASSWORD: process.env.DB_PASSWORD,
      JWT_SECRET_KEY: process.env.JWT_SECRET_KEY,
    }
  }]
};
```

### Systemd Service

Create `/etc/systemd/system/ingenuitylab-console.service`:

```ini
[Unit]
Description=IngenuityLab Console API
After=network.target mysql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/console
Environment="DB_HOST=localhost"
Environment="DB_PORT=3306"
Environment="DB_NAME=ingenuity_lab"
Environment="DB_USER=root"
Environment="DB_PASSWORD=your_password"
Environment="JWT_SECRET_KEY=your_secret_key"
Environment="API_HOST=0.0.0.0"
Environment="API_PORT=8000"
ExecStart=/usr/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## License

MIT
