# AI Chat Application with LLM Consensus - Project Plan

## Overview

A sophisticated AI chat application that enables multi-LLM conversations, document management, and collaborative editing with consensus-based decision making.

## Tech Stack

### Frontend

- **React** with  - [x] Chat interface development
  - [x] React + TypeScript chat UI scaffolded (ChatApp, ChatInterface, Sidebar, Header, AuthModal)
  - [x] Custom CSS and branding applied per style guide
  - [x] Integrated with FastAPI backend for authentication and chat endpoints
  - [x] Real chat session loading and message sending (with consensus response display)
  - [x] TypeScript errors and runtime errors resolved for clean build
  - [x] Backend Real-time messaging with Socket.IO
  - [x] Frontend Real-time messaging with Socket.IO
    - [x] Socket.IO client service created with connection management
    - [x] Custom useSocket hook for React integration
    - [x] Authentication context for token management
    - [x] Real-time message handling and display
    - [x] Connection status indicators in UI
    - [x] Fallback to HTTP API when Socket.IO unavailable
  - [x] File upload and document management UI
    - [x] FileUpload component with drag & drop functionality
    - [x] FileList component for viewing and managing files
    - [x] File validation and progress tracking
    - [x] Integrated into sidebar Files tab
    - [x] Backend file storage and database persistence
    - [x] File upload, listing, and deletion functionality
  - [x] Model selection and consensus debate simulation UI
    - [x] ModelSelection component with model toggle, debate modes, and advanced options
    - [x] ConsensusDebateVisualizer component for real-time debate visualization
    - [x] Integration with chat interface to show consensus process
    - [x] Enhanced model API with capabilities and status information
    - [x] Model selection state management across components
    - [x] Debate process visualization with confidence scores and reasoning
  - [x] Production-ready error handling and loading states
    - [x] Global ErrorBoundary component for uncaught React errors
    - [x] Centralized ErrorContext and useErrorHandler hook
    - [x] Toast notification system for user-friendly error messages
    - [x] Enhanced API service with retry logic and typed errors
    - [x] LoadingIndicator component with multiple variants
    - [x] Refactored FileUpload, FileList, ChatInterface, and ModelSelection components
    - [x] Comprehensive error handling documentation and testing
  - [x] Responsive/mobile UI polish
    - [x] Mobile-optimized header with collapsible elements and compact status indicators  
    - [x] Responsive sidebar with improved touch targets and swipe gestures
    - [x] Mobile-friendly chat interface with optimized message bubbles and input area
    - [x] Touch-optimized buttons and form elements with proper sizing (44px minimum)
    - [x] Custom responsive breakpoints including extra-small screens (xs: 475px)
    - [x] Mobile status bar for quick access to connection and model information
    - [x] Viewport meta tags optimized for mobile with proper scaling and PWA support
    - [x] Auto-resizing textarea with mobile keyboard optimization
    - [x] Responsive file upload component with mobile-friendly drag and drop
    - [x] Enhanced CSS with mobile-specific optimizations and touch improvements
    - [x] Custom responsive hooks for device detection and viewport management
- **Tailwind CSS** for styling
- **React Query** for API state management
- **React Hook Form** for form handling
- **React Dropzone** for file uploads
- **Socket.IO Client** for real-time chat

### Backend

- **FastAPI** with Python 3.11+
- **SQLAlchemy** with PostgreSQL/SQLite
- **OpenAI Responses API** for structured outputs
- **OpenAI Agents SDK** for agent orchestration
- **Grok API** (via xAI)
- **Google Drive API** and **Google Docs API**
- **Socket.IO** for real-time communication
- **JWT** for authentication
- **Pydantic** for data validation

### Deployment

- **Railway** for hosting
- **PostgreSQL** (Railway managed)
- **Environment variables** for API keys

## Application Architecture

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  React Frontend │────│ FastAPI Backend │────│  External APIs  │
│                 │    │                 │    │                 │
│ • Chat Interface│    │ • Auth Service  │    │ • OpenAI API    │
│ • File Manager  │    │ • LLM Orchestr. │    │ • Grok API      │
│ • Model Select. │    │ • File Service  │    │ • Google APIs   │
│ • Auth UI       │    │ • Consensus Eng.│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Features Breakdown

