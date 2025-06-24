# Consensus Agent Backend Testing Guide

This guide will walk you through testing the Consensus Agent backend step by step.

## Prerequisites

Before testing, ensure you have:

- Python 3.11+ installed
- Git installed (if cloning)
- A text editor

## Step 1: Setup Environment

### 1.1 Navigate to Backend Directory

```bash
cd c:\Users\rthid\myapps\Agent_Mark\backend
```

### 1.2 Create Virtual Environment (Recommended)

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux
```

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configuration

### 2.1 Create Environment File

```bash
copy .env.example .env
```

### 2.2 Edit .env File

Open `.env` in a text editor and update with your API keys:

```env
# Required for full functionality
OPENAI_API_KEY=sk-your-actual-openai-key-here
GROK_API_KEY=xai-your-actual-grok-key-here

# Optional - can use defaults for testing
DATABASE_URL=sqlite:///./agent_mark.db
JWT_SECRET_KEY=test-secret-key-change-in-production
```

**Note**: You can test basic functionality without API keys, but consensus features won't work.

## Step 3: Run Backend Tests

### 3.1 Run Automated Tests

```bash
python test_backend.py
```

This will test:

- ✅ Configuration loading
- ✅ Pydantic schemas
- ✅ Authentication utilities
- ✅ Database connection
- ✅ LLM orchestrator
- ✅ FastAPI app creation

### 3.2 Expected Output

```text
🚀 Starting Consensus Agent Backend Tests

🔍 Testing configuration...
✅ Config loaded - Environment: development
✅ Database URL configured: Yes
✅ OpenAI API key configured: Yes/No
✅ Grok API key configured: Yes/No

[... more test output ...]

==================================================
TEST RESULTS SUMMARY
==================================================
Configuration        ✅ PASSED
Schemas              ✅ PASSED
Authentication       ✅ PASSED
Database             ✅ PASSED
LLM Orchestrator     ✅ PASSED
FastAPI App          ✅ PASSED
==================================================
Total: 6 | Passed: 6 | Failed: 0

🎉 All tests passed! Backend is ready for testing.
```

## Step 4: Initialize Database

### 4.1 Run Setup Script

```bash
python setup.py
```

This will:

- Create database tables
- Seed LLM models (GPT-4o, Grok-2, etc.)
- Create default user: `admin` / `password123`

### 4.2 Expected Output

```text
Setting up Consensus Agent backend...
Created uploads directory
Initializing database...
Database tables created successfully!
Seeded 4 LLM models
Created default user: admin / password123

Setup completed successfully!
```

## Step 5: Start Development Server

### 5.1 Start Server

```bash
python dev.py
```

### 5.2 Expected Output

```text
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Step 6: Test API Endpoints

### 6.1 Access API Documentation

Open your browser and go to: `http://localhost:8000/docs`

You should see the interactive Swagger API documentation.

### 6.2 Test Health Check

**Browser**: Visit `http://localhost:8000/health`

**Expected Response**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 6.3 Test Authentication

#### Register a New User (Optional)

**Endpoint**: `POST /auth/register`
**Body**:

```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

#### Login with Default User

**Endpoint**: `POST /auth/login`
**Body**:

```json
{
  "username": "admin",
  "password": "password123"
}
```

**Expected Response**:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### 6.4 Test Protected Endpoints

Copy the `access_token` from the login response and use it in the Authorization header:
`Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`

#### Get Current User

**Endpoint**: `GET /auth/me`
**Headers**: `Authorization: Bearer <your_token>`

#### List Available Models

**Endpoint**: `GET /models/`
**Headers**: `Authorization: Bearer <your_token>`

**Expected Response**:

```json
[
  {
    "id": "gpt-4o",
    "provider": "openai",
    "display_name": "GPT-4o",
    "description": "Most capable OpenAI model",
    "supports_streaming": true,
    "supports_function_calling": true
  },
  {
    "id": "grok-2",
    "provider": "grok",
    "display_name": "Grok-2",
    "description": "xAI's most capable model",
    "supports_streaming": true,
    "supports_function_calling": false
  }
]
```

### 6.5 Test Chat Functionality (Requires API Keys)

#### Send a Chat Message

**Endpoint**: `POST /chat/message`
**Headers**: `Authorization: Bearer <your_token>`
**Body**:

```json
{
  "message": "Hello, can you explain what quantum computing is?",
  "use_consensus": true
}
```

**Expected Response** (if API keys are configured):

```json
{
  "message": {
    "id": 1,
    "session_id": 1,
    "role": "assistant",
    "content": "Quantum computing is a revolutionary computing paradigm...",
    "model_used": "consensus",
    "consensus_data": {
      "openai_response": { ... },
      "grok_response": { ... },
      "confidence_score": 0.85,
      "reasoning": "Consensus based on 2 valid responses",
      "debate_points": [...]
    },
    "created_at": "2025-06-22T10:30:00Z"
  },
  "session": {
    "id": 1,
    "user_id": 1,
    "title": "Hello, can you explain what quantum computing...",
    "created_at": "2025-06-22T10:30:00Z"
  }
}
```

## Step 7: Troubleshooting

### Common Issues

#### 1. Import Errors

```text
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**: Install dependencies

```bash
pip install -r requirements.txt
```

#### 2. Database Errors

```text
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
```

**Solution**: Run setup script

```bash
python setup.py
```

#### 3. API Key Errors

```textt
OpenAI API error: Incorrect API key provided
```

**Solution**: Update your `.env` file with valid API keys

#### 4. Port Already in Use

```text
OSError: [Errno 48] Address already in use
```

**Solution**: Kill existing process or change port

```bash
# Change port in dev.py or set environment variable
set PORT=8001
python dev.py
```

### Testing Without API Keys

If you don't have API keys yet, you can still test:

- ✅ Authentication system
- ✅ Database operations
- ✅ Model listing
- ✅ Chat session creation
- ❌ Actual chat responses (will show error messages)

### Logs and Debugging

The development server shows real-time logs:

- Request/response information
- Database queries (in development mode)
- Error messages with stack traces

## Step 8: Next Steps

Once the backend is working:

1. **Test all endpoints** using the Swagger UI at `/docs`
2. **Verify database** by checking the `agent_mark.db` file
3. **Test file uploads** (basic functionality works without API keys)
4. **Ready for frontend development** 🎉

## Success Criteria

✅ All automated tests pass
✅ Server starts without errors
✅ API documentation loads at `/docs`
✅ Health check returns success
✅ User authentication works
✅ Protected endpoints require authentication
✅ Chat messages can be sent (responses depend on API keys)

## Performance Notes

- **Startup time**: ~2-3 seconds
- **Response time**: <100ms for database operations
- **Consensus responses**: 2-5 seconds (depends on API latency)
- **Memory usage**: ~50-100MB

Your backend is now ready for integration with the React frontend!
