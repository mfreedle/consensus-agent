# Consensus Agent Backend

FastAPI backend for the Consensus Agent AI chat application with multi-LLM consensus.

## Features

- **Authentication**: JWT-based user authentication
- **Multi-LLM Integration**: OpenAI Responses API + Grok API consensus
- **Chat Management**: Session-based chat with message history
- **File Management**: Upload and process documents for AI context
- **Google Drive Integration**: Connect and edit Google Docs (planned)
- **Real-time Communication**: WebSocket support (planned)

## API Stack

The API uses the new OpenAI Responses API and OpenAI Agents SDK for structured outputs and agent workflows.

### Core Technologies

- **FastAPI**: Modern async web framework
- **OpenAI Responses API**: Structured AI responses
- **OpenAI Agents SDK**: Multi-agent workflows
- **Grok API**: xAI's powerful language model
- **PostgreSQL**: Database with async SQLAlchemy
- **JWT**: Secure authentication

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL (or SQLite for development)
- OpenAI API key
- Grok API key (xAI)

### Installation

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Copy environment variables:

    ```bash
    cp .env.example .env
    ```

3. Update `.env` with your API keys:

    ```env
    OPENAI_API_KEY=sk-your-openai-key
    GROK_API_KEY=xai-your-grok-key
    DATABASE_URL=postgresql://user:pass@localhost/agent_mark
    ```

4. Initialize database:

    ```bash
    python setup.py
    ```

5. Start development server:

    ```bash
    python dev.py
    ```

The API will be available at `http://localhost:8000`

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```text
backend/
├── app/
│   ├── auth/           # Authentication logic
│   ├── chat/           # Chat endpoints and logic
│   ├── database/       # Database connection and models
│   ├── files/          # File management
│   ├── google/         # Google Drive integration
│   ├── llm/            # LLM orchestration
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── config.py       # Configuration
│   └── main.py         # FastAPI app
├── requirements.txt    # Dependencies
├── setup.py           # Database setup
├── dev.py             # Development server
└── Dockerfile         # Container setup
```

## Key Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user

### Chat

- `POST /chat/sessions` - Create chat session
- `GET /chat/sessions` - List user sessions
- `POST /chat/message` - Send message (triggers consensus)

### Models

- `GET /models` - List available LLM models
- `POST /models/sync` - Sync model availability

### Files

- `POST /files/upload` - Upload file
- `GET /files` - List user files

## Multi-LLM Consensus

The consensus mechanism works as follows:

1. User sends a message
2. Parallel queries to OpenAI and Grok
3. Response analysis and comparison
4. Debate simulation (iterative exchanges)
5. Consensus generation with confidence scores
6. Final unified response delivery

Example consensus response:

```json
{
  "openai_response": {
    "content": "OpenAI's response...",
    "confidence": 0.9,
    "reasoning": "Based on training data..."
  },
  "grok_response": {
    "content": "Grok's response...", 
    "confidence": 0.85,
    "reasoning": "Real-time analysis..."
  },
  "final_consensus": "Combined insight...",
  "confidence_score": 0.88,
  "reasoning": "Consensus reasoning...",
  "debate_points": ["Point 1", "Point 2"]
}
```

## OpenAI Responses API Integration

Uses the new OpenAI Responses API for structured outputs:

```python
response = await client.responses.create(
    model="gpt-4o",
    instructions="You are a helpful assistant...",
    input=user_message,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "structured_response",
            "schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string"},
                    "confidence": {"type": "number"},
                    "reasoning": {"type": "string"}
                }
            }
        }
    }
)
```

## Development

### Default User

After running `setup.py`, a default user is created:

- Username: `admin`
- Password: `password123`

**Change this password in production!**

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

## Deployment

The backend is designed for Railway deployment with PostgreSQL.

### Environment Variables for Production

```env
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-production-secret
OPENAI_API_KEY=sk-...
GROK_API_KEY=xai-...
APP_ENV=production
```

## License

MIT License