### 1. Authentication System

- **Single User Setup**: Simple username/password
- JWT token-based session management
- Secure password hashing (bcrypt)
- Session persistence

### 2. Chat Interface

- Real-time messaging with Socket.IO
- Message history persistence
- Chat session management
- Export chat functionality

### 3. LLM Integration & Consensus Engine

#### OpenAI Integration

- **Responses API**: Structured outputs for consistent formatting
- **Agents SDK**: Multi-agent workflows and tool calling
- Model selection: GPT-4, GPT-4-turbo, GPT-3.5-turbo

#### Grok Integration

- Direct API integration with xAI's Grok models
- Model variants: Grok-2, Grok-2-mini

#### Consensus Mechanism

```python
# Consensus Flow
1. User submits question/topic
2. Parallel queries to OpenAI + Grok
3. Response analysis and comparison
4. Debate simulation (iterative exchanges)
5. Consensus generation with confidence scores
6. Final unified response delivery
```

### 4. File Management System

#### Local File Operations

- File upload (multiple formats: PDF, DOCX, TXT, MD)
- File parsing and text extraction
- Local storage with organized directory structure
- File versioning system

#### Google Drive Integration

- OAuth2 authentication flow
- Real-time file access during chats
- File modification capabilities via Google Docs API
- Sync mechanisms for updated documents

#### Supported File Types

- **Documents**: PDF, DOCX, TXT, MD, Google Docs
- **Spreadsheets**: XLSX, CSV, Google Sheets
- **Presentations**: PPTX, Google Slides

### 5. Document Update & Approval System

- **Change Preview**: Show proposed modifications
- **Approval Workflow**: Button-based or chat command approval
- **Version Control**: Track document changes
- **Rollback Capability**: Undo changes if needed

### 6. Model Management

- **Dynamic Model Selection**: Dropdown with available models
- **Model Addition/Removal**: Admin interface for model management
- **Model Configuration**: Parameters, rate limits, capabilities

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    google_drive_token TEXT
);

