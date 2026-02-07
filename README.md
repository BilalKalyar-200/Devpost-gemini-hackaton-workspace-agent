🤖 Workspace Agent - Autonomous AI Assistant for Google Workspace
An intelligent, autonomous AI agent that proactively monitors your Google Workspace (Gmail, Classroom, Calendar) and provides daily insights without you asking. Built for the Google Gemini Devpost Hackathon.
🎯 What Makes This an "Agent" (Not Just a Chatbot)
FeatureTraditional ChatbotOur AgentObservationWaits for user input🟢 Actively monitors Gmail, Classroom, CalendarAutonomyReactive only🟢 Runs daily at 6 PM automaticallyMemoryNo persistence🟢 Stores history across days/weeksReasoningSingle-turn Q&A🟢 Multi-step analysis loopsInitiativeUser-driven🟢 Proactively generates reportsTemporal AwarenessNo time context🟢 Understands trends and patterns
Key Difference: This agent runs even when you're not using it. It observes, thinks, remembers, and acts autonomously.

✨ Features
🔄 Autonomous Observation Loop

Scheduled Execution: Runs every day at 6 PM automatically
Data Collection: Monitors 3 Google Workspace sources:

📧 Gmail (unread/important emails)
📚 Google Classroom (assignments, deadlines)
📅 Google Calendar (meetings, schedule)



🧠 AI-Powered Reasoning

Gemini Integration: Analyzes collected data for:

Urgency detection (what needs immediate attention)
Risk identification (deadline conflicts, missed items)
Priority sorting (urgent vs. important vs. low priority)


Context-Aware: Considers historical patterns and trends

💾 Persistent Memory System

Short-term Memory: Today's observations
Long-term Memory: Historical EOD summaries
Episodic Memory: Chat conversation history
Structured Storage: SQLite database with queryable data

📊 End-of-Day Reports

Automatic Generation: Daily summary without user interaction
Contextual Insights: Compares with past week's data
Actionable Recommendations: Specific next steps

💬 Interactive Chat

Natural Language Queries: "What's due this week?"
Memory Retrieval: Searches across all stored data
Contextual Responses: Uses full workspace context

🛠️ Tech Stack
Backend

Python 3.11+
FastAPI: REST API framework
APScheduler: Autonomous task scheduling
SQLAlchemy: Database ORM
Google API Client: Workspace integration
Google Gemini API: AI reasoning

Frontend

React 18 with Vite
React Router: Navigation
Axios: API communication
Lucide React: Icons

Database

SQLite: Lightweight persistence

Deployment

Backend: Render / Fly.io
Frontend: Vercel


🚀 Quick Start
Prerequisites

Python 3.11+
Node.js 18+
Google Cloud Account
Gemini API Key

1. Clone Repository
bashgit clone https://github.com/your-username/workspace-agent.git
cd workspace-agent
2. Backend Setup
a) Install Dependencies
bashcd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
b) Google Cloud Setup

Go to Google Cloud Console
Create a new project: workspace-agent
Enable APIs:

Gmail API
Google Classroom API
Google Calendar API


Create OAuth 2.0 credentials:

Application type: Desktop app
Download as credentials.json
Place in backend/ folder



c) Get Gemini API Key

Go to Google AI Studio
Create API key
Copy key

d) Configure Environment
Create backend/.env:
envGEMINI_API_KEY=your_gemini_api_key_here
e) Run Backend
bashpython main.py
First-time authentication:

Browser will open
Sign in with Google account
Allow all permissions
Token saved to token.json

