# 🤖 Workspace Agent

> An intelligent, autonomous AI assistant that proactively monitors your Google Workspace and provides daily insights without you asking.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node](https://img.shields.io/badge/Node-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Built for the **Google Gemini Devpost Hackathon** 🚀

---

## 📖 Table of Contents

- [Overview](#overview)
- [What Makes This an Agent](#what-makes-this-an-agent)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [How It Works](#how-it-works)
- [Use Cases](#use-cases)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Team](#team)
- [License](#license)

---

## 🎯 Overview

**Workspace Agent** is not just another chatbot—it's an autonomous AI agent that:

- 📊 **Observes** your Gmail, Google Classroom, and Calendar automatically
- 🧠 **Reasons** using Google Gemini to detect urgency and risks
- 💾 **Remembers** everything across days and weeks
- 📝 **Acts** by generating daily End-of-Day reports at 6 PM
- 💬 **Responds** to your questions with full context

The key difference? **It runs even when you're not using it.**

---

## 🔥 What Makes This an Agent?

| Feature | Traditional Chatbot | Workspace Agent |
|---------|---------------------|-----------------|
| **Observation** | Waits for user input | ✅ Actively monitors Gmail, Classroom, Calendar |
| **Autonomy** | Reactive only | ✅ Runs daily at 6 PM automatically |
| **Memory** | No persistence | ✅ Stores history across days/weeks |
| **Reasoning** | Single-turn Q&A | ✅ Multi-step analysis loops |
| **Initiative** | User-driven | ✅ Proactively generates reports |
| **Temporal Awareness** | No time context | ✅ Understands trends and patterns |

**Bottom Line:** This agent observes, thinks, remembers, and acts autonomously—not just when you ask it to.

---

## ✨ Features

### 🔄 Autonomous Operation
- **Scheduled Execution**: Runs every day at 6 PM without your intervention
- **Multi-Source Monitoring**: Connects to Gmail, Google Classroom, and Google Calendar
- **Automatic Reports**: Generates End-of-Day summaries you wake up to

### 🧠 Intelligent Reasoning
- **Urgency Detection**: Identifies what needs immediate attention
- **Risk Analysis**: Spots deadline conflicts and missed items
- **Priority Sorting**: Categorizes tasks as urgent, important, or low priority
- **Trend Recognition**: Notices patterns across days and weeks

### 💾 Persistent Memory
- **Short-term Memory**: Today's emails, assignments, and meetings
- **Long-term Memory**: Historical End-of-Day summaries
- **Episodic Memory**: Complete chat conversation history
- **Queryable Storage**: SQLite database for fast retrieval

### 💬 Conversational Interface
- Ask natural questions: *"What's due this week?"*
- Get context-aware answers based on your complete workspace
- Maintains conversation history for follow-up questions

---

## 🛠️ Tech Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - REST API framework
- **APScheduler** - Autonomous task scheduling
- **SQLAlchemy** - Database ORM
- **Google API Client** - Workspace integration
- **Google Gemini API** - AI reasoning engine

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icons

### Database
- **SQLite** - Lightweight local database

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- **Node.js 18 or higher** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Google Cloud Account** (Free tier is sufficient)
- **Google Gemini API Key** (Free tier available)

---

## 🚀 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/workspace-agent.git
cd workspace-agent
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2.3 Set Up Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., `workspace-agent`)
3. Enable the following APIs:
   - Gmail API
   - Google Classroom API
   - Google Calendar API
4. Create OAuth 2.0 Credentials:
   - Navigate to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Choose **Desktop app**
   - Download credentials as `credentials.json`
   - Move file to `backend/` directory

#### 2.4 Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **Get API Key**
3. Create new API key
4. Copy the key (you'll need it for configuration)

### Step 3: Frontend Setup
```bash
cd frontend
npm install
```

---

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the `backend/` directory:
```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (defaults shown)
EOD_REPORT_HOUR=18
EOD_REPORT_MINUTE=0
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./workspace_agent.db
```

**Note:** Replace `your_gemini_api_key_here` with your actual Gemini API key.

### Frontend Configuration

The frontend is pre-configured to connect to `http://localhost:8000`. If your backend runs on a different port, update `frontend/src/api/client.js`.

---

## 🎮 Usage

### Starting the Backend
```bash
cd backend

# Activate virtual environment first
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

python main.py
```

**First-time authentication:**
- A browser window will open automatically
- Sign in with your Google account
- Click **Allow** for all requested permissions
- The browser will show "Authentication complete"
- Authentication token saved to `token.json`

Backend will be running at: `http://localhost:8000`

### Starting the Frontend
```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### Using the Application

1. **View Dashboard**: See your latest End-of-Day report and workspace statistics
2. **Generate Report**: Click "Generate Report Now" to manually trigger a report
3. **Chat Interface**: Navigate to Chat tab and ask questions about your workspace

**Example Questions:**
- "What assignments are due this week?"
- "Do I have any important emails?"
- "What's my schedule for today?"
- "Any deadline conflicts?"

---

## 🔌 API Endpoints

### Health Check
```http
GET /api/health
```
Returns API status and availability.

### Get Latest EOD Report
```http
GET /api/eod-report
```
**Response:**
```json
{
  "date": "2024-02-07",
  "content": "Today you had 5 unread emails, 3 upcoming assignments..."
}
```

### Generate EOD Report (Manual)
```http
POST /api/eod-report/generate
```
Manually triggers the autonomous observation cycle.

### Chat with Agent
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What's due this week?"
}
```

### Get Today's Snapshot
```http
GET /api/snapshot/today
```
Returns current day's observations (emails, assignments, meetings).

### Get Chat History
```http
GET /api/chat/history
```
Returns recent conversation history.

---

## 🔄 How It Works

### Autonomous Cycle (Daily at 6 PM)
```
┌─────────────────────────────────────┐
│  1. OBSERVE                         │
│  └─ Fetch Gmail emails              │
│  └─ Get Classroom assignments       │
│  └─ Pull Calendar meetings          │
├─────────────────────────────────────┤
│  2. STRUCTURE                       │
│  └─ Convert to clean JSON schemas   │
├─────────────────────────────────────┤
│  3. REASON (via Gemini)             │
│  └─ Analyze urgency & priorities    │
│  └─ Detect risks & conflicts        │
│  └─ Identify patterns               │
├─────────────────────────────────────┤
│  4. REMEMBER                        │
│  └─ Store observations in database  │
│  └─ Save insights & analysis        │
├─────────────────────────────────────┤
│  5. ACT                             │
│  └─ Generate End-of-Day summary     │
│  └─ Store report for user access    │
└─────────────────────────────────────┘
```

### Chat Interaction Flow
```
User Query → Retrieve Context (today + history) → 
Build Prompt → Gemini Reasoning → 
Contextual Response → Store Conversation
```

---

## 💡 Use Cases

### For Students
- ✅ Never miss assignment deadlines
- ✅ Prioritize which professor emails need responses
- ✅ Detect scheduling conflicts between classes and meetings
- ✅ Weekly workload summaries

### For Professionals
- ✅ Morning briefings on yesterday's activities
- ✅ AI-sorted task priorities
- ✅ Meeting prep with relevant context
- ✅ Track email response rates

### For Teams
- ✅ Shared workspace monitoring
- ✅ Collaborative deadline tracking
- ✅ Meeting overlap detection

---

## 🐛 Troubleshooting

### Issue: "Module not found" Error

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Google Authentication Fails

**Solution:**
```bash
# Delete old token
rm backend/token.json

# Restart server (will re-authenticate)
python main.py
```

### Issue: CORS Error on Frontend

**Solution:**  
Check `backend/main.py` includes:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Gemini API Quota Exceeded

**Solution:**
- Check usage at [Google AI Studio](https://aistudio.google.com/)
- Free tier: 60 requests/minute
- Wait for quota reset or upgrade plan

### Issue: Database Locked

**Solution:**
```bash
# Stop all running instances
# Delete database file
rm backend/workspace_agent.db

# Restart server (creates fresh database)
python main.py
```

### Issue: Frontend Can't Connect to Backend

**Solution:**
- Ensure backend is running on port 8000
- Check `frontend/src/api/client.js` has correct URL
- Verify no firewall blocking localhost connections

---

## 🌟 Future Enhancements

- [ ] **Proactive Alerts**: Email/Slack notifications for critical deadlines
- [ ] **Smart Scheduling**: AI-suggested meeting times based on workload
- [ ] **Email Draft Assistant**: Auto-generate reply suggestions
- [ ] **Voice Interface**: Voice commands and responses
- [ ] **Multi-user Support**: Team workspace collaboration
- [ ] **Mobile App**: iOS/Android applications
- [ ] **Additional Integrations**: Notion, Todoist, Slack, Microsoft Teams
- [ ] **Predictive Analytics**: Forecast busy weeks and suggest time blocking
- [ ] **Custom Workflows**: User-defined automation rules
- [ ] **Data Visualization**: Charts and graphs for productivity insights

---

## 👥 Team

**Built for Google Gemini Devpost Hackathon 2026**

- **Backend Developer** - Bilal & Talha
- **Frontend Developer** - Bilal & Talha

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini API** - For powerful AI reasoning capabilities
- **Google Workspace APIs** - For seamless data integration
- **FastAPI & React Communities** - For excellent documentation and support

---

## ⭐ Star This Repository

If you find this project helpful or interesting, please give it a star! ⭐

It helps others discover agentic AI patterns and supports our work.

---

## 🚀 Quick Links

- [Google Gemini API Docs](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

**Made with ❤️ for the Google Gemini Devpost Hackathon**

*Demonstrating autonomous AI agents, not just chatbots.*