-- Chat sessions
CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    title VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES chat_sessions(id),
    role VARCHAR(20) NOT NULL, -- user, assistant, system
    content TEXT NOT NULL,
    model_used VARCHAR(50),
    consensus_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Files
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    google_drive_id VARCHAR(100),
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LLM Models
CREATE TABLE llm_models (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL, -- openai, grok
    model_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    capabilities JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Authentication

- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info

### Chat

- `POST /chat/sessions` - Create new chat session
- `GET /chat/sessions` - List user's chat sessions
- `GET /chat/sessions/{id}/messages` - Get session messages
- `POST /chat/message` - Send message (triggers LLM consensus)

### Files

- `POST /files/upload` - Upload file
- `GET /files` - List user's files
- `DELETE /files/{id}` - Delete file
- `POST /files/{id}/update` - Update file content

### Google Drive

- `GET /google/auth` - Initiate Google OAuth
- `POST /google/callback` - Handle OAuth callback
- `GET /google/files` - List Google Drive files
- `POST /google/files/{id}/edit` - Edit Google Doc

### Models

- `GET /models` - List available LLM models
- `POST /models` - Add new model (admin)
- `PUT /models/{id}` - Update model settings
- `DELETE /models/{id}` - Remove model

## Key Implementation Details

### 1. OpenAI Responses API Usage

```python
# Structured response for consensus
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "consensus_response",
        "schema": {
            "type": "object",
            "properties": {
                "primary_response": {"type": "string"},
                "confidence_score": {"type": "number"},
                "reasoning": {"type": "string"},
                "debate_points": {"type": "array"}
            }
        }
    }
}
```

### 2. OpenAI Agents SDK Integration

```python
# Agent-based consensus workflow
from openai_agents import Agent, Workflow

consensus_workflow = Workflow()
openai_agent = Agent("openai_analyst")
grok_agent = Agent("grok_analyst")
moderator_agent = Agent("consensus_moderator")
```

### 3. Google APIs Integration

- **Google Drive API v3**: File access and management
- **Google Docs API v1**: Document editing capabilities
- **OAuth2 Flow**: Secure authentication

### 4. Real-time Features

- Socket.IO for live chat updates
- Progress indicators for LLM processing
- Real-time file sync status

## Security Considerations

1. **API Key Management**: Environment variables, no hardcoding
2. **File Security**: Validated uploads, sanitized file names
3. **Google OAuth**: Secure token storage and refresh
4. **Rate Limiting**: Prevent API abuse
5. **Input Validation**: Sanitize all user inputs

## Development Phases

### Phase 1: Core Infrastructure (Week 1-2)

- [x] FastAPI backend setup
- [x] React frontend initialization (pending)
- [x] Database schema implementation
- [x] Basic authentication system
- [x] Docker containerization

### Phase 2: LLM Integration (Week 3-4)

- [x] OpenAI Responses API integration
- [x] Grok API integration
- [x] Basic consensus mechanism
- [ ] Chat interface development
  - [x] React + TypeScript chat UI scaffolded (ChatApp, ChatInterface, Sidebar, Header, AuthModal)
  - [x] Custom CSS and branding applied per style guide
  - [x] Integrated with FastAPI backend for authentication and chat endpoints
  - [x] Real chat session loading and message sending (with consensus response display)
  - [x] TypeScript errors and runtime errors resolved for clean build  - [x] Backend Real-time messaging with Socket.IO
  - [x] Frontend Real-time messaging with Socket.IO
    - [x] Socket.IO client service created with connection management
    - [x] Custom useSocket hook for React integration
    - [x] Authentication context for token management
    - [x] Real-time message handling and display
    - [x] Connection status indicators in UI
    - [x] Fallback to HTTP API when Socket.IO unavailable
  - [x] File upload and document management UI
    - [x] FileUpload component with drag & drop functionality
    - [x] FileList component for viewing and managing files
    - [x] File validation and progress tracking
    - [x] Integrated into sidebar Files tab
    - [x] Backend file storage and database persistence
    - [x] File upload, listing, and deletion functionality
  - [x] Model selection and consensus debate simulation UI
    - [x] ModelSelection component with model toggle, debate modes, and advanced options
    - [x] ConsensusDebateVisualizer component for real-time debate visualization
    - [x] Integration with chat interface to show consensus process
    - [x] Enhanced model API with capabilities and status information
    - [x] Model selection state management across components
    - [x] Debate process visualization with confidence scores and reasoning
  - [X] Production-ready error handling and loading states
  - [X] Responsive/mobile UI polish

### Phase 3: File Management (Week 5-6)

- [x] File upload/download system
- [x] Local file operations
- [ ] Google Drive OAuth integration
- [ ] Google Docs API integration
- [ ] Google Slides API integration
- [ ] Google Sheets API integration

### Phase 4: Advanced Features (Week 7-8)

- [x] Consensus debate simulation
- [x] Document approval workflow
- [ ] Model management interface (user interface complete, admin interface pending)
- [x] Real-time features with Socket.IO

### Phase 5: Testing & Deployment (Week 9-10)

- [ ] Comprehensive testing
- [ ] Railway deployment setup
- [ ] Performance optimization
- [ ] Documentation and user guides

### Phase 6 (Optional)

Next Steps for Further Enhancement:
File Preview/Download: Add ability to preview or download files
File Search/Filter: Add search and filtering capabilities
File Categories: Organize files by type or purpose
File Sharing: Share files with other users or in chats
Google Drive Integration: Connect with Google Drive for cloud storage
File Versioning: Track file versions and changes

## Environment Variables Required

```env
# Database
DATABASE_URL=postgresql://...

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Grok/xAI
GROK_API_KEY=xai-...

# Google APIs
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...

# App Settings
APP_ENV=production
CORS_ORIGINS=["https://yourdomain.com"]
```

## File Structure

```text
Agent_Mark/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── auth/
│   │   ├── chat/
│   │   ├── files/
│   │   ├── llm/
│   │   ├── models/
│   │   └── database/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── README.md
└── PROJECT_PLAN.md
```

## Next Steps

1. Set up the project structure
2. Initialize backend with FastAPI
3. Create React frontend with basic routing
4. Implement authentication system
5. Begin LLM integration