Backend runs on: http://localhost:8000
3. Frontend Setup
bashcd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## 📁 Project Structure
```
workspace-agent/
├── backend/
│   ├── agent/
│   │   ├── core.py              # Main agent loop
│   │   ├── scheduler.py         # APScheduler setup
│   │   └── prompts.py           # Gemini prompt templates
│   ├── connectors/
│   │   ├── gmail_connector.py   # Gmail API wrapper
│   │   ├── classroom_connector.py
│   │   └── calendar_connector.py
│   ├── reasoning/
│   │   ├── gemini_client.py     # Gemini API client
│   │   └── context_builder.py   # Context preparation
│   ├── memory/
│   │   ├── db_manager.py        # Database operations
│   │   ├── models.py            # SQLAlchemy models
│   │   └── retriever.py         # Memory search
│   ├── schemas/
│   │   ├── email.py             # Data models
│   │   ├── assignment.py
│   │   └── meeting.py
│   ├── api/
│   │   └── routes.py            # FastAPI endpoints
│   ├── main.py                  # Application entry
│   ├── config.py                # Configuration
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx    # EOD report display
│   │   │   └── ChatInterface.jsx
│   │   ├── api/
│   │   │   └── client.js        # API calls
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
└── README.md

🔌 API Endpoints
Health Check
httpGET /api/health
Get Latest EOD Report
httpGET /api/eod-report
Response:
json{
  "date": "2024-02-07",
  "content": "Today you had 5 unread emails..."
}
Generate Report (Manual Trigger)
httpPOST /api/eod-report/generate
Chat with Agent
httpPOST /api/chat
Content-Type: application/json

{
  "query": "What assignments are due this week?"
}
Get Today's Snapshot
httpGET /api/snapshot/today
Get Chat History
httpGET /api/chat/history

🔄 Agent Lifecycle
Autonomous Cycle (Runs Daily at 6 PM)
python1. OBSERVE
   └─ Fetch emails, assignments, meetings from Google APIs

2. STRUCTURE
   └─ Convert raw data to clean JSON schemas

3. REASON
   └─ Send structured data to Gemini
   └─ Gemini analyzes urgency, risks, priorities

4. REMEMBER
   └─ Store observations + insights in SQLite

5. ACT
   └─ Generate End-of-Day summary
   └─ Store report for user access
Chat Cycle (User-Initiated)
python1. RECEIVE QUERY
   └─ User asks: "What's due this week?"

2. RETRIEVE CONTEXT
   └─ Get today's snapshot
   └─ Search relevant historical data
   └─ Load recent chat history

3. REASON
   └─ Build context-aware prompt
   └─ Send to Gemini

4. RESPOND
   └─ Return answer to user
   └─ Store conversation in memory

🧪 Testing
Test Backend
bash# Test health
curl http://localhost:8000/api/health

# Trigger EOD report manually
curl -X POST http://localhost:8000/api/eod-report/generate

# Chat test
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What emails need my attention?"}'
Test Frontend

Open http://localhost:5173
Click "Generate Report Now"
Navigate to Chat tab
Ask: "What's due this week?"


🎯 Use Cases
For Students

Never miss deadlines: Daily reminders of upcoming assignments
Email prioritization: Know which professor emails need responses
Schedule optimization: See meeting conflicts before they happen

For Professionals

Morning briefings: Wake up to yesterday's summary
Task prioritization: AI-sorted to-do lists
Meeting prep: Context about upcoming meetings


🌟 Why This is Agentic
1. Autonomous Observation

Doesn't wait for user input
Continuously monitors data sources
Runs on schedule (6 PM daily)

2. Reasoning Loops

Multi-step analysis: Observe → Analyze → Decide
Not just keyword matching
Contextual understanding with Gemini

3. Persistent Memory

Remembers across sessions
Learns patterns over time
Historical context informs current decisions

4. Proactive Action

Generates reports without prompting
Could expand to: send alerts, create calendar events, draft email responses

5. Temporal Awareness

Understands "yesterday", "this week", "trends"
Compares current state with historical data

📝 Environment Variables
Create .env file in backend/:
env# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional (defaults shown)
EOD_REPORT_HOUR=18
EOD_REPORT_MINUTE=0
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./workspace_agent.db

🐛 Troubleshooting
"Module not found" Error
bashpip install -r requirements.txt
Google Auth Issues
bash# Delete old token
rm backend/token.json

# Restart server (will re-authenticate)
python main.py
CORS Error on Frontend
Check backend/main.py has:
pythonapp.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Gemini API Quota Exceeded

Check usage at Google AI Studio
Free tier: 60 requests/minute
Consider upgrading or implementing rate limiting


📄 License
MIT License - feel free to use for your own projects!

🙏 Acknowledgments

Google Gemini API for AI reasoning
Anthropic for inspiration on agentic systems
FastAPI and React communities

⭐ Star This Repo!
If you find this project helpful, please give it a star ⭐
It helps others discover agentic AI patterns!

Built with ❤️ for the Google Gemini Devpost Hackathon
